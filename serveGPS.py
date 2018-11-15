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

USERS = {'smk762': 'Nighteyes'}
HOME = os.environ['HOME']
CONFIGDIR = str(HOME+'/.Dragonhound/')
HTMLDIR = str(HOME+'/Dragonhound/html/')

lon_min = 115.933;
lon_max = 115.936;
lat_min = -32.032;
lat_max = -32.029;
 
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
			amount = 5
			print("adding oracle funds")
			result = getconf.oraclessubscribe_rpc(CHAIN, ORCLID, publisher, amount)
			print(result)
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
				try:
					timestamp = datetime.utcfromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')+" UTC"				 	
				except Exception as e:
					timestamp = data['published_at']
					pass

				if lastpoint == "":
					print("adding first point")
					print('time: '+str(timestamp))
					print('lon: '+dataList[0])
					print('lat: '+dataList[1])
					print('c: '+dataList[2])
					lastpoint = makePoint([dataList[0],dataList[1]], 'skrunch', str(timestamp), 'lastping', '1')
					bounds = ""+str(dataList[0])+","+str(dataList[1])+","+str(dataList[0])+","+str(dataList[1])+""
					view = ""+dataList[0]+","+dataList[1]+""
					lastcharge = dataList[2]
				elif (float(dataList[1]) > lon_max or float(dataList[1]) < lon_min or float(dataList[0]) > lat_max or float(dataList[0]) < lat_min):
					point_var += makePoint([dataList[0],dataList[1]], 'paw', str(timestamp), 'paws', str(opac) )
					leaflet_data.append(json.loads('{"time":"'+timestamp+'", "lat":'+dataList[1]+', "lon":'+dataList[0]+',"charge":'+dataList[2]+'}'))
					opac -= 0.01;
					points.append([dataList[0],dataList[1]])
			except Exception as e:
				print(e)
		#print("point_var: "+str(point_var))
		try:
			if 1 != 1:
				underlay1 = makeLines('UNDERLAY_VAR1','UNDERLAY_1', points[0:11], '#ffffff', '4.2', '0.7', '30', 'underlay')
				underlay2 = makeLines('UNDERLAY_VAR2','UNDERLAY_2', points[10:22], '#ffffff', '4', '0.7', '30', 'underlay')
				underlay3 = makeLines('UNDERLAY_VAR3','UNDERLAY_3', points[21:33], '#ffffff', '3.8', '0.7', '30', 'underlay')
				underlay4 = makeLines('UNDERLAY_VAR4','UNDERLAY_4', points[32:44], '#ffffff', '3.6', '0.7', '30', 'underlay')
				underlay5 = makeLines('UNDERLAY_VAR5','UNDERLAY_5', points[43:55], '#ffffff', '3.4', '0.7', '30', 'underlay')
				underlay6 = makeLines('UNDERLAY_VAR6','UNDERLAY_6', points[54:66], '#ffffff', '2.6', '0.7', '30', 'underlay')
				underlay7 = makeLines('UNDERLAY_VAR7','UNDERLAY_7', points[65:77], '#ffffff', '2', '0.7', '30', 'underlay')
				underlay8 = makeLines('UNDERLAY_VAR8','UNDERLAY_8', points[76:88], '#ffffff', '2', '0.7', '30', 'underlay')
				underlay9 = makeLines('UNDERLAY_VAR9','UNDERLAY_9', points[87:99], '#ffffff', '2', '0.7', '30', 'underlay')
				track1 = makeLines('TRACK_VAR1','TRACK_1', points[0:11], '#667DFF', '2.2', '0.7', '30', 'dogtracks')
				track2 = makeLines('TRACK_VAR2','TRACK_2', points[10:22], '#057DFF', '2', '0.7', '30', 'dogtracks')
				track3 = makeLines('TRACK_VAR3','TRACK_3', points[21:33], '#057DFF', '1.8', '0.7', '30', 'dogtracks')
				track4 = makeLines('TRACK_VAR4','TRACK_4', points[32:44], '#057DFF', '1.6', '0.7', '30', 'dogtracks')
				track5 = makeLines('TRACK_VAR5','TRACK_5', points[43:55], '#057DFF', '1.4', '0.7', '30', 'dogtracks')
				track6 = makeLines('TRACK_VAR6','TRACK_6', points[54:66], '#057DFF', '1.2', '0.7', '30', 'dogtracks')
				track7 = makeLines('TRACK_VAR7','TRACK_7', points[65:77], '#057DFF', '1', '0.7', '30', 'dogtracks')
				track8 = makeLines('TRACK_VAR8','TRACK_8', points[76:88], '#057DFF', '1', '0.7', '30', 'dogtracks')
				track9 = makeLines('TRACK_VAR9','TRACK_9', points[87:99], '#057DFF', '1', '0.7', '30', 'dogtracks')
		except Exception as e:
			raise e

		try:
			with open(HTMLDIR+'scrunch.html', 'r') as file:
				print("Populating template")
				numPoints = len(points)
				print("numPoints: "+str(numPoints))
				dh_map = file.read()
				if 1 != 1:
					dh_map = dh_map.replace('UNDERLAY_VAR1',underlay1)
					dh_map = dh_map.replace('UNDERLAY_VAR2',underlay2)
					dh_map = dh_map.replace('UNDERLAY_VAR3',underlay3)
					dh_map = dh_map.replace('UNDERLAY_VAR4',underlay4)
					dh_map = dh_map.replace('UNDERLAY_VAR5',underlay5)
					dh_map = dh_map.replace('UNDERLAY_VAR6',underlay6)
					dh_map = dh_map.replace('UNDERLAY_VAR7',underlay7)
					dh_map = dh_map.replace('UNDERLAY_VAR8',underlay8)
					dh_map = dh_map.replace('UNDERLAY_VAR9',underlay9)
					dh_map = dh_map.replace('TRACK_VAR1',track1)
					dh_map = dh_map.replace('TRACK_VAR2',track2)
					dh_map = dh_map.replace('TRACK_VAR3',track3)
					dh_map = dh_map.replace('TRACK_VAR4',track4)
					dh_map = dh_map.replace('TRACK_VAR5',track5)
					dh_map = dh_map.replace('TRACK_VAR6',track6)
					dh_map = dh_map.replace('TRACK_VAR7',track7)
					dh_map = dh_map.replace('TRACK_VAR8',track8)
					dh_map = dh_map.replace('TRACK_VAR9',track9)
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
		'server.socket_port': 5000,
		'server.thread_pool': 10,
		'tools.staticdir.root':'/home/smk762/Dragonhound/'
	},
   '/DragonHound': {
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