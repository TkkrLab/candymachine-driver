#!/usr/bin/python3
import hardware, time, artnet, pygame, sys, ui

class App:
  def __init__(self):
    self._deviceManager = None
    self._running = False
    self._drawers = []
    self._onewire = []
    self.debug = False
    self.demo = False
    self.ui = None
    
    self.waitForKey = True
    self.currentKey = ''
    self.oneWireLed = False
    
    self.halted = False
    self.disableUIinput = False
    
  def handle_exception(self, exctype, value, traceback):
    if exctype==KeyboardInterrupt:
      sys.exit(0)
    print("EXCEPTION:",exctype,value,traceback)
    self.ui.draw("=== EXCEPTION ===",True)
    self.ui.draw(str(value))
    self.halt("PYTHON.EXCEPTION")

  def halt(self,text=""):
    print("HALT: "+text)
    border = False
    self.halted = True
    self.ui.show_fatal_error(text, True)
    while True:
        self.sleep(1000)

  def on_logout(self):
    self.ui.draw("Logout")
    self.currentKey = ""
    self.waitForKey = True

  def on_init(self, dev=False, demo=False):
    self.dev = dev
    self.demo = demo
    pygame.init()
    self.ui = ui.UiManager(self)
    self.ui.register_kb_handler(self.on_keyboard_command)
    self.ui.register_logout_handler(self.on_logout)
    
    #sys.excepthook = self.handle_exception
        
    self._running = True
    #self.ui.addTimerFunction(self.ui.render_loading, True)
    self.ui.setDrawFunc(self.ui.render_loading)
    #self.ui.render_dialog("STARTING SYSTEM", "Initializing hardware...")
    #self.ui.draw()
    self._deviceManager = hardware.DeviceManager(self.ui.draw, self.halt, self.sleep)
    self._drawers = self._deviceManager.getDrawers()
    self._onewire = self._deviceManager.getOnewire()
    
    for onewire in self._onewire:
      onewire.setKeyCb(self.on_key)

    if not dev and not demo:
      if (len(self._drawers)!=6):
        self.halt("INIT.DRAWER.AMOUNT.INVALID."+str(len(self._drawers)))
        
    #And fix the sorting (la 0 zit op positie 4) (NO LONGER NEEDED)
    #self._drawers[0].setPosition(4)
    #self._drawers[4].setPosition(0)
    #self._deviceManager.sort()
    #self._drawers = self._deviceManager.getDrawers()
    
    #self.ui.render_dialog("STARTING SYSTEM", "Initializing Artnet...")
    #self.ui.draw()
    artnet.init()
    
    #self.ui.render_dialog("STARTING SYSTEM", "Welcome!")
    #self.ui.draw()
    
    self.ui.setDrawFunc()
    
    #self.ui.delTimerFunction(self.ui.render_loading)

  def on_event(self, event):
    busy = self.isBusy()
    if event.type == pygame.QUIT:
      self._running = False
    if event.type == pygame.KEYDOWN:
      self.ui.on_key_down(event, busy)
    elif event.type == pygame.KEYUP:
      self.ui.on_key_up(event, busy)
    elif event.type == pygame.MOUSEBUTTONDOWN:
      self.ui.on_mouse_down(event, busy)
    elif event.type == pygame.MOUSEBUTTONUP:
      self.ui.on_mouse_up(event, busy)
    elif event.type == pygame.MOUSEMOTION:
      self.ui.on_mouse_move(event, busy)
    elif event.type == pygame.USEREVENT:
      self.ui.on_timer(event, busy)

  def on_loop(self):
    for event in pygame.event.get():
      self.on_event(event)
    self.handleArtnet()
    if not self._deviceManager is None:
      self._deviceManager.update()
    pass

  def isBusy(self):
    deviceManagerBusy = True
    if not self._deviceManager is None:
      deviceManagerBusy = self._deviceManager.isBusy()
    return deviceManagerBusy or self.halted or self.disableUIinput #or self.waitForKey

  def on_render(self):
    if (self._deviceManager.isDrawerBusy()):
      self.ui.setDrawFunc(self.ui.render_vending)
    elif (self._deviceManager.isOnewireBusy()):
      self.ui.setDrawFunc(self.ui.render_removeIbutton)
    #elif self.waitForKey:
    #  if not self.oneWireLed:
    #    self._deviceManager.setOnewireLed(True)
    #    self.oneWireLed = True
    #  self.ui.setDrawFunc(self.ui.render_waitIbutton)
    elif (self._deviceManager.isBusy()):
      self.ui.setDrawFunc(self.ui.render_busy)
    else:
      if len(self.currentKey)>0:
        self.ui.debugMessage = ["Your iButton id: "+self.currentKey]
      else:
        #self.ui.debugMessage = ["Please present your iButton to the reader"]
        self.ui.debugMessage = [""]
      self.ui.setDrawFunc(self.ui.render)
      
  def on_key(self, key, type):
    self._deviceManager.setOnewireLed(False)
    self.oneWireLed = False
    self.ui.draw("Key: "+key+" of type "+type)
    self.waitForKey = False
    self.currentKey = key

  def on_keyboard_command(self, command):
    if (self.dev or self.demo) and command[0:6]=="error:":
        self.disableUIinput = True
        self.ui.show_fatal_error(command[6:], True)
        self.sleep(5)
        self.disableUIinput = False
        self.ui.draw("Error demo completed.")
    elif (self.dev) and command[0:5]=="vend:":
      self.vend(int(command[5:]))
    else:
      self.ui.draw("Command ignored.")
  
  def vend(self, location):
    try:
      location = str(location)
      unit = -1
      pos = -1
      if (len(location)==2):
        unit = int(location[0])-1
        pos = int(location[1])-1
      if (len(location)!=2) or (unit<0) or (unit>5) or (pos<0) or (pos>=len(self._drawers)):
        self.disableUIinput = True
        self.ui.show_error("Invalid input", "Please enter a number in the format \"XY\"!", True)
        self.ui.draw("Invalid input: "+str(unit)+" / "+str(pos))
        self.sleep(1)
        self.disableUIinput = False
        return False
      self.ui.draw("Vend: "+str(unit)+" / "+str(pos))
      self._drawers[unit].dispense(pos)
    except Exception as e:
      self.ui.draw("Error while parsing input.")
      print(e)
      
  def on_cleanup(self):
    pygame.quit()
    
  def on_execute(self, dev=False, demo=False):
    if self.on_init(dev, demo) == False:
      self._running = False

    while( self._running ):
      self.on_loop()
      self.on_render()
    self.on_cleanup()

  def showPos(self):
    for i in range(0,len(self._drawers)):
      self.ui.draw("Drawer #"+str(i)+" with id #"+str(self._drawers[i].getId())+" at position #"+str(self._drawers[i].getPosition()))
      self._drawers[i].setAllLeds(0,0,0)
      self._drawers[i].setLed(drawers[i].getPosition(),255,0,0,0)
      self._drawers[i].updateLeds()

  def handleArtnet(self):
    dmx = artnet.receive()
    if dmx:
      for u in range(0,len(self._drawers)):
        for led in range(0,9):
          try:
            r = dmx[u*9*3+led*3]
            g = dmx[u*9*3+led*3+1]
            b = dmx[u*9*3+led*3+2]
          except:
            r = 0
            g = 0
            b = 0
          self._drawers[u].setLed(led,r,g,b)
        self._drawers[u].updateLeds()
        
  def sleep(self, t):
    remaining = t*1000
    while remaining > 0:
      remaining -= 1
      self.on_loop()
      time.sleep(0.001)


if __name__ == "__main__" :
    app = App()
    dev = False
    demo = False
    if len(sys.argv) > 1:
      dev = int(sys.argv[1])&0x01
    if len(sys.argv) > 2:
      demo = int(sys.argv[2])&0x01
    if dev:
      print("Development mode enabled!")
    if demo:
      print("Demonstration mode enabled!")
    app.on_execute(dev, demo)
