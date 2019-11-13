import json
import os
import time
import winsound

import falcon

from printer.printer import genereate_file_to_print, xlsx_to_pdf, print_file
from resources.common import log

@falcon.before(log)
class Printer():
	def __init__(self, db_connection, shared_data_obj=None, config=None):
		self.shared_data_obj = shared_data_obj
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()

	def on_get(self, req, resp, action=None, subaction=None):
		if action == 'templates' and not subaction:
			sql = 'select * from templates'
			self.cursor.execute(sql)
			data = self.cursor.fetchall()
			resp.body = json.dumps(data)
			return

		raise falcon.HTTPNotFound(title=f'{req.method}:{action}/{subaction} - not found')

	def on_post(self, req, resp, action=None, subaction=None):
		params = json.load(req.stream)

		if action=='label' and subaction==None:
			frequency, duration = 4500, 70
			winsound.Beep(frequency, duration)
			sql = """select * from production where id={} and deleted=0""".format(params['id'])
			self.cursor.execute(sql)
			data = self.cursor.fetchone()
			data['weight'] = params.get('weight')
			data['date1'] = params.get('date1')
			data['date2'] = params.get('date2')
			data['date3'] = params.get('date3')
			data['user'] = params.get('user')
			data['ean_13'] = data['bar_code']
			data['code_128'] = params['code128']

			t = time.time()

			template = params.get("template", 0)
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

			resp.body = json.dumps('ok')

		if action=='prepare' and subaction==None:
			self.shared_data_obj.setPrintData(params)
