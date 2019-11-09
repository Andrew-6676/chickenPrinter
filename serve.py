import glob
import logging
import os

import re
from multiprocessing import Process
from multiprocessing.managers import BaseManager

import colorama
import waitress

from general.config import Config
from general.scales_process import scales_reader
from resources import create_app
from general.shared_data_object import DataClass
from general.websocket_server import start_ws_server

colorama.init()

# ------------------------------------------------------------------------------------------------ #

if __name__ == '__main__':
	log_num = 0
	logs = glob.glob("./logs/*.log")
	if len(logs) > 0:
		log_num = int(re.findall(r'log_(\d+)\.log', logs[len(logs) - 1])[0]) + 1

	logging.basicConfig(
		format=u'%(levelname)-8s [%(asctime)s] %(message)s',
		level=logging.DEBUG,
		filename=f'./logs/log_{log_num}.log')

	logging.debug(u'START PROGRAMM')
	cfg = Config('./config.ini').getConfig()
	# start_ws_server(8888)

	BaseManager.register('DataClass', DataClass)
	manager = BaseManager()
	manager.start()
	# расшареный между процесами объект с данными
	obj = manager.DataClass()
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
