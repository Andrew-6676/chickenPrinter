import json
import random
import time
import traceback
import winsound

import fdb
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

import serial
import websockets
from colorama import Fore, Style

from resources import User, Production, Index, Printer, setup_middlewares

colorama.init()

logging.config.fileConfig('logger.conf')
LOGGER = logging.getLogger('app')
# LOGGER.handlers[0].doRollover()


def exit_handler():
	print('=========================My application is ending!===========================')


# ------------------------------------------------------------------------------------------------ #

LOGGER.info(u'START PROGRAMM')

cfg = Config('./config.ini').getConfig()
# -----------------------------------

WS = set()

async def notify_state():
	if WS:  # asyncio.wait doesn't accept an empty list
		message = json.dumps({'event': 'messages', 'data': json.dumps({'message':'Connected'})})
		await asyncio.wait([user.send(message) for user in WS])


async def sendWSMessage(event, data):
	if WS:  # asyncio.wait doesn't accept an empty list
		message = json.dumps({'event': event, 'data': json.dumps(data)})
		LOGGER.debug(f'[ws ----->] {data}')
		await asyncio.wait([client.send(message) for client in WS])


async def register(websocket):
	WS.add(websocket)
	await notify_state()

##############################################################################

print('Открытие базы данных...')
database = cfg.report.database
db_connection = fdb.connect(dsn=database, user='sysdba', password='masterkey')

# расшареный между процесами объект с данными
shared_data_obj = DataClass(cfg, db_connection, sendWSMessage)

# atexit.register(exit_handler)
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
			LOGGER.debug('[ws <-----] {}'.format(data['event']))
			if data['event'] == 'get-status':
				scst = shared_data_obj.getScalesState()
				await sendWSMessage('scales', {
					'connected': scst,
					'message': 'связь установлена' if scst else 'связь потеряна'
				})
			if data['event'] == 'get-tare':
				shared_data_obj.setTareMode(data['data'])
		except Exception as ex:
			print(ex)
			data = message
			await asyncio.sleep(0.01)

bound_handler = functools.partial(websocket_handler, shared_data_obj=shared_data_obj)
start_ws_server = websockets.serve(bound_handler, "0.0.0.0", 8888)


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
				await sendWSMessage('messages', {'message': f'error connect {port}'})
				await sendWSMessage('scales',
				                    '{connected: false, '
				                    'message: Ошибка подключения к порту ' + str(port) + '}')
				LOGGER.error(str(exc))
				print(Fore.RED + 'Не удалось открыть порт ' + port + Style.RESET_ALL, end='. ')
				print('Повтор через 5 секунд...')
				await asyncio.sleep(5)

		print(Fore.GREEN + '{} connected'.format(port) + Style.RESET_ALL)
		return connect

	print('BEGIN SCALES SCAN....', scales_port)
	LOGGER.info('BEGIN SCALES SCAN....' + scales_port)

	ser_scales = await connect(scales_port)
	shared_data_obj.setScalesState(True)
	await sendWSMessage('scales', '{connected: true, '
	                              'message: Подключено к порту ' + str(scales_port) + '}')
	new_weight = True  # признак того, что груз на весах сменили
	ttt = time.time()
	while True:
		await asyncio.sleep(0.01)

		# ждём когда придёт стабильный не нулевой вес
		data = ser_scales.readline()

		# КУСОК КОДА ДЛЯ ТЕСТИРОВАНИЯ ПОКА НЕТ ВЕСОВ
		# if (time.time() - ttt) > 7:
		# 	ttt = time.time()
		# 	cw = abs(round(random.random() * 10  - 1, 3))
		# 	data = '__ST___________' + str(cw) + 'kg'
		# 	print(data, len(data))
		# 	await asyncio.sleep(0.01)
		# else:
		# 	await asyncio.sleep(1.01)
		# 	data = '__ST___________' + '0.000' + 'kg'

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
						await shared_data_obj.print(curr_weight)
					else:
						# глухой и долгий бууууууп
						winsound.Beep(200, 900)
						LOGGER.error('Вес слишком мал:' + str(curr_weight))
						# await sendWSMessage('weight', curr_weight)
						await sendWSMessage('messages', {'message': 'Вес слишком мал:' + str(curr_weight)})
			except Exception as ex:
				LOGGER.error(f'Ошибка чтения веса: {data}: ' + str(ex))
				traceback.print_exc()
		else:
			await asyncio.sleep(0.01)
			#LOGGER.error(f'Ошибка взвешивания: {str(data)}')
			#await sendWSMessage('messages', f'Ошибка взвешивания: {str(data)}')



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

	printer = Printer(db_connection, shared_obj, config, sendWSMessage)
	app.add_routes([
		web.get('/api/print/{action}', printer.get),
		web.post('/api/print/{action}', printer.post),
		web.get('/api/print/{action}/{subaction}', printer.get),
		web.post('/api/print/{action}/{subaction}', printer.post),
		web.delete('/api/print/{action}/{subaction}', printer.delete)
	])

	index = Index(db_connection, shared_obj, config)
	app.add_routes([
		web.get('/', index.get),
		web.get('/users', index.get),
		web.get('/weighing', index.get),
		web.get('/templates', index.get),
		web.get('/production/list', index.get),
		web.get('/api/{action}', index.get)
	])

	app.add_routes([
		web.static('/', './static'),
	])

	setup_middlewares(app)
	runner = web.AppRunner(app, logger=LOGGER)
	await runner.setup()
	site = web.TCPSite(runner, '0.0.0.0', 8080)
	await site.start()


####################################################################################

# db = connect_db(cfg)

ioloop = asyncio.get_event_loop()
tasks = [
	ioloop.create_task(scales_reader(shared_data_obj, cfg)),
	start_ws_server,
	http_server(db_connection, shared_data_obj, cfg),
]
wait_tasks = asyncio.wait(tasks)

ioloop.run_until_complete(wait_tasks)
asyncio.get_event_loop().run_forever()
