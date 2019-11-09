import atexit
import os
import logging.config
import traceback

from multiprocessing import Process
from multiprocessing.managers import BaseManager

import colorama
import waitress

from general.config import Config
from general.scales_process import scales_reader
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

	app = create_app(shared_obj, cfg)
	waitress.serve(app, port=8080)

	process_scales.join()
