import os
import re
import sqlite3
import time
from multiprocessing import Process
from multiprocessing.managers import BaseManager

import serial
import waitress

import colorama
from colorama import Style, Fore

import logging

from app import Production, User
from config import Config
from report import Report

colorama.init()
####################################################################################


logging.basicConfig(
	format=u'%(levelname)-8s [%(asctime)s] %(message)s',
	level=logging.DEBUG,
	filename=u'log.log')


def create_app(q, config):
	# optlist, args = getopt.getopt(sys.argv[1:], 'd:', ['database='])
	database = './report.db'

	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	db_connection = sqlite3.connect(database, check_same_thread=False)
	db_connection.row_factory = dict_factory

	# for opt, arg in optlist:
	# 	if opt in ('-d', '--database'):
	# 		database = arg

	import os
	import falcon
	# from app import Config_Writer
	# from app import Reporter


	app = falcon.API()

	# config = Config_Writer('./config.ini')
	# report = Reporter(database, q, config)



	# app.add_route('/report/', report)
	# app.add_route('/report/{action}', report)

	production = Production(db_connection, q, config)
	app.add_route('/api/production', production)
	app.add_route('/api/production/{id}', production)

	user = User(db_connection, q, config)
	app.add_route('/api/users', user)
	app.add_route('/api/users/{id}', user)

	from app import Index
	index = Index(q, config)
	app.add_route('/', index)
	# app.add_route('/{action}', index)

	app.add_static_route('/', os.path.abspath('static'))

	return app


####################################################################################

class DataClass(object):
	part_number = 0
	part_date = '0000-00-00'
	rows = []
	rows_err = []
	scales_state = False
	controller_state = False
	pause = False
	config = None

	def setConfig(self, cfg):
		self.config = cfg

	def setPause(self, p):
		self.pause = p

	def setScalesState(self, state):
		self.scales_state = state

	def setControllerState(self, state):
		self.controller_state = state

	def getScalesState(self):
		return self.scales_state

	def getControllerState(self):
		return self.controller_state

	def startNewPart(self, n, d):
		logging.info(u'start new part: {}, {}'.format(n, d))
		self.rows = []
		self.rows_err = []
		self.setPartNumber(n)
		self.setPartDate(d)
		with open('curr_part.info', 'w') as file:
			file.write(str(n)+','+str(d))

	def setPartNumber(self, n):
		self.part_number = n

	def setPartDate(self, d):
		self.part_date = d

	def getPartNumber(self):
		return self.part_number

	def getPartDate(self):
		return self.part_date

	def addRow(self, x):
		self.rows.append(x)

	def addRowErr(self, x):
		self.rows_err.append(x)

	def getRows(self):
		return self.rows

	def getRowsErr(self):
		return self.rows_err

	def loadFromDb(self):
		database = './report.db'
		conn = sqlite3.connect(database, check_same_thread=False)
		cursor = conn.cursor()
		sql = """select `date`, `time`, weight 
				 from raw_data 
				 where `date`='{}' and part={} and weight>{}""".format(self.part_date,
                                                                       self.part_number,
                                                                       self.config.minWeight)
		cursor.execute(sql)
		data = cursor.fetchall()
		conn.close()
		if data and len(data):
			print('load current part from DB')
			logging.info('load current part from DB')
		for r in data:
			self.addRow({'time': r[0] + ' ' + r[1], 'weight': r[2], 'part': self.part_number})

####################################################################################

def scales_reader(obj, config=None):
	if config:
		scales_port = config.scalesPort
		controller_port = config.controllerPort
	else:
		scales_port = 'COM2'
		controller_port = 'COM4'

	report = Report('report.db', config)

	def save_to_db(w, r=0):
		report.addRecord({'date': obj.getPartDate(), 'time': time.strftime('%H:%M:%S'), 'weight': w, 'rest': r,
		                  'part': obj.getPartNumber()})

	def connect(port):
		connect = None
		while not connect or not connect.is_open:
			print(Fore.RED + 'Не удалось открыть порт ' + port + Style.RESET_ALL, end='. ')
			print('Повтор через 5 секунд...')
			time.sleep(50)
			try:
				connect = serial.Serial(port, 9600, timeout=2)
			except Exception as exc:
				logging.error(str(exc))
				print('Error during opening port: ', str(exc))
		print(Fore.GREEN + '{} connected'.format(port) + Style.RESET_ALL)
		return connect

	def get_weight(ser):
		try:
			ser.reset_output_buffer()
			ser.write(b'\x00')
			data = ser.readline()
			match = re.findall(r'(-*)\s*([0-9]+\.\d+)', str(data))
			if len(match) == 0:
				print('Невозможно извлечь показания:', data)
				return 0

			val = float(match[0][1])
			if match[0][0] == '-':
				val *= -1
			print(Fore.BLACK + Style.BRIGHT + 'Вес: {} = {}'.format(data, val) + Style.RESET_ALL)
			return val
		except Exception as exc:
			logging.error(str(exc))
			print('Error read weight: ', str(exc))
			return -1

	print('BEGIN SCALES SCAN....', scales_port, controller_port)

	ser_scales = connect(scales_port)
	obj.setScalesState(ser_scales.is_open)

	ser_controller = connect(controller_port)
	obj.setControllerState(ser_controller.is_open)

	cts = 1
	while True:
		# ждём когда можно будет взвешивать
		if ser_controller and ser_controller.is_open:
			if ser_controller.cts == 0:
				cts = 0
			if cts == 0 and ser_controller.cts == 1:
				cts = 1
				print(time.strftime('%Y-%m-%d %H:%M:%S'), ' Взвешиваем!')
				weight = get_weight(ser_scales)

				save_to_db(weight, 0)
				if weight < config.minWeight:
					logging.warning(u'small weight: {}'.format(weight))
					obj.addRowErr(
						{'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'weight': weight, 'part': obj.getPartNumber()})
				else:
					logging.info(u'get weight: {}'.format(weight))
					obj.addRow(
						{'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'weight': weight, 'part': obj.getPartNumber()})

				if weight < 0:
					logging.error(u'bad weight: {}. reconnect scales'.format(weight))
					obj.setScalesState(False)
					ser_scales.close()
					ser_scales = connect(scales_port)
					obj.setScalesState(ser_scales.is_open)

			time.sleep(config.pollingInterval)
		else:
			obj.setControllerState(False)
			print('connection with {} lost'.format(controller_port))
			cts = 1
			ser_controller = connect(controller_port)
		# if ser_controller:
		# 	print("Connected to port {}!".format(controller_port))
		# except:
		# 	ser_controller = None
		# 	print("error connect to port {}".format(controller_port))
		# 	obj.addRow({'time': '2019-01-01 11:44:56', 'weight': random() * 10})
		# 	time.sleep(2)


if __name__ == '__main__':
	logging.debug(u'START PROGRAMM')

	BaseManager.register('DataClass', DataClass)
	manager = BaseManager()
	manager.start()
	# расшареный между процесами объект с данными
	obj = manager.DataClass()
	cfg = Config('./config.ini')
	obj.setConfig(cfg)

	if os.path.exists('curr_part.info'):
		with open("curr_part.info", "r") as f:
			n,d = f.read().strip().split(',')
			# obj.setPartNumber(n)
			# obj.setPartDate(d)
			obj.startNewPart(n,d)
			obj.loadFromDb()

	# фоновый процесс работы с весами и контроллером
	process_scales = Process(target=scales_reader, args=(obj, cfg))
	process_scales.start()

	app = create_app(obj, cfg)
	waitress.serve(app, port=8080)

	process_scales.join()
