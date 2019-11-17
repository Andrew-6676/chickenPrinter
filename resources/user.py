import json

from aiohttp import web

class User:
	def __init__(self, db_connection, q=None, config=None):
		self.qqq=q
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()

	async def get(self, request):
		id = request.match_info.get('id', None)
		if id:
			sql = """select * from user where id={} and deleted=0""".format(id)
			self.cursor.execute(sql)
			data = self.cursor.fetchone()
		else:
			sql = """select * from user where not deleted"""
			self.cursor.execute(sql)
			data = self.cursor.fetchall()

		return web.Response(text=json.dumps(data))

	async def post(self, request):
		user = json.loads(await request.text())
		print('post ', user)
		sql = f"insert into user (name, pass) values('{user['name']}', '{user['pass']}')"
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			return web.Response(text=json.dumps({'status': 'ok'}))
		except Exception as e:
			self.conn.rollback()
			print(e)
			return web.Response(text=json.dumps({'status': 'error'}))

	async def put(self, request):
		user = json.loads(await request.text())
		id = request.match_info.get('id', None)
		print('put ', id, user)
		sql = f"update user set name='{user['name']}', pass='{user['pass']}' where id={id}"
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			return web.Response(text=json.dumps({'status': 'ok'}))
		except Exception as e:
			self.conn.rollback()
			print(e)
			return web.Response(text=json.dumps({'status': 'error'}))

	async def delete(self, request):
		id = request.match_info.get('id', None)
		print('del ', id)
		sql = f'update user set deleted=1 where id={id}'
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			return web.Response(text=json.dumps({'status': 'ok'}))
		except Exception as e:
			self.conn.rollback()
			print(e)
			return web.Response(text=json.dumps({'status': 'error'}))
