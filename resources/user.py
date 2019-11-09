import json

import falcon

from resources.common import log, set_json

@falcon.before(log)
@falcon.before(set_json)
class User():
	def __init__(self, db_connection, q=None, config=None):
		self.qqq=q
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()

	def on_get(self, req, resp, id=None):
		if id:
			sql = """select * from user where id={} and deleted=0""".format(id)
			self.cursor.execute(sql)
			data = self.cursor.fetchone()
		else:
			sql = """select * from user where not deleted"""
			self.cursor.execute(sql)
			data = self.cursor.fetchall()


		resp.body = json.dumps(data)

	def on_post(self, req, resp):
		user = json.load(req.stream)
		print('post ', user)
		sql = f"insert into user (name, pass) values('{user['name']}', '{user['pass']}')"
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			resp.body = json.dumps({'status': 'ok'})
		except Exception as e:
			self.conn.rollback()
			print(e)
			resp.body = json.dumps({'status': 'error'})

	def on_put(self, req, resp, id=None):
		user = json.load(req.stream)
		print('put ', id, user)
		sql = f"update user set name='{user['name']}', pass='{user['pass']}' where id={id}"
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			resp.body = json.dumps({'status': 'ok'})
		except Exception as e:
			self.conn.rollback()
			print(e)
			resp.body = json.dumps({'status': 'error'})

	def on_delete(self, req, resp, id=None):
		print('del ', id)
		sql = f'update user set deleted=1 where id={id}'
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			resp.body = json.dumps({'status': 'ok'})
		except Exception as e:
			self.conn.rollback()
			print(e)
			resp.body = json.dumps({'status': 'error'})
