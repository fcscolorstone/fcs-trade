
from fcs_trade.event import EventEngine

from fcs_trade.trader.engine import MainEngine
from fcs_trade.trader.ui import MainWindow, create_qapp

from fcs_trade.gateway.bitmex import BitmexGateway
from fcs_trade.gateway.futu import FutuGateway
from fcs_trade.gateway.ib import IbGateway
from fcs_trade.gateway.ctp import CtpGateway
# from fcs_trade.gateway.ctptest import CtptestGateway
from fcs_trade.gateway.femas import FemasGateway
from fcs_trade.gateway.tiger import TigerGateway
from fcs_trade.gateway.oes import OesGateway
from fcs_trade.gateway.okex import OkexGateway
from fcs_trade.gateway.huobi import HuobiGateway
from fcs_trade.gateway.bitfinex import BitfinexGateway
from fcs_trade.gateway.onetoken import OnetokenGateway
from fcs_trade.gateway.okexf import OkexfGateway
from fcs_trade.gateway.xtp import XtpGateway
from fcs_trade.gateway.hbdm import HbdmGateway

from fcs_trade.app.cta_strategy import CtaStrategyApp
from fcs_trade.app.csv_loader import CsvLoaderApp
from fcs_trade.app.algo_trading import AlgoTradingApp
from fcs_trade.app.cta_backtester import CtaBacktesterApp
from fcs_trade.app.data_recorder import DataRecorderApp


def main():
    """"""
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(XtpGateway)
    main_engine.add_gateway(CtpGateway)
    # main_engine.add_gateway(CtptestGateway)
    main_engine.add_gateway(FemasGateway)
    main_engine.add_gateway(IbGateway)
    main_engine.add_gateway(FutuGateway)
    main_engine.add_gateway(BitmexGateway)
    main_engine.add_gateway(TigerGateway)
    main_engine.add_gateway(OesGateway)
    main_engine.add_gateway(OkexGateway)
    main_engine.add_gateway(HuobiGateway)
    main_engine.add_gateway(BitfinexGateway)
    main_engine.add_gateway(OnetokenGateway)
    main_engine.add_gateway(OkexfGateway)
    main_engine.add_gateway(HbdmGateway)

    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(CsvLoaderApp)
    main_engine.add_app(AlgoTradingApp)
    main_engine.add_app(DataRecorderApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()
