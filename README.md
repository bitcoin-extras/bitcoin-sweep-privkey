# Python Private-Key Sweeper

This wonderful piece of software is a python based private key sweeper.
It allows you to sweep any private key to a central wallet. This feature is useful,
to for example collect funds from multiple, different wallets (e.g. depositing wallets at a bitcoin gambling site) into a central place.

# Privacy

While blockchain.info allows you to sweep a private key, we wanted to introduce a complete autonomous solution. While it can be used with blockchain.info as a backend, you can as well use your own blockchain API server like the INSIGHT API so drive this software.

Transactions get pushed to the network through your local bitcoind node, so your transactions (if chosen so) never leave your own infrastructure prior to relaying.

# Running

The funds can be swept easily by issuing this command with the private key as an argument.
So for example to sweep all funds from 1LdgTMX2MEqdfT3VcDpX4GyD1mqCP8LkYe do:

```
python sweeper.py 5JZB4ewYsbJhej6Psb5gL1h5BL26EoA49EzwoLSSXB8rtEDX8su
```

# Configuration

The configuration takes place in the file sweeper.py, more precisely in this piece of code. This should be self explaining. Make sure to put in the correct settings.

```python
DESTINATION_ADDRESS="1SEX4FWWSxEHfRZ9Q8ugrC3rqEdW2tJVo"
FEE_PER_KB = 10000
BTCD_USER = "bitcoinrpc"
BTCD_PASS = "yourpassword"
BTCD_HOST = "localhost"
BTCD_PORT = "8332"

# this should point to your INSIGHT API Server
#UNSPENT_CHECKER = "http://localhost:3000/api/addr/%s/utxo?noCache=1"

MAX_BITCOIND_TRIES = 10
MAX_BLOCKCHAIN_API_URL_TRIES = 10
```

Also, the time configurations are telling the script, how often to try reaching a service before exiting.

Make sure your bitcoin client is configured as a server, e.g. edit (or create) a bitcoin.conf file with at least this content. The file usually lies in ~/.bitcoin/bitcoin.conf:

```
rpcuser=bitcoinrpc
rpcpassword=yourpassword
server=1
```

If you want to use your own Bitcoin API Server (for example insight) you need the txindex=1 flag as well.

```
rpcuser=bitcoinrpc
rpcpassword=yourpassword
server=1
txindex=1
```
