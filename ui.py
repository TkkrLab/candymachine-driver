import pygame, menu

class UiManager:
	def __init__(self, app):
		self.dev = app.dev
		self.demo = app.demo
		self.app = app
		self._windowSize = 600, 1024
		self._fonts = []
		self._colorBg1 = (0x00, 0x00, 0x00)
		self._colorBg2 = (0x00, 0x00, 0x00)
		self._colorBgButton = (0xFF, 0xFF, 0x00)
		self._colorFgButton = (0x0, 0x0, 0x0)
		self._colorBgButtonSelected = (0x0, 0x0, 0x0)
		self._colorFgButtonSelected = (0xFF, 0xFF, 0x00)
		self._colorFg1 = (0xDB, 0xE2, 0xDF)
		self._colorFg2 = (0x00, 0xFF, 0xFF)
		self._colorFg3 = (0xFF, 0xFF, 0x00)
		self._colorBgError = (0x00, 0x00, 0x00)
		self._colorFgError = (0xFF, 0x00, 0x00)
		self._colorBgVending = (0x00, 0x00, 0x00)
		self._colorFgVending = (0x00, 0xFF, 0x00)
		self._colorBgIbutton = (0x00, 0x00, 0x00)
		self._colorFgIbutton = (0xFF, 0xFF, 0x00)
		
		self._errorText = ["No error", "?"]
		self._errorBorder = True
		self._errorBlink = False
		self._errorBlinkState = False
		self._errorBlinkCounter = 0
		
		self._images = {
			"loadingBar":[pygame.image.load("resources/spinner/bar_128x32.png"), (128,32), 23, 0],
			"loadingSquare":[pygame.image.load("resources/spinner/square_128.png"), (128,128), 7, 2],
			"banana":[pygame.image.load('resources/banana.png'), (365,360), 7, 0],
			"tkkrlab":[pygame.image.load('resources/tkkrlab.png'), (340,396), 0, 0]
			}
		
		self._imageAnimState = {}
		for image in self._images:
			self._imageAnimState[image] = [0,0];
		
		self._messages = []
		self._objects = []
		self._kbInputBuffer = ""
		self._kbHandler = None
		self._menu = None
		
		self._mouse = False
		self._mouseColor = (0,0,0)
		self.pos = 0
		
		self.debugMessage = []
		
		pygame.mouse.set_visible(self.dev or self.demo)
		pygame.font.init()
		
		self.display = pygame.display.set_mode(self._windowSize, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.NOFRAME)
		#self._fonts.append(pygame.font.Font("resources/fonts/OCRAEXT.TTF", 50))
		#self._fonts.append(pygame.font.Font("resources/fonts/NotoSans-Regular.ttf", 25))
		self._fonts.append(pygame.font.SysFont('Roboto Condensed', 35))
		self._fonts.append(pygame.font.SysFont('Roboto Condensed', 25))
		self._fonts.append(pygame.font.SysFont('Hack', 20))
		self._fonts.append(pygame.font.SysFont('Hack', 15))
		self.render_simple_message("Please wait...")
		self.menu = menu.MenuManager(self)
		
		self.progressMessage = ""
		
		self.timerFunctions = []
		pygame.time.set_timer(pygame.USEREVENT, 25)
		
	def addTimerFunction(self, func, runNow=False):
		if not func in self.timerFunctions:
			print("addTimerFunction")
			self.timerFunctions.append(func)
			if runNow:
				func()
			return True
		return False
	
	def delTimerFunction(self, func):
		if func in self.timerFunctions:
			print("delTimerFunction")
			self.timerFunctions.remove(func)
			return True
		return False
	
	def setProgressMessage(message):
		self.progressMessage = message
		
	def register_logout_handler(self, cb):
		self.menu.setLogoutCb(cb)
		
	def register_kb_handler(self,handler):
		self._kbHandler = handler
		
	def on_key_down(self,event, busy):
		if not busy:
			if (event.unicode=='\r'):
				if (self._kbHandler):
					self._kbHandler(self._kbInputBuffer)
				else:
					self.draw("No keyboard handler registered.")
				self._kbInputBuffer = ""
			else:
				self._kbInputBuffer += event.unicode
			self.render()
			
	def on_key_up(self,event, busy):
		pass
		
	def render_simple_message(self,m):
		self.display.fill(self._colorBg1)
		textSurface = self._fonts[0].render(m, False, self._colorFg1)
		textRect = textSurface.get_rect(center=(self._windowSize[0]/2, self._windowSize[1]/2))
		self.display.blit(textSurface, textRect)
		pygame.display.flip()
	
	def draw(self,text="",forceDebug=False):
		if not self.drawFunc is None:
			self.drawFunc()
		if forceDebug:
			self.dev = True
		if not text == "":
			print(text)
			self._messages.append(text)
		while len(self._messages) > 10:
			self._messages.pop(0)
		if self.dev:
			y = self._windowSize[1] - 165
			pygame.draw.rect(self.display,self._colorBg2,(0,y,self._windowSize[0],165))
			for message in self._messages:
				textSurface = self._fonts[1].render(message, False, self._colorFg1)
				self.display.blit(textSurface, (10,y))
				y = y + 16
				
		if (self._mouse):
			pygame.draw.circle(self.display, self._mouseColor, self._mouse, 30, 4)
			
			
		pygame.display.flip()
		
	def render_dialog(self, text1="", text2="", border=True, fgColor=(0xFF,0xFF,0xFF), bgColor=(0,0,0)):
		#self.display.fill(self._colorBgError)
		pygame.draw.rect(self.display,bgColor,(45,self._windowSize[1]/2-45,self._windowSize[0]-90,90))
		if (border):
			pygame.draw.rect(self.display,fgColor,(40,self._windowSize[1]/2-50,self._windowSize[0]-80,100))
			pygame.draw.rect(self.display,bgColor,(45,self._windowSize[1]/2-45,self._windowSize[0]-90,90))
		textSurface = self._fonts[2].render(text1, False, fgColor)
		textRect = textSurface.get_rect(center=(self._windowSize[0]/2, self._windowSize[1]/2 - 20))
		self.display.blit(textSurface, textRect)
		textSurface = self._fonts[3].render(text2, False, fgColor)
		textRect = textSurface.get_rect(center=(self._windowSize[0]/2, self._windowSize[1]/2 + 10))
		self.display.blit(textSurface, textRect)
		#pygame.display.flip()
		
	def show_error(self, text1, text2, border=False, blink=False):
		self._errorText[0] = text1
		self._errorText[1] = text2
		self._errorBorder = border
		self._errorBlink = blink
		self.setDrawFunc(self.render_error)		
		
	def show_fatal_error(self, text="", border=False, blink=False):
		self._errorText[0] = "Fatal Error. Machine out of service."
		self._errorText[1] = "Guru Meditation #"+text
		self._errorBorder = border
		self._errorBlink = blink
		self.setDrawFunc(self.render_error)
		
	def render_error(self):
		#self.display.fill(self._colorBgError)
		#self.render_dialog(self._errorText[0], self._errorText[1], self._errorBlinkState and self._errorBlink, self._colorFgError, self._colorBgError)
		self.display.fill((0xFF,0xFF,0xFF))
		self.render_dialog(self._errorText[0], self._errorText[1], self._errorBorder or (self._errorBlinkState and self._errorBlink), self._colorFgError, (0xFF,0xFF,0xFF))
		
		
	def render_vending(self):
		self.display.fill(self._colorBgVending)
		#self.render_overlay(self._colorBgVending)
		#self.render_dialog("PROCESSING", "Please wait...", True, self._colorFgVending, self._colorBgVending)
		self.render_dialog("Vergeet niet af te rekenen in de bar!", "(Dit programma is nog niet gekoppeld met het barsysteem!)", True, self._colorFgVending, self._colorBgVending)
		
	def render_busy(self):
		self.display.fill(self._colorBgVending)
		#self.render_overlay(self._colorBgVending)
		self.render_dialog("PROCESSING", "Please wait...", True, self._colorFgVending, self._colorBgVending)
		
	def setDrawFunc(self, func=None):
		self.drawFunc = func

	def on_timer(self, event, busy):
		#for i in self._images:
		#	self._images[i][3] += 1
		#	if self._images[i][3] > self._images[i][2]:
		#		self._images[i][3] = 0
				
		for i in self._imageAnimState:
			self._imageAnimState[i][0] -= 1;
			if self._imageAnimState[i][0] < 1:
				self._imageAnimState[i][0] = self._images[i][3]
				self._imageAnimState[i][1] += 1
				if self._imageAnimState[i][1] > self._images[i][2]:
					self._imageAnimState[i][1] = 0
		
		for func in self.timerFunctions:
			func()
		
		self._errorBlinkCounter -= 1
		if self._errorBlinkCounter < 0:
			self._errorBlinkState = ~self._errorBlinkState
			self._errorBlinkCounter = 5
			
		self.draw()
			
	def draw_image(self, name, location, centered = False):
		size = self._images[name][1]
		cropRect = (size[0]*self._imageAnimState[name][1],0,size[0],size[1])
		l = location
		if centered:
			l = (location[0]/2-size[0]/2,location[1]/2-size[1]/2)
		self.display.blit(self._images[name][0], l, cropRect)
		
	def draw_image_repeated(self, name, location, repeat):
		pos = 0
		while repeat > 0:
			newLocation = (location[0]+(pos*self._images[name][1][0]), location[1])
			self.draw_image(name, newLocation)
			pos += 1
			repeat -= 1
		
	def render_loading(self):
		self.display.fill((255,255,255))
		#self.draw_image('tkkrlab', (self._windowSize[0], 450), True)
		#self.draw_image('loadingSquare', (self._windowSize[0], self._windowSize[1]+200), True)
		#self.draw_image_repeated('loadingBar', (0, self._windowSize[1]-32-100), 5)
		self.draw_image_repeated('loadingBar', (0, self._windowSize[1]/2-16), 5)

		textSurface = self._fonts[0].render("Even geduld alstublieft", False, (0x00, 0x00, 0x00) )
		self.display.blit(textSurface, (10, self._windowSize[1]/2 - 100))
		message = ""
		if len(self._messages) > 0:
		  message = self._messages[0]
		if len(self.progressMessage) > 0:
			message = self.progressMessage
		textSurface = self._fonts[1].render(message, False, (0xA2, 0xA2, 0xA2) )
		self.display.blit(textSurface, (10, self._windowSize[1]/2 - 58))
		
		#self.render_dialog("Please wait...", self.progressMessage, False, (0,0,0),(255,255,255)) #self._colorFgIbutton, self._colorBgIbutton)

	def render_waitIbutton(self):
		self.display.fill((255,255,255)) #self._colorBgIbutton)
		self.render_dialog("Welcome!", "Please present your key to the iButton reader to begin", False, (0,0,0),(255,255,255)) #self._colorFgIbutton, self._colorBgIbutton)
		
		self.draw_image('tkkrlab', (self._windowSize[0], 450), True)
		#self.draw_image_repeated('loadingBar', (0, self._windowSize[1]-32-100), 5)
		#cropRect = (0+365*self._images['background'][3],0,365,360)
		#self.display.blit(self._images['background'][0], (self._windowSize[0]/2-365/2,50), cropRect)

	
		
	def render_removeIbutton(self):
		self.display.fill(self._colorBgVending)
		#self.render_overlay(self._colorBgVending)
		self.render_dialog("Please remove your key from the reader", "", False, self._colorFgVending, self._colorBgVending)

	def render_overlay(self, color=(0x0A, 0x0A, 0x0A)):
		s = pygame.Surface(self._windowSize)
		s.set_alpha(0x80)
		s.fill(color)
		self.display.blit(s, (0,0))
		
	def render_background(self):
		headerBackground = pygame.draw.rect(self.display,self._colorBg2,(0,0,self._windowSize[0],50))
		textSurface = self._fonts[0].render("Tkkrlab Candymachine", False, self._colorFg3)
		self.display.blit(textSurface, (10,10))
	
	def on_mouse_move(self,event,busy):
		if self._mouse:
			self._mouse = event.pos
	
	def on_mouse_down(self,event,busy):
		self._mouse = event.pos
		if not busy:
			self._mouseColor = (0,255,0)
			if self._kbInputBuffer=="":
				if event.button==1:
					self.menu.action(event.pos,False)
		else:
			self._mouseColor = (255,0,0)
	
	def on_mouse_up(self,event,busy):
		self._mouse = False
		if not busy:
			if self._kbInputBuffer=="":
				if event.button==1:
					self.menu.action(event.pos,True)
		
	def render(self):
		self.display.fill((0x00, 0x00, 0x00))
		#self.render_background()
		self.menu.render()
		if (len(self._kbInputBuffer)>0):
			self.render_overlay()
			self.render_dialog("Command?", self._kbInputBuffer, True, (0x2A, 0x2A, 0x2A), (0xFF,0xE7,0x00))
		if (len(self.debugMessage)>0):
			#textSurface = self._fonts[1].render(self.debugMessage, False, (0,255,255))
			#textRect = textSurface.get_rect(center=(self._windowSize[0]/2, self._windowSize[1]/2 + 10))
			#self.display.blit(textSurface, textRect)
			y = 60
			for line in self.debugMessage:
				textSurface = self._fonts[1].render(line, False, (0x2A,0x2A,0x2A))
				self.display.blit(textSurface, (10,y))
				y += 30
		pass
	
	
	
class Button:
	def __init__(self, uiManager, location, size, text, callback=None):
		self.uiManager = uiManager
		self.location = location
		self.size = size
		self.text = text
		self._callback = callback
		self.highlighted = False
		
	def callback(self):
		self._callback(self)
	
	def render(self):
		fgColor = self.uiManager._colorFgButton
		bgColor = self.uiManager._colorBgButton
		if (self.highlighted):
			fgColor = self.uiManager._colorFgButtonSelected
			bgColor = self.uiManager._colorBgButtonSelected
		pygame.draw.rect(self.uiManager.display,bgColor,(self.location[0],self.location[1],self.size[0],self.size[1]))
		textSurface = self.uiManager._fonts[0].render(self.text, False, fgColor)
		textRect = textSurface.get_rect(center=(self.location[0]+self.size[0]/2, self.location[1]+self.size[1]/2))
		self.uiManager.display.blit(textSurface, textRect)
	
	def highlight(self, h):
		self.highlighted = h
			
	def checkSelected(self,location):
		if (location[0]>=self.location[0]) and (location[1]>=self.location[1]):
			if (location[0]<=self.location[0]+self.size[0]) and (location[1]<=self.location[1]+self.size[1]):
				return True
		return False
