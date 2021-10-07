import os
import typing
import asyncio
import _bcolors
import _prices
import _websockets

ROWS = {}
COL_WIDTH = 17
TABLE_HEADERS = [
    {"value": "SPOT", "style": _bcolors.BOLD},
    {"value": "LAST", "style": _bcolors.BOLD},
    {"value": "UPDATES", "style": _bcolors.BOLD},
    {"value": "DELTA", "style": _bcolors.BOLD},
    {"value": "TREND", "style": _bcolors.BOLD},
    {"value": "A/D", "style": _bcolors.BOLD},
    {"value": "24H CHANGE", "style": _bcolors.BOLD},
]
ROW_SEPARATOR = list(map(lambda c: "─".join(
    "" for i in range(COL_WIDTH)), TABLE_HEADERS))

# ticker example
# {
#     "e": "24hrTicker",  // Event type
#     "E": 123456789,     // Event time
#     "s": "BNBBTC",      // Symbol
#     "p": "0.0015",      // Price change
#     "P": "250.00",      // Price change percent
#     "w": "0.0018",      // Weighted average price
#     "x": "0.0009",      // First trade(F)-1 price (first trade before the 24hr rolling window)
#     "c": "0.0025",      // Last price
#     "Q": "10",          // Last quantity
#     "b": "0.0024",      // Best bid price
#     "B": "10",          // Best bid quantity
#     "a": "0.0026",      // Best ask price
#     "A": "100",         // Best ask quantity
#     "o": "0.0010",      // Open price
#     "h": "0.0025",      // High price
#     "l": "0.0010",      // Low price
#     "v": "10000",       // Total traded base asset volume
#     "q": "18",          // Total traded quote asset volume
#     "O": 0,             // Statistics open time
#     "C": 86400000,      // Statistics close time
#     "F": 0,             // First trade ID
#     "L": 18150,         // Last trade Id
#     "n": 18151          // Total number of trades
#     }


def textColorizer(text: str) -> str:

    return text\
        .replace("⇣", f"{_bcolors.FAIL}⇣{_bcolors.END}")\
        .replace("BEAR", f"{_bcolors.FAIL}BEAR{_bcolors.END}")\
        .replace("DIST", f"{_bcolors.FAIL}DIST{_bcolors.END}")\
        .replace("⇡", f"{_bcolors.GREEN}⇡{_bcolors.END}")\
        .replace("BULL", f"{_bcolors.GREEN}BULL{_bcolors.END}")\
        .replace("ACCU", f"{_bcolors.GREEN}ACCU{_bcolors.END}")


def tableCellFormat(cell: typing.Union[str, typing.Dict[str, str]], colWidth: int) -> str:
    if isinstance(cell, str):

        return textColorizer(cell.ljust(colWidth))
    elif isinstance(cell, dict) and "value" in cell:
        value = str(cell["value"])
        style = cell["style"] if "style" in cell and cell["style"] is not None else ""
        prepend = cell["prepend"] if "prepend" in cell and cell["prepend"] is not None else ""

        return textColorizer(f"{prepend}{value}".ljust(colWidth).replace(value, f"{style}{value}{_bcolors.END}"))
    else:

        return "".ljust(colWidth)


def tableRowFormat(row: typing.List[typing.Dict[str, str]], colWidth: int = COL_WIDTH) -> str:
    return f"{'│ '.join(tableCellFormat(cell, colWidth) for cell in row)}\n"


async def updateRow(symbol: str) -> None:
    row = ""

    spot = _prices.SYMBOLS[symbol]
    timeline = spot['timeline']
    timelineLength = len(timeline)

    pullLast = None if timelineLength == 0 \
        else timeline[-1]['pull']
    tickerLast = None if timelineLength == 0 \
        else timeline[-1]['ticker']

    t15m = 15 * 60
    t1h = 1 * 60 * 60
    t4h = 4 * 60 * 60

    ticker15m = None if timelineLength < t15m \
        else timeline[-t15m]['ticker']
    ticker1h = None if timelineLength < t1h \
        else timeline[-t1h]['ticker']
    ticker4h = None if timelineLength < t4h \
        else timeline[-t4h]['ticker']
    timeline15mDelta = 0 if ticker15m is None or tickerLast is None \
        else float(tickerLast['c']) - float(ticker15m['c'])
    timeline1hDelta = 0 if ticker1h is None or tickerLast is None \
        else float(tickerLast['c']) - float(ticker1h['c'])
    timeline4hDelta = 0 if ticker4h is None or tickerLast is None \
        else float(tickerLast['c']) - float(ticker4h['c'])

    historyPullLabel = ""
    sum15mQ = 0
    sum15mH = 0
    sum15mF = 0
    sum1hQ = 0
    sum1hH = 0
    sum1hF = 0
    sum4hQ = 0
    sum4hH = 0
    sum4hF = 0
    for index, point in enumerate(reversed(timeline)):
        historyPullLabel += "-" if point['pull'] == 0 \
            else "⇣" if point['pull'] == -1 \
            else "⇡"
        if index < t15m / 4:
            sum15mQ += float(point['ticker']['c'])
        if index < t15m / 2:
            sum15mH += float(point['ticker']['c'])
        if index < t15m:
            sum15mF += float(point['ticker']['c'])
        if index < t1h / 4:
            sum1hQ += float(point['ticker']['c'])
        if index < t1h / 2:
            sum1hH += float(point['ticker']['c'])
        if index < t1h:
            sum1hF += float(point['ticker']['c'])
        if index < t4h / 4:
            sum4hQ += float(point['ticker']['c'])
        if index < t4h / 2:
            sum4hH += float(point['ticker']['c'])
        if index < t4h:
            sum4hF += float(point['ticker']['c'])

    sma15mQ = 0 if timelineLength < t15m else sum15mQ / (t15m / 4)
    sma15mH = 0 if timelineLength < t15m else sum15mH / (t15m / 2)
    sma15mF = 0 if timelineLength < t15m else sum15mF / t15m
    sma1hQ = 0 if timelineLength < t1h else sum1hQ / (t1h / 4)
    sma1hH = 0 if timelineLength < t1h else sum1hH / (t1h / 2)
    sma1hF = 0 if timelineLength < t1h else sum1hF / t1h
    sma4hQ = 0 if timelineLength < t4h else sum4hQ / (t4h / 4)
    sma4hH = 0 if timelineLength < t4h else sum4hH / (t4h / 2)
    sma4hF = 0 if timelineLength < t4h else sum4hF / t4h

    mfv15m = 0 if ticker15m is None \
        else ((float(ticker15m['c']) - float(ticker15m['l']))
              - (float(ticker15m['h']) - float(ticker15m['c']))) \
        / (float(ticker15m['h']) - float(ticker15m['l'])) * float(ticker15m['v'])
    mfv1h = 0 if ticker1h is None \
        else ((float(ticker1h['c']) - float(ticker1h['l']))
              - (float(ticker1h['h']) - float(ticker1h['c']))) \
        / (float(ticker1h['h']) - float(ticker1h['l'])) * float(ticker1h['v'])
    mfv4h = 0 if ticker4h is None \
        else ((float(ticker4h['c']) - float(ticker4h['l']))
              - (float(ticker4h['h']) - float(ticker4h['c']))) \
        / (float(ticker4h['h']) - float(ticker4h['l'])) * float(ticker4h['v'])
    mfvLast = 0 if tickerLast is None \
        else ((float(tickerLast['c']) - float(tickerLast['l']))
              - (float(tickerLast['h']) - float(tickerLast['c']))) \
        / (float(tickerLast['h']) - float(tickerLast['l'])) * float(tickerLast['v'])

    ad15m = 0 if ticker15m is None else mfv15m + mfvLast
    ad1h = 0 if ticker1h is None else mfv1h + mfvLast
    ad4h = 0 if ticker4h is None else mfv4h + mfvLast

    row += tableRowFormat(ROW_SEPARATOR)
    # 15 minutes
    row += tableRowFormat([
        None,
        None,
        None,
        {
            "prepend": "15m │ ",
            "value": f"({timelineLength-t15m})" if ticker15m is None or tickerLast is None
            else round(timeline15mDelta, 2),
            "style": "" if timeline15mDelta == 0
            else _bcolors.FAIL if timeline15mDelta < 0
            else _bcolors.GREEN,
        },
        {
            "prepend": "15m │ ",
            "value": f"({timelineLength-t15m})" if timelineLength < t15m
            else "BEAR" if sma15mQ < sma15mF
            else "BULL" if sma15mQ > sma15mH
            else "-",
            "style": "",
        },
        {
            "prepend": "15m │ ",
            "value": f"({timelineLength-t15m})" if ticker15m is None
            else "DIST" if ad15m < 0
            else "ACCU" if ad15m > 0
            else "-",
            "style": "",
        },
        None,
    ])
    # 1 hour
    row += tableRowFormat([
        {
            "value": f"{spot['coin'].upper()}/{spot['pair'].upper()}",
            "style": f"{_bcolors.BOLD}" if symbol not in _websockets.CONNECTIONS or _websockets.CONNECTIONS[symbol].closed
            else f"{_bcolors.BOLD}{_bcolors.CYAN}",
        },
        {
            "value": "-" if tickerLast is None
            else float(tickerLast['c']),
            "style": "" if pullLast is None
            or pullLast == 0
            else _bcolors.FAIL if pullLast == -1
            else _bcolors.GREEN,
        },
        {
            "value": historyPullLabel[0:COL_WIDTH-1],
            "style": "",
        },
        {
            "prepend": "1h  │ ",
            "value": f"({timelineLength-t1h})" if ticker1h is None or tickerLast is None
            else round(timeline1hDelta, 2),
            "style": "" if timeline1hDelta == 0
            else _bcolors.FAIL if timeline1hDelta < 0
            else _bcolors.GREEN,
        },
        {
            "prepend": "1h  │ ",
            "value": f"({timelineLength-t1h})" if timelineLength < t1h
            else "BEAR" if sma1hQ < sma1hF
            else "BULL" if sma1hQ > sma1hH
            else "-",
            "style": "",
        },
        {
            "prepend": "1h  │ ",
            "value": f"({timelineLength-t1h})" if ticker1h is None
            else "DIST" if ad1h < 0
            else "ACCU" if ad1h > 0
            else "-",
            "style": "",
        },
        {
            "value": "-" if tickerLast is None
            else float(tickerLast['p']),
            "style": "" if tickerLast is None
            or tickerLast['p'] == '0'
            else _bcolors.FAIL if tickerLast['p'] < '0'
            else _bcolors.GREEN,
        },
    ])
    # 4 hours
    row += tableRowFormat([
        None,
        None,
        None,
        {
            "prepend": "4h  │ ",
            "value": f"({timelineLength-t4h})" if ticker4h is None or tickerLast is None
            else round(timeline4hDelta, 2),
            "style": "" if timeline4hDelta == 0
            else _bcolors.FAIL if timeline4hDelta < 0
            else _bcolors.GREEN,
        },
        {
            "prepend": "4h  │ ",
            "value": f"({timelineLength-t4h})" if timelineLength < t4h
            else "BEAR" if sma4hQ < sma4hF
            else "BULL" if sma4hQ > sma4hH
            else "-",
            "style": "",
        },
        {
            "prepend": "4h  │ ",
            "value": f"({timelineLength-t4h})" if ticker4h is None
            else "DIST" if ad4h < 0
            else "ACCU" if ad4h > 0
            else "-",
            "style": "",
        },
        None,
    ])

    ROWS[symbol] = row


async def updateRows() -> None:
    await asyncio.wait([
        updateRow(symbol) for symbol in _prices.SYMBOLS
    ])


async def printTable() -> None:
    table = tableRowFormat(TABLE_HEADERS)
    # list rows by the init order
    for symbol in _prices.SYMBOLS:
        if symbol in ROWS:
            table += ROWS[symbol]

    os.system('cls' if os.name == 'nt' else 'clear')
    print(table, end="")
