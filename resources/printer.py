import asyncio
import json
import logging
import os
import sys
import time
import traceback
import winsound

from aiohttp import web

from general.fetchData import fetchDataAll, fetchDataOne
from printer.printer import genereate_file_to_print, xlsx_to_pdf, print_file

LOGGER = logging.getLogger('app')

class Printer():
	def __init__(self, db_connection, shared_data_obj=None, config=None, smf=None):
		self.shared_data_obj = shared_data_obj
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()
		self.smf = smf

	async def get(self, request):
		action = request.match_info.get('action', None)
		subaction = request.match_info.get('subaction', None)
		if action == 'templates' and not subaction:
			sql = 'select * from "TEMPLATES"'
			self.cursor.execute(sql)
			data = fetchDataAll(self.cursor)
			return web.Response(text=json.dumps(data))
		if action == 'templates' and subaction:
			with open(f'./printer/templates/template_{subaction}.xlsx', 'rb') as f:
				return web.Response(body=f.read())

	async def delete(self, request):
		action = request.match_info.get('action', None)
		subaction = request.match_info.get('subaction', None)
		if action == 'templates' and subaction:
			sql = f'delete from "TEMPLATES" where "id"={subaction}'
			try:
				self.cursor.execute(sql)
				self.conn.commit()
				try:
					os.remove(f'./printer/templates/template_{subaction}.xlsx')
				except:
					pass
				try:
					os.remove(f'./printer/templates/template_{subaction}_total.xlsx')
				except:
					pass
				LOGGER.debug('RUN SQL: ' + sql)
				return web.Response(text=json.dumps({'status': 'ok'}))
			except Exception as e:
				self.conn.rollback()
				LOGGER.error(str(e) + '; SQL = ' + sql)
				return web.Response(text=json.dumps({'status': 'error'}))

	async def post(self, request):
		action = request.match_info.get('action', None)
		subaction = request.match_info.get('subaction', None)

		if action == 'templates' and subaction == 'append':
			params = json.loads(await request.text())
			sql = f'insert into "TEMPLATES" ("name") values (\'{params["title"]}\') RETURNING "id"'
			try:
				self.cursor.execute(sql)
				self.conn.commit()
				self.cursor.execute('select GEN_ID("GEN_public_templates_ID",0) from RDB$DATABASE;')
				res = fetchDataOne(self.cursor)
				return web.Response(text=json.dumps({'new_id': res['GEN_ID']}))
			except Exception as ex:
				LOGGER.error('Upload template error: ' + str(ex) + '. SQL=' + sql)
				return web.Response(text=json.dumps({'status': 'error'}))

		if action == 'templates' and subaction == 'upload':
			data = await request.post()
			tid = data['id'] + ('_total' if data['total']=='true' else '')
			with open(f'./printer/templates/template_{tid}.xlsx', 'wb') as f:
				f.write(data['file'].file.read())
			return web.Response(text=json.dumps({'status': 'ok'}))

		if (action=='label' or action == 'total') and subaction==None:
			params = json.loads(await request.text())
			await self.smf('print', f'start{" totals" if action == "total" else ""}')
			winsound.Beep(4500, 70)
			sql = """select * from "PRODUCTION" where "id"={} and "deleted"=0""".format(params['id'])
			self.cursor.execute(sql)
			data = fetchDataOne(self.cursor)
			data['weight'] = params.get('weight') if action == 'label' else params.get('totalWeight')
			data['date1'] = params.get('date1')
			data['date2'] = params.get('date2')
			data['date3'] = params.get('date3')
			data['user'] = params.get('user')
			data['code_128'] = params.get('code128')
			data['packs'] = params.get('packs')
			data['ean_13'] = data['bar_code']

			template = str(params.get("template", 0))
			if action == 'total':
				template += '_total'
			try:
				times = []
				t0 = time.time()

				# формиреум xlxs с данными
				t = time.time()
				x = await genereate_file_to_print(f'./printer/templates/template_{template}.xlsx', data)
				times.append(round(time.time() - t, 3))
				# print('generate xls', time.time() - t)
				await asyncio.sleep(0.01)

				# генерируем pdf для печати
				t = time.time()
				p = xlsx_to_pdf(x)
				times.append(round(time.time() - t, 3))
				# print('generate pdf', time.time() - t)
				await asyncio.sleep(0.01)

				# отправляем на принтер
				t = time.time()
				print_file(p, self.config.printer.gs)
				print('print file', time.time() - t)
				tt = round(time.time() - t0, 3)
				times.append(round(time.time() - t, 3))
				# print('total', tt)

				winsound.Beep(1000, 100)
				LOGGER.info(f'Printing{" totals" if action == "total" else ""}: time={str(times)}, {tt}c, template={template}')
				await self.smf('print', f'end{" totals" if action == "total" else ""}')
				# if action == "total":
				# 	sys.exit(2)
			except Exception as ex:
				LOGGER.error('Printing error: ' + str(ex))
				await self.smf('print', f'end{" totals" if action == "total" else ""}')
				traceback.print_exc()

			return web.Response(text=json.dumps({'status': 'ok'}))

		if action=='prepare' and subaction==None:
			params = json.loads(await request.text())
			self.shared_data_obj.setPrintData(params)
			return web.Response(text=json.dumps({'status': 'ok'}))
