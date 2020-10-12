import sys
sys.path.insert(0, './Core/')
from DataPool import DataPool
DP = DataPool()
DP.start(prod=True)
app = DP.app
#from werkzeug.contrib.fixers import ProxyFix
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)


