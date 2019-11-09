from colorama import Fore,  Style

#--------------------------------------------------------------------------------------------------#
def log(req, resp, resource, params):
	print((Fore.RED + '{}: ' + Fore.GREEN + '{}' + Style.RESET_ALL).format(req.method, req.path))

def set_json(req, resp, resource, params):
	resp.content_type = 'application/json'
#--------------------------------------------------------------------------------------------------#
