# flake8: noqa
import unittest
import platform


# noinspection PyUnresolvedReferences
class ImportTest(unittest.TestCase):

    # noinspection PyUnresolvedReferences
    def test_import_all(self):
        from fcs_trade.event import EventEngine

    def test_import_main_engine(self):
        from fcs_trade.trader.engine import MainEngine

    def test_import_ui(self):
        from fcs_trade.trader.ui import MainWindow, create_qapp

    def test_import_bitmex_gateway(self):
        from fcs_trade.gateway.bitmex import BitmexGateway

    def test_import_futu_gateway(self):
        from fcs_trade.gateway.futu import FutuGateway

    def test_import_ib_gateway(self):
        from fcs_trade.gateway.ib import IbGateway

    @unittest.skipIf(platform.system() == "Darwin", "Not supported yet under osx")
    def test_import_ctp_gateway(self):
        from fcs_trade.gateway.ctp import CtpGateway

    def test_import_tiger_gateway(self):
        from fcs_trade.gateway.tiger import TigerGateway

    @unittest.skipIf(platform.system() == "Darwin", "Not supported yet under osx")
    def test_import_oes_gateway(self):
        from fcs_trade.gateway.oes import OesGateway

    def test_import_cta_strategy_app(self):
        from fcs_trade.app.cta_strategy import CtaStrategyApp

    def test_import_csv_loader_app(self):
        from fcs_trade.app.csv_loader import CsvLoaderApp


if __name__ == '__main__':
    unittest.main()
