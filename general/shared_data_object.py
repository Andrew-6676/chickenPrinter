import logging
import sqlite3


class DataClass(object):
	part_number = 0
	part_date = '0000-00-00'
	rows = []
	rows_err = []
	scales_state = False
	controller_state = False
	pause = False
	config = None

	def setConfig(self, cfg):
		self.config = cfg

	def setPause(self, p):
		self.pause = p

	def setScalesState(self, state):
		self.scales_state = state

	def setControllerState(self, state):
		self.controller_state = state

	def getScalesState(self):
		return self.scales_state

	def getControllerState(self):
		return self.controller_state

	def startNewPart(self, n, d):
		logging.info(u'start new part: {}, {}'.format(n, d))
		self.rows = []
		self.rows_err = []
		self.setPartNumber(n)
		self.setPartDate(d)
		with open('curr_part.info', 'w') as file:
			file.write(str(n)+','+str(d))

	def setPartNumber(self, n):
		self.part_number = n

	def setPartDate(self, d):
		self.part_date = d

	def getPartNumber(self):
		return self.part_number

	def getPartDate(self):
		return self.part_date

	def addRow(self, x):
		self.rows.append(x)

	def addRowErr(self, x):
		self.rows_err.append(x)

	def getRows(self):
		return self.rows

	def getRowsErr(self):
		return self.rows_err

	def loadFromDb(self):
		database = './report.db'
		conn = sqlite3.connect(database, check_same_thread=False)
		cursor = conn.cursor()
		sql = """select `date`, `time`, weight 
				 from raw_data 
				 where `date`='{}' and part={} and weight>{}""".format(self.part_date,
                                                                       self.part_number,
                                                                       self.config.minWeight)
		cursor.execute(sql)
		data = cursor.fetchall()
		conn.close()
		if data and len(data):
			print('load current part from DB')
			logging.info('load current part from DB')
		for r in data:
			self.addRow({'time': r[0] + ' ' + r[1], 'weight': r[2], 'part': self.part_number})
