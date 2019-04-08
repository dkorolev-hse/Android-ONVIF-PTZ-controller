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
            
mycam = ONVIFCamera('192.168.11.12', 80, 'admin', 'Supervisor', '/usr/local/wsdl')
media = mycam.create_media_service()
ptz = mycam.create_ptz_service()
media_profile = media.GetProfiles()[0];
token = media_profile._token
CamList = []
IPList = []


# В этой функции ищем камеры через WS-discovery,  записываем их в список камер CamList. 
@app.route('/Discovery', methods=['GET'])
def Discovery
        wsd = WSDiscovery()
        wsd.start()

        ret = wsd.searchServices()

        for service in ret:
            global CamList
            global IPList
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
            CamList.append(ONVIFCamera(ip,port,'admin','Supervisor','/usr/local/wsdl'))
            IPList.append(ip)
            print(service.getEPR() + ":" + service.getXAddrs()[0])
            print('ip=' + ip + '     port=' + port)
            
        wsd.stop()

#Вызываем пресет через его номер (aka Preset Token)
@app.route('/GotoPreset', methods=['POST'])
def GotoPreset():
        Preset = ptz.create_type('GotoPreset')
        Preset.ProfileToken = token
        ptz.GotoPreset({'ProfileToken':Preset.ProfileToken,'PresetToken':request.args.get("PresetNumber")})
        print(Preset.PresetToken)

#Начало зума
@app.route('/ZoomIn', methods=['POST'])
def ZoomIn():
        Cmove = ptz.create_type('ContinuousMove')
        Cmove.ProfileToken = token
        Cmove.Velocity.Zoom._x = 0.2
        ptz.ContinuousMove(Cmove)
        
#Начало зума
@app.route('/ZoomOut', methods=['POST'])
def ZoomOut():
        Cmove = ptz.create_type('ContinuousMove')
        Cmove.ProfileToken = token
        Cmove.Velocity.Zoom._x = -0.2
        ptz.ContinuousMove(Cmove)

        
#Устанавливаем пресет в текущей позиции
@app.route('/SetPreset', methods=['POST'])
def SetPreset():
        Preset = ptz.create_type('SetPreset')
        Preset.ProfileToken = token
        Preset.PresetName = request.args.get("PresetName")
        Preset.PresetToken = request.args.get("PresetNumber")
        print(Preset.PresetName)

#Начало ContinuousMove, передаём скорость движения        
@app.route('/ContinuousMove', methods=['POST'])
def CMove():
        Cmove = ptz.create_type('ContinuousMove')
        Cmove.ProfileToken = token
        Cmove.Velocity.PanTilt._x = request.args.get("x")
        Cmove.Velocity.PanTilt._y = request.args.get("y")
        print(Cmove.Velocity)

#Остановка ContinuousMove
@app.route('/MoveStop', methods=['POST'])
def MoveStop():
        ptz.Stop({'ProfileToken': token})

#В этой функции выбираем рабочую камеру, передавая ей IP и port камеры
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

#запускаем http сервер на порте 80
if __name__ == '__main__':
        app.run(host='localhost', port=80)
