import asyncio
import json
import threading

import websockets

import snapcast

VOL = None


async def listen_wake():
    global VOL

    try:
        print("listening for wake")
        async with websockets.connect('ws://10.0.0.110:12101/api/events/wake') as ws:
            while True:
                wake = await ws.recv()
                VOL = await snapcast.cur_vol('radiopi')
                await snapcast.volume_change('radiopi', 2, step_multiplier=5)
    except websockets.ConnectionClosedError as e:
        print(e)
        asyncio.sleep(5)
        start_wake_thread()


async def listen_intent():
    try:
        print("listening for intent")
        async with websockets.connect('ws://10.0.0.10:12101/api/events/intent') as ws:
            while True:
                data = await ws.recv()
                jdata = json.loads(data)
                await intent_switch(jdata)
    except websockets.ConnectionClosedError as e:
        print(e)
        asyncio.sleep(5)
        start_intent_thread()


async def intent_switch(jdata):
    name = jdata.get('intent').get('name')
    if name == 'MusicVolume':
        await snapcast.volume_change('kitchen' if 'kitchen' in jdata.get('raw_text') else 'radiopi',
                                     jdata.get('slots').get('volume'))
        if 'kitchen' not in jdata.get('raw_text'):
            return None
    await snapcast.volume_change('radiopi', VOL)


def start_intent_thread():
    intent_thread = threading.Thread(target=asyncio.run, args=(listen_intent(),))
    intent_thread.start()


def start_wake_thread():
    wake_thread = threading.Thread(target=asyncio.run, args=(listen_wake(),))
    wake_thread.start()


if __name__ == '__main__':
    start_intent_thread()
    start_wake_thread()
