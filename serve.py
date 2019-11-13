import atexit
import os
import logging.config
import sqlite3
import traceback

from multiprocessing import Process
from multiprocessing.managers import BaseManager

import colorama
import waitress

from general.config import Config
from general.scales_process import scales_reader
from general.websocket_server import start_ws_server
from resources import create_app
from general.shared_data_object import DataClass

colorama.init()

logging.config.fileConfig('logger.conf')
LOGGER = logging.getLogger('app')
LOGGER.handlers[0].doRollover()

def exit_handler():
	print('=========================My application is ending!===========================')

# ------------------------------------------------------------------------------------------------ #
if __name__ == '__main__':
	LOGGER.info(u'START PROGRAMM')

	cfg = Config('./config.ini').getConfig()
	# start_ws_server(8888)

	def dict_factory(cursor, row):
			d = {}
			for idx, col in enumerate(cursor.description):
				d[col[0]] = row[idx]
			return d


	print('Открытие базы данных...')
	database = cfg.report.database
	db_connection = sqlite3.connect(database, check_same_thread=False)
	db_connection.row_factory = dict_factory

	BaseManager.register('DataClass', DataClass)
	manager = BaseManager()
	manager.start()
	# расшареный между процесами объект с данными
	shared_obj = manager.DataClass()
	shared_obj.setConfig(cfg)

	atexit.register(exit_handler)


	# фоновый процесс работы с весами и контроллером
	process_scales = Process(target=scales_reader, args=(shared_obj, cfg))
	process_scales.start()

	# process_ws = Process(target=start_ws_server, args=(8888, shared_obj, cfg))
	# process_ws.start()

	app = create_app(shared_obj, cfg, db_connection)
	waitress.serve(app, port=8080)

	process_scales.join()
	# process_ws.join()
	#print('****************-------------*************')
