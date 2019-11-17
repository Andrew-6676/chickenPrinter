import logging
import sqlite3
import time
import winsound

import win32com
import win32com.client

from comtypes import CoInitializeEx

from general.reporter import Reporter
from printer.printer import genereate_file_to_print, xlsx_to_pdf

LOGGER = logging.getLogger('app')

class DataClass(object):
	ws = None
	scales_state = False
	pause = False
	config = None
	excel = None

	printData = None
	tareMode = False

	def __init__(self):
		print('**************** shared_data_obj INIT **********************')

	def hello(self):
		return 'hello'

	def setConfig(self, cfg):
		self.config = cfg
		CoInitializeEx()
		self.excel = win32com.client.Dispatch("Excel.Application")
		self.excel.Visible = False
		LOGGER.info('Excel started')

		def dict_factory(cursor, row):
			d = {}
			for idx, col in enumerate(cursor.description):
				d[col[0]] = row[idx]
			return d

		database = cfg.report.database
		db_connection = sqlite3.connect(database, check_same_thread=False)
		db_connection.row_factory = dict_factory

		self.cursor = db_connection.cursor()
		self.reporter = Reporter(db_connection, cfg)

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
		self.tareMode = mode

	def print(self, weight):
		if self.tareMode:
			LOGGER.error('Режим считывания тары')
			self.tareMode = False
			winsound.Beep(500, 300)
			return
		if not self.printData:
			LOGGER.error('Нет данных для печати')
			winsound.Beep(500, 150)
			winsound.Beep(500, 150)
			return 1

		winsound.Beep(4500, 70)
		winsound.Beep(4500, 70)
		winsound.Beep(3500, 200)

		code128 = self.printData['code128'].replace('-----', str(weight).replace('.','').zfill(5))

		sql = """select * from production where id={} and deleted=0""".format(self.printData['id'])
		self.cursor.execute(sql)
		data = self.cursor.fetchone()
		data['weight'] = weight
		data['date1'] = self.printData.get('date1')
		data['date2'] = self.printData.get('date2')
		data['date3'] = self.printData.get('date3')
		data['user'] = self.printData.get('user')
		data['ean_13'] = data['bar_code']
		data['code_128'] = code128

		t = time.time()

		template = self.printData.get("template", 0)
		x = genereate_file_to_print(f'./printer/templates/template_{template}.xlsx', data)
		print(time.time() - t)
		t = time.time()
		p = xlsx_to_pdf(x)
		print(time.time() - t)
		t = time.time()
		# print_file(p)
		print(time.time() - t)

		log_data = {
			'id_user': self.printData.get('user_id'),
			'id_product': data['id'],
			'weight': weight,
			'party': self.printData.get('date1'),
			'tare': self.printData.get('tare')
		}
		self.reporter.log_weighing(log_data)

		winsound.Beep(2500, 100)
