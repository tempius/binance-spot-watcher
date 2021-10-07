import asyncio
import threading
import _prices
import _table

SET_INTERVAL = []


def setInterval(func: callable, sec: int) -> None:
    def funcWrapper():
        timer.cancel()
        SET_INTERVAL.remove(timer)
        setInterval(func, sec)
        asyncio.run(func())
    timer = threading.Timer(sec, funcWrapper)
    timer.start()
    SET_INTERVAL.append(timer)


def stopIntervals() -> None:
    for timer in SET_INTERVAL:
        timer.cancel()


async def update() -> None:
    await _prices.updateSymbols()
    await _table.updateTable()
