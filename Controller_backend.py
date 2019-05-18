
from flask import Flask, request, send_file
from onvif import ONVIFCamera
from time import sleep
from wsdiscovery import WSDiscovery, QName, Scope
import urllib2
import requests
import json

app = Flask(__name__)

flag = False
CamList = []
IPList = []


@app.route('/GetSnapshot', methods=['POST'])
def GetSnapshot():
	global IPList
	i = int(request.args.get("number"))
	media = IPList[i].Media
	token = IPList[i].Token
	GetUri = media.GetSnapshotUri({'ProfileToken':token}).Uri
	filename = "img.jpg"
	resource = urllib2.urlopen(GetUri)
	out = open("./img.jpg", 'wb')
	out.write(resource.read())
	out.close()
	return send_file(filename, mimetype='image/jpg')

@app.route('/Discovery', methods=['POST'])
def Discovery():
	global IPList 
	global CamList
	class IPL(object):
		def __init__(self, IP, Port):
			self.IP = IP
			self.Port = Port
			self.Mycam = ONVIFCamera(self.IP, self.Port, 'admin', 'Supervisor', '/usr/local/wsdl')
			try:
				self.Media = self.Mycam.create_media_service()
				self.Token = self.Media.GetProfiles()[0]._token
			except:
				print ("Device doesn't support MEDIA profile")
				self.Media = 'error'
				self.Token = 'error'
			try:
				self.Ptz = self.Mycam.create_ptz_service()
			except:
				self.Ptz = 'error'
				print ("Device doesn't support PTZ profile")

		def test(self):
			print (self.IP + ' ' + self.Port + ' ' + self.Token + ' ')
	del CamList[:]
	del IPList[:]
	PortList = []
	wsd = WSDiscovery()
	wsd.start()

	ret = wsd.searchServices()

	stroka = ''

	for service in ret:
		addrs = service.getXAddrs()[0]
		x = addrs.find('/')
		ip = addrs[x+1:]
		x = addrs.find('/')
		y = addrs.rfind(':')
		if y <= x :
			y = addrs[x+2:].find('/')
			ip = addrs[x+2:x+2+y]
			port = '80'
		else:
			ip = addrs[x+2:y]
			x = addrs[y:].find('/')
			port = addrs[y+1:y+x]
			print (ip + '      ' + port)
            try:
                SMT = IPL(ip, port)
                if SMT.Ptz == 'error':
                    print ('error')
                else:
                    IPList.append(SMT)
#            				print(service.getEPR() + ":" + service.getXAddrs()[0])
                    print('ip=' + ip + '     port=' + port)
            except:
                print ('something happend')
	IPList.sort(key=lambda x: x.IP)
	for i, IPL in enumerate(IPList):
		stroka = stroka + IPL.IP + ',' + IPL.Port + ',' + str(i) + ','
	wsd.stop()
	
	f = open ('discovery.txt', 'w')
	f.write(stroka)
	f.close()
	
	return(stroka)

@app.route('/TestDiscovery', methods=['POST'])
def TestDiscovery():
	global IPList
	for IPL in IPList:
		IPL.test()
	return('Everything fine')

@app.route('/GotoPreset', methods=['POST'])
def GotoPreset():
	global IPList 
	i = int(request.args.get("number"))
	Preset = IPList[i].Ptz.create_type('GotoPreset')
	Preset.ProfileToken = IPList[i].Token
	IPList[i].Ptz.GotoPreset({'ProfileToken':Preset.ProfileToken,'PresetToken':request.args.get("PresetNumber"),'Speed':1})
	print(request.args.get("PresetNumber"))
	return("GotoPreset" + request.args.get("PresetNumber"))

@app.route('/SetPreset', methods=['POST'])
def SetPreset():
	global IPList
	i = int(request.args.get("number"))
	ptz = IPList[i].Ptz
	token = IPList[i].Token
	Preset = ptz.create_type('SetPreset')
	Preset.ProfileToken = token
	Preset.PresetName = "name"
	Preset.PresetToken = request.args.get("PresetNumber")
	ptz.SetPreset(Preset)
	return("SetPreset " + Preset.PresetToken)

@app.route('/ZoomIn', methods=['POST'])
def ZoomIn():
	global IPList
	i = int(request.args.get("number"))
	ptz = IPList[i].Ptz
	token = IPList[i].Token
	Cmove = ptz.create_type('ContinuousMove')
	Cmove.ProfileToken = token
	Cmove.Velocity.Zoom._x = 0.2
	ptz.ContinuousMove(Cmove)
	return("ZoomIn")
@app.route('/ZoomOut', methods=['POST'])
def ZoomOut():
	global IPList
	i = int(request.args.get("number"))
	ptz = IPList[i].Ptz
	token = IPList[i].Token
	Cmove = ptz.create_type('ContinuousMove')
	Cmove.ProfileToken = token
	Cmove.Velocity.Zoom._x = -0.2
	ptz.ContinuousMove(Cmove)
	return("ZoomOut")
@app.route('/ContinuousMove', methods=['POST'])
def CMove():
	global IPList
	i1 = request.args.get("number")
	i = int(i1)
	ptz = IPList[i].Ptz
	Cmove = ptz.create_type('ContinuousMove')
	#Cmove = IPList[i].Ptz.create_type('ContinuousMove')
#	Cmove.ProfileToken = IPList[i].Token
	Cmove.Velocity.PanTilt._x = request.args.get("x")
	Cmove.Velocity.PanTilt._y = request.args.get("y")
	ptz.ContinuousMove(Cmove)
	print (IPList[i].IP)
	#IPList[i].Ptz.ContinuousMove(Cmove)
	print("moving")
	return("moving")

@app.route('/MoveStop', methods=['POST'])
def MoveStop():
	global IPList
	i = int(request.args.get("number"))
	IPList[i].Ptz.Stop({'ProfileToken': IPList[i].Token})
	return("stopped")

@app.route('/GotoHome', methods=['POST'])
def GotoHome():
	global IPList
	i = int(request.args.get("number"))
	ptz = IPList[i].Ptz
	Preset = ptz.create_type('GotoHomePosition')
	Preset.ProfileToken = IPList[i].Token
	ptz.GotoHomePosition({'ProfileToken':Preset.ProfileToken})
	return ('done')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8081)
