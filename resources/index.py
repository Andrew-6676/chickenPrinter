import json

from aiohttp import web


class Index:
	def __init__(self, db_connection, shared_data_obj=None, config=None):
		self.shared_data_obj = shared_data_obj
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()

	async def get(self, request):
		action = request.match_info.get('action', None)
		if not action:
			with open('./static/index.html', 'r') as f:
				print('index')
				return web.Response(body=f.read(), content_type='text/html')

		if action == 'params':
			sql = 'select * from params'
			self.cursor.execute(sql)
			data = self.cursor.fetchall()
			return web.Response(text=json.dumps(data))

		if action == 'ping':
			return web.Response(text='{"pong":"ok"}')
		#raise falcon.HTTPNotFound(title=f'{req.method}:{action} - not found')
