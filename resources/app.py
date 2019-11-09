import os
import sqlite3

import falcon

from resources import Production, User, Index


def create_app(q, config):
	database = './report.db'

	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	db_connection = sqlite3.connect(database, check_same_thread=False)
	db_connection.row_factory = dict_factory

	app = falcon.API()

	production = Production(db_connection, q, config)
	app.add_route('/api/production', production)
	app.add_route('/api/production/{id}', production)

	user = User(db_connection, q, config)
	app.add_route('/api/users', user)
	app.add_route('/api/users/{id}', user)

	index = Index(q, config)
	app.add_route('/', index)

	app.add_static_route('/', os.path.abspath('static'))

	return app
