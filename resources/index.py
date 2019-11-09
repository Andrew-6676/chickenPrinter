import falcon

from resources.common import log

@falcon.before(log)
class Index():
	def __init__(self, q=None, config=None):
		self.qqq=q
		self.config=config

	def on_get(self, req, resp, action=None):
		# resp.body = filename
		if not action:
			resp.content_type = 'text/html'
			with open('./static/index.html', 'r') as f:
				print('index')
				resp.body = f.read()
