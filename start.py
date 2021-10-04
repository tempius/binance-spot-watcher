import asyncio
import _utils
import _bcolors
import _prices
import _table
import _websockets

# ADD HERE THE COIN/PAIR TO WATCH
SPOTS_TO_CHECK = [
    {'coin': 'btc', 'pair': 'busd'},
    {'coin': 'atom', 'pair': 'busd'},
    {'coin': 'avax', 'pair': 'busd'},
    {'coin': 'dot', 'pair': 'busd'},
    {'coin': 'icp', 'pair': 'busd'},
    {'coin': 'near', 'pair': 'busd'},
    {'coin': 'sol', 'pair': 'busd'},
]


def start(loop):
    _prices.initPrices(SPOTS_TO_CHECK)
    _utils.setInterval(_utils.update, 1)
    _utils.setInterval(_table.printTable, 1)
    loop.run_until_complete(_websockets.openConnections(SPOTS_TO_CHECK))


def stop(loop):
    print(f"\n{_bcolors.CYAN}GRACEFULLY STOPPING, PLEASE WAIT... (press Ctrl+C again to force){_bcolors.END}")
    _utils.stopIntervals()
    try:
        loop.run_until_complete(_websockets.closeConnections())
        print(f"\n{_bcolors.GREEN}STOP COMPLETED!{_bcolors.END}")
    except KeyboardInterrupt:
        print(f"\n{_bcolors.FAIL}FORCED STOP!{_bcolors.END}")
    exit()


# Run the script
try:
    loop = asyncio.get_event_loop()
    start(loop)
except KeyboardInterrupt:
    stop(loop)
