import asyncio
import threading
import _prices
import _table

SET_INTERVAL = []


def setInterval(func, sec):
    def funcWrapper():
        timer.cancel()
        SET_INTERVAL.remove(timer)
        setInterval(func, sec)
        asyncio.run(func())
    timer = threading.Timer(sec, funcWrapper)
    timer.start()
    SET_INTERVAL.append(timer)

def stopIntervals():
    for timer in SET_INTERVAL:
        timer.cancel()

async def update():
    await _prices.updateSymbols()
    await _table.updateTable()