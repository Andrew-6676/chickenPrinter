import falcon
import json
from colorama import Fore, Style

from config import Config
from report import Report
from openpyxl import Workbook

#--------------------------------------------------------------------------------------------------#
def log(req, resp, resource, params):
	print((Fore.RED + '{}: ' + Fore.GREEN + '{}' + Style.RESET_ALL).format(req.method, req.path))

def set_json(req, resp, resource, params):
	resp.content_type = 'application/json'
#--------------------------------------------------------------------------------------------------#

class Index():
	def __init__(self, q=None, config=None):
		self.qqq=q
		self.config=config

	def on_get(self, req, resp, action=None):
		# resp.body = filename
		if not action:
			resp.content_type = 'text/html'
			with open('./static/index.html', 'rb') as f:
				resp.body = f.read()
		# if action=='setPartNumber':
		# 	self.qqq.setPartNumber(req.params.get('number', -1))
		# 	resp.body = json.dumps({'message': 'num changed'})
		# if action=='startNewPart':
		# 	self.qqq.startNewPart(req.params.get('number', -1), req.params.get('date', '0000-00-00'))
		# 	self.qqq.loadFromDb()
		#
		# 	resp.body = json.dumps({'message': 'part started'})
		# if action == 'getPortsState':
		# 	resp.body = json.dumps({
		# 		'scales': self.qqq.getScalesState(),
		# 		'controller': self.qqq.getControllerState()
		# 	})

#--------------------------------------------------------------------------------------------------#
@falcon.before(log)
@falcon.before(set_json)
class Production():
	def __init__(self, db_connection, q=None, config=None):
		self.qqq=q
		self.config = config
		self.cursor = db_connection.cursor()

	def on_get(self, req, resp, id=None):
		if id:
			sql = """select * from production where id={} and not deleted""".format(id)
			self.cursor.execute(sql)
			data = self.cursor.fetchone()
		else:
			sql = """select * from production where not deleted"""
			self.cursor.execute(sql)
			data = self.cursor.fetchall()


		resp.body = json.dumps(data)

#--------------------------------------------------------------------------------------------------#

# class Reporter(Report):
# 	def __init__(self, database, q=None, config=None):
# 		self.qqq=q
# 		self.config = config
# 		Report.__init__(self, database, config)
#
# 	def on_options(self, req, res):
# 		res.set_header('Access-Control-Allow-Origin', '*')
# 		res.set_header('Access-Control-Allow-Methods', 'GET,POST,PUT')
# 		res.set_header('Access-Control-Allow-Headers', 'Content-Type')
#
# 	def on_get(self, req, resp, action='data'):
# 		resp.set_header('Access-Control-Allow-Origin', '*')
# 		resp.set_header('Access-Control-Allow-Methods', 'GET')
# 		resp.set_header('Access-Control-Allow-Headers', 'Content-Type')
#
# 		res = None
# 		if action=='data':
# 			#res = {'data': Report.getReport(self, req.params, )}
# 			res = {
# 				'partNumber': self.qqq.getPartNumber(),
# 				'partDate': self.qqq.getPartDate(),
# 				'data': self.qqq.getRows(),
# 				'dataErr': self.qqq.getRowsErr()
# 			}
# 		else:
# 			print(Fore.BLACK + Style.BRIGHT + 'GET: report('+action+')' + Style.RESET_ALL)
# 		# if action == 'getOnePart':
# 		# 	res = Report.getOnePart(self, req.params.get('date'), req.params.get('num'))
# 		if action == 'getAllParts':
# 			res = Report.getLastParts(self, req.params.get('limit'))
# 		if action == 'getLastParts':
# 			res = Report.getLastParts(self, req.params.get('limit', 10))
# 		if action=='getPartData':
# 			res = Report.getPartData(self, req.params.get('date'), req.params.get('num', 0))
# 		if action=='getDay':
# 			res = Report.getDay(self, req.params.get('date'))
# 		if action=='excel_part':
# 			data = Report.getPartData(self, req.params.get('date'), req.params.get('num', 0))
# 			header = 'Варка № {} от {}'.format(req.params.get('num', 0), req.params.get('date'))
# 			res = {'link': self.makeExcel(data,  header=header, sum=[1], title=('Время', 'Вес'))}
# 		if action=='excel_day':
# 			data = Report.getDay(self, req.params.get('date'))
# 			header = 'Отчёт за {}'.format(req.params.get('date'))
# 			res = {'link': self.makeExcel(data, header=header, sum=[1,2], title=('Номер варки', 'Вес', 'Кол-во голов', 'Мин. вес', 'Средний вес', 'Макс. вес'))}
# 		if action=='stat':
# 			res = Report.getStat(self)
# 			# print(self.qqq.getRows())
# 		if action=='pack':
# 			print(Fore.BLACK + Style.BRIGHT + 'POST: report(' + action + ')' + Style.RESET_ALL)
# 			res = Report.packData(self, req.params)
#
# 		resp.body = json.dumps(res)
#
# 	def makeExcel(self, data, header='Заголовок отчёта', sum=[1], title=('Время','Вес')):
# 		wb = Workbook()
# 		ws = wb.active
#
# 		ws['A1'] = header
#
# 		i = 0
# 		for t in title:
# 			ws['ABCDEFG'[i] + str(3)] = t
# 			i += 1
#
# 		r = 4
# 		_sum = {}
# 		for i in sum:
# 			_sum[i] = 0
#
# 		for row in data:
# 			# ws['A'+str(r)] = row['time'] #time.strftime('%d.%m.%Y', time.strptime(row[1], "%Y-%m-%d"))
# 			# ws['B'+str(r)] = row['weight'] #round(row[2])
# 			for i in sum:
# 				_sum[i] += row[i]
#
# 			i = 0
# 			for f in row:
# 				ws['ABCDEFG'[i] + str(r)] = f
# 				i += 1
#
# 			r += 1
# 		ws['A'+str(r)] = 'ИТОГО:'
# 		# ws['B'+str(r)] = '=СУММ(B1:B'+str(r-1)+')'
# 		for i in sum:
# 			ws['ABCDEFG'[i]+str(r)] = _sum[i]
#
# 		file = './static/reports/report.xlsx'
# 		wb.save(file)
#
# 		return 'reports/report.xlsx'
#
# 	def on_put(self, req, res):
# 		res.set_header('Access-Control-Allow-Origin', '*')
# 		res.set_header('Access-Control-Allow-Methods', 'PUT')
# 		res.set_header('Access-Control-Allow-Headers', 'Content-Type')
# 		print(Fore.BLACK + Style.BRIGHT + 'Put: report()' + Style.RESET_ALL)
#
# 		data = json.load(req.stream)
# 		sql= """update days_data set total_weight="""+str(data['val'])+""" where id="""+str(data['id'])
# 		print(sql)
#
# 		try:
# 			self.cursor.execute(sql)
# 			self.conn.commit()
# 			res.body = json.dumps({'status': 'ok'})
# 		except Exception as e:
# 			self.conn.rollback()
# 			res.body = json.dumps({'status': 'error'})
		
#--------------------------------------------------------------------------------------------------#
