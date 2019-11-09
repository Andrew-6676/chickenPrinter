import logging
import re
import time

import serial
from colorama import Style, Fore

from general.reporter import Reporter

LOGGER = logging.getLogger('app')

def scales_reader(obj, config=None):
	if config:
		scales_port = config.scales.port
		controller_port = 'COM4'
	else:
		scales_port = 'COM2'
		controller_port = 'COM4'

	report = Reporter(config.report.database, config)

	def save_to_db(w, r=0):
		report.addRecord({'date': obj.getPartDate(), 'time': time.strftime('%H:%M:%S'), 'weight': w, 'rest': r,
		                  'part': obj.getPartNumber()})

	def connect(port):
		connect = None
		while not connect or not connect.is_open:
			try:
				connect = serial.Serial(port, 9600, timeout=2)
			except Exception as exc:
				LOGGER.error(str(exc))
			print(Fore.RED + 'Не удалось открыть порт ' + port + Style.RESET_ALL, end='. ')
			print('Повтор через 5 секунд...')
			time.sleep(50)

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
			LOGGER.error(str(exc))
			print('Error read weight: ', str(exc))
			return -1

	print('BEGIN SCALES SCAN....', scales_port)

	ser_scales = connect(scales_port)
	obj.setScalesState(ser_scales.is_open)

	ser_controller = connect(controller_port)
	obj.setControllerState(ser_controller.is_open)

	cts = 1
	while True:
		# ждём когда можно будет взвешивать - стабильный вес больше минимально заданного
		if ser_controller and ser_controller.is_open:
			if ser_controller.cts == 0:
				cts = 0
			if cts == 0 and ser_controller.cts == 1:
				cts = 1
				print(time.strftime('%Y-%m-%d %H:%M:%S'), ' Взвешиваем!')
				weight = get_weight(ser_scales)

				save_to_db(weight, 0)
				if weight < config.minWeight:
					LOGGER.warning(u'small weight: {}'.format(weight))
					obj.addRowErr(
						{'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'weight': weight, 'part': obj.getPartNumber()})
				else:
					LOGGER.info(u'get weight: {}'.format(weight))
					obj.addRow(
						{'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'weight': weight, 'part': obj.getPartNumber()})

				if weight < 0:
					LOGGER.error(u'bad weight: {}. reconnect scales'.format(weight))
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
