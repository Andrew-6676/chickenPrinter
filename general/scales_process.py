import logging
import re
import time

import serial
from colorama import Style, Fore

from general.reporter import Reporter

LOGGER = logging.getLogger('app')

def scales_reader(shared_data_obj, config=None):
	if config:
		scales_port = config.scales.port
	else:
		scales_port = 'COM2'

	# report = Reporter(config.report.database, config)

	# def save_to_db(w, r=0):
	# 	report.addRecord({'date': obj.getPartDate(), 'time': time.strftime('%H:%M:%S'), 'weight': w, 'rest': r,
	# 	                  'part': obj.getPartNumber()})

	def connect(port):
		connect = None
		while not connect or not connect.is_open:
			try:
				connect = serial.Serial(port, 9600, timeout=0.1)
			except Exception as exc:
				LOGGER.error(str(exc))
				print(Fore.RED + 'Не удалось открыть порт ' + port + Style.RESET_ALL, end='. ')
				print('Повтор через 5 секунд...')
				time.sleep(5)

		print(Fore.GREEN + '{} connected'.format(port) + Style.RESET_ALL)
		return connect

	# def get_weight(ser):
	# 	try:
	# 		ser.reset_output_buffer()
	# 		ser.write(b'\x00')
	# 		data = ser.readline()
	# 		match = re.findall(r'(-*)\s*([0-9]+\.\d+)', str(data))
	# 		if len(match) == 0:
	# 			print('Невозможно извлечь показания:', data)
	# 			return 0
	#
	# 		val = float(match[0][1])
	# 		if match[0][0] == '-':
	# 			val *= -1
	# 		print(Fore.BLACK + Style.BRIGHT + 'Вес: {} = {}'.format(data, val) + Style.RESET_ALL)
	# 		return val
	# 	except Exception as exc:
	# 		LOGGER.error(str(exc))
	# 		print('Error read weight: ', str(exc))
	# 		return -1

	print('BEGIN SCALES SCAN....', scales_port)
	LOGGER.info('BEGIN SCALES SCAN....' + scales_port)

	ser_scales = connect(scales_port)
	shared_data_obj.setScalesState(ser_scales.is_open)

	while True:
		time.sleep(0.01)
		# ждём когда придёт вес
		data = ser_scales.readline()
		if data:
			#data = ser_scales.readline()
			match = re.findall(r'-*0*([0-9]+\.\d+)', str(data))
			LOGGER.info(f'Read weight data: {data} = {match}')

			if match:
				# запускаем печать этикетки
				shared_data_obj.print(match[0])
			else:
				LOGGER.error(f'Ошибка чтения веса: {data}')
