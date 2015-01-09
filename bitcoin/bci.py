#!/usr/bin/python
import json
import re
import random
import sys
from six.moves import urllib


# wiped any thirdparty services so nothing goes wrong due to privacy


# Makes a request to a given URL (first arg) and optional params (second arg)
def make_request(*args):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent',
                          'Mozilla/5.0'+str(random.randrange(1000000)))]
    try:
        return opener.open(*args).read().strip()
    except Exception as e:
        try:
            p = e.read().strip()
        except:
            p = e
        raise Exception(p)

# Gets the transaction output history of a given set of addresses,
# including whether or not they have been spent
def history(*args):
    # Valid input formats: history([addr1, addr2,addr3])
    #                      history(addr1, addr2, addr3)
    if len(args) == 0:
        return []
    elif isinstance(args[0], list):
        addrs = args[0]
    else:
        addrs = args

    txs = []
    for addr in addrs:
        offset = 0
        while 1:
            data = make_request(
                'https://blockchain.info/address/%s?format=json&offset=%s' %
                (addr, offset))
            try:
                jsonobj = json.loads(data)
            except:
                raise Exception("Failed to decode data: "+data)
            txs.extend(jsonobj["txs"])
            if len(jsonobj["txs"]) < 50:
                break
            offset += 50
            sys.stderr.write("Fetching more transactions... "+str(offset)+'\n')
    outs = {}
    for tx in txs:
        for o in tx["out"]:
            try: # Add try catch, as some custom outputs do not have a addr field which leads to errors
                if o['addr'] in addrs:
                    key = str(tx["tx_index"])+':'+str(o["n"])
                    outs[key] = {
                        "address": o["addr"],
                        "value": o["value"],
                        "output": tx["hash"]+':'+str(o["n"]),
                        "block_height": tx.get("block_height", None)
                    }
            except:
                pass
    for tx in txs:
        for i, inp in enumerate(tx["inputs"]):
            try: # Add try catch, as some custom inputs do not have a addr field which leads to errors
                if inp["prev_out"]["addr"] in addrs:
                    key = str(inp["prev_out"]["tx_index"]) + \
                        ':'+str(inp["prev_out"]["n"])
                    if outs.get(key):
                        outs[key]["spend"] = tx["hash"]+':'+str(i)
            except:
                pass
    return [outs[k] for k in outs]




def last_block_height():
    data = make_request('https://blockchain.info/latestblock')
    jsonobj = json.loads(data)
    return jsonobj["height"]


