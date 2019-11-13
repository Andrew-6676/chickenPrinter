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
	scales_state = False
	pause = False
	config = None
	excel = None

	printData = None

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

	def setPause(self, p):
		self.pause = p

	def setScalesState(self, state):
		self.scales_state = state

	def getScalesState(self):
		return self.scales_state

	def setPrintData(self, data):
		self.printData = data

	def print(self, weight):
		if not self.printData:
			LOGGER.error('Нет данных для печати')
			winsound.Beep(1500, 100)
			winsound.Beep(1500, 100)
			winsound.Beep(1000, 200)
			return 1

		winsound.Beep(4500, 70)
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
			'id_party': 0,
			'tare': self.printData.get('tare')
		}
		self.reporter.log_weighing(log_data)

		winsound.Beep(2500, 100)

	# def startNewPart(self, n, d):
	# 	logging.info(u'start new part: {}, {}'.format(n, d))
	# 	self.rows = []
	# 	self.rows_err = []
	# 	self.setPartNumber(n)
	# 	self.setPartDate(d)
	# 	with open('curr_part.info', 'w') as file:
	# 		file.write(str(n)+','+str(d))
	#
	# def setPartNumber(self, n):
	# 	self.part_number = n
	#
	# def setPartDate(self, d):
	# 	self.part_date = d
	#
	# def getPartNumber(self):
	# 	return self.part_number
	#
	# def getPartDate(self):
	# 	return self.part_date
	#
	# def addRow(self, x):
	# 	self.rows.append(x)
	#
	# def addRowErr(self, x):
	# 	self.rows_err.append(x)
	#
	# def getRows(self):
	# 	return self.rows
	#
	# def getRowsErr(self):
	# 	return self.rows_err
	#
	# def loadFromDb(self):
	# 	database = './report.db'
	# 	conn = sqlite3.connect(database, check_same_thread=False)
	# 	cursor = conn.cursor()
	# 	sql = """select `date`, `time`, weight
	# 			 from raw_data
	# 			 where `date`='{}' and part={} and weight>{}""".format(self.part_date,
    #                                                                    self.part_number,
    #                                                                    self.config.minWeight)
	# 	cursor.execute(sql)
	# 	data = cursor.fetchall()
	# 	conn.close()
	# 	if data and len(data):
	# 		print('load current part from DB')
	# 		logging.info('load current part from DB')
	# 	for r in data:
	# 		self.addRow({'time': r[0] + ' ' + r[1], 'weight': r[2], 'part': self.part_number})
