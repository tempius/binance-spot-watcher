SYMBOLS = {}
TICKERS = {}
MAX_TIMELINE = 4 * 60 * 60


def initPrices(_spotsToCheck=[]):
    for spot in _spotsToCheck:
        symbol = spot['coin'] + spot['pair']
        SYMBOLS[symbol] = {
            'coin': spot['coin'],
            'pair': spot['pair'],
            'timeline': [],
        }


def updateTickers(symbol, ticker):
    TICKERS[symbol] = ticker


async def updateSymbols():
    for symbol in SYMBOLS:
        if symbol in TICKERS:
            lastTicker = TICKERS[symbol]
            spot = SYMBOLS[symbol]
            previousTicker = None if len(spot['timeline']) == 0 \
                else spot['timeline'][-1]['ticker']
            spot['timeline'].append({
                "pull": 0 if previousTicker is None or previousTicker['c'] == lastTicker['c']
                else -1 if previousTicker['c'] > lastTicker['c']
                else 1,
                "ticker": lastTicker,
            })
            if len(spot['timeline']) > MAX_TIMELINE:
                spot['timeline'].pop(0)
