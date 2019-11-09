import json
import logging

from colorama import Fore,  Style

LOGGER = logging.getLogger('app')
#--------------------------------------------------------------------------------------------------#
def log(req, resp, resource, params):
	if req.method == 'POST':
		r_params = json.dumps(json.load(req.stream))
		req.stream.seek(0)
	else:
		r_params = req.params
	print((Fore.RED + '{}: ' + Fore.GREEN + '{}' + Style.RESET_ALL).format(req.method, req.path), r_params)
	LOGGER.debug(f'{req.method}:{req.path} - {r_params}]')

def set_json(req, resp, resource, params):
	resp.content_type = 'application/json'
#--------------------------------------------------------------------------------------------------#
