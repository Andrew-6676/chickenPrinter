import configparser
from colorama import Fore, Back, Style, init
init()

######################################################################

class Config:
	def __init__(self, file, rewrite={}):
		print(Back.GREEN+'Чтение параметров...'+Style.RESET_ALL)
		self.file = file
		self.cfg = configparser.ConfigParser()
		self.cfg.read(file)

		#print(rewrite)		
		self.database = rewrite.get('database', self.cfg.get('report', 'database'))
		self.limit    = rewrite.get('limit',    self.cfg.get('report', 'limit'))

		self.scalesPort = rewrite.get('scalesPort',      self.cfg.get('scales', 'port'))
		self.minWeight  = float(rewrite.get('minWeight', self.cfg.get('scales', 'minWeight')))

		self.controllerPort = rewrite.get('controllerPort', self.cfg.get('controller', 'port'))
		self.pollingInterval = float(rewrite.get('pollingInterval', self.cfg.get('controller', 'pollingInterval')))

		print(Fore.GREEN + 'database'       + Style.RESET_ALL+': ' + self.database)

		print(Fore.GREEN+'scalesPort'     + Style.RESET_ALL+': ' + self.scalesPort)
		print(Fore.GREEN+'minWeight'   + Style.RESET_ALL+': ' + str(self.minWeight)   + ' кг')

		print(Fore.GREEN + 'controllerPort'  + Style.RESET_ALL + ': ' + self.controllerPort)
		print(Fore.GREEN + 'pollingInterval' + Style.RESET_ALL + ': ' + str(self.pollingInterval) + ' c')

		print()

	def save(self, data):
		self.cfg.set("report", "database", data['database'])
		self.cfg.set("report", "limit", str(7))

		self.cfg.set("scales", "port", data['scalesPort'])
		self.cfg.set("scales", "mode", str(data['scalesMode']))
		self.cfg.set("scales", "targetWeight", str(data['targetWeight']))
		self.cfg.set("scales", "pollingInterval", str(data['pollingInterval']))
		self.cfg.set("scales", "stableTime", str(data['stableTime']))

		self.cfg.set("controller", "port", data['controllerPort'])
		self.cfg.set("controller", "beforeGetWeightTime", data['beforeGetWeightTime'])
		self.cfg.set("controller", "beforeOpenGateTime", data['beforeOpenGateTime'])

		print(Back.GREEN+'Сохранение параметров...'+Style.RESET_ALL)

		# Вносим изменения в конфиг. файл.
		with open(self.file, "w") as config_file:
			self.cfg.write(config_file)

		self.database        = data['database']
		self.limit           = data['limit']

		# обновляем текущие настройки
		self.scalesPort      = data['scalesPort']
		self.scalesMode      = data['scalesMode']
		self.targetWeight    = data['targetWeight']
		self.pollingInterval = data['pollingInterval']
		self.stableTime      = data['stableTime']

		self.controllerPort       = data['controllerPort']
		self.beforeGetWeightTime  = data['beforeGetWeightTime']
		self.beforeOpenGateTime   = data['beforeOpenGateTime']
