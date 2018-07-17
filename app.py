#!/usr/bin/python3
import hardware, time, artnet, sys

class App:
	def __init__(self):
		self._deviceManager = None
		self._running = False
		self._drawers = []
		self._onewire = []
		self.waitForKey = True
		self.currentKey = ''
		self.oneWireLed = False
		self.halted = False
		self.disableInput = False
	
	def handle_exception(self, exctype, value, traceback):
		if exctype==KeyboardInterrupt:
			sys.exit(0)
		self.halt("A Python exception occured.")
		
		print("EXCEPTION:",exctype,value,traceback)
		print("=== EXCEPTION ===",True)
		print(str(value))
	
	def halt(self,text=""):
		print("Fatal error: "+text)
		self.halted = True
		self._running = False
	
	def on_logout(self):
		print("Logout")
		self.currentKey = ""
		self.waitForKey = True
	
	def on_init(self):
		sys.excepthook = self.handle_exception
		self._running = True
		self._deviceManager = hardware.DeviceManager(print, self.halt, self.sleep)
		self._drawers = self._deviceManager.getDrawers()
		self._onewire = self._deviceManager.getOnewire()
		for onewire in self._onewire:
			onewire.setKeyCb(self.on_key)
		if (len(self._drawers)!=6):
			self.halt("Could not find 6 drawers. Amount found: "+str(len(self._drawers)))
			return
			
		#And fix the sorting (la 0 zit op positie 4) (NO LONGER NEEDED)
		#self._drawers[0].setPosition(4)
		#self._drawers[4].setPosition(0)
		#self._deviceManager.sort()
		#self._drawers = self._deviceManager.getDrawers()
		
		print("Initializing Artnet...")
		artnet.init()
	
	def on_loop(self):
		self.handleArtnet()
		if not self._deviceManager is None:
			self._deviceManager.update()
		#if (self._deviceManager.isDrawerBusy()):
		#elif (self._deviceManager.isOnewireBusy()):

	def isBusy(self):
		deviceManagerBusy = True
		if not self._deviceManager is None:
			deviceManagerBusy = self._deviceManager.isBusy()
		return deviceManagerBusy or self.halted or self.disableInput #or self.waitForKey    
		
	def on_key(self, key, type):
		self._deviceManager.setOnewireLed(False)
		self.oneWireLed = False
		print("Key: "+key+" of type "+type)
		self.waitForKey = False
		self.currentKey = key
	
	def vend(self, location):
		try:
			location = str(location)
			unit = -1
			pos = -1
			if (len(location)==2):
				unit = int(location[0])-1
				pos = int(location[1])-1
			if (len(location)!=2) or (unit<0) or (unit>5) or (pos<0) or (pos>=len(self._drawers)):
				self.disableInput = True
				print("Invalid input: "+str(unit)+" / "+str(pos))
				self.sleep(1)
				self.disableInput = False
				return False
			print("Vend: "+str(unit)+" / "+str(pos))
			self._drawers[unit].dispense(pos)
		except Exception as e:
			print("Error while parsing input.")
			print(e)
		
	def on_cleanup(self):
		pass
		
	def on_execute(self):
		if self.on_init() == False:
			self._running = False
		while( self._running ):
			self.on_loop()
			self.on_cleanup()

	def showPos(self):
		for i in range(0,len(self._drawers)):
			print("Drawer #"+str(i)+" with id #"+str(self._drawers[i].getId())+" at position #"+str(self._drawers[i].getPosition()))
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
    app.on_execute()
