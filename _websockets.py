import asyncio
import websockets
import json
import _prices

CONNECTIONS = {}
CLOSE_CONNECTIONS = False


def updateConnections(symbol, websocket):
    CONNECTIONS[symbol] = websocket


async def handleWebsocket(symbol):
    async with websockets.connect(f"wss://stream.binance.com:9443/ws/{symbol}@ticker") as websocket:
        updateConnections(symbol, websocket)
        # Process messages received on the connection.
        async for msg in websocket:
            json_obj = json.loads(msg)
            _prices.updateTickers(symbol, json_obj)


async def handleTicker(symbol):
    while not CLOSE_CONNECTIONS:
        await handleWebsocket(symbol)


async def closeConnections():
    global CLOSE_CONNECTIONS

    CLOSE_CONNECTIONS = True
    if len(CONNECTIONS.keys()) > 0:
        await asyncio.wait([
            CONNECTIONS[symbol].close() for symbol in CONNECTIONS
        ])


async def openConnections(_spotsToCheck=[]):
    await asyncio.wait([
        handleTicker(f"{spot['coin']}{spot['pair']}") for spot in _spotsToCheck
    ])
