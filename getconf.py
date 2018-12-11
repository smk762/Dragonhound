#!/usr/bin/env python3

#Credit to @Alright for the RPCs

import re
import os
import requests
import json
import platform

# define function that fetchs rpc creds from .conf
def def_credentials(chain):
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Win64':
        ac_dir = "dont have windows machine now to test"
    # define config file path
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    #define rpc creds
    with open(coin_config_file, 'r') as f:
        #print("Reading config file for credentials:", coin_config_file)
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    return('http://' + rpcuser + ':' + rpcpassword + '@127.0.0.1:' + rpcport)

# define function that posts json data
def post_rpc(url, payload, auth=None):
    try:
        r = requests.post(url, data=json.dumps(payload), auth=auth)
        return(json.loads(r.text))
    except Exception as e:
        raise Exception("Couldn't connect to " + url + ": ", e)

# Return current -pubkey=
def getpubkey_rpc(chain):
    getinfo_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "getinfo",
        "params": []}
    getinfo_result = post_rpc(def_credentials(chain), getinfo_payload)

    return(getinfo_result['result']['pubkey'])

# return latest batontxid from all publishers
def get_latest_batontxids(chain, oracletxid):
    oraclesinfo_result = oraclesinfo_rpc(chain, oracletxid)
    latest_batontxids = {}
    # fill "latest_batontxids" dictionary with publisher:batontxid data
    for i in oraclesinfo_result['registered']:
        latest_batontxids[i['publisher']] = i['batontxid']
    return(latest_batontxids)

#VANILLA RPC

def sendrawtx_rpc(chain, rawtx):
    sendrawtx_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "sendrawtransaction",
        "params": [rawtx]}
    #rpcurl = def_credentials(chain)
    return(post_rpc(def_credentials(chain), sendrawtx_payload))

def signmessage_rpc(chain, address, message):
    signmessage_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "signmessage",
        "params": [
            address,
            message
        ]
    }
    signmessage_result = post_rpc(def_credentials(chain), signmessage_payload)
    return(signmessage_result['result'])

def verifymessage_rpc(chain, address, signature, message):
    verifymessage_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "verifymessage",
        "params": [
            address,
            signature,
            message
        ]
    }
    verifymessage_result = post_rpc(def_credentials(chain), verifymessage_payload)
    return(verifymessage_result['result'])

def kvsearch_rpc(chain, key):
    kvsearch_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "kvsearch",
        "params": [
            key
        ]
    }
    kvsearch_result = post_rpc(def_credentials(chain), kvsearch_payload)
    return(kvsearch_result['result'])

def kvupdate_rpc(chain, key, value, days, password):
    # create dynamic oraclessamples payload
    kvupdate_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "kvupdate",
        "params": [
            key,
            value,
            str(days),
            password]}
    # make kvupdate rpc call
    kvupdate_result = post_rpc(def_credentials(chain), kvupdate_payload)
    return(kvupdate_result)

def oraclesdata_rpc(chain, oracletxid, hexstr):
    oraclesdata_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "oraclesdata",
        "params": [
            oracletxid,
            hexstr]}
    oraclesdata_result = post_rpc(def_credentials(chain), oraclesdata_payload)
    return(oraclesdata_result['result'])

def oraclescreate_rpc(chain, name, description, oracle_type):
    oraclescreate_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "oraclescreate",
        "params": [
            name,
            description,
            oracle_type]}
    oraclescreate_result = post_rpc(def_credentials(chain), oraclescreate_payload)
    return(oraclescreate_result['result'])

def oraclesinfo_rpc(chain, oracletxid):
    oraclesinfo_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "oraclesinfo",
        "params": [oracletxid]}
    oraclesinfo_result = post_rpc(def_credentials(chain), oraclesinfo_payload)
    return(oraclesinfo_result['result'])

def oracleslist_rpc(chain):
    oracleslist_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "oracleslist",
        "params": []}
    oracleslist_result = post_rpc(def_credentials(chain), oracleslist_payload)
    return(oracleslist_result['result'])

def oraclessubscribe_rpc(chain, oracletxid, publisher, amount):
    oraclessubscribe_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "oraclessubscribe",
        "params": [oracletxid, publisher, amount]}
    oraclessubscribe_result = post_rpc(def_credentials(chain), oraclessubscribe_payload)
    return(oraclessubscribe_result['result'])

def oraclesregister_rpc(chain, oracletxid, datafee):
    oraclesregister_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "oraclesregister",
        "params": [
            oracletxid,
            str(datafee)]}
    oraclesregister_result = post_rpc(def_credentials(chain), oraclesregister_payload)
    return(oraclesregister_result['result'])

def oraclessamples_rpc(chain, oracletxid, batonutxo, num):
    oraclessamples_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "oraclessamples",
        "params": [
            oracletxid,
            batonutxo,
            str(num)]}
    oraclessamples_result = post_rpc(def_credentials(chain), oraclessamples_payload)
    return(oraclessamples_result['result'])

def getlastsegidstakes_rpc(chain, depth):
    oraclessubscribe_payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": "oraclessubscribe",
        "params": [depth]}
    getlastsegidstakes_result = post_rpc(def_credentials(chain), oraclessubscribe_payload)
return(getlastsegidstakes_result['result'])
