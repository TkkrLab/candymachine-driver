import ui, pygame

class MenuManager:
	def __init__(self, uiManager):
		self.dev = uiManager.dev
		self.demo = uiManager.demo
		self.app = uiManager.app
		self.uiManager = uiManager
		self.menuKeypad = MenuKeypad(uiManager, self.keypadCb)
		self.menuMain = MenuMain(uiManager, self.mainCb)
		self.current = self.menuMain
		self.logout = self.logoutStub
	
	def setLogoutCb(self, cb):
		self.logout = cb
	
	def logoutStub(self):
		pass
	
	def render(self):
		self.current.render()
	
	def action(self, location, execute=False):
		self.current.action(location, execute)
		#print("Mouse event at "+str(location[0])+","+str(location[1])+": "+str(execute))
		
	def keypadCb(self, success, value):
		if (success):
			self.app.vend(value)
		self.current = self.menuMain
		self.current.reset()
		
	def mainCb(self, action):
		if action=="logout":
			self.current = self.menuMain
			self.logout()
		elif action=="keypad":
			self.current = self.menuKeypad
		elif action=="sensors1":
			self.app.vend(51)
		elif action=="sensors2":
			self.app.vend(52)
		elif action=="breadboard":
			self.app.vend(56)
		elif action=="sensors3":
			self.app.vend(54)
		elif action=="servo":
			self.app.vend(55)
		elif action=="arduino":    
			self.app.vend(55)
		elif action=="usb-cable":
			self.app.vend(32)
		elif action=="jawbreaker":
			self.app.vend(33)
		self.current.reset()
		
class MenuKeypad:
	def __init__(self, uiManager, callback):
		self.callback  = callback
		self.uiManager = uiManager
		self.buttons = []
		self.input = ""
		
		amount = (3,4)
		size = (80,80)
		distance = (10,10)
		top = ((uiManager._windowSize[0]-(size[0]+distance[0])*amount[0])/2,
			   (uiManager._windowSize[1]-(size[1]+distance[1])*amount[1])/2)
		
		self.keypadTop = top
		
		for x in range (0,amount[0]):
			for y in range(0,amount[1]):
				label = str(y*3+x+1)
				if y==3:
					if x==0:
						label = "BACK"
					elif x==1:
						label = "0"
					elif x==2:
						label = "OK"
				self.buttons.append(ui.Button(uiManager, (top[0]+x*(size[0]+distance[0]), top[1]+y*(size[1]+distance[1])), size, label, self.keypadCb))
	
	def reset(self):
		self.input = ""
	
	def keypadCb(self, btn):
		print("Callback for button "+btn.text)
		if btn.text=="BACK":
			self.callback(False, 0)
			self.input = ""
		elif btn.text=="OK":
			if (len(self.input)>0):
				self.callback(True, int(self.input))
				self.input = ""
		elif len(self.input)<3:
			self.input += btn.text
	
	def render(self):
		textSurface = self.uiManager._fonts[0].render(self.input, False, self.uiManager._colorFg1)
		textRect = textSurface.get_rect(center=(self.uiManager._windowSize[0]/2, self.keypadTop[1]-20))
		self.uiManager.display.blit(textSurface, textRect)
		
		for button in self.buttons:
			button.render()
	
	def action(self, location, execute):
		for button in self.buttons:
			button.highlight(button.checkSelected(location))		
		self.render()
		
		if (execute):
			for button in self.buttons:
				if button.checkSelected(location):
					button.callback()
					button.highlight(0)
		
class MenuMain:
	def __init__(self, uiManager, callback):
		self.callback  = callback
		self.uiManager = uiManager
		self.buttons = []
		
		self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 - 180), (400, 50), "Arduino", self.productCb))
		self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 - 120), (400, 50), "Breadboard", self.productCb))
		#self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 - 60), (400, 50), "Sensors [3]", self.productCb))
		#self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 - 0), (400, 50), "Breadboard", self.productCb))
		#self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 + 60), (400, 50), "Servo motor", self.productCb))
		#self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 + 120 ), (400, 50), "Arduino", self.productCb))
		#self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 + 180 ), (400, 50), "Jawbreaker", self.productCb))
		#self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 + 240), (400, 50), "USB A-B cable", self.productCb))
		#self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 + 360), (400, 50), "Manual location entry...", self.manualCb))
		
		
		#self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0]/2 - 200, uiManager._windowSize[1]/2 - 0), (400, 50), "Click here for a demo!", self.demoCb))
		
		#self.buttons.append(ui.Button(uiManager, (uiManager._windowSize[0] - 150, uiManager._windowSize[1] - 150), (100, 100), "STOP", self.logoutCb))
	
	def reset(self):
		self.input = ""
		
	def logoutCb(self, btn):
		self.callback("logout")
	
	def manualCb(self, btn):
		self.callback("keypad")
	
	def demoCb(self, btn):
		self.callback("jawbreaker")
	
	def productCb(self, btn):
		if btn.text=="Sensors [1]":
			self.callback("sensors1")
		if btn.text=="Sensors [2]":
			self.callback("sensors2")
		if btn.text=="Sensors [3]":
			self.callback("sensors3")
		if btn.text=="Breadboard":
			self.callback("breadboard")
		if btn.text=="Servo motor":
			self.callback("servo")
		if btn.text=="Arduino":
			self.callback("arduino")
		if btn.text=="USB A-B cable":
			self.callback("usb-cable")
		if btn.text=="Jawbreaker":
			self.callback("jawbreaker")
	
	def render(self):
		#pygame.draw.rect(self.uiManager.display,self.uiManager._colorBg2,(0,0,self.uiManager._windowSize[0],50))
		#textSurface = self.uiManager._fonts[0].render("Tkkrlab Candymachine", False, self.uiManager._colorFg3)
		#self.uiManager.display.blit(textSurface, (10,10))
		
		self.instruction = []
		#self.instruction.append("NOTE:")
		#self.instruction.append("De testproducten in de automaat zijn van Renze")
		#self.instruction.append("en liggen er alleen maar in om de automaat te testen")
		#self.instruction.append("")
		#self.instruction.append("Neem alsjeblieft geen breadboards of servos mee!")
		
		y = 60
		for line in self.instruction:
			textSurface = self.uiManager._fonts[1].render(line, False, (0x2A, 0x2A, 0x2A))
			self.uiManager.display.blit(textSurface, (10,y))
			y += 30
		
		
		for button in self.buttons:
			button.render()
	
	def action(self, location, execute):
		for button in self.buttons:
			button.highlight(button.checkSelected(location))		
		self.render()
		
		if (execute):
			for button in self.buttons:
				if button.checkSelected(location):
					button.callback()
					button.highlight(0)
