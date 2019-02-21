#!/usr/bin/env python3
import sys
import codecs
import requests
import time
import getconf
import psycopg2
import time
import enc
import pgio

userdb = 'authentication_oracle'


def create_oracle(chain, houndname, user_id):
	result = getconf.oraclescreate_rpc(chain, houndname, username+"'s Dragonhound Track History", "S")
	print("oracle_create: "+str(result))
	oracleHex=result['hex']
	print("oracleHex: "+oracleHex)
	oracleResult=result['result']
	print("oracleResult: "+oracleResult)
	while oracleResult != 'success':
		result = getconf.oraclescreate_rpc(chain, houndname, username+"'s Dragonhound Track History", "S")
		print("oracle_create: "+result)
		oracleHex=result['hex']
		print("oracleHex: "+oracleHex)
		oracleResult=result['result']
		print("create oracleResult: "+oracleResult)

	print('----------- SENDING RAW -----------')
	result = getconf.sendrawtx_rpc(chain, oracleHex)
	print("rawtx: "+str(result))
	print("raw_result: "+result['result'])
	while len(result['result']) != 64:
		time.sleep(15)
		result = getconf.sendrawtx_rpc(chain, oracleHex)
		print("rawtx: "+result)
		print("raw_result: "+result['result'])
	orclid = result['result']

	print("--------------------- Confirm Tx --------------------- ")
	memPool = str(getconf.getrawmempool_rpc(chain))
	while memPool.find(orclid) < 0:
		time.sleep(15)
		memPool = str(getconf.getrawmempool_rpc(chain))
		print(memPool)
		print(orclid)
	print("Oracle creation tx confirmed")

	print("--------------------- Confirm Listing --------------------- ")
	oraclesList = str(getconf.oracleslist_rpc(chain))
	while oraclesList.find(orclid) < 0:
		time.sleep(15)
		oraclesList = str(getconf.oracleslist_rpc(chain))
		print(oraclesList)
		print(orclid)
	print("Oracle Listing confirmed")

	print("--------------------- Registering Oracle --------------------- ")
	datafee = '1000000'
	rego = getconf.oraclesregister_rpc(chain, orclid, datafee)
	print("rego: "+str(rego))
	oracleHex=rego['hex']
	print("oracleHex: "+oracleHex)
	oracleResult=rego['result']
	print("oracleResult: "+oracleResult)
	while oracleResult != 'success':
		rego = getconf.oraclesregister_rpc(chain, orclid, datafee)
		print("rego: "+str(rego))
		oracleHex=rego['hex']
		print("oracleHex: "+oracleHex)
		oracleResult=rego['result']
		print("reg oracleResult: "+oracleResult)
	print("Oracle registered")


	print("--------------------- SENDING RAW --------------------- ")
	result = getconf.sendrawtx_rpc(chain, oracleHex)
	print("rawtx: "+str(result))
	print("rawtx['result']: "+result['result'])
	while len(result['result']) != 64:
		time.sleep(15)
		result = getconf.sendrawtx_rpc(chain, oracleHex)
		print("rawtx: "+str(result))
		print("rawtx['result']: "+result['result'])
	rego_hex = result['result']
	print("raw rego_hex: "+rego_hex)

	print("--------------------- Confirm Tx --------------------- ")
	memPool = str(getconf.getrawmempool_rpc(chain))
	while memPool.find(rego_hex) < 0:
		time.sleep(15)
		memPool = str(getconf.getrawmempool_rpc(chain))
		print(memPool)
		print("mempool rego_hex: "+rego_hex)
	print("Oracle rego confirmed")

	print("--------------------- Get Info --------------------- ")
	time.sleep(60)
	orcl_info = getconf.oraclesinfo_rpc(chain, orclid)
	print("info: "+str(orcl_info))
	reg_json=orcl_info['registered']
	print("reg: "+str(reg_json))
	while len(reg_json) < 1:
		time.sleep(30)
		reg_json=orcl_info['registered']
		print("reg: "+str(reg_json))
		print("len: "+str(len(reg_json)))
	print("reg: "+str(reg_json))
	print("len: "+str(len(reg_json)))
	print("DONE --------------------------------------------------------------------------------")
	name=orcl_info['name']
	print("name: "+str(name))
	orclid=orcl_info['txid']
	print("orclid: "+str(orclid))
	funds='{:.2f}'.format(float(orcl_info['registered'][0]['funds']))
	print("funds: "+str(funds))
	publisher=str(orcl_info['registered'][0]['publisher'])
	print("pub: "+str(publisher))
	#sql = "UPDATE "+userdb+" SET orcl_id = '"+orclid+"', orcl_pub = '"+publisher+"' WHERE user_id = '"+user_id+"';"
	print(sql)
	result = pgio.pgsqlio(sql)
	print(result)
	return orclid


def write2oracle(CHAIN, ORCLID, MSG):
	print("MSG: " + str(MSG))
	rawhex = codecs.encode(MSG).hex()

	#get length in bytes of hex in decimal
	bytelen = int(len(rawhex) / int(2))
	hexlen = format(bytelen, 'x')

	#get length in big endian hex
	if bytelen < 16:
		bigend = "000" + str(hexlen)
	elif bytelen < 256:
		bigend = "00" + str(hexlen)
	elif bytelen < 4096:
		bigend = "0" + str(hexlen)
	elif bytelen < 65536:
		bigend = str(hexlen)
	else:
		print("message too large, must be less than 65536 characters")

	#convert big endian length to little endian, append rawhex to little endian length
	lilend = bigend[2] + bigend[3] + bigend[0] + bigend[1]
	fullhex = lilend + rawhex

	print("CHAIN: "+ CHAIN)
	print("ORCLID: "+ ORCLID)
	print("fullhex: "+ fullhex)
	oraclesdata_result = getconf.oraclesdata_rpc(CHAIN, ORCLID, fullhex)
	print(str(oraclesdata_result))
	result = oraclesdata_result['result']
	if result == 'error':
		print('ERROR:' + oraclesdata_result['error'] + ', try using oraclesregister if you have not already')
	else:
		print('event written to '+CHAIN)
		print('aes: '+MSG)
		rawtx = oraclesdata_result['hex']
		sendrawtx_result = getconf.sendrawtx_rpc(CHAIN, rawtx)
	return result



def read_oracle(CHAIN, ORCLID, numrec):
	orcl_info = getconf.oraclesinfo_rpc(CHAIN, ORCLID)
	batonutxo=orcl_info['registered'][0]['batontxid']
	name=orcl_info['name']
	funds='{:.2f}'.format(float(orcl_info['registered'][0]['funds']))
	publisher=orcl_info['registered'][0]['publisher']
	samples = getconf.oraclessamples_rpc(CHAIN, ORCLID, batonutxo, numrec)
	return samples['samples']



def fund_oracle(chain, orclid ,publisher, funds):
	amount = funds/10;
	for x in range(1,10):
		oracleSubscription = getconf.oraclessubscribe_rpc(chain, orclid, publisher, amount)
		#print(oracleSubscription)
		result=oracleSubscription['result']
		while result != 'success':
			oracleSubscription = getconf.oraclessubscribe_rpc(chain, orclid, publisher, amount)
			#print(oracleSubscription)
			result=oracleSubscription['result']

def create_oraclekey(Radd):
	oraclekey = enc.genPass(32)
	return oraclekey
