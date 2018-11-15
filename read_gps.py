#!/usr/bin/env python3
import sys
import os
import json
import getconf
import colorTable
import enc

HOME = os.environ['HOME']
CONFIGDIR = str(HOME+'/.Dragonhound/')

def selectRange(low,high, msg): 
	while True:
		try:
			number = int(input(msg))
		except ValueError:
			print("integer only, try again")
			continue
		if low <= number <= high:
			return number
		else:
			print("input outside range, try again")

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
num = selectRange(0,999999999,"How many records? ")
samples = getconf.oraclessamples_rpc(CHAIN, ORCLID, batonutxo, num)
for sample in samples['samples']:
	#print(sample[0])
	try:
		dec = enc.decrypt(str.encode(sample[0]), pword)
		#print(dec)
		msg = bytes.decode(dec)
		print(msg)
	except Exception as e:
		pass