
from flask import Flask, request, send_file
from onvif import ONVIFCamera
from time import sleep
from wsdiscovery import WSDiscovery, QName, Scope
import urllib2
import time
import requests
import json
import threading

app = Flask(__name__)

def SetIPL(IP, Port, Login = 'admin', Password = 'Supervisor'):
 class IPL(object):
  def __init__(self, IP, Port, Login = 'admin', Password = 'Supervisor'):
   self.IP = IP
   self.Port = Port
   self.Login = Login
   self.Password = Password
   self.Mycam = ONVIFCamera(self.IP, self.Port, self.Login, self.Password, '/usr/local/wsdl')
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
 SMT = IPL (IP, Port, Login, Password)
 return(SMT)


@app.route('/Discovery_original', methods=['POST'])
def Discovery_original():
 global IPList
 global IPL
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
  if ip[9] == '1':
   print (ip + '      ' + port)
       #   try:
   SMT = SetIPL(ip, port)
   if SMT.Ptz == 'error':
    print ('error')
   else:
    IPList.append(SMT)
    print('ip=' + ip + '     port=' + port)
#except:
#   print ('something happend')
   IPList.sort(key=lambda x: x.IP)
 for i, IPL in enumerate(IPList):
  stroka = stroka + IPL.IP + ',' + IPL.Port + ',' + str(i) + ','
 wsd.stop()
    
 f = open ('discovery.txt', 'w')
 f.write(stroka)
 f.close()
 return('ODiscovery_ready')


ManList = []
IPList = []
f = open('Man_add.txt', 'w')
f.close()

@app.route('/Discovery1', methods=['POST'])
def Discovery1():
 f = open ('discovery.txt', 'r')
 stroka = f.read()
 f.close()
 f = open ('Man_add.txt', 'r')
 stroka1 = f.read()
 f.close()
 i = stroka + stroka1
 print(i)
 return (stroka + stroka1)

@app.route('/Discovery', methods=['POST'])
def Discovery():
 global IPList
 global ManList
 stroka = ''
 for i, IPL in enumerate(IPList):
  stroka = stroka + IPL.IP + ',' + IPL.Port + ',' + str(i) + ','
 for i, IPL in enumerate(ManList):
  stroka = stroka + IPL.IP + ',' + IPL.Port + ',' + str(i + len(IPList)) + ','
 return(stroka)

def Camera_select(number):
 global IPList
 global ManList
 if number+1 > len(IPList):
  i = number - len(IPList)-1
  print(i)
  SMT = ManList[i]
 else:
  i = number
  print (i)
  SMT = IPList[i]
 return(SMT)


@app.route('/GetSnapshot', methods=['POST'])
def GetSnapshot():
 i = int(request.args.get("number"))
 SMT = Camera_select(i)
 media = SMT.Media
 token = SMT.Token
 GetUri = media.GetSnapshotUri({'ProfileToken':token}).Uri
 filename = "img.jpg"
 resource = urllib2.urlopen(GetUri)
 out = open("./img.jpg", 'wb')
 out.write(resource.read())
 out.close()
 return send_file(filename, mimetype='image/jpg')

@app.route('/AddCamera', methods=['POST'])
def AddCamera():
 global IPList
 global ManList
 global IPL
 ip = request.args.get("ip")
 port = request.args.get("port")
 login = request.args.get("login")
 Password = request.args.get("password")
 SMT = SetIPL(ip, port, login, Password)
 ManList.append(SMT)
 f = open('Man_add.txt', 'a')
 stroka = str(ip) + ',' + str(port) + ','
 f.write(stroka)
 f.close()
 return("added")

@app.route('/TestDiscovery', methods=['POST'])
def TestDiscovery():
 global IPList
 for IPL in IPList:
  IPL.test()
 return('Everything fine')

@app.route('/GotoPreset', methods=['POST'])
def GotoPreset():
 i = int(request.args.get("number"))
 SMT = Camera_select(i)
 Preset = SMT.Ptz.create_type('GotoPreset')
 Preset.ProfileToken = SMT.Token
 SMT.Ptz.GotoPreset({'ProfileToken':Preset.ProfileToken,'PresetToken':request.args.get("PresetNumber"),'Speed':1})
 print(request.args.get("PresetNumber"))
 return("GotoPreset" + request.args.get("PresetNumber"))

@app.route('/SetPreset', methods=['POST'])
def SetPreset():
 i = int(request.args.get("number"))
 SMT = Camera_select(i)
 ptz = SMT.Ptz
 token = SMT.Token
 Preset = ptz.create_type('SetPreset')
 Preset.ProfileToken = token
 Preset.PresetName = "name"
 Preset.PresetToken = request.args.get("PresetNumber")
 ptz.SetPreset(Preset)
 return("SetPreset " + Preset.PresetToken)

@app.route('/ZoomIn', methods=['POST'])
def ZoomIn():
 i = int(request.args.get("number"))
 SMT = Camera_select(i)
 ptz = SMT.Ptz
 token = SMT.Token
 Cmove = ptz.create_type('ContinuousMove')
 Cmove.ProfileToken = token
 Cmove.Velocity.Zoom._x = 0.2
 ptz.ContinuousMove(Cmove)
 return("ZoomIn")

@app.route('/ZoomOut', methods=['POST'])
def ZoomOut():
 global IPList
 i = int(request.args.get("number"))
 SMT = Camera_select(i)
 ptz = SMT.Ptz
 token = SMT.Token
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
 SMT = Camera_select(i)
 ptz = SMT.Ptz
 token = SMT.Token
 Cmove = ptz.create_type('ContinuousMove')
 #Cmove = IPList[i].Ptz.create_type('ContinuousMove')
 Cmove.ProfileToken = token
 Cmove.Velocity.PanTilt._x = request.args.get("x")
 Cmove.Velocity.PanTilt._y = request.args.get("y")
 ptz.ContinuousMove(Cmove)
 print (SMT.IP + "moving")
 return("moving")

@app.route('/MoveStop', methods=['POST'])
def MoveStop():
 i = int(request.args.get("number"))
 SMT = Camera_select(i)
 ptz = SMT.Ptz
 token = SMT.Token
 ptz.Stop({'ProfileToken': token})
 return("stopped")

@app.route('/GotoHome', methods=['POST'])
def GotoHome():
 i = int(request.args.get("number"))
 SMT = Camera_select(i)
 ptz = SMT.Ptz
 token = SMT.Token
 Preset = ptz.create_type('GotoHomePosition')
 Preset.ProfileToken = token
 ptz.GotoHomePosition({'ProfileToken':Preset.ProfileToken})
 return ('done')

def OD():
 threading.Timer(120.0, OD).start()
 Discovery_original()
 time.sleep(0.01)

def StartServer():
 if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8081)

thread = threading.Thread(target=StartServer, args=())
thread2 = threading.Thread(target=Discovery_original, args=())

thread.start()
thread2.start()
thread2.join()
OD()
thread.join()
