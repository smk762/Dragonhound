#!/usr/bin/env python3
import os
import enc
import shutil
import pycurl
import json
import requests
import enc
import sys
import codecs
import time
import getconf
import oraclesio
import random
import calendar
import datetime

#file and path vars
HOME = os.environ['HOME']
CONFIGDIR = str(HOME+'/.DragonhoundDemo/')


if not os.path.exists(CONFIGDIR):
	print('generating password')
	os.makedirs(CONFIGDIR)	
	f = open(CONFIGDIR+'gps.pgs', 'w+')
	password = enc.genPass(32)
	f.write(password)
	f.close()


try:
	with open(CONFIGDIR+'gps.pgs', 'r') as file:
		pword = file.read()
except IOError as e:
	print("Password not set or access denied!")

try:
	with open(CONFIGDIR+'orclid.gps', 'r') as file:
		ORCLID = file.read()
except IOError as e:
	print("Oracle Tx ID not set!")

try:
	with open(CONFIGDIR+'chain.gps', 'r') as file:
		CHAIN = file.read()
except IOError as e:
	print("CHAIN not set!")

chosen_info = getconf.oraclesinfo_rpc(CHAIN, ORCLID)
batonutxo=chosen_info['registered'][0]['batontxid']
try:
	num = 1
	sample = getconf.oraclessamples_rpc(CHAIN, ORCLID, batonutxo, num)
	print(json.dumps(sample['samples'][0][0]))
	dec = enc.decrypt(str.encode(sample['samples'][0][0]), pword)
	msg = bytes.decode(dec)
	msg2 = msg.replace("'","\"")
	data = json.loads(msg2)
	dataList = data['data'].split(',')
	timestamp = int(time.time())
	lon = dataList[0]
	lat = dataList[1]
	charge = dataList[2]
except IOError as e:
	print(e)
	lon = 56
	lat = 95
	charge = 100 
	pass
while True:
	if float(charge) > 30:
		x = 0.97
	else:
		x = 1.03
	lon = float(lon) + (random.random()-0.5)/100
	lat = float(lat) + (random.random()-0.5)/100
	charge = float(charge)*x
	fakegps = '{"data":"'+str("{:.4f}".format(lon))+','+str("{:.4f}".format(lat))+','+str("{:.2f}".format(charge))+'","ttl":60,"published_at":"'+str(timestamp)+'","coreid":"999999999999999999999999"}'
	data = json.loads(fakegps)
	gpsdata = data['data']
	dataList = gpsdata.split(',')
	gps_aes = enc.encrypt(str(data),str(pword))
	result = oraclesio.write2oracle(CHAIN, ORCLID, bytes.decode(gps_aes))
	while result == 'error':
		time.sleep(30)
		result = oraclesio.write2oracle(CHAIN, ORCLID, bytes.decode(gps_aes))
		print(result)	
	gps_dec = enc.decrypt(gps_aes,pword)
	time.sleep(300)
