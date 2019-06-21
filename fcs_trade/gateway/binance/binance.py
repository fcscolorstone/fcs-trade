from urllib import request
# import urllib2 # python3中没有 urllib2 用urllib.request替代
import datetime
from copy import copy

#@profile(precision=4)
#print(datetime.datetime.utcnow())
# get请求
#resu = request.urlopen('https://www.binance.com/api/v1/depth?symbol=BTCUSDT&limit=10', data=None, timeout=10)
try:
    resu = request.urlopen('https://www.binance.com/api/v1/trades?symbol=BTCUSDT&limit=1', data=None, timeout=10)
    data = resu.read().decode()
    #res = copy(data)
    print(data)
    #print(res['price'])
    #print(datetime.datetime.utcnow())
    resu = request.urlopen('https://www.binance.com/api/v1/trades?symbol=BTCUSDT&limit=1', data=None, timeout=10)
    data = resu.read().decode()
    #print(data['price'])
    print(data)
    #print(datetime.datetime.utcnow())
    #resu.close()
except Exception as e:
    print('connect failed')