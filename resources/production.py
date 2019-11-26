import json
import logging

from aiohttp import web

from general.fetchData import fetchDataAll, fetchDataOne

LOGGER = logging.getLogger('app')

class Production:
	def __init__(self, db_connection, q=None, config=None):
		self.qqq=q
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()

	async def get(self, request):
		id = request.match_info.get('id', None)
		if id:
			if id == 'new':
				sql = 'select max("id")+1 as "id" from "PRODUCTION"'
				self.cursor.execute(sql)
				data = fetchDataOne(self.cursor)
			else:
				sql = 'select * from "PRODUCTION" where "id"={} and "deleted"=0'.format(id)
				self.cursor.execute(sql)
				data = fetchDataOne(self.cursor)
		else:
			sql = 'select * from "PRODUCTION" where "deleted"=0 order by "name"'
			self.cursor.execute(sql)
			data = fetchDataAll(self.cursor)

		try:
			return web.Response(text=json.dumps(data))
		except Exception as ex:
			LOGGER.error(str(ex) + '; SQL = ' + sql)



	async def post(self, request):
		prod = json.loads(await request.text())
		print('post ', prod)
		sql = 'insert into "PRODUCTION" ' \
		      '("group_name", "name", "descr", "ingridients", "storage_conditions", ' \
		      '"nutritional_value", "energy_value", "RC_BY", "TU_BY", "STB", ' \
		      '"expiration_date", "bar_code", "code128_prefix") ' \
		      'values' \
		      f"('{prod['group_name']}', '{prod['name']}', '{prod['descr']}', '{prod['ingridients']}', '{prod['storage_conditions']}', " \
		      f"'{prod['nutritional_value']}', '{prod['energy_value']}', '{prod['RC_BY']}', '{prod['TU_BY']}', '{prod['STB']}', " \
		      f"'{prod['expiration_date']}', '{prod['bar_code']}', '{prod['code128_prefix']}')"
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			LOGGER.debug('RUN SQL: ' + sql)
			return web.Response(text=json.dumps({'status': 'ok'}))
		except Exception as e:
			self.conn.rollback()
			LOGGER.error(str(e) + '; SQL = ' + sql)
			return web.Response(text=json.dumps({'status': 'error'}))

	async def put(self, request):
		prod = json.loads(await request.text())
		id = request.match_info.get('id', None)
		print('put ', prod)
		sql = 'update "PRODUCTION" ' \
			  "set " \
		      f"\"group_name\"='{prod['group_name']}', " \
		      f"\"name\"='{prod['name']}', " \
		      f"\"descr\"='{prod['descr']}', " \
		      f"\"ingridients\"='{prod['ingridients']}', " \
		      f"\"storage_conditions\"='{prod['storage_conditions']}', " \
		      f"\"nutritional_value\"='{prod['nutritional_value']}', " \
		      f"\"energy_value\"='{prod['energy_value']}', " \
		      f"\"RC_BY\"='{prod['RC_BY']}', " \
		      f"\"TU_BY\"='{prod['TU_BY']}', " \
		      f"\"STB\"='{prod['STB']}', " \
		      f"\"expiration_date\"='{prod['expiration_date']}', " \
		      f"\"bar_code\"='{prod['bar_code']}', " \
		      f"\"code128_prefix\"='{prod['code128_prefix']}' " \
		      f"where \"id\"={id}"
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			LOGGER.debug('RUN SQL: ' + sql)
			return web.Response(text=json.dumps({'status': 'ok'}))
		except Exception as e:
			self.conn.rollback()
			LOGGER.error(str(e) + '; SQL = ' + sql)
			return web.Response(text=json.dumps({'status': 'error'}))

	async def delete(self, request):
		id = request.match_info.get('id', None)
		print('delete prod', id)
		sql = f'update "PRODUCTION" set "deleted"=1 where "id"={id}'
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			LOGGER.debug('RUN SQL: ' + sql)
			return web.Response(text=json.dumps({'status': 'ok'}))
		except Exception as e:
			self.conn.rollback()
			LOGGER.error(str(e) + '; SQL = ' + sql)
			return web.Response(text=json.dumps({'status': 'error'}))
