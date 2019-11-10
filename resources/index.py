import json

import falcon

from resources.common import log

@falcon.before(log)
class Index():
	def __init__(self, db_connection, shared_data_obj=None, config=None):
		self.shared_data_obj = shared_data_obj
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()

	def on_get(self, req, resp, action=None):
		# resp.body = filename
		if not action:
			resp.content_type = 'text/html'
			with open('./static/index.html', 'r') as f:
				print('index')
				resp.body = f.read()

		if action == 'params':
			sql = 'select * from params'
			self.cursor.execute(sql)
			data = self.cursor.fetchall()
			resp.body = json.dumps(data)
			return

		raise falcon.HTTPNotFound(title=f'{req.method}:{action} - not found')
