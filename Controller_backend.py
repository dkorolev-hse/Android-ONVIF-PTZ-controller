from flask import Flask, request
from onvif import ONVIFCamera
from time import sleep
from wsdiscovery import WSDiscovery, QName, Scope

import json

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():
        #preset_number = request.args['preset_number']
        #data = {"x": x, "y": y, "preset_number": preset_number}
        #return json.dumps(data)
        if request.method == "GET":
                return("GET")
        else:
                print(request.args.get("num"))
                return("FUCK" + str(request.args.get("num")))

flag = False
mycam = ONVIFCamera('192.168.15.43', 80, 'admin', 'Supervisor', '/usr/local/wsdl')
media = mycam.create_media_service()
ptz = mycam.create_ptz_service()
media_profile = media.GetProfiles()[0];
token = media_profile._token
CamList = []
IPList = []

@app.route('/GetSnapshot', methods=['POST'])
def GetSnapshot():
	global media
	global token
	GetUri = media.GetSnapshotUri({'ProfileToken':token})
	return(GetUri.Uri)


@app.route('/Discovery', methods=['POST'])
def Discovery():
	global CamList
	global IPList
	del CamList[:]
	del IPList[:]
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
            print(service.getEPR() + ":" + service.getXAddrs()[0])
            print('ip=' + ip + '     port=' + port)
            stroka = stroka + ip + "," + port + ','
        wsd.stop()
	return(stroka)

@app.route('/GotoPreset', methods=['POST'])
def GotoPreset():
        Preset = ptz.create_type('GotoPreset')
        Preset.ProfileToken = token
        ptz.GotoPreset({'ProfileToken':token,'PresetToken':request.args.get("PresetNumber"),'Speed':1})
        print(Preset.ProfileToken)
	return(request.args.get("PresetNumber"))

@app.route('/SetPreset', methods=['POST'])
def SetPreset():
        Preset = ptz.create_type('SetPreset')
        Preset.ProfileToken = token
        Preset.PresetName = request.args.get("PresetName")
        Preset.PresetToken = request.args.get("PresetNumber")
        ptz.SetPreset(Preset)
	print(Preset.PresetName)
	return(Preset.PresetToken)

@app.route('/ZoomIn', methods=['POST'])
def ZoomIn():
	Cmove = ptz.create_type('ContinuousMove')
	Cmove.ProfileToken = token
	Cmove.Velocity.Zoom._x = 0.2
	ptz.ContinuousMove(Cmove)
	
@app.route('/ZoomOut', methods=['POST'])
def ZoomOut():
	Cmove = ptz.create_type('ContinuousMove')
	Cmove.ProfileToken = token
	Cmove.Velocity.Zoom._x = -0.2
	ptz.ContinuousMove(Cmove)

@app.route('/ContinuousMove', methods=['POST'])
def CMove():
	global flag
	if flag == True:
		print("FUCK")
        	Cmove = ptz.create_type('ContinuousMove')
        	Cmove.ProfileToken = token
        	Cmove.Velocity.PanTilt._x = request.args.get("x")
		Cmove.Velocity.PanTilt._y = request.args.get("y")
        	ptz.ContinuousMove(Cmove)
		print(Cmove.Velocity)
		return("1")
@app.route('/SetFlag', methods=['POST'])
def SetFlag():
	global flag
	flag = True
	if flag == True:
		print("FUCK")
	else:
		print("SUCK")
	return("1")

@app.route('/UnsetFlag', methods=['POST'])
def UnsetFlag():
	global flag
	flag = False
	ptz.Stop({'ProfileToken':token})
	print(flag)
	return("2")

@app.route('/MoveStop', methods=['POST'])
def MoveStop():
	print("STOP")
        ptz.Stop({'ProfileToken': token})

@app.route('/SelectCamera', methods=['POST'])
def SelectCamera():
	global mycam
	mycam  = ONVIFCamera(request.args.get("IP"), request.args.get("Port"),'admin','Supervisor', '/usr/local/wsdl')
	global media
	media = mycam.create_media_service()
	global ptz
	ptz  = mycam.create_ptz_service()
	global media_profile
	media_profile = media.GetProfiles()[0];
	global token
	token = media_profile._token
        print("IP :" + request.args.get("IP"))
        print("Port :" + str(request.args.get("Port")))
	return(request.args.get("Port"))

if __name__ == '__main__':
        app.run(host='188.246.233.224', port=8080)
