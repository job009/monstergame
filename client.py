# Created by Haley Wichman for Louisiana Tech Cyber Storm
from socket import socket, AF_INET, SOCK_STREAM
from time import time
from sys import stdout
from threading import Thread
import random
import pygame
import hashlib
import pyperclip
DELAY_BETWEEN_PUZZLES = 50
DEFAULT_BORDER_WIDTH = 2
countdownPt = -1
connectionError = False
monsterDefeated = False
pygame.init()
monsterRoars = [pygame.mixer.Sound("monsterRoar0.wav"),pygame.mixer.Sound("monsterRoar1.wav"),pygame.mixer.Sound("monsterRoar2.wav"),pygame.mixer.Sound("monsterRoar3.wav"),pygame.mixer.Sound("monsterRoar4.wav"),pygame.mixer.Sound("monsterRoar5.wav")]
timeUpSound = pygame.mixer.Sound("timeup.wav")
newPuzzleSound = pygame.mixer.Sound("newPuzzle.wav")
backgroundImage=pygame.image.load("rathalos.jpg")
#backgroundEndImage = pygame.image.load("")

class Background(pygame.sprite.Sprite):
    def __init__(self,pygameImage, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygameImage
        self.rect=self.image.get_rect()
        self.rect.left, self.rect.top = location

class TextBox:
    def __init__(self, x, y, w, h, colorInactive = (150,150,150), colorActive = (255,255,255),textSize=32, textColor = (255,255,255)):
        self.input_box = pygame.Rect(x, y, w, h)
        self.active = False
        self.colorInactive = colorInactive
        self.colorActive = colorActive
        self.color = colorInactive
        self.textSize = textSize
        self.font = pygame.font.Font(None, self.textSize)
        self.textColor = textColor
        self.contents = ""
        self.marker = textColor
        self.markerRect = pygame.Rect(x,y,2,h)
        self.txt_surface = self.font.render(self.contents, True, self.textColor)
        self.border_width = DEFAULT_BORDER_WIDTH
    def update(self, event=None):
        global connectionError
        # If the user clicked on the solution box
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
            else:
                self.active = False
                # Change the current color of the input box.
            self.color = self.colorActive if self.active else self.colorInactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    #hashes it so people cant sniff the network and find the answer from other teams
                    answer = str(hashlib.sha224(self.contents.encode("utf8")).hexdigest())
                    if (not connectionError):
                        send("[A]"+answer)
                        self.contents = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.contents = solutionBox.contents[:-1]
                else:
                    self.contents += event.unicode
    def render(self):
        global screen
        self.txt_surface = self.font.render(self.contents, True, self.textColor)
        self.markerRect = pygame.Rect(self.input_box.x+5+self.txt_surface.get_width(), self.input_box.y, 2, self.input_box.h)
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.input_box.w = width
        # Blit the text.
        screen.blit(self.txt_surface, (self.input_box.x+5, self.input_box.y+5))
        # Blit the input_box rect.
        pygame.draw.rect(screen, self.color, self.input_box, self.border_width)
        #the marker for the text
        if (self.active):
            pygame.draw.rect(screen, self.colorActive, self.markerRect, self.border_width)

class GameLog:
    def __init__(self, x, y, w, h, textSize = 24, textColor=(255,255,255), boxColor = (200,200,200)):
        self.log_box = pygame.Rect(x,y,w,h)
        self.border_width = DEFAULT_BORDER_WIDTH
        self.textSize = textSize
        self.textColor = textColor
        self.boxColor = boxColor
        self.contents = ["","","",""]
    def update(self, event = None):
        pass
    def render(self):
        global screen
        #handles the gamelogs for the puzzle
        font = pygame.font.Font(None, self.textSize)
        pygame.draw.rect(screen, self.boxColor, self.log_box, self.border_width)
        for i in range(0, len(gameLog.contents)):
            screen.blit(font.render(self.contents[len(self.contents)-1-i],True, self.textColor), (80, 500-i*15))

class MonsterHealthBar:
    def __init__(self, x,y,w,h,maxHealth, healthColor = pygame.Color('red')):
        self.monsterHealthBarFrame = pygame.Rect(x, y, w, h)
        self.monsterHealthBarFill = pygame.Rect(x, y, w, h)
        self.maxHealth = maxHealth
        self.currentHealth = maxHealth
        self.healthColor = healthColor
        self.border_width = DEFAULT_BORDER_WIDTH
    def update(self,event = None):
        if not (connectionError):
            self.monsterHealthBarFill.width = (self.currentHealth*self.monsterHealthBarFrame.width)/self.maxHealth
    def render(self):
        global countdownPt
        pygame.draw.rect(screen, pygame.Color('red'), self.monsterHealthBarFill, 0)
        pygame.draw.rect(screen, pygame.Color('black'), self.monsterHealthBarFrame, self.border_width)

class Text:
    def __init__(self, x, y, contents,textColor=(255,255,255), textSize=24):
        self.textSize = textSize
        self.contents = contents
        self.textColor = textColor
        self.pos = (x,y)
    def update(self, event = None):
        pass
    def render(self):
        global screen
        font = pygame.font.Font(None, self.textSize)
        text = font.render(self.contents, True, self.textColor)
        screen.blit(text,self.pos)

class Button:
    def __init__(self, x, y, w, h, activeColor =(0,255,255),inactiveColor = (0, 200, 200),label = "",textSize = 24, shown = True, target =None):
        self.buttonFrame = pygame.Rect(x,y,w,h)
        self.inactiveColor = inactiveColor
        self.activeColor = activeColor
        self.color = inactiveColor
        self.label = label
        self.textSize = textSize
        self.target = target
        self.shown = shown
        self.border_width = DEFAULT_BORDER_WIDTH
    def changeShown(self):
        self.shown = not self.shown
    def update(self,event = None):
        if (self.buttonFrame.collidepoint(pygame.mouse.get_pos())):
            self.color = self.activeColor
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (self.target is not None):
                    try:
                        self = self.target(self)
                    except TypeError:
                        self.target()
        else:
            self.color = self.inactiveColor
    def render(self):
        global screen
        if (self.shown):
            font = pygame.font.Font(None, self.textSize)
            pygame.draw.rect(screen, self.color, self.buttonFrame, 0)
            pygame.draw.rect(screen, (0,0,0), self.buttonFrame, self.border_width)
            screen.blit(font.render(self.label, True, (0,0,0)), (self.buttonFrame.x+5, self.buttonFrame.y+5))

class ParagraphBox:
    def __init__(self, x, y, w, h, contents,textColor = (0,0,0), boxColor = (200,200,200),textSize = 24):
        self.textSize = textSize
        self.contents = contents
        self.w = w
        self.paragraphFrame = pygame.Rect(x, y, w+self.textSize/4, h)
        self.textColor = textColor
        self.boxColor = boxColor
        self.shown = False
    def changeShown(self, button):
        self.shown = not self.shown
        button.label = "Show Puzzle" if not self.shown else "Hide Puzzle"
        return button
    def update(self,event = None):
        pass
    def render(self):
        global screen
        if (self.shown):
            font = pygame.font.Font(None, self.textSize)
            parsedContents = self.contents.split(" ")
            currentGrouping = ""
            textGroupings = []
            for word in parsedContents:
                finishedWithWord = False
                while (not finishedWithWord):
                    word_surface = font.render(word, True, self.textColor)
                    if (currentGrouping == "" and word_surface.get_width() > self.w):
                        wrapTimes = int(word_surface.get_width()/self.w)
                        extraWidth = word_surface.get_width() % self.w
                        #extraLength = int((extraWidth*len(word))/word_surface.get_width())
                        otherWidth = (word_surface.get_width() - extraWidth) / wrapTimes
                        otherLength = int((otherWidth*len(word))/word_surface.get_width())
                        for i in range(0, wrapTimes):
                            currentGrouping = word[(i*otherLength):((i+1)*otherLength)]
                            textGroupings.append(currentGrouping)
                            currentGrouping = ""
                        currentGrouping = word[wrapTimes*otherLength:]
                        finishedWithWord = True
                    else:
                        txt_surface = font.render(currentGrouping, True, self.textColor)
                        if (txt_surface.get_width() + word_surface.get_width() > self.w):
                            textGroupings.append(currentGrouping)
                            currentGrouping = ""
                        else:
                            if (currentGrouping == ""):
                                currentGrouping += word
                            else:
                                currentGrouping += " "+word
                            finishedWithWord = True
            textGroupings.append(currentGrouping)
            pygame.draw.rect(screen, self.boxColor, self.paragraphFrame, 0)
            for i,grouping in enumerate(textGroupings):
                text = font.render(grouping, True, self.textColor)
                screen.blit(text,(self.paragraphFrame.x+self.textSize/4,self.paragraphFrame.y+self.textSize/4+i*(self.textSize+5)))
            pygame.draw.rect(screen, pygame.Color('black'), self.paragraphFrame, 2)

def renderLeaderboard():
    font = pygame.font.Font(None, 32)
    screen.blit(font.render("Scores",True, (255,255,255)), (650, 115))
    font = pygame.font.Font(None, 24)
    #handles the leaderboard for the game
    for i in range (0, len(leaderboard)):
        screen.blit(font.render(str(leaderboard[len(leaderboard)-1-i][0]+": "+leaderboard[len(leaderboard)-1-i][1]), True, (255,255,255)), (650, 150+i*15))

def renderHints():
    global cycle
    global start_hint_time
    global monsterDefeated
    font = pygame.font.Font(None, 24)
    passed_hint_time = pygame.time.get_ticks() - start_hint_time
    if (passed_hint_time > 20000):
        start_hint_time = pygame.time.get_ticks()
        if (cycle != 5):
            cycle += 1
        else:
            cycle = 0
    if (monsterDefeated):
        screen.blit(font.render("The monster has been defeated. There are no more puzzles to be released. Final scores on right side.", True, (255,255,255)), (5,610))
    elif (cycle == 0):
        screen.blit(font.render("TIP - Players joining mid-round may find themselves short on time. It may be wise to wait until next round.", True, (255,255,255)), (5,610))
    elif (cycle == 1):
        screen.blit(font.render("TIP - If your team attacks the monster first, you'll do extra damage based on number of participating teams.", True, (255,255,255)), (5,610))
    elif (cycle == 2):
        screen.blit(font.render("TIP - You can find the copyable puzzle text on the console if the 'Copy to clipboard' button is finnicky.", True, (255,255,255)), (5,610))
    elif (cycle == 3):
        screen.blit(font.render("TIP - If you need to close the game, your team score will be safe on the server.", True, (255,255,255)), (5,610))
    elif (cycle == 4):
        screen.blit(font.render("TIP - Click the 'Show Puzzle' button to view the puzzle, use the same button to hide the puzzle.", True, (255,255,255)), (5,610))
    elif (cycle == 5):
        screen.blit(font.render("TIP - You can paste to the solution box directly from the clipboard using the 'Paste' button", True, (255,255,255)), (5,610))
    elif (cycle == 6):
        screen.blit(font.render("Client created by Haley Wichman", True, (255,255,255)), (5,610))
    font = pygame.font.Font(None, 32)

def renderBackground():
    screen.fill([255,255,255])
    screen.blit(background.image,background.rect)

def renderTimeLeft():
    timePassed = pygame.time.get_ticks() - startTime
    screen.blit(font.render("%.2f" % (countdownPt - timePassed/1000), True, (255,255,255)),(50, 50))

def receive():
    global countdownPt
    global startTime
    global monsterHealthBar
    global connectionError
    global monsterDefeated
    while True:
        try:
            data = s.recv(BUFSIZ)
            datadecode = str(data.decode())
            if ("[C]" in datadecode):
                addToGamelog("That was correct! Please wait until next round.")
            if ("[I]"in datadecode):
                addToGamelog("That was incorrect. Try again.")
            if ("[T]" in datadecode):
                timeData = getData("[T]", datadecode)
                startTime = pygame.time.get_ticks()
                countdownPt = float(timeData)
                print (countdownPt)
            if (("[U]") in datadecode):
                pygame.mixer.Sound.play(timeUpSound)
            if ("[S]" in datadecode):
                announcementData = getData("[S]", datadecode)
                addToGamelog(announcementData)
            if ("[Z]" in datadecode):
                attackData = getData("[Z]", datadecode)
                addToGamelog(attackData)
                roarChoice = random.randint(0, len(monsterRoars)-1)
                pygame.mixer.Sound.play(monsterRoars[roarChoice])
            if ("[P]" in datadecode):
                puzzleData = getData("[P]", datadecode)
                changePuzzle(puzzleData)
                pygame.mixer.Sound.play(newPuzzleSound)
                print (puzzleData)
            if ("[H]" in datadecode):
                healthData = getData("[H]", datadecode)
                monsterHealthBar.currentHealth = int(healthData)
            if ("[L]" in datadecode):
                leaderboardData = getData("[L]", datadecode)
                updateLeaderboard(leaderboardData)
            if ("[D]" in datadecode):
                addToGamelog("Game over, the monster was defeated.")
                monsterDefeated=True
        except OSError:
            print ("error receiving data")
            connectionError = True
            break

def send(msg, event=None):
    s.send(bytes(msg, "utf8"))
    

leaderboard = []
def updateLeaderboard(leaderboardData):
    global leaderboard
    leaderboard = []
    namestart = 0
    divider = 0
    for i,char in enumerate(leaderboardData):
        if (char == ":"):
            divider = i
            teamName = leaderboardData[namestart:divider]
        elif (char == ";"):
            namestart = i+1
            leaderboard.append((teamName,leaderboardData[divider+1:i]))
        

#this helps parse the code a bit, for example, if the packet received is [A]answerishere[S]announcementishere, it
#starts the guess at the end of "[A]" in answerishere and ends the guess at the next '[', if another '[' is not in the
#packet, it will instead take the entire packet to be the answer
def getData(instruction, datadecode):
        endIndex = datadecode.find("[",datadecode.find(instruction)+3)
        if (endIndex == -1):
            endIndex = len(datadecode)
        return datadecode[datadecode.find(instruction)+3:endIndex]
 
def changePuzzle(puzzleData):
    currentPuzzleBox.contents = puzzleData

def addToGamelog(msg):
    del gameLog.contents[0]
    gameLog.contents.append(msg)


def update():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        showHidePuzzleButton.update(event)
        currentPuzzleBox.update(event)
        copyPuzzleTextButton.update(event)
        solutionBox.update(event)
        monsterHealthBar.update(event)
        gameLog.update(event)
        pasteToTextBoxButton.update(event)
        clearTextBoxButton.update(event)
        sendTextBoxButton.update(event)
    #clock.tick(30)
        
def render():
    global monsterDefeated
    renderBackground()
    if (not monsterDefeated):
        renderTimeLeft()
    solutionBox.render()
    gameLog.render()
    monsterHealthBar.render()
    currentPuzzleBox.render()
    copyPuzzleTextButton.render()
    showHidePuzzleButton.render()
    renderLeaderboard()
    renderHints()
    pasteToTextBoxButton.render()
    clearTextBoxButton.render()
    solutionText.render()
    sendTextBoxButton.render()
    if (connectionError):
        connectionErrorText.render()
    pygame.display.flip()


#Button Functions
def copyPuzzleText():
    try:
        pyperclip.copy(currentPuzzleBox.contents)
    except:
        print("No workie on your system!");
        pass
    
def pasteToTextBox():
    try:
        solutionBox.contents = pyperclip.paste()
    except:
        print("No workie on your system!");
        pass

def clearTextBox():
    solutionBox.contents=""

def sendTextBox():
    answer = str(hashlib.sha224(solutionBox.contents.encode("utf8")).hexdigest())
    if (not connectionError):
        send("[A]"+answer)
        solutionBox.contents = ''
    

def showTotalPuzzleBox():
    global showHidePuzzleButton
    global currentPuzzleBox
    global copyPuzzleTextButton
    currentPuzzleBox.changeShown(showHidePuzzleButton)
    copyPuzzleTextButton.changeShown()

#Global'
background = Background(backgroundImage, [0,0])
screen = pygame.display.set_mode((840, 630))
currentPuzzleBox = ParagraphBox(250,200, 300, 350,"", textSize = 24)
copyPuzzleTextButton = Button(300, 500, 180, 30, label = "Copy To Clipboard", inactiveColor = (255,0,0),activeColor = (255,150,150),shown = False, target = copyPuzzleText)
showHidePuzzleButton = Button(70,415,120,30, label = "Show Puzzle",target = showTotalPuzzleBox)
pasteToTextBoxButton = Button (348, 585, 75,20, label = "Paste", target = pasteToTextBox)
clearTextBoxButton = Button(420, 585, 75, 20, label = "Clear", target = clearTextBox)
sendTextBoxButton = Button(480, 585, 75, 20, label = "Send", target = sendTextBox)
solutionBox = TextBox(840/2-70, 550, 140, 32)
monsterHealthBar = MonsterHealthBar(840/2-150, 100, 300, 15, 1000000)
gameLog = GameLog(70, 445, 400, 80)
solutionText = Text(solutionBox.input_box.x-100,solutionBox.input_box.y+5,"Solution:",(255,255,255),32)
connectionErrorText = Text(10,300,"Connection lost. See the server admin if you think it's a problem with the server",(255,255,255),32)
clock = pygame.time.Clock()
startTime = pygame.time.get_ticks()
start_hint_time = pygame.time.get_ticks()
cycle = 0
font = pygame.font.Font(None, 32)
#gameloop
running = True
HOST = "10.50.50.50"
PORT = 23435
BUFSIZ = 4096

ADDR = (HOST,PORT)
s = socket(AF_INET, SOCK_STREAM)
try:
    s.connect(ADDR)
    receive_thread = Thread(target=receive)
    receive_thread.start()
except ConnectionRefusedError:
    connectionError = True

#gameloop
while (running):
    update()
    render()
    clock.tick(30)
pygame.quit()    
send("[Q]")
