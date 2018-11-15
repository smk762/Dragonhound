#!/usr/bin/env python3
import cherrypy
from cherrypy.lib import auth_digest
import sys
import os
import json
import getconf
import colorTable
import enc
from datetime import datetime

USERS = {'test': 'gps'}
HOME = os.environ['HOME']
CONFIGDIR = str(HOME+'/.DragonhoundDemo/')
HTMLDIR = str(HOME+'/Dragonhound/html/')

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

def makeLines(trackvar, trackname, points, col, wt, alpha, sf, classname):
	trackvar = """var """+trackvar+""" = """+str(points)+""";
    var """+trackname+""" = new L.Polyline("""+trackvar+""", {
        color: '"""+col+"""',
        weight: """+wt+""",
        opacity: """+alpha+""",
        smoothFactor: """+sf+""",
        className: '"""+classname+"""'
    });                                               
    map.addLayer("""+trackname+""");"""
	return trackvar    

def makePoint(point, icon, tip, classname, alpha):
	pointvar ="""
		L.marker("""+str(point)+""", {className: '"""+classname+"""', icon: """+icon+""", opacity: """+alpha+"""}).bindTooltip('"""+tip+"""').addTo(map)
	""";	
	return pointvar	


class MapPage:
	@cherrypy.expose
	def default(self, token):
		gpsdata = "";
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
		name=chosen_info['name']
		funds='{:.2f}'.format(float(chosen_info['registered'][0]['funds']))
		publisher=chosen_info['registered'][0]['publisher']
		print("name: "+str(name))
		print("funds: "+str(funds))
		print("publisher: "+str(publisher))
		if float(funds) < 200:
			amount = 50
			result = getconf.oraclessubscribe_rpc(CHAIN, ORCLID, publisher, amount)
			print("oracle funds added!")
			chosen_info = getconf.oraclesinfo_rpc(CHAIN, ORCLID)
			funds='{:.2f}'.format(float(chosen_info['registered'][0]['funds']))
			print("Oracle funds: "+funds)
		num = 99
		samples = getconf.oraclessamples_rpc(CHAIN, ORCLID, batonutxo, num)
		num_samples = len(samples['samples'])
		print("num_samples: "+str(num_samples))
		leaflet_data = []
		points = []
		lastpoint =""
		lastcharge = ""
		bounds =""
		view = ""
		point_var=""
		opac = 0.99;
		i = 0;
		for sample in samples['samples']:
			try:
				dec = enc.decrypt(str.encode(sample[0]), pword)
				msg = bytes.decode(dec)
				msg2 = msg.replace("'","\"")
				data = json.loads(msg2)
				dataList = data['data'].split(',')
				timestamp = data['published_at']
				#print('time: '+timestamp)
				timestamp = datetime.utcfromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')+" UTC"
				#print('time: '+str(timestamp))
				if lastpoint == "":
					print("adding last point")
					print('time: '+str(timestamp))
					print('lon: '+dataList[0])
					print('lat: '+dataList[1])
					print('c: '+dataList[2])
					lastpoint = makePoint([dataList[0],dataList[1]], 'skrunch', str(timestamp), 'lastping', '1')
					bounds = ""+str(dataList[0])+","+str(dataList[1])+","+str(dataList[0])+","+str(dataList[1])+""
					view = ""+dataList[0]+","+dataList[1]+""
					lastcharge = dataList[2]
				else:
					point_var += makePoint([dataList[0],dataList[1]], 'paw', str(timestamp), 'paws', str(opac) )
					leaflet_data.append(json.loads('{"time":"'+timestamp+'", "lat":'+dataList[1]+', "lon":'+dataList[0]+',"charge":'+dataList[2]+'}'))
					opac -= 0.01;
					points.append([dataList[0],dataList[1]])
			except Exception as e:
				print(e)
		numPoints = len(points)
		print("numPoints: "+str(numPoints))
		try:
			with open(HTMLDIR+'demo.html', 'r') as file:
				dh_map = file.read()
				dh_map = dh_map.replace('BOUNDS_VAR',bounds)
				dh_map = dh_map.replace('SETVEIW_VAR',view)
				dh_map = dh_map.replace('CHARGE_VAR',lastcharge)
				dh_map = dh_map.replace('POINTS_VAR',point_var)
				dh_map = dh_map.replace('LASTPOINT_VAR',lastpoint)
				dh_map = dh_map.replace('FUNDS_VAR',funds)


				#print(dh_map)
		except IOError as e:
			print("Password not set or access denied!")

		return dh_map


conf = {
	'global': {
		'server.socket_host': "127.0.0.1",
		'server.socket_port': 5050,
		'server.thread_pool': 10,
		'tools.staticdir.root':'/home/smk762/DragonhoundDemo/'
	},
   '/DragonhoundDemo': {
		'tools.auth_digest.on': True,
		'tools.auth_digest.realm': 'localhost',
		'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(USERS),
		'tools.auth_digest.key': 'a565c27146791cfb',
		'tools.auth_digest.accept_charset': 'UTF-8',
		'tools.staticdir.on': True,
		'tools.staticdir.dir': 'html',
   }
}

if __name__ == '__main__':
	cherrypy.quickstart(MapPage(), '/', conf)