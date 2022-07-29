import asyncio
import datetime

import requests

URL = 'http://10.0.0.10:1780/jsonrpc'
HEADERS = {"content-type": "application/json"}


def mac_from_device(device):
    if device == 'kitchen':
        return 'b8:27:eb:92:32:63'
    elif device == 'laundry':
        return 'c8:d3:ff:9e:56:93'
    else:
        return 'b8:27:eb:a6:6a:47'


async def volume_change(device, end_vol, step_multiplier=1):
    mac = mac_from_device(device)
    current_vol = await cur_vol(device)
    vol_steps = []

    direction = 1 if end_vol >= current_vol else -1
    step = direction * step_multiplier
    for x in range(current_vol, end_vol + direction, step):
        await asyncio.sleep(.1)
        if abs(x - end_vol) < abs(step):
            x = end_vol
        if x < 0 or x > 100:
            print(f'Just tried to set the volume to {x}... aborting')
            break
        vol_data = {"id": 1337, "jsonrpc": "2.0", "method": "Client.SetVolume",
                    "params": {"id": mac, "volume": {"muted": False, "percent": x}}}
        vol_steps.append(x)
        resp = requests.post(URL, json=vol_data, headers=HEADERS)
        print(resp.json())

    print(f'At {datetime.datetime.now()} I changed the volume in this order : {vol_steps}')


async def cur_vol(device):
    mac = mac_from_device(device)
    get_status_data = {"id": 1337, "jsonrpc": "2.0", "method": "Client.GetStatus", "params": {"id": mac}}
    resp = requests.post(URL, json=get_status_data, headers=HEADERS)
    jresp = resp.json()
    return jresp.get('result').get('client').get('config').get('volume').get('percent')
