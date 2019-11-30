import json
import logging
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

	async def post(self, request):
		action = request.match_info.get('action', None)
		subaction = request.match_info.get('subaction', None)
		params = json.loads(await request.text())

		if (action=='label' or action == 'total') and subaction==None:
			await self.smf('print', 'start')
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

			t0 = time.time()
			t = time.time()

			template = str(params.get("template", 0))
			if action == 'total':
				template += '_total'
			try:
				x = genereate_file_to_print(f'./printer/templates/template_{template}.xlsx', data)
				print('generate xls', time.time() - t)
				t = time.time()
				p = xlsx_to_pdf(x)
				print('generate pdf', time.time() - t)
				t = time.time()
				print_file(p)
				print('print file', time.time() - t)
				tt = round(time.time() - t0, 3)
				print('total', tt)
				winsound.Beep(1000, 100)
				winsound.Beep(2500, 100)
				LOGGER.info(f'Printing: time={tt}c, template={template}')
			except Exception as ex:
				LOGGER.error('Printing error: ' + str(ex))
				traceback.print_exc()
			finally:
				await self.smf('print', 'end')

			return web.Response(text=json.dumps({'status': 'ok'}))

		if action=='prepare' and subaction==None:
			self.shared_data_obj.setPrintData(params)
			return web.Response(text=json.dumps({'status': 'ok'}))
