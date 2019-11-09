import falcon

from resources.common import log, set_json

@falcon.before(log)
@falcon.before(set_json)
class Scales():
	def __init__(self, db_connection, q=None, config=None):
		self.qqq=q
		self.config = config
		self.conn = db_connection
		self.cursor = db_connection.cursor()

	def on_get(self, req, resp, id=None):
		pass
		# resp.body = json.dumps(data)

	def on_post(self, req, resp):
		pass
		# resp.body = json.dumps({'status': 'error'})
