import serial, glob, time

class Device:
  def __init__(self, port, debug=print, errorHandler=print):
    self.port = port
    self.id = -1
    self.motors = -1
    self.leds = -1
    self.position = -1
    self.busy = False
    self.boot = 'unknown'
    self.debug = debug
    self.type = 'unknown'
    self.errorHandler = errorHandler
    port.write(bytes("i", 'ascii'))
    port.write(bytes("m", 'ascii'))
    port.write(bytes("t", 'ascii'))
    self.keyCb = self.logKey
    self.key = ""
    
  def logKey(self, key, type):
    self.debug("["+str(self.id)+"] Found "+self.type+" key with id "+self.key)

  def setKeyCb(self, cb):
    self.debug("["+str(self.id)+"] onKey callback configured")
    self.keyCb = cb

  def _setId(self, id):
    self.id = int(id)
    self.position = self.id - 1

  def _setMotors(self, motors):
    self.motors = int(motors)
    
  def _setType(self, type):
    self.type = type
    
  def getType(self):
    return self.type
    
  def _setState(self, state):
    self.state = state
    
  def _setBusy(self, busy):
    self.busy = busy

  def _setField(self, data):
    if (data[0]=='id'):
      self._setId(data[1])
    elif (data[0]=='type'):
      self._setType(data[1])
    elif (data[0]=='motors'):
      self._setMotors(data[1])
    elif (data[0]=='state'):
      self._setState(data[1])
      self.debug("["+str(self.id)+"] State is '"+self.state+"'")
      if (data[1]=='busy'):
        self._setBusy(True)
      else:
        self._setBusy(False)
    elif (data[0]=='ibutton'):
      self.key = data[1]
      self.keyCb(self.key, self.type)
    elif (data[0]=='boot'):
      self.boot = ",".join(data[1:])
    elif (data[0]=='error'):
      error = self.type.upper()+'.'+str(self.id)+'.HWERROR.'+".".join(data[1:]).upper().replace(',','.')
      self.errorHandler(error)
    else:
      self.debug("["+str(self.id)+"] Unknown field '"+data[0]+"': "+data[1])      

  def _serialInput(self, data):
    if (data[0]=="#"):
      data = data.replace("#", "", 1)
      self.debug("["+str(self.id)+"] "+data)
    else:
      data = data.split("=")
      if (len(data)<2):
        self.debug("["+str(self.id)+"] Garbage data? "+data[0])
      else:
        self._setField(data)

  def update(self):
    #try:
      while self.port.in_waiting:
        line = self.port.readline().decode("ascii")
        if (line != "" and line!="\n" and line!="\r" and line!="\r\n"):
          line = line.replace("\r","").replace("\n","")
          self._serialInput(line)
    #except Exception as e:
    #  print("RX EXCEPTION", e)

  def getNumLeds(self):
    return self.leds

  def getNumMotors(self):
    return self.motors

  def getId(self):
    return self.id

  def getPosition(self):
    return self.position

  def setPosition(self,p):
    self.position = p

  def flush(self):
    self.update()
    try:
      self.port.read(9999)
    except:
      pass

  def rgb2rgbw(self,r,g,b):
    w = 0
    while (r>0) and (g>0) and (b>0):
      if (r>0):
        r -= 1
      if (g>0):
        g -= 1
      if (b>0):
        b -= 1
      w += 1
    return (r,g,b,w)
  def dispense(self,location):
    self.port.write(bytes('d'+str(location)+'\n','ascii'))

  def setLed(self,i,r,g,b,w=-1):
    if (w<0):
      r,g,b,w = self.rgb2rgbw(r,g,b)
    #self.debug("setLed",self.id,i)
    self.port.write(bytes("s"+str(i)+"c"+str(w)+","+str(r)+","+str(g)+","+str(b),'ascii'))
    
  def setOnewireLed(self, s):
    self.port.write(bytes("l"+str(s)+"\n",'ascii'))

  def setAllLeds(self,r,g,b,w=-1):
    for i in range(0,9):
      self.setLed(i,r,g,b,w)

  def updateLeds(self):
    self.port.write(bytes('u','ascii'))
    

class DeviceManager:
  ready = False
  
  def __init__(self, debug=print, errorHandler=print, sleep=time.sleep):
    self.ports = []
    self.debug = debug
    self.errorHandler = errorHandler
    self.sleep = sleep
    self.debug("Hardware initialiseren...")
    for name in glob.glob('/dev/ttyUSB*'):
      try:
        self.ports.append(serial.Serial(name, 115200, timeout=0.2))
        self.debug("Connected to port '"+name+"'.")
      except:
        self.debug("Could not access port '"+name+"'!")
    self.sleep(2)
    
    self.devices = []
    
    self.debug("Searching for devices...")
    for port in self.ports:
      d = Device(port, self.debug, self.errorHandler)
      timeout = 20
      while(timeout>0):
        d.update()
        self.sleep(0.01)
        timeout-=1
      if (d.getId()<1):
        self.debug("Port '"+port.name+"' is not a device.")
      else:
        self.debug("Port '"+port.name+"' is device #"+str(d.getId())+" of type "+d.getType()+" ("+str(d.getNumMotors())+" motors)")
        self.devices.append(d)
    #self.debug("Found "+str(len(self.devices))+" devices.")
    temp = self.devices
    hid = 0
    for device in temp:
      id = device.getId()
      if (id>hid):
        hid = id
    self.devices = [None]*(hid)
    for device in temp:
      id = device.getId()
      if self.devices[id-1] is None:
        self.devices[id-1] = device
      else:
        self.debug("Duplicate device ID detected: #"+str(id))
        self.debug(" - "+self.devices[id].port.name)
        self.debug(" - "+device.port.name)
    #temp = self.devices
    #self.devices = []
    #for device in temp:
    #  if not device is None:
    #    self.devices.append(device)
    self.debug("Device init complete: found "+str(len(self.devices))+" devices.")
    self.ready = True

  def sort(self):
    devices = self.devices
    max = 0
    for d in devices:
      p = d.getPosition()
      if (p>max):
        max = p
    self.devices = []
    for i in range(0,max+1):
      for d in devices:
        if d.getPosition()==i:
          self.devices.append(d)

  def amount(self):
    return len(self.devices)

  def amountOfDrawers(self):
    drawers = 0
    for device in self.devices:
      if not device is None:
        if device.type == "drawer":
          drawers += 1
    return drawers
  
  def getDevice(self,id):
    for device in self.devices:
      if not device is None:
        if device.getId()==id:
          return device
    return None

  def getDevices(self,type=""):
    if (type==""):
      return self.devices
    result = []
    for device in self.devices:
      if not device is None:
        if device.type == type:
          result.append(device)
    return result

  def getDrawers(self):
    return self.getDevices("drawer")
  
  def getOnewire(self):
    return self.getDevices("ibutton")
  
  def setOnewireLed(self, state):
    self.debug("Onewire led: "+str(state))
    for d in self.getOnewire():
      if state > 0:
        state = 1
      d.setOnewireLed(state)
      
  def update(self):
    if self.ready:
      for device in self.devices:
        if not device is None:
          device.update()
  
  def isDrawerBusy(self):
    return self.isBusy('drawer')
  
  def isOnewireBusy(self):
    return self.isBusy('ibutton')

  def isBusy(self,type=''):
    if not self.ready:
      return True
    for device in self.devices:
      if not device is None:
        if type=='' or type==device.type:
          if (device.busy):
            return True
    return False
