import sqlite3
import os
import time
from colorama import Fore, Back, Style, init
init()

###############################################################

""" Выгрузка данных осуществляется в Excel в формате "Дата" и "Количество груза итого за сутки". """
class Report:
	def __init__(self, database, config):
		print(Back.GREEN+'Открытие базы данных...'+Style.RESET_ALL)
		self.database = database
		self.config = config
		self.conn = sqlite3.connect(database, check_same_thread=False) # или :memory: чтобы сохранить в RAM
		self.cursor = self.conn.cursor()
		
		# проверяем наличие таблиц
		try:
			self.cursor.execute('SELECT count(*) as ee FROM raw_data')
			print('Записей в `raw_data`:  '+str(self.cursor.fetchone()[0]))
		except sqlite3.OperationalError:
			print(Fore.RED+'Отсутствует таблица `raw_data`'+Style.RESET_ALL+' пересоздаём...')
			self.createTables(['raw_data'])
			
		try:
			self.cursor.execute('SELECT count(*) FROM days_data')
			print('Записей в `days_data`: '+str(self.cursor.fetchone()[0]))
		except sqlite3.OperationalError:
			print(Fore.RED+'Отсутствует таблица `days_data`'+Style.RESET_ALL+' пересоздаём...')
			self.createTables(['days_data'])
		
	def __del__(self):
		if hasattr(self, 'conn'):
			self.conn.close()
			print('Database closed')		
		
	
	def createTables(self, tables=['raw_data', 'days_data']):	
		if tables.count('raw_data')>0:
			self.cursor.execute("""CREATE TABLE `raw_data`
									(`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
									`date` TEXT, 
									`time` TEXT, 
									`weight` REAL, 
									`rest` REAL, 
									`part` INTEGER)
								""")
		if tables.count('days_data')>0:
			self.cursor.execute("""CREATE TABLE `days_data`
									(`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
									`date` TEXT, 
									`total_weight` REAL, 
									`total_part` INTEGER)
								""")
			   
	def addRecord(self, data={'date':0, 'time':0, 'weight':0, 'part':0}):
		st = time.time()
		print(Fore.BLACK+Style.BRIGHT+'Запись в БД: '+str(data['weight'])+' ('+str(data['rest'])+') кг', end=' ')
		self.cursor.execute("INSERT INTO `raw_data` (`date`, `time`, weight, rest, part) VALUES (:date, :time, :weight, :rest, :part)", data)
		self.conn.commit()
		et = time.time()-st
		print(' ('+str(et)+' c)'+Style.RESET_ALL)
		
	def getStat(self):
		self.cursor.execute('SELECT count(*) FROM raw_data')
		rc = self.cursor.fetchone()[0]
		self.cursor.execute('SELECT count(*) FROM days_data')
		dc = self.cursor.fetchone()[0]
		return {
			'size': os.path.getsize(self.database),
			'rawRecordsCount': rc,
			'daysRecordsCount': dc,
		}

	def getDay(self, date='2019-01-01'):
		sql = """select part, sum(weight), count(*), min(weight), avg(weight), max(weight) from raw_data where `date`='{}' and weight>{} group by `part`""".format(date, self.config.minWeight)
		self.cursor.execute(sql)
		# print(sql)
		print(Fore.BLACK + Style.BRIGHT + 'Выборка данных за день '+ str(date) + Style.RESET_ALL)
		
		data = self.cursor.fetchall()
		return data

	# def getOnePart(self, date, num):


	def getLastParts(self, limit=10):
		sql = """select `date`, sum(weight) from raw_data where weight>{} group by `date` order by `date` desc limit {}""".format(self.config.minWeight, limit)
		# print(sql)
		self.cursor.execute(sql)
		print(Fore.BLACK + Style.BRIGHT + 'Выборка дней' + Style.RESET_ALL)

		data = self.cursor.fetchall()
		return data

	def getPartData(self, date, num):
		sql = """select `time`, weight from raw_data where `date`='{}' and part={} and weight>{}""".format(date, num, self.config.minWeight)
		# print(sql)
		self.cursor.execute(sql)
		print(Fore.BLACK + Style.BRIGHT + 'Выборка данных по варке' + Style.RESET_ALL)
		
		data = self.cursor.fetchall()
		return data

	def getReport(self, params={}):
		sql = """select 0 as id, date(time) as date, round(sum(weight-rest)) as weight, round(sum(rest)) as rest
					from raw_data
					where date(time)>='"""+params['dateBegin']+"""' and date(time)<='"""+params['dateEnd']+"""'
					group by date(time)
					
					union
					
					select id, `date`, total_weight as weight, total_rest as rest
					from days_data
					where `date`>='"""+params['dateBegin']+"""' and `date`<='"""+params['dateEnd']+"""'
					order by date(time) desc"""
		self.cursor.execute(sql)
		print(Fore.BLACK + Style.BRIGHT + 'Выборка данных для отчёта' + Style.RESET_ALL)
		
		data = self.cursor.fetchall()
		#data2 = []
		#for row in data:
		#	t = (row[0], row[1], round(row[2]))
		#	data2.append(t)
			
		return data

	def packData(self, params):
		sql= """insert into days_data 
				select null, date(time) as date, round(sum(weight-rest)) as weight, round(sum(rest)) as total_rest, -1 as total_part
				from raw_data
				where date(time)<='"""+params['datePack']+"""'
				group by date(time)"""

		sql_del = "delete from raw_data where date(time)<='"+params['datePack']+"'"

		try:
			self.cursor.execute(sql)
			if (self.cursor.rowcount>0):
				self.cursor.execute(sql_del)
			self.conn.commit()
			return {'status': 'ok'}
			#else:
			#	return {'status': 'error'}
		except Exception as e:
			self.conn.rollback()
			return {'status': 'error'}

