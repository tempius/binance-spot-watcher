import typing
import asyncio
import websockets
import json
import _prices

CONNECTIONS = {}
KEEP_CONNECTING = True


async def handleWebsocket(symbol: str) -> None:
    while KEEP_CONNECTING:
        try:
            async with websockets.connect(f"wss://stream.binance.com:9443/ws/{symbol}@ticker") as websocket:
                CONNECTIONS[symbol] = websocket
                # Process messages received on the connection.
                async for msg in websocket:
                    json_obj = json.loads(msg)
                    _prices.updateTickers(symbol, json_obj)
        except:
            if KEEP_CONNECTING:
                continue


async def closeConnections() -> None:
    global KEEP_CONNECTING

    KEEP_CONNECTING = False
    if len(CONNECTIONS.keys()) > 0:
        await asyncio.wait([
            CONNECTIONS[symbol].close() for symbol in CONNECTIONS
        ])


async def openConnections(_spotsToCheck: typing.List[typing.Dict[str, str]]) -> None:
    await asyncio.wait([
        handleWebsocket(f"{spot['coin']}{spot['pair']}") for spot in _spotsToCheck
    ])
