import json
import time
import winsound

from aiohttp import web

from printer.printer import genereate_file_to_print, xlsx_to_pdf

class Printer():
	def __init__(self, db_connection, shared_data_obj=None, config=None):
		self.shared_data_obj = shared_data_obj
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()

	async def get(self, request):
		action = request.match_info.get('action', None)
		subaction = request.match_info.get('subaction', None)
		if action == 'templates' and not subaction:
			sql = 'select * from templates'
			self.cursor.execute(sql)
			data = self.cursor.fetchall()
			return web.Response(text=json.dumps(data))

	async def post(self, request):
		action = request.match_info.get('action', None)
		subaction = request.match_info.get('subaction', None)
		params = json.loads(await request.text())

		if (action=='label' or action == 'total') and subaction==None:
			frequency, duration = 4500, 70
			winsound.Beep(frequency, duration)
			sql = """select * from production where id={} and deleted=0""".format(params['id'])
			self.cursor.execute(sql)
			data = self.cursor.fetchone()
			data['weight'] = params.get('weight') if action == 'label' else params.get('totalWeight')
			data['date1'] = params.get('date1')
			data['date2'] = params.get('date2')
			data['date3'] = params.get('date3')
			data['user'] = params.get('user')
			data['code_128'] = params.get('code128')
			data['packs'] = params.get('packs')
			data['ean_13'] = data['bar_code']

			t = time.time()

			template = str(params.get("template", 0))
			if action == 'total':
				template += '_total'

			x = genereate_file_to_print(f'./printer/templates/template_{template}.xlsx', data)
			print(time.time() - t)
			t = time.time()
			p = xlsx_to_pdf(x)
			print(time.time() - t)
			t = time.time()
			# print_file(p)
			print(time.time() - t)
			frequency = 2500  # Set Frequency To 2500 Hertz
			duration = 100  # Set Duration To 1000 ms == 1 second
			winsound.Beep(frequency, duration)

			return web.Response(text=json.dumps({'status': 'ok'}))

		if action=='prepare' and subaction==None:
			self.shared_data_obj.setPrintData(params)
			return web.Response(text=json.dumps({'status': 'ok'}))
