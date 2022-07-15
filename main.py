import asyncio
import json
import threading

import websockets

import snapcast

VOL = None


async def listen_wake():
    global VOL
    async with websockets.connect('ws://10.0.0.110:12101/api/events/wake') as ws:
        while True:
            wake = await ws.recv()
            print(wake)
            VOL = await snapcast.cur_vol('radiopi')
            await snapcast.volume_change('radiopi', 2)


async def listen_intent():
    async with websockets.connect('ws://10.0.0.10:12101/api/events/intent') as ws:
        while True:
            data = await ws.recv()
            jdata = json.loads(data)
            print(jdata)
            await intent_switch(jdata)


async def intent_switch(jdata):
    name = jdata.get('intent').get('name')
    if name == 'MusicVolume':
        await snapcast.volume_change('kitchen' if 'kitchen' in jdata.get('raw_text') else 'radiopi',
                                     jdata.get('slots').get('volume'))
        if 'kitchen' not in jdata.get('raw_text'):
            return None
    await snapcast.volume_change('radiopi', VOL)


if __name__ == '__main__':
    intent_thread = threading.Thread(target=asyncio.run, args=(listen_intent(),))
    wake_thread = threading.Thread(target=asyncio.run, args=(listen_wake(),))

    intent_thread.start()
    wake_thread.start()
