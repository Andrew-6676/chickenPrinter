import logging
import os
import sqlite3
import traceback

import falcon

from resources import Production, User, Index, Printer

LOGGER = logging.getLogger('app')
# ------------------------------------------------------------------------------------------------ #

def error_handler(req, resp, ex, params):
	trace = traceback.format_exc()
	LOGGER.error(f'{req.method}:{req.path}. {type(ex).__name__} - {ex}\n{trace}')
	# print(trace)
	raise ex
# ------------------------------------------------------------------------------------------------ #

def create_app(shared_obj, config, db_connection):
	database = config.report.database

	# def dict_factory(cursor, row):
	# 	d = {}
	# 	for idx, col in enumerate(cursor.description):
	# 		d[col[0]] = row[idx]
	# 	return d
	#
	# db_connection = sqlite3.connect(database, check_same_thread=False)
	# db_connection.row_factory = dict_factory

	app = falcon.API()
	app.add_error_handler(Exception, error_handler)

	production = Production(db_connection, shared_obj, config)
	app.add_route('/api/production', production)
	app.add_route('/api/production/{id}', production)

	user = User(db_connection, shared_obj, config)
	app.add_route('/api/users', user)
	app.add_route('/api/users/{id}', user)

	printer = Printer(db_connection, shared_obj, config)
	app.add_route('/api/print/{action}', printer)
	app.add_route('/api/print/{action}/{subaction}', printer)

	index = Index(db_connection, shared_obj, config)
	app.add_route('/', index)
	app.add_route('/api/{action}', index)

	app.add_static_route('/', os.path.abspath('static'))

	return app
