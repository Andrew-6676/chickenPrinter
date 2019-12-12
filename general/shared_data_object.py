import asyncio
import logging

import time
import traceback
import winsound

import win32com
import win32com.client

from comtypes import CoInitializeEx

from general.fetchData import fetchDataOne
from general.reporter import Reporter
from printer.printer import genereate_file_to_print, xlsx_to_pdf, print_file

LOGGER = logging.getLogger('app')

class DataClass(object):
	ws = None
	scales_state = False
	pause = False
	config = None
	excel = None

	printData = None
	tareMode = False

	def __init__(self,  cfg, db_connection, sendWSMessage):
		print('**************** shared_data_obj INIT **********************')
		self.config = cfg
		self.cursor = db_connection.cursor()
		self.reporter = Reporter(db_connection, cfg)
		self.sendWSMessage = sendWSMessage

	def hello(self):
		return 'hello'

	def getExcel(self):
		return self.excel

	def setWsClient(self, ws):
		self.ws = ws
	def getWsClient(self):
		return self.ws

	def setPause(self, p):
		self.pause = p

	def setScalesState(self, state):
		self.scales_state = state

	def getScalesState(self):
		return self.scales_state

	def setPrintData(self, data):
		if data and data.get('clear', None):
			self.printData = None
		else:
			self.printData = data


	def setTareMode(self, mode):
		LOGGER.debug(f'Set tare mode = {mode}')
		self.tareMode = mode

	async def print(self, weight):
		if self.tareMode:
			LOGGER.info('Режим считывания тары')
			self.tareMode = False
			winsound.Beep(4500, 70)
			winsound.Beep(3500, 200)
			return
		if not self.printData:
			LOGGER.error('Нет данных для печати')
			await self.sendWSMessage('messages', {'message': 'Нет данных для печати'})
			winsound.Beep(500, 150)
			winsound.Beep(500, 150)
			return 1

		await self.sendWSMessage('print', 'start')
		await asyncio.sleep(0.01)
		winsound.Beep(4500, 70)
		winsound.Beep(4500, 70)
		winsound.Beep(3500, 200)

		code128 = self.printData['code128'].replace('-----', str(weight).replace('.','').zfill(5))

		sql = """select * from "PRODUCTION" where "id"={} and "deleted"=0""".format(self.printData['id'])
		self.cursor.execute(sql)
		data = fetchDataOne(self.cursor)
		data['weight'] = weight
		data['date1'] = self.printData.get('date1')
		data['date2'] = self.printData.get('date2')
		data['date3'] = self.printData.get('date3')
		data['user'] = self.printData.get('user')
		data['ean_13'] = data['bar_code']
		data['code_128'] = code128


		template = self.printData.get("template", 0)
		try:
			await asyncio.sleep(0.01)
			times = []
			t0 = time.time()

			# формиреум xlxs с данными
			t = time.time()
			x = await genereate_file_to_print(f'./printer/templates/template_{template}.xlsx', data)
			times.append(round(time.time() - t, 3))
			# print('xls', time.time() - t)
			await asyncio.sleep(0.01)

			# генерируем pdf для печати
			t = time.time()
			p = xlsx_to_pdf(x)
			times.append(round(time.time() - t, 3))
			# print('pdf', time.time() - t)
			await asyncio.sleep(0.01)

			# отправляем на принтер
			t = time.time()
			print_file(p, self.config.printer.gs)
			# print('print', time.time() - t)
			tt = round(time.time() - t0, 3)
			times.append(round(time.time() - t, 3))
			# print('total times', times)

			log_data = {
				'id_user': self.printData.get('user_id'),
				'id_product': data['id'],
				'weight': weight,
				'party': self.printData.get('date1'),
				'tare': self.printData.get('tare')
			}
			self.reporter.log_weighing(log_data)

			await asyncio.sleep(0.01)
			LOGGER.info(f'Printing: time={str(times)}, {tt}c, template={template}')
			await self.sendWSMessage('print', 'end')
			winsound.Beep(2500, 700)
		except Exception as ex:
			await self.sendWSMessage('print', 'end')
			LOGGER.error('Printing error: ' + str(ex))
			traceback.print_exc()
