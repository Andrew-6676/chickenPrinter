import json

import falcon

from resources.common import log, set_json


@falcon.before(log)
@falcon.before(set_json)
class Production():
	def __init__(self, db_connection, q=None, config=None):
		self.qqq=q
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()

	def on_get(self, req, resp, id=None):
		if id:
			if id == 'new':
				sql = 'select max(id)+1 as id from production'
				self.cursor.execute(sql)
				data = self.cursor.fetchone()
			else:
				sql = """select * from production where id={} and deleted=0""".format(id)
				self.cursor.execute(sql)
				data = self.cursor.fetchone()
		else:
			sql = """select * from production where not deleted"""
			self.cursor.execute(sql)
			data = self.cursor.fetchall()

		resp.body = json.dumps(data)

	def on_post(self, req, resp):
		prod = json.load(req.stream)
		print('post ', prod)
		sql = "insert into production " \
		      "(group_name, name, descr, ingridients, storage_conditions, " \
		      "nutritional_value, energy_value, RC_BY, TU_BY, STB, " \
		      "expiration_date, bar_code, code128_prefix) " \
		      "values" \
		      f"('{prod['group_name']}', '{prod['name']}', '{prod['descr']}', '{prod['ingridients']}', '{prod['storage_conditions']}', " \
		      f"'{prod['nutritional_value']}', '{prod['energy_value']}', '{prod['RC_BY']}', '{prod['TU_BY']}', '{prod['STB']}', " \
		      f"'{prod['expiration_date']}', '{prod['bar_code']}', '{prod['code128_prefix']}')"
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			resp.body = json.dumps({'status': 'ok'})
		except Exception as e:
			self.conn.rollback()
			print(e)
			resp.body = json.dumps({'status': 'error'})

	def on_put(self, req, resp, id=None):
		prod = json.load(req.stream)
		print('put ', prod)
		sql = "update production " \
			  "set " \
		      f"group_name='{prod['group_name']}', " \
		      f"name='{prod['name']}', " \
		      f"descr='{prod['descr']}', " \
		      f"ingridients='{prod['ingridients']}', " \
		      f"storage_conditions='{prod['storage_conditions']}', " \
		      f"nutritional_value='{prod['nutritional_value']}', " \
		      f"energy_value='{prod['energy_value']}', " \
		      f"RC_BY='{prod['RC_BY']}', " \
		      f"TU_BY='{prod['TU_BY']}', " \
		      f"STB='{prod['STB']}', " \
		      f"expiration_date='{prod['expiration_date']}', " \
		      f"bar_code='{prod['bar_code']}' " \
		      f"bar_code='{prod['code128_prefix']}' " \
		      f"where id={id}"
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			resp.body = json.dumps({'status': 'ok'})
		except Exception as e:
			self.conn.rollback()
			print(e)
			resp.body = json.dumps({'status': 'error'})

	def on_delete(self, req, resp, id=None):
		print('delete prod', id)
		sql = f"update production set deleted=1 where id={id}"
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			resp.body = json.dumps({'status': 'ok'})
		except Exception as e:
			self.conn.rollback()
			print(e)
			resp.body = json.dumps({'status': 'error'})
