import json
import sys
import winsound

from aiohttp import web
import atexit
import logging.config

import colorama

from general.config import Config

from general.shared_data_object import DataClass
import asyncio
import functools
import logging
import re
import sqlite3
import time

import serial
import websockets
from colorama import Fore, Style, Back

from resources import User, Production, Index, Printer

colorama.init()

logging.config.fileConfig('logger.conf')
LOGGER = logging.getLogger('app')
LOGGER.handlers[0].doRollover()


def exit_handler():
	print('=========================My application is ending!===========================')


# ------------------------------------------------------------------------------------------------ #

LOGGER.info(u'START PROGRAMM')

cfg = Config('./config.ini').getConfig()


def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d


print('Открытие базы данных...')
database = cfg.report.database
db_connection = sqlite3.connect(database, check_same_thread=False)
db_connection.row_factory = dict_factory

# расшареный между процесами объект с данными
shared_data_obj = DataClass()
shared_data_obj.setConfig(cfg)

atexit.register(exit_handler)

# -----------------------------------

WS = set()


async def notify_state():
	if WS:  # asyncio.wait doesn't accept an empty list
		message = json.dumps({'event': 'messages', 'data': 'Connected'})
		await asyncio.wait([user.send(message) for user in WS])


async def sendWSMessage(event, data):
	if WS:  # asyncio.wait doesn't accept an empty list
		message = json.dumps({'event': event, 'data': json.dumps(data)})
		LOGGER.info(f'[ws ----->] {data}')
		await asyncio.wait([client.send(message) for client in WS])


async def register(websocket):
	WS.add(websocket)
	await notify_state()


##############################################################################

def connect_db(cfg):
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	print('Открытие базы данных...')
	database = cfg.report.database
	db_connection = sqlite3.connect(database, check_same_thread=False)
	db_connection.row_factory = dict_factory

	return db_connection


##############################################################################

async def websocket_handler(websocket, path, shared_data_obj=None):
	print('-----> CONNECTED:', websocket, path)
	await register(websocket)
	shared_data_obj.setWsClient(websocket)
	shared_data_obj.setPrintData(None)
	while True:
		message = await websocket.recv()
		try:
			data = json.loads(message.replace('\\', ''))
			LOGGER.info('[ws <-----] {}'.format(data['event']))
			if data['event'] == 'get-status':
				await sendWSMessage('scales',
				                    {'connected': True, 'message': 'Подключено к порту COM3'})
			if data['event'] == 'get-tare':
				shared_data_obj.setTareMode(True)
		except Exception as ex:
			print(ex)
			data = message
			await asyncio.sleep(0.01)

	# 	scales_port = 'COM3'
	# 	if shared_data_obj.setScalesState():
	# 		await sendWSMessage('scales', '{connected: true, '
	# 		                              'message: Подключено к порту ' + scales_port + '}')
	# 	else:
	# 		await sendWSMessage('scales', '{connected: false, '
	# 		                              'message: Не удалось подключитсья к порту ' + scales_port + '}')
	# else:
	# 	await websocket.send(json.dumps({'event':'messages', 'data': 'test response'}))


bound_handler = functools.partial(websocket_handler, shared_data_obj=shared_data_obj)
start_ws_server = websockets.serve(bound_handler, "localhost", 8888)


##############################################################################

async def scales_reader(shared_data_obj, config=None):
	if config:
		scales_port = config.scales.port
	else:
		scales_port = 'COM2'

	async def connect(port):
		connect = None
		while not connect or not connect.is_open:
			try:
				connect = serial.Serial(port, 9600, timeout=0.1)
			except Exception as exc:
				shared_data_obj.setScalesState(False)
				await sendWSMessage('message', f'error connect {port}')
				await sendWSMessage('scales',
				                    '{connected: false, '
				                    'message: Ошибка подключения к порту ' + str(port) + '}')
				LOGGER.error(str(exc))
				print(Fore.RED + 'Не удалось открыть порт ' + port + Style.RESET_ALL, end='. ')
				print('Повтор через 5 секунд...')
				time.sleep(5)

		print(Fore.GREEN + '{} connected'.format(port) + Style.RESET_ALL)
		return connect

	print('BEGIN SCALES SCAN....', scales_port)
	LOGGER.info('BEGIN SCALES SCAN....' + scales_port)

	ser_scales = await connect(scales_port)
	shared_data_obj.setScalesState(True)
	await sendWSMessage('scales', '{connected: true, '
	                              'message: Подключено к порту ' + str(scales_port) + '}')
	new_weight = True  # признак того, что груз на весах сменили
	while True:
		await asyncio.sleep(0.01)
		# ждём когда придёт стабильный не нулевой вес
		data = ser_scales.readline()
		if len(data) == 22:
			try:
				match = re.findall(r'..(..).*-*0*([0-9]+\.\d+)', str(data))
				curr_weight = float(match[0][1])
				if curr_weight == 0 and not new_weight:
					await sendWSMessage('weight', 0)
					new_weight = True
					continue
				if match and match[0][0] == 'ST' and new_weight and curr_weight != 0:
					new_weight = False  # чтобы не считввать многократно вес одной и той же курицы
					LOGGER.info(f'Read weight data: {data} = {match}')
					if curr_weight > float(config.scales.minweight):
						# сообщаем в браузер о факте взвешивания
						await sendWSMessage('weight', curr_weight)
						shared_data_obj.print(curr_weight)
					else:
						winsound.Beep(300, 700)
						LOGGER.error(f'Вес слишком мал: {curr_weight}')
						await sendWSMessage('weight', curr_weight)
						await sendWSMessage('messages', f'Вес слишком мал: {curr_weight}')
			except Exception as ex:
				LOGGER.error(f'Ошибка чтения веса: {data}')
				print(ex)
		else:
			pass
		# await sendWSMessage('messages', f'error read weight {data}')
		# LOGGER.error(f'Ошибка чтения веса: {data}')


####################################################################################

async def http_server(db_connection, shared_obj, config):
	app = web.Application()

	user = User(db_connection, shared_obj, config)
	app.add_routes([
		web.get('/api/users', user.get),
		web.get('/api/users/{id}', user.get),
		web.post('/api/users', user.post),
		web.put('/api/users/{id}', user.put),
		web.delete('/api/users/{id}', user.delete),
	])

	production = Production(db_connection, shared_obj, config)
	app.add_routes([
		web.post('/api/production', production.post),
		web.get('/api/production', production.get),
		web.get('/api/production/{id}', production.get),
		web.put('/api/production/{id}', production.put),
		web.delete('/api/production/{id}', production.delete),
	])

	printer = Printer(db_connection, shared_obj, config)
	app.add_routes([
		web.get('/api/print/{action}', printer.get),
		web.post('/api/print/{action}', printer.post),
		web.post('/api/print/{action}/{subaction}', printer.post)
	])

	index = Index(db_connection, shared_obj, config)
	app.add_routes([
		web.get('/', index.get),
		web.get('/api/{action}', index.get)
	])

	app.add_routes([
		web.static('/', './static')
	])

	runner = web.AppRunner(app)
	await runner.setup()
	site = web.TCPSite(runner, 'localhost', 8080)
	await site.start()


####################################################################################

db = connect_db(cfg)

ioloop = asyncio.get_event_loop()
tasks = [
	ioloop.create_task(scales_reader(shared_data_obj, cfg)),
	start_ws_server,
	http_server(db, shared_data_obj, cfg),
]
wait_tasks = asyncio.wait(tasks)

ioloop.run_until_complete(wait_tasks)
asyncio.get_event_loop().run_forever()
