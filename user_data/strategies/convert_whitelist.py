
import json
listPairs = str("MATIC/BTC, THETA/BTC, ETH/BTC, TFUEL/BTC, COS/BTC, BAND/BTC, BNB/BTC, ONG/BTC, MBL/BTC, ENJ/BTC, RVN/BTC, ZIL/BTC, WRX/BTC, XRP/BTC, LINK/BTC, ADA/BTC, ONT/BTC, REN/BTC, VET/BTC, NEO/BTC, XMR/BTC, HBAR/BTC, IOTX/BTC, DREP/BTC, LTC/BTC, KAVA/BTC, XLM/BTC, XTZ/BTC, EOS/BTC, ZRX/BTC, ANKR/BTC, ATOM/BTC, TRX/BTC, ALGO/BTC, GAS/BTC, ICX/BTC, OMG/BTC, ETC/BTC, WABI/BTC, LTO/BTC, QKC/BTC, BAT/BTC, KNC/BTC, CHZ/BTC, SNGLS/BTC, QTUM/BTC, WTC/BTC, IOST/BTC, NKN/BTC, POE/BTC, POA/BTC, TROY/BTC, STORM/BTC, COTI/BTC, OGN/BTC, DASH/BTC, TNB/BTC, PHB/BTC, WAVES/BTC, ZEC/BTC, MTL/BTC, HIVE/BTC, TNT/BTC, CELR/BTC, AION/BTC, CHR/BTC, ONE/BTC, FTT/BTC, INS/BTC, AGI/BTC, NANO/BTC, FUN/BTC, PERL/BTC, TOMO/BTC, IOTA/BTC, DOCK/BTC, BEAM/BTC, BQX/BTC, FET/BTC, RLC/BTC, ERD/BTC, FTM/BTC, XVG/BTC, QLC/BTC, NXS/BTC, AE/BTC, BCPT/BTC, CTSI/BTC, POWR/BTC, SC/BTC, DATA/BTC, LEND/BTC, VIB/BTC, NAS/BTC, ARPA/BTC, FUEL/BTC, MANA/BTC, DUSK/BTC, MCO/BTC, AMB/BTC").split(', ')
# print(listPairs.replace("'", '"'))
print(json.dumps(listPairs))

