# encoding: UTF-8

'''
WBFEX交易接口
'''
from __future__ import print_function

import json
import zlib
import requests
from datetime import timedelta, datetime
from copy import copy

from fcs_trade.api.websocket import WebsocketClient
from fcs_trade.trader.gateway import BaseGateway
from threading import Thread, Lock

WEBSOCKET_MARKET_HOST = 'wss://ws.wbfex.com/kline-api/ws'  # 市场api

# 方向和订单类型映射
directionMap = dict()
directionMap[(DIRECTION_BUY)] = "BUY"
directionMap[(DIRECTION_SELL)] = "SELL"

orderTypeMap = dict()
orderTypeMap[(PRICETYPE_MARKETPRICE)] = '2'
orderTypeMap[(PRICETYPE_LIMITPRICE)] = '1'

dealStatusMapReverse = {v: k for k, v in dealStatusMap.items()}
orderStatusMapReverse = {v: k for k, v in orderStatusMap.items()}
directionMapReverse = {v: k for k, v in directionMap.items()}
orderTypeMapReverse = {v: k for k, v in orderTypeMap.items()}

TransferStatus = dict()
TransferStatus[1] = '已转出，未转入'
TransferStatus[2] = '划转成功'


class WbfexGateway(BaseGateway):
    """WBFEX接口"""
    # ----------------------------------------------------------------------
    def __init__(self, eventEngine, gatewayName=''):
        """Constructor"""
        super().__init__(eventEngine, gatewayName)
        self.localID = 10000

        self.accountDict = {}
        self.orderDict = {}
        #self.localOrderDict = {}
        self.wsMarketApi = WbfexMarketApi(self)

        self.fileName = ''.join(['GatewayConfig/', self.gatewayName, '_connect.json'])
        self.filePath = getJsonPath(self.fileName, __file__)
        #symbols_filepath = os.getcwd() + '\GatewayConfig' + '/' + self.fileName

    def connect(self):
        """连接"""
        try:
            f = open(self.filePath)
        except IOError:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = '读取连接配置出错，请检查'
            self.onLog(log)
            return

        # 解析json文件
        setting = json.load(f)
        f.close()

        try:
            apiKey = str(setting['apiKey'])
            secretKey = str(setting['secretKey'])
            symbols = setting['symbols']
        except KeyError:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = '连接配置缺少字段，请检查'
            self.onLog(log)
            return
        except Exception as e:
            print(e)

        # 创建行情接口对象
        try:
            self.wsMarketApi.connect(symbols)
        except Exception as e:
            print(e)

    # ----------------------------------------------------------------------
    def sendOrder(self, orderReq):
        """发单"""
        self.WbfexRestApi.sendOrder(orderReq)

    # ----------------------------------------------------------------------
    def cancelOrder(self, cancelOrderReq):
        """撤单"""
        self.WbfexRestApi.cancelOrder(cancelOrderReq)

    def close(self):
        """关闭"""
        self.WbfexRestApi.stop()
        self.wsMarketApi.stop()

    def write_log(self, msg):
        """"""
        try:
            log = VtLogData()
            log.logContent = msg
            log.gatewayName = self.gatewayName

            event = Event(EVENT_LOG)
            event.dict_['data'] = log
            self.eventEngine.put(event)

            now = str(datetime.now())
            filename =  ''.join(['logs\\', self.gatewayName, '_gateway.log'])
            f_debug_handler = open(filename, 'a')
            f_debug_handler.write(''.join([now, " ", self.gatewayName, " ", msg, "\n"]))
            f_debug_handler.close()
        except Exception as e:
            print('write_log error')
            print(e)

    def write_debug_log(self, msg):
        """"""
        try:
            now = str(datetime.now())
            filename = ''.join(['logs\\', self.gatewayName, '_debug_gateway.log'])
            f_debug_handler = open(filename, 'a')
            f_debug_handler.write(''.join([now, " ", self.gatewayName, " ", msg, "\n"]))
            f_debug_handler.close()
        except Exception as e:
            print('write_debug_log error')
            print(self.gatewayName)
            print(e)


# 市场接口
class WbfexMarketApi(WebsocketClient):
    def __init__(self, gateway):
        """Constructor"""
        super().__init__()

        self.gateway = gateway
        self.gatewayName = gateway.gatewayName

        self.symbols = ''

        #self.callbackDict = {}
        self.tickDict = {}
        self.dealDict = {}

    # ----------------------------------------------------------------------
    def unpackData(self, data):
        """重载"""
        return json.loads(zlib.decompress(data, -zlib.MAX_WBITS))

    # ----------------------------------------------------------------------
    def connect(self, symbols):
        proxy_host = "127.0.0.1"
        proxy_port = 1080
        self.init(WEBSOCKET_MARKET_HOST, proxy_host, proxy_port)
        self.symbols = symbols
        self.start()

    def on_connected(self):
        """连接回调"""
        self.gateway.write_log('WbfexMarketApi API连接成功')
        #time.sleep(3)
        self.subscribe()

    def on_packet(self, packet: dict):
        """"""
        #print(packet)
        if isinstance(packet, dict):
            self.onData(packet)
        else:
            self.on_update(packet)

    def on_response(self, data):
        #print(data)
        self.onData(data)

    def on_update(self, data):
        """"""
        print(data)
        print('WbfexMarketApi on_update')

    def onData(self, data):
        #print(data)
        try:
            #if data.__contains__('event_rep'):
            #    return

            """数据回调"""
            if data.__contains__('channel'):
                if '_depth' in data['channel']:
                    self.onDepth(data)
                elif '_trade_ticker' in data['channel']:
                    self.onDeals(data)
                elif '_ticker' in data['channel']:
                    self.onTick(data)
        except Exception as e:
            print('onData')
            print(e)

    def pong(self, data):
        """响应心跳"""
        #print('send pong WbfexMarketApi')
        req = {'pong': data['ping']}
        self.send_packet(req)

    # ----------------------------------------------------------------------
    def onDisconnected(self):
        """连接回调"""
        self.gateway.write_log('WbfexMarketApi 连接断开')

    # ----------------------------------------------------------------------
    def onPacket(self, packet):
        """数据回调"""
        print('onPacket')
        print(packet)
        d = packet[0]

        channel = d['channel']
        callback = self.callbackDict.get(channel, None)
        if callback:
            callback(d)

    def subscribe(self):
        try:
            # 初始化
            for symbol in self.symbols:
                tick = VtTickData()
                tick.gatewayName = self.gatewayName
                tick.symbol = symbol
                tick.exchange = self.gatewayName
                tick.vtSymbol = '.'.join([tick.exchange, tick.symbol])
                self.tickDict[symbol] = tick

                deal = VtDealData()
                deal.gatewayName = self.gatewayName
                deal.symbol = symbol
                deal.exchange = self.gatewayName
                deal.vtSymbol = '.'.join([deal.exchange, deal.symbol])
                self.dealDict[symbol] = deal

            for symbol in self.symbols:
                # 订阅前24小时行情
                params = {
                        "channel": "market_" + symbol.lower() + "_ticker",
                        "cb_id": 150
                     }
                req = {
                    "event": "sub",
                    'params': params
                }
                self.send_packet(req)
                #return

                # 订阅市场深度
                params = {
                        "channel": "market_" + symbol.lower() + "_depth_step0",
                        "cb_id": 150,
                        "asks": 150,
                        "bids": 150
                     }
                req = {
                    "event": "sub",
                    'params': params
                }
                self.send_packet(req)

                # 订阅-实时成交信息
                params = {
                        "channel": "market_" + symbol.lower() + "_trade_ticker",
                        "cb_id": "150"
                     }
                req = {
                    "event": "sub",
                    'params': params
                }
                self.send_packet(req)
        except Exception as e:
            print('subscribe')
            print(e)

    # ----------------------------------------------------------------------
    def onTick(self, d):
        """"""
        #print(d)
        try:
            data = d['tick']
            symbol = d['channel'].split('_')[1]
            tick = self.tickDict[symbol]
            tick.lastPrice = float(data['close'])
            tick.highPrice = float(data['high'])
            tick.lowPrice = float(data['low'])
            tick.volume = float(data['vol'])
            tick.datetime = datetime.fromtimestamp(int(d['ts'] / 1000))
            tick.time = tick.datetime.strftime('%H:%M:%S')
            self.gateway.onTick(tick)
        except Exception as e:
            print('onTick')
            print(e)

    # 成交回报
    def onDeals(self, d):
        #print(d)
        """"""
        try:
            data_dict = d['tick']['data']
            for data in data_dict:
                symbol = d['channel'].split('_')[1]
                deal = self.dealDict[symbol]
                deal.price = float(data['price'])
                deal.volume = float(data['vol'])
            #deal.type = dealStatusMapReverse[data['type']]
                deal.datetime = datetime.fromtimestamp(int(data['ts']/1000))
                deal.time = deal.datetime.strftime('%H:%M:%S')
                self.gateway.onDeal(copy(deal))
        except Exception as e:
            print('onDeals')
            print(e)

    # 市场深度
    def onDepth(self, d):
        try:
            symbol = d['channel'].split('_')[1]
            tick = self.tickDict[symbol]

            bids = d['tick']['buys']
            asks = d['tick']['asks']

            depth = 20
            # 买单
            for index in range(depth):
                #para = "bidPrice" + str(index + 1)
                para = ''.join(['bidPrice', str(index + 1)])
                if index >= len(bids):
                    setattr(tick, para, 0)
                else:
                    setattr(tick, para, bids[index][0])

                #para = "bidVolume" + str(index + 1)
                para = ''.join(['bidVolume', str(index + 1)])
                if index >= len(bids):
                    setattr(tick, para, 0)
                else:
                    setattr(tick, para, float(bids[index][1]))  # float can sum

            # 卖单
            for index in range(depth):
                #para = "askPrice" + str(index + 1)
                para = ''.join(['askPrice', str(index + 1)])
                if index >= len(asks):
                    setattr(tick, para, 0)
                else:
                    setattr(tick, para, asks[index][0])

                #para = "askVolume" + str(index + 1)
                para = ''.join(['askVolume', str(index + 1)])
                if index >= len(asks):
                    setattr(tick, para, 0)
                else:
                    setattr(tick, para, float(asks[index][1]))

            tick.datetime = datetime.fromtimestamp(int(d['ts']/1000))
            tick.time = tick.datetime.strftime('%H:%M:%S')
            self.gateway.onTick(copy(tick))
        except Exception as e:
            print('onDepth')
            print(e)
