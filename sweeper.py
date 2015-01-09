import urllib2
import sys
from deserialize import *
import utils
from json import *
from bitcoin import *
import signal

DESTINATION_ADDRESS="1SEX4FWWSxEHfRZ9Q8ugrC3rqEdW2tJVo" 
FEE_PER_KB = 10000 
BTCD_USER = "bitcoinrpc"
BTCD_PASS = "yourpassword"
BTCD_HOST = "localhost"
BTCD_PORT = "8332"

# this line is when you want to use your own INSIGHT-API server
#UNSPENT_CHECKER = "http://localhost:3000/api/addr/%s/utxo?noCache=1"

# otherwise just use blockchain.info to get the history
UNSPENT_CHECKER = "https://blockchain.info/de/unspent?active=%s"

MAX_BITCOIND_TRIES = 10
MAX_BLOCKCHAIN_API_URL_TRIES = 10


class BlockchainProcessor:
    def hasunspent(self, addr):
        global MAX_BLOCKCHAIN_API_URL_TRIES
        while True:
            try:
                f = urllib2.urlopen(UNSPENT_CHECKER % addr)
                res =  f.read()
                if len(res)>10:
                    return True
                else:
                    return False
            except urllib2.HTTPError, e:
                if e.code == 500:
                    # some services as blockchain return error 500 when no unspent outputs present
                    return False
                elif e.code == 404:
                    print "[HTTP] error 404 on blockchain api webserver. check the url please."
                    return False
            except urllib2.URLError, e:
                MAX_BLOCKCHAIN_API_URL_TRIES = MAX_BLOCKCHAIN_API_URL_TRIES - 1
                if MAX_BLOCKCHAIN_API_URL_TRIES == 0:
                    print "[HTTP] no connection to blockchain api webserver. check the url please."
                    return False
                else:
                    print "[HTTP] blockchain api webserver offline. retrying."
                    try:
                        time.sleep(1)
                    except:
                        pass


    def sweep_afterward(self, privkey):
        priv = privkey
        pub = privtopub(priv)
        addr = pubtoaddr(pub)
        print "[sweep] address:",addr,"priv:",priv

        if not self.hasunspent(addr):
            return
        try:
            h = history(addr)
        except:
            print "[sweep] ERROR: cannot sweep account with fucked up inputs"
            return
        unspent = 0
        fee = 30000
        inputs = 0
        for p in h:
            if 'spend' in p and p['spend'] != '':
                continue
            inputs += 1
            unspent += p['value']
        print "[sweep] found unspent coins:",unspent
        

        # deduct fee only if this would not result in balance <= 0.
        # otherwise, just try to send without fee ... for fucks sake.
        # TODO: Here we could think about putting a large "pseudo input" in to make this transaction free
        sizeOfTx = 148 * inputs + 34 * 1 + 10 
        wholeThousands = (sizeOfTx / 1000) + 1
        feePerKb = fee * wholeThousands
        print "[sweep] deducting fee:",feePerKb
        amnt = unspent-feePerKb
        if amnt <=0:
            amnt = amnt + feePerKb; # restore again

        if amnt<=0:
            print "[sweep] no balance"
            return

        print "[sweep] sweeping:",amnt
        dest = DESTINATION_ADDRESS
        outs = [{'value': amnt, 'address': dest}]
        print "[sweep] destination:",amnt
        tx = mktx(h,outs)
        print "[sweep] signing",inputs,"inputs"

        for i in range(inputs):
            tx = sign(tx,i,priv)

        self.pushtx(tx)
        print "[sweep] pushed"

    def push_bitcoind_threaded(self,tx):
        self.bitcoind('sendrawtransaction', [tx], True)
        print "[PUSH] successfully pushed to local bitcoind node."

    def pushtx(self, tx):
        if not re.match('^[0-9a-fA-F]*$', tx):
            tx = tx.encode('hex')

        self.push_bitcoind_threaded(tx) # no need for threads, as no other pushes should occur simultaneously

    def bitcoind(self, method, params=[], retry=False):
        global MAX_BITCOIND_TRIES
        postdata = dumps({"method": method, 'params': params, 'id': 'jsonrpc'})
        while True:
            try:
                request = urllib2.Request(self.bitcoind_url)
                base64string = base64.encodestring('%s:%s' % (BTCD_USER, BTCD_PASS)).replace('\n', '')
                request.add_header("Authorization", "Basic %s" % base64string)   
                respdata = urllib2.urlopen(request, postdata).read()
                r = loads(respdata)
                if r['error'] is not None:
                    raise BaseException(r['error'])
                return r.get('result')
            except Exception as e:
                MAX_BITCOIND_TRIES = MAX_BITCOIND_TRIES - 1
                if MAX_BITCOIND_TRIES == 0:
                    return
                print "[btcd] cannot reach bitcoind, retrying in 1s."
                try:
                    time.sleep(1)
                except:
                    pass
                continue
        return {'error':'exiting'}

        

if __name__ == '__main__':
    global processor
    processor = BlockchainProcessor()
    processor.sweep_afterward(sys.argv[1])
   
