import configparser
from colorama import Fore,  Style


class Cfg_class():
	pass
# ------------------------------------------------------------------------------------------------ #
def obj_dic(d):
	top = Cfg_class()
	seqs = tuple, list, set, frozenset
	for i, j in d.items():
		if isinstance(j, dict):
			setattr(top, i, obj_dic(j))
		elif isinstance(j, seqs):
			setattr(top, i, type(j)(obj_dic(sj) if isinstance(sj, dict) else sj for sj in j))
		else:
			setattr(top, i, j)
	return top

# ------------------------------------------------------------------------------------------------ #

class Config:
	def __init__(self, file, rewrite={}):
		print('Чтение параметров...')
		self.file = file
		self.cfg = configparser.ConfigParser()
		self.cfg.read(file, encoding='utf-8')
		# cfg.readfp(codecs.open("myconfig", "r", "utf8"))

		config_dict = {}
		for section in self.cfg.sections():
			config_dict[section] = {}
			print(f'{Fore.BLUE}{section.upper()}{Style.RESET_ALL}')
			for option in self.cfg.options(section):
				value = self.cfg.get(section, option)
				config_dict[section][option] = value
				print(f'{Fore.GREEN}  - {option}{Style.RESET_ALL}: {value}')

		self.config = obj_dic(config_dict)

	def getConfig(self):
		return self.config

	# def save(self, data):
	# 	self.cfg.set("report", "database", data['database'])
	# 	self.cfg.set("report", "limit", str(7))
	#
	# 	self.cfg.set("scales", "port", data['scalesPort'])
	# 	self.cfg.set("scales", "mode", str(data['scalesMode']))
	# 	self.cfg.set("scales", "targetWeight", str(data['targetWeight']))
	# 	self.cfg.set("scales", "pollingInterval", str(data['pollingInterval']))
	# 	self.cfg.set("scales", "stableTime", str(data['stableTime']))
	#
	# 	self.cfg.set("controller", "port", data['controllerPort'])
	# 	self.cfg.set("controller", "beforeGetWeightTime", data['beforeGetWeightTime'])
	# 	self.cfg.set("controller", "beforeOpenGateTime", data['beforeOpenGateTime'])
	#
	# 	print(Back.GREEN+'Сохранение параметров...'+Style.RESET_ALL)
	#
	# 	# Вносим изменения в конфиг. файл.
	# 	with open(self.file, "w") as config_file:
	# 		self.cfg.write(config_file)
	#
	# 	self.database        = data['database']
	# 	self.limit           = data['limit']
	#
	# 	# обновляем текущие настройки
	# 	self.scalesPort      = data['scalesPort']
	# 	self.scalesMode      = data['scalesMode']
	# 	self.targetWeight    = data['targetWeight']
	# 	self.pollingInterval = data['pollingInterval']
	# 	self.stableTime      = data['stableTime']
	#
	# 	self.controllerPort       = data['controllerPort']
	# 	self.beforeGetWeightTime  = data['beforeGetWeightTime']
	# 	self.beforeOpenGateTime   = data['beforeOpenGateTime']
