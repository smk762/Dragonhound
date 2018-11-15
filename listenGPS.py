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
import calendar;


#file and path vars
HOME = os.environ['HOME']
CONFIGDIR = str(HOME+'/.Dragonhound/')
CACHE = str(CONFIGDIR+'/cache/')


if not os.path.exists(CONFIGDIR):
	print('generating password')
	os.makedirs(CONFIGDIR)	
	f = open(CONFIGDIR+'gps.pgs', 'w+')
	password = enc.genPass(32)
	f.write(password)
	f.close()

if os.path.exists(CACHE):
	shutil.rmtree('CACHE')
	os.makedirs(CACHE)

try:
	with open(CONFIGDIR+'gps.pgs', 'r') as file:
		pword = file.read()
except IOError as e:
	print("Password not set or access denied!")

try:
	with open(CONFIGDIR+'token.pio', 'r') as file:
		token = file.read()
except IOError as e:
	print("Particle.io token not set!")

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


r = requests.get('https://api.particle.io/v1/devices/events?access_token='+token, stream=True)

if r.encoding is None:
	r.encoding = 'utf-8'

timestamp = int(time.time())
print('time: '+str(timestamp))
for line in r.iter_lines(decode_unicode=True):
	if line:
		if line[0:5]=='data:':
			timestamp = int(time.time())
			print("data recieved at "+ str(timestamp))
			print('line: '+str(line))
			data = json.loads(line[6:])
			print('data: '+str(data))
			gpsdata = data['data']
			print('gpsdata: '+str(gpsdata))
			dataList = gpsdata.split(',')
			print('dataList length: '+str(len(dataList)))
			try :
				if len(dataList) == 3:
					lon = str(dataList[0])
					lat = str(dataList[1])
					charge = str(dataList[2])
					timestamp = int(time.time())
					#print('time: '+str(time))
					#print('lon: '+lon)
					#print('lat: '+lat)
					#print('c: '+charge)
					#print('---------------')
					gps = '{"data":"'+lon+','+lat+','+charge+'","published_at":"'+str(timestamp)+'"}'
					print(gps)
					gps_aes = enc.encrypt(gps,str(pword))
					print("aes: "+str(gps_aes))
					result = oraclesio.write2oracle(CHAIN, ORCLID, bytes.decode(gps_aes))
					while result == 'error':
						time.sleep(30)
						result = oraclesio.write2oracle(CHAIN, ORCLID, bytes.decode(gps_aes))
						print(result)	
					print('bytes.decode(aes): '+bytes.decode(gps_aes))
					gps_dec = enc.decrypt(gps_aes,pword)
					print('dec: '+bytes.decode(gps_dec))
			except Exception as e:
				print(e)
				pass