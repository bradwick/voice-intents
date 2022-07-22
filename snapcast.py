import asyncio
import json
import time

import websockets


def mac_from_device(device):
    if device == 'kitchen':
        return 'b8:27:eb:92:32:63'
    else:
        return 'b8:27:eb:a6:6a:47'


async def volume_change(device, end_vol, step_multiplier=1):
    mac = mac_from_device(device)
    current_vol = await cur_vol(device)
    async with websockets.connect('ws://10.0.0.10:1780/jsonrpc',
                                  extra_headers={"content-type": "application/json"}) as ws:
        direction = 1 if end_vol >= current_vol else -1
        step = direction * step_multiplier
        for x in range(current_vol, end_vol + direction, step):
            await asyncio.sleep(.1)
            if abs(x - end_vol) < abs(step):
                x = end_vol
            vol_data = {"id": 1337, "jsonrpc": "2.0", "method": "Client.SetVolume",
                        "params": {"id": mac, "volume": {"muted": False, "percent": x}}}
            await ws.send(json.dumps(vol_data))


async def cur_vol(device):
    mac = mac_from_device(device)
    async with websockets.connect('ws://10.0.0.10:1780/jsonrpc',
                                  extra_headers={"content-type": "application/json"}) as ws:
        tick = int(time.time())
        get_status_data = {"id": tick, "jsonrpc": "2.0", "method": "Client.GetStatus", "params": {"id": mac}}
        await ws.send(json.dumps(get_status_data))
        resp = await ws.recv()
        jresp = json.loads(resp)
        if jresp.get('id') == tick:
            # this is our message response
            return jresp.get('result').get('client').get('config').get('volume').get('percent')
