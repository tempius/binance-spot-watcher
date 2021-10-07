import typing
import asyncio

SYMBOLS = {}
TICKERS = {}
MAX_TIMELINE = 4 * 60 * 60


def updateTickers(symbol: str, ticker: dict) -> None:
    TICKERS[symbol] = ticker


def initSymbol(spot: typing.Dict[str, str]) -> None:
    symbol = spot['coin'] + spot['pair']
    SYMBOLS[symbol] = {
        'coin': spot['coin'],
        'pair': spot['pair'],
        'timeline': [],
    }


def initSymbols(_spotsToCheck: typing.List[typing.Dict[str, str]]) -> None:
    for spot in _spotsToCheck:
        initSymbol(spot)


async def updateSymbol(symbol: str) -> None:
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


async def updateSymbols() -> None:
    await asyncio.wait([
        updateSymbol(symbol) for symbol in SYMBOLS
    ])
