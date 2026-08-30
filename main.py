import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, sys, random, math, time, datetime, json
#from pypresence import Presence #for discord right presence
from setupvars import *

doRPC = False

if doRPC:
    RPC = Presence(1541135004078309517)
    RPC.connect()
pygame.init()
pygame.font.init()
pygame.mixer.init()

oldSave = False
tempUpgradeLines = []

with open('.saves/save.philooxy', 'r') as f:
    tempLines = f.readlines()
    if len(tempLines) != 4:
        oldSave = True

        for i in range(5):
            tempUpgradeLines.append(tempLines[2])
            tempLines.remove(tempLines[2])
if oldSave:
    with open('.saves/save.philooxy', 'w') as f:
        f.writelines(tempLines)
    with open('.saves/upgrades.philooxy', 'w') as f:
        f.writelines(tempUpgradeLines)
        f.write(f'[1, 0]\n')


def load(data):
    global fishesHeld, balance, reelTime, maxFishes, fishSpawnCap, fishScaredRange, catchTimer, fishRarity, fishCount, fullscreen, lowGraphicsMode, volume, theme, wideMode, fishSFX, fastSun, achs
    if data == "var":
        with open('.saves/save.philooxy', 'r') as f:
            lines = f.readlines()
            fishesHeld = json.loads(lines[0])
            balance = int(lines[1])
            fishCount = int(lines[2])
        with open('.saves/upgrades.philooxy', 'r') as f:
            lines = f.readlines()
            reelTime = json.loads(lines[0])[0]
            maxFishes = json.loads(lines[1])[0]
            fishSpawnCap = json.loads(lines[2])[0]
            fishScaredRange = json.loads(lines[3])[0]
            catchTimer = json.loads(lines[4])[0]
            fishRarity = json.loads(lines[5])[0]
    elif data == "bought":
        with open('.saves/upgrades.philooxy', 'r') as f:
            lines = f.readlines()
            reeltimeupgrade.bought = json.loads(lines[0])[1]
            hookupgrade.bought = json.loads(lines[1])[1]
            spawncapupgrade.bought = json.loads(lines[2])[1]
            scaredrangeupgrade.bought = json.loads(lines[3])[1]
            catchtimeupgrade.bought = json.loads(lines[4])[1]
    elif data == "achs":
        with open('.saves/save.philooxy', 'r') as f:
            lines = f.readlines()
            achs_temp = json.loads(lines[3])
            j = 0
            for i in achs:
                try:
                    i.got = bool(int(achs_temp[j]))
                except IndexError:
                    i.got = "no"

                if i.got == True:
                    i.got2 = True

                if i.got == False:
                    i.got = "no"
                    i.got2 = "no2"
                j += 1
    if data == "settings":
        with open('settings.philooxy', 'r') as f:
            lines = f.readlines()
            fullscreen = bool(int(lines[0]))
            lowGraphicsMode = bool(int(lines[1]))
            volume = float(lines[2])
            #theme = int(lines[3])

            wideMode = bool(int(lines[4]))
            fishSFX = bool(int(lines[5]))
            fastSun = bool(int(lines[6]))


load("var")
load("settings")
#i have no idea what to name this
def buttonCheck(rect, image, slider):
    global startTransitionY, startTransitionX, hovering
    check = False
    image = pygame.transform.scale(image, (rect[2], rect[3]))
    if rect.collidepoint(pygame.mouse.get_pos()):
        hovering = True
        match startTransitionY:
            case 0 | 100 | 200:
                match startTransitionX:
                    case 0 | 100 | 200:
                        check = True
    if check and not(slider):
        image = pygame.transform.scale(image, (rect[2]*1.2, rect[3]*1.2))
        rect = rect.inflate(rect[2]*0.2, rect[3]*0.2)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    return rect, image, check

def checkClick(resetClick):
    global isClicking
    click = False
    if pygame.mouse.get_pressed()[0] == False and isClicking == True:
        isClicking = False
    elif pygame.mouse.get_pressed()[0]:
        if isClicking == False:
            click = True
        if resetClick:
            isClicking = True
    return click

def updateButton(baseRect, image):
    update = False
    image = pygame.transform.scale(image, (baseRect[2], baseRect[3]))
    check = False

    rect, image, check = buttonCheck(baseRect, image, False)

    if check:
        click = checkClick(False)
        if click:
            update = True

    screen.blit(image, rect)

    return update

class button():
    def __init__(self, newarea, image):
        self.image = pygame.image.load(image)
        self.newarea = newarea

    def update(self, rect):
        global area
        update = updateButton(pygame.Rect(rect), self.image)
        if update:
            area = self.newarea

class toggleButton():
    def __init__(self, var):
        self.image_on = toggle_on
        self.image_off = toggle_off
        if var:
            self.var = True
        else:
            self.var = False
    def update(self, var, rect):
        toggle = False
        if var:
            self.image = self.image_on
        else:
            self.image = self.image_off
        update = updateButton(pygame.Rect(rect), self.image)
        if update:
            toggle = True
        if toggle:
            if self.var:
                self.var = False
            else:
                self.var = True
        return self.var

fishSFX_toggle = toggleButton(fishSFX)
fullscreen_toggle = toggleButton(fullscreen)
wideMode_toggle = toggleButton(wideMode)
fastSun_toggle = toggleButton(fastSun)
lowGraphicsMode_toggle = toggleButton(lowGraphicsMode)

class slider():
    def __init__(self, var, maxvar):
        self.image_bar = slider_bar
        self.image_ball = slider_ball
        self.max = maxvar
        self.pos = (var/maxvar)*100
        self.click = False
    def update(self, var, pos):
        global isClicking
        check = False
        click = False
        screen.blit(self.image_bar, pos)
        rect = pygame.Rect(pos[0]-15, pos[1]-15, 130, 40)
        useless, useless, check = buttonCheck(rect, self.image_bar, True)
        if check:
            
            if pygame.mouse.get_pressed()[0] == False and self.click == True:
                self.click = False
            elif pygame.mouse.get_pressed()[0]:
                if self.click == False:
                    click = True

            if click:
                self.pos = pygame.mouse.get_pos()[0]-pos[0]
                if self.pos > 100:
                    self.pos = 100
                elif self.pos < 0:
                    self.pos = 0
        screen.blit(self.image_ball, (pos[0]+self.pos-7.5, pos[1]-2.5))

        var = self.pos/100*self.max

        return var

themeSlider = slider(theme, 4)
volumeSlider = slider(volume*100, 100)

def setVolume(volume):
    ykwtm.set_volume(volume)
    mus_menu.set_volume(volume)
    mus_fishing.set_volume(volume)

class fishy():
    def __init__(self):
        global fishes, fishingrect, fishingrect2, fishRarity, coopLevel, coop

        #print("You know what that means")

        self.pos = (random.randint(-200, 200), random.randint(20, 200))
        if coop:
            tempFishRarity = coopLevel
        else:
            tempFishRarity = fishRarity
        self.type = random.randint(1,tempFishRarity)
        if (self.type/3).is_integer():
            self.type = 2
        elif (self.type/7).is_integer():
            self.type = 3
        else:
            self.type = 1
        self.dir = random.randint(1, 2)
        self.caught = False
        self.scared = 0
        self.speed = random.random()+0.5*self.type
        self.speed2 = self.speed
        self.anim = 0
        self.catchTimer = -31
        if self.type == 1:
            self.catchTime = 50
        if self.type == 2:
            self.catchTime = 25

        self.imagepath = f'assets/fishes/fish{self.type}'
        self.image = pygame.image.load(f'{self.imagepath}_0.png')
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1], self.rect[2], self.rect[3])

        self.rotate = random.randint(0,4)*90
        self.bobber = ""

        fishes.append(self)

    def update(self):
        global moving, offsetX, offsetY, fishCount, bobberFallAnim, reelAnim, fishes, fishesHeld, maxFishes, fishCaughtArray, catchTimer, scaredCounter, outranFish, clickFish, startTransitionX, startTransitionY

        self.image = pygame.image.load(f'{self.imagepath}_{int((self.anim*self.speed/10)%2)}.png')

        self.speed = self.speed2

        self.anim += 1
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.caught == True:
            self.image = pygame.transform.rotate(self.image, self.rotate)

        if self.pos[0] < -180:
            self.dir = 1
        elif self.pos [0] > 180:
            self.dir = 2

        if self.catchTimer > -30:
            self.catchTimer -= 1


        if self.caught:
            self.scared = 30
        if self.scared > 0:
            self.speed = 3*self.speed2

            if self.caught == False:
                if self.pos[0] > self.bobber.pos[0]:
                    self.dir = 1
                elif self.pos[0] < self.bobber.pos[0]:
                    self.dir = 2

            self.scared -= 1

        if self.bobber != "":
            if self.bobber.reel == False:
                if -30 < self.catchTimer <= 0:
                    self.caught = False

                if self.catchTimer == 0:
                    self.bobber.fishCaughtArray.remove(self)
                    self.pos = (self.pos[0], self.pos[1]+(16+-64*random.randint(0,1)))
                    if self.pos[1] < 20:
                        self.pos = (self.pos[0], 20)

        if self.dir == 2:
            self.pos = (self.pos[0]-1*self.speed, self.pos[1])
        else:
            self.pos = (self.pos[0]+1*self.speed, self.pos[1])

        if self.caught == True:
            self.pos = (self.bobber.pos[0], self.bobber.pos[1]+24+11)

        if self.pos[0] > 320 or self.pos[0] < -320 or ((self.pos[1] > 200) and self.caught == False) or 0 < startTransitionY < 100:
            if not(0 < startTransitionY < 100):
                scaredCounter += 1
            fishes.remove(self)

        self.rect[0], self.rect[1] = WIDTH/2 - 16 + self.pos[0]+640-startTransitionX*6.4, HEIGHT/2 - 16 + self.pos[1]-startTransitionY*6

        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            clickFish = True

        screen.blit(self.image, self.rect)

#basic upgrade item
class shopItem():
    def __init__(self, name, desc, image, cost, costIncrement, increment, cap):
        global upgradeList
        self.image = pygame.image.load(image)
        self.imagepath = image
        self.cost = cost
        self.cost2 = cost
        self.costIncrement = costIncrement
        self.increment = increment
        self.name = name
        self.desc = desc
        self.cap = cap
        self.isClicking = False
        self.upgrade = False
        self.capCheck = True
        self.capCheck2 = True
        self.bought = 0
        self.coopBought = 0
        self.coopMax = False
        upgradeList.append(self)

    def update(self, var, rect):
        global balance, hovering, startTransitionY, startTransitionX, shop, upgradeList

        coopBuy = False

        check = False
        click = False
        self.upgrade = False

        self.rect, self.image, check = buttonCheck(pygame.Rect(rect), self.image, False)

        if check:


            self.cost = self.cost2 + self.costIncrement*self.bought

            if self.increment > 0:
                self.capCheck = (var+self.increment < self.cap)
            elif self.increment < 0:
                self.capCheck = (var+self.increment > self.cap)

            if self.increment > 0:
                self.capCheck2 = (var < self.cap)
            elif self.increment < 0:
                self.capCheck2 = (var > self.cap)

            click = checkClick(True)
            if click:
                if balance - self.cost >= 0 and not coop:

                    if self.capCheck2:
                        self.bought += 1
                        var += self.increment
                        balance -= self.cost
                elif coop:
                    var += self.increment
                    coopBuy = True

            desc1, desc1Rect = renderText(self.desc, ut_xs)
            desc1Rect.center = (self.rect.center[0], self.rect.center[1] + self.rect[3]/2 + 10 + 20)
            screen.blit(desc1, desc1Rect)

            if self.capCheck2:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                if self.increment > 0:
                    self.capCheck2 = var+self.increment > self.cap
                elif self.increment < 0:
                    self.capCheck2 = var+self.increment < self.cap

                if self.capCheck2:
                    var2 = self.cap
                else:
                    var2 = var+self.increment
                desc2Text = f'{var} -> {var2}'

                if not coop:
                    cost, costRect = renderText(f'Cost: ${self.cost}', ut_xs)
                    costRect.center = (self.rect.center[0], self.rect.center[1] + self.rect[3]/2 + desc1Rect[3]/2 + 20 + 16)
                    screen.blit(cost, costRect)

            else:
                var = self.cap
                upgradeList.remove(self)
                desc2Text = f'MAX ({var})'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)

            desc2, desc2Rect = renderText(desc2Text, ut_xs)
            desc2Rect.center = (self.rect.center[0], self.rect.center[1] + self.rect[3]/2 + desc1Rect[3]/2 + 20 + 30)
            screen.blit(desc2, desc2Rect)

        name, nameRect = renderText(self.name, ut_s)
        nameRect.center = (self.rect.center[0], self.rect.bottom + 10)
        screen.blit(name, nameRect)

        screen.blit(self.image, self.rect)

        if not coop:
            return var
        else:
            return var, var, coopBuy

class achievement():
    def __init__(self, icon, name, desc, hidden):
        global achs
        self.icon = pygame.image.load(icon)
        self.bg = ach_bg
        self.name = name
        self.desc = desc
        self.got = "no"
        self.got2 = "no2"
        self.easing = 0
        self.showing = False
        self.hidden = hidden
        achs.append(self)
    def update(self, got):
        global achs_unlocked, achs, achs_showing, showingAch
        
        if got and (self.got2 == "no2"):
            self.got = True
            if showingAch == "":
                showingAch = self
                self.got2 = False

        if (not(self.got2)) and not(self in achs_unlocked) and showingAch == self:
            self.showing = True
            if self.easing == 0:
                showingAch = self
                self.got = True
                #achs_unlocked.append(self)
                achs_showing.append(self)
                self.easing += 0.01
            if self.easing <= 5:
                self.pos = pygame.math.lerp(220, 0, ease(self.easing))
                self.easing += 0.01
            elif self.easing <= 6:
                self.pos = pygame.math.lerp(0, 220, ease(self.easing-5))
                self.easing += 0.01
            elif self.easing == 6.0:
                self.got2 = True
                achs_showing.remove(self)
                self.showing = False
                self.easing += 1
            else:
                showingAch = ""

            rect = pygame.Rect(-self.pos-5, HEIGHT-75, 220, 75)
            screen.blit(self.bg, rect)

            name, nameRect = renderText(self.name, ut_s)
            nameRect.topright = (rect[0]+210-8, HEIGHT-75+16)
            screen.blit(name, nameRect)

            desc, descRect = renderText(self.desc, ut_xs)
            descRect.topright = (rect[0]+210-8, HEIGHT-20)
            screen.blit(desc, descRect)

            screen.blit(self.icon, (rect[0]+16, HEIGHT-75+18))


    def draw(self, rect):
        if self.got == True:
            tempicon = self.icon
        elif self.got == "no":
            tempicon = ach_locked
        rect, tempicon, check = buttonCheck(rect, tempicon, False)
        if check:
            if self.hidden and self.got == "no":
                tempname = "???"
                tempdesc = "???"
            else:
                tempname = self.name
                tempdesc = self.desc
            name, nameRect = renderText(tempname, ut_s)
            nameRect.center = (rect[0]+rect[2]/2, rect[1]+rect[3]/2+rect[3])
            screen.blit(name, nameRect)

            desc, descRect = renderText(tempdesc, ut_xs)
            descRect.center = (nameRect.center[0], nameRect.center[1]+20)
            screen.blit(desc, descRect)
        screen.blit(tempicon, rect)


ach_realistic_check = achievement("assets/achs/ach_realistic.png", "Realistic Fishing", "Catch a fish without moving", False)
ach_scared_check = achievement("assets/achs/ach_scared.png", "Fish Fear Me", "Scare 5 fish off the screen", False)
#ach_outrun_check = achievement("assets/achs/ach_outrun.png", "You Can't Run", "Outrun a fish and catch it", False)
ach_click_check = achievement("assets/achs/ach_click.png", "Not How You Do It", "Click a fish", True)
ach_notscared_check = achievement("assets/achs/ach_notscared.png", "Fish Don't Fear Me", "Max out the better lure upgrade", False)
showingAch = ""
load("achs")
#upgrades
reeltimeupgrade = shopItem("Reel time upgrade", "Decrease the time to reel in fish", "assets/upgrade/reelupgrade.png", 35, 15, -5, 10)
hookupgrade = shopItem("Hook upgrade", "Increase how much fish you can hold", "assets/upgrade/hookupgrade.png", 40, 25, 3, 50)
spawncapupgrade = shopItem("Max fish upgrade", "Increase how much fish spawn at a time", "assets/upgrade/maxfishupgrade.png", 30, 20, 1, 20)
scaredrangeupgrade = shopItem("Better lure", "Decrease the area where fish get scared", "assets/upgrade/scaredrangeupgrade.png", 55, 5, -4, 16)
catchtimeupgrade = shopItem("Hook glue", "Increase time that fish stay on hook", "assets/upgrade/catchtimeupgrade.png", 50, 25, 20, 200)
fishrarityupgrade = shopItem("Luck", "Increase fish rarity", "assets/upgrade/fishrarityupgrade.png", 30, 20, 2, 20)
upgradeList.remove(fishrarityupgrade)
load("bought")
#buttons
startbutton = button("single", "assets/button/fishbutton.png")
coopbutton = button("coop", "assets/button/coopbutton.png")
shopbutton = button("shop", "assets/button/shopbutton.png")
settingsbutton = button("settings", "assets/button/settingsbutton.png")
exitbutton = button("exit", "assets/button/exitbutton.png")
sellbutton = button("sell", "assets/button/sellfishbutton.png")
achbutton = button("achs", "assets/button/achbutton.png")

homebutton = button("title", "assets/button/homebutton.png")
homebutton_up = button("title", "assets/button/homebutton-up.png")
homebutton_right = button("fishing", "assets/button/homebutton-right.png")
homebutton_down = button("title", "assets/button/homebutton-down.png")

minute, hour = 0, 1

#functions
def checkSunset():

    global sunsetCheck, sunriseCheck, nightCheck, hour, minute, fastSun, theme, sunLerp

    if fastSun:
        minute += 1
        if minute > 60:
            minute = 1
            hour += 1
        if hour > 23:
            hour = 0

    else:
        now = datetime.datetime.now()

        hour = int(now.strftime("%H"))
        minute = int(now.strftime("%m"))

    if theme == 3 or theme == 4:
        hour = 23
        minute = 0
    if theme == 2:
        hour = 5
        minute = 30
    if theme == 1:
        hour = 12
        minute = 0

    if 0 <= hour <= 11:
        sunLerp = 1-(hour/11)-(minute/60)/11
    elif 12 <= hour <= 14:
        sunLerp = 0
    elif 15 <= hour <= 23:
        sunLerp = ((hour-15)/11)+(minute/60)/11

    sunsetCheck = 19 <= hour <= 23
    sunriseCheck = 0 <= hour <= 7
    nightCheck = 22 <= hour <= 23 or 0 <= hour <= 3

def checkSprites():
    global sunsetCheck, sunriseCheck, nightCheck, cloudsImage2, cloudsImage, fisherImage_normal, fisherImage_pull, fisherImage, dockImage, dockImage2, dockImageFull, skyColor, waterImage, waterImage2, sunImage, bobberImage, titleImage, skin_current

    cloudsImage2 = cloudsImage2_noon
    cloudsImage = cloudsImage_noon
    fisherImage_normal = skin_current[0]
    fisherImage_pull = skin_current[1]
    dockImage = dockImage_noon
    dockImageFull = dockImageFull_noon
    skyColor = skyColor_noon
    waterImage = waterImage_noon
    sunImage = sunImage_noon
    bobberImage = bobberImage_noon
    titleImage = titleImage_noon

    if sunsetCheck or sunriseCheck:
        cloudsImage2 = cloudsImage2_sunset
        cloudsImage = cloudsImage_sunset
        fisherImage_normal = skin_current[2]
        fisherImage_pull = skin_current[3]
        dockImage = dockImage_sunset
        dockImageFull = dockImageFull_sunset
        skyColor = skyColor_sunset
        waterImage = waterImage_sunset
        sunImage = sunImage_sunset
        bobberImage = bobberImage_sunset
        titleImage = titleImage_sunset
    
    if nightCheck:
        cloudsImage2 = cloudsImage2_night
        cloudsImage = cloudsImage_night
        fisherImage_normal = skin_current[4]
        fisherImage_pull = skin_current[5]
        dockImage = dockImage_night
        dockImageFull = dockImageFull_night
        skyColor = skyColor_night
        waterImage = waterImage_night
        sunImage = sunImage_night
        bobberImage = bobberImage_night
        titleImage = titleImage_night

    dockImage2 = pygame.transform.flip(dockImage, True, False)
    waterImage2 = waterImage
    fisherImage = fisherImage_normal

def checkMusic():
    global sunsetCheck, sunriseCheck, mus_fishing

    if sunsetCheck or sunriseCheck:
        mus_fishing = mus_hotel2
    else:
        mus_fishing = mus_paradise

checkSunset()
checkMusic()

setVolume(volume)

if sunsetCheck or sunriseCheck:
    mus_menu.play(loops=-1)

#Thank you to my friend for teaching me how to ease
def ease(t):
    return 1 - ((1 - t) ** 9)

prevMin = minute
if 0 <= hour <= 11:
    sunLerp = 1-(hour/11)-(minute/60)/11
elif 12 <= hour <= 14:
    sunLerp = 0
elif 15 <= hour <= 23:
    sunLerp = ((hour-14)/11)+(minute/60)/11

def drawbg():
    global cloudOffset, cloudOffset2, waterOffset, startTransitionY, skyColor, fishes, bobberPos, sunsetCheck, fishingrect, linePos, sunMove, sunsetCheck, sunriseCheck, nightCheck, sunLerp, prevMin, minute, hour, lowGraphicsMode, wideMode

    checkSunset()

    checkMusic()

    checkSprites()

    screen.fill(skyColor)

    if nightCheck:
        screen.blit(stars, (0,0+startTransitionY/10))

    if minute != prevMin:
        if 0 <= hour <= 11:
            sunLerp -= 1/660
        if 14 <= hour <= 23:
            sunLerp += 1/660

        prevMin = minute

        if sunLerp < 0:
            sunLerp = 0
        if sunLerp > 1:
            sunLerp = 1

    sunMove = pygame.math.lerp(-250, 250, sunLerp)

    screen.blit(sunImage, (320,startTransitionY+sunMove))

    if lowGraphicsMode == False:
        screen.blit(cloudsImage2, (cloudOffset2,15+startTransitionY/4))

        cloudOffset2 += 0.25
        if cloudOffset2 > 0:
            cloudOffset2 = -680

    screen.blit(cloudsImage, (cloudOffset, -40+2*startTransitionY/5))

    cloudOffset += 0.5
    if cloudOffset > 0:
        cloudOffset = -730

    screen.blit(waterImage, (-100-70*math.sin(waterOffset),startTransitionY))

    if lowGraphicsMode == False:
        screen.blit(waterImage2, (-100+100*math.sin(waterOffset),startTransitionY*3))

    if sunsetCheck or sunriseCheck:
        waterOffset += 0.005
    else:
        waterOffset += 0.01

    for i in fishes:
        i.update()

def drawTitle():
    global version
    screen.blit(titleImage, (100+700-startTransitionX*7, 50-700+startTransitionY*7))
    startbutton.update((WIDTH/2 - 50+640-startTransitionX*6.4, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40))
    coopbutton.update((WIDTH/2 - 50+640-startTransitionX*6.4, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40))
    settingsbutton.update((WIDTH/2 - 50+640-startTransitionX*6.4, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40))
    exitbutton.update((WIDTH/2 - 50+640-startTransitionX*6.4, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40))
    achbutton.update((WIDTH-42+640-startTransitionX*6.4, HEIGHT-42 - 600 +startTransitionY*6, 32, 32))
    text, rect = renderText(f'v{version}', ut_xs)
    rect.bottomleft = (10, -600+startTransitionY*6+HEIGHT-5)
    screen.blit(text, rect)

def drawShop():
    global maxFishes, fishSpawnCap, reelTime, fishScaredRange, catchTimer, fishesHeld, balance, fishRarity
    screen.blit(dockImageFull, (-startTransitionX*6.4, startTransitionY*6-100))
    maxFishes = hookupgrade.update(maxFishes, (WIDTH/4 - 16-startTransitionX*6.4, HEIGHT/4, 32, 32))
    fishSpawnCap = spawncapupgrade.update(fishSpawnCap, (2*WIDTH/4 - 16-startTransitionX*6.4, HEIGHT/4, 32, 32))
    reelTime = reeltimeupgrade.update(reelTime, (3*WIDTH/4 - 16-startTransitionX*6.4, HEIGHT/4, 32, 32))
    fishScaredRange = scaredrangeupgrade.update(fishScaredRange, (WIDTH/4 - 16-startTransitionX*6.4, 2*HEIGHT/4, 32, 32))
    catchTimer = catchtimeupgrade.update(catchTimer, (2*WIDTH/4 - 16-startTransitionX*6.4, 2*HEIGHT/4, 32, 32))
    fishRarity = fishrarityupgrade.update(fishRarity, (3*WIDTH/4 - 16-startTransitionX*6.4, 2*HEIGHT/4, 32, 32))
    homebutton_right.update((30-startTransitionX*6.4, 20, 100, 40))
    sellbutton.update((30-startTransitionX*6.4, HEIGHT - 60, 100, 40))

    fishCounter, fishCounterRect = renderText(f'Fish: {len(fishesHeld)}', ut)
    fishCounterRect.topright = (WIDTH-20-startTransitionX*6.4, 20)
    screen.blit(fishCounter, fishCounterRect)

    balanceCounter, balanceCounterRect = renderText(f'Balance: ${balance}', ut)
    balanceCounterRect.topright = (WIDTH-20-startTransitionX*6.4, 60)
    screen.blit(balanceCounter, balanceCounterRect)

def drawFishing():
    global wideMode, fisherImage_wide, fishcount, fishCaughtArray, maxFishes, bobbers, area, coopUpgradeList, coopShop, fishRarity, upgradeList, fishReq, coopLevel, coopMaxFishes, prevRandUpgrade, randUpgrade, coopFishCount
    screen.blit(dockImage, (640-startTransitionX*6.4, startTransitionY*6-100))
    screen.blit(dockImage2, (WIDTH - 158+640-startTransitionX*6.4, startTransitionY*6-100))

    for bobber in range(len(bobbers)):
        if (not(coop) and bobber == 0) or coop:

            if not(coop):
                tempFishCount = fishCount
                tempMaxFishes = maxFishes
                fishCounter, fishCounterRect = renderText(f'Total Fish Caught: {tempFishCount}', ut)
                fishCounterRect.topright = (WIDTH - 20+640-startTransitionX*6.4, 20 + startTransitionY*6)

                shopbutton.update((20+120+640-startTransitionX*6.4, 20+startTransitionY*6, 100, 40))

                fishCounter2, fishCounter2Rect = renderText(f'Fish Caught: {len(fishesHeld2)}', ut)
                fishCounter2Rect.topright = (WIDTH - 20+640-startTransitionX*6.4, 20 + 40 + startTransitionY*6)
                screen.blit(fishCounter2, fishCounter2Rect)
            else:
                tempFishCount = bobbers[bobber].fishCount
                tempMaxFishes = bobbers[bobber].upgrades[1][0]
                fishCounter, fishCounterRect = renderText(f"P{bobber+1}'s Fish: {tempFishCount}", ut)
                fishCounterRect.bottomleft = (20+640-startTransitionX*6.4, HEIGHT - 15 -20*bobber + startTransitionY*6)

                if bobber == 0:
                    text, rect = renderText(f'Level {coopLevel}: {coopFishCount}/{fishReq}$', ut)
                    rect.midbottom = (WIDTH/2+640-startTransitionX*6.4, HEIGHT-20+startTransitionY*6)
                    screen.blit(text, rect)
            
                if coopFishCount >= fishReq and area == "fishing":
                    if not coopShop:
                        coopShop = True
                        fishRarity += 1
                        coopLevel += 1
                        fishReq += 5*(fishReq/5)
                        fishReq = int(fishReq)
                        coopUpgradeList = []
                        coopFishCount = 0
                        if len(upgradeList) <= 0:
                            coopShop = False
                        if len(upgradeList) == 1:
                            tempRange = 1
                        if len(upgradeList) >= 2:
                            tempRange = 2
                        for upgrade in range(tempRange):
                            while prevRandUpgrade == randUpgrade:
                                randUpgrade = random.randint(0, len(upgradeList)-1)
                            prevRandUpgrade = randUpgrade
                            upgrade = upgradeList[randUpgrade]
                            coopUpgradeList.append([upgrade, randUpgrade])

                    for i in bobbers:
                        i.moving = False
                        i.cast = False
                        i.reel = False
                        i.fishCaughtArray = []
                        i.linePos = (i.linePos2[0], i.linePos2[1])
                        if not(i.fisherFlip):
                            i.pos = (i.fisherPos[0]-240+97-7-10, -124)
                        else:
                            i.pos = (i.fisherPos[0]-240-97+7+10, -124)

            screen.blit(fishCounter, fishCounterRect)

            fishesHelder, fishesHelderRect = renderText(f'P{bobber+1} Fish Held: {len(bobbers[bobber].fishCaughtArray)}/{tempMaxFishes}', ut)
            fishesHelderRect.bottomright = (WIDTH - 20+640-startTransitionX*6.4, HEIGHT - 15 -20*bobber + startTransitionY*6)
            screen.blit(fishesHelder, fishesHelderRect)

    if not coopShop:
        homebutton_up.update((20+640-startTransitionX*6.4, 20+startTransitionY*6, 100, 40))

    cameraStopped = False

    match startTransitionY:
        case 0 | 100 | 200:
            match startTransitionX:
                case 0 | 100 | 200:
                    cameraStopped = True


    for i in bobbers:

        if not cameraStopped:
            i.castAnimCounter = 0
            i.cast = True
            exponent = 10
            if not(i.fisherFlip):
                i.pos = (i.fisherPos[0]-240+97-7-10, -124)
            else:
                i.pos = (i.fisherPos[0]-240-97+7+10, -124)

        if (not(coop) and i == bobbers[0]) or coop:

            if i.reel and cameraStopped and area == "fishing":
                i.reelAnim()

            moving = False
            if i.cast and cameraStopped and area == "fishing":
                i.castAnim()

            if not(i.cast) and not(i.reel) and cameraStopped and not(coopShop):
                i.move()
            i.update()

    if coopShop:
        screen.blit(cover)
        for upgrades in range(len(coopUpgradeList)):
            upgradeType = coopUpgradeList[upgrades][1]
            if upgradeType == 2:
                coopMaxFishes, useless, coopBuy = coopUpgradeList[upgrades][0].update(coopMaxFishes, ((upgrades+1)*WIDTH/3, HEIGHT/2-16, 32, 32))
            else:
                bobbers[0].upgrades[upgradeType][0], bobbers[1].upgrades[upgradeType][0], coopBuy = coopUpgradeList[upgrades][0].update(bobbers[0].upgrades[upgradeType][0], ((upgrades+1)*WIDTH/3, HEIGHT/2-16, 32, 32))
            if coopBuy:
                coopShop = False
                if bobbers[0].upgrades[upgradeType][0] == coopUpgradeList[upgrades][0].cap:
                    upgradeList.remove[upgrades]
                for k in bobbers:
                    k.cast = True

def drawToggleSetting(text, coords, var, var_toggle):
    settings, settingsRect = renderText(text, ut)
    settingsRect.topright = coords
    screen.blit(settings, settingsRect)

    var = var_toggle.update(var, (coords[0]+10, coords[1]-2, 32, 32))
    
    return var

def drawSettings():
    global startTransitionX, fullscreen, wideMode, lowGraphicsMode, fishSFX, fastSun, theme, volume
    tempOffsetX = 1280-startTransitionX*6.4

    settings, settingsRect = renderText("Main Settings", ut_b)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 50)
    screen.blit(settings, settingsRect)

    fullscreen = drawToggleSetting("Fullscreen:", (WIDTH+tempOffsetX-82, 100), fullscreen, fullscreen_toggle)
    lowGraphicsMode = drawToggleSetting("Low Graphics Mode:", (WIDTH+tempOffsetX-82, 140), lowGraphicsMode, lowGraphicsMode_toggle)

    settings, settingsRect = renderText(f'Volume: {int(volume*100)}', ut)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 180)
    screen.blit(settings, settingsRect)

    volume = volumeSlider.update(volume, (WIDTH+tempOffsetX-82-100-7, 210))/100

    setVolume(volume)

    if theme == 0:
        themeText = "None"
    elif theme == 1:
        themeText = "Noon"
    elif theme == 2:
        themeText = "Sunset"
    else:
        themeText = "Night"

    settings, settingsRect = renderText(f'Theme: {themeText}', ut)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 250)
    screen.blit(settings, settingsRect) 

    theme = int(themeSlider.update(theme, (WIDTH+tempOffsetX-82-100-7, 280)))


    settings, settingsRect = renderText("silly settings", ut_b)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 300)
    screen.blit(settings, settingsRect)

    wideMode = drawToggleSetting("W I D E M O D E :", (WIDTH+tempOffsetX-82, 350), wideMode, wideMode_toggle)
    fishSFX = drawToggleSetting("fish spawn sfx:", (WIDTH+tempOffsetX-82, 390), fishSFX, fishSFX_toggle)
    fastSun = drawToggleSetting("weird sun:", (WIDTH+tempOffsetX-82, 430), fastSun, fastSun_toggle)

    if wideMode:
        fisherImage_normal = fisherImage_wide

    homebutton.update((20+tempOffsetX, 20, 100, 40))

def save():
    global balance, reelTime, maxFishes, fishSpawnCap, fishScaredRange, catchTimer, fishRarity, fishCount, fishesHeld, reeltimeupgrade, fullscreen, lowGraphicsMode, volume, theme, wideMode, fishSFX, fastSun, achs
    achs_temp = []
    with open('.saves/save.philooxy', 'w') as f:
        for i in achs:
            if i.got == "no":
                i.got = 0
            achs_temp.append(int(i.got))
        saveLines = [f'{fishesHeld}\n', f'{balance}\n', f'{fishCount}\n', f'{achs_temp}\n']
        f.writelines(saveLines)

    with open('.saves/upgrades.philooxy', 'w') as f:
        reelTime = [reelTime, reeltimeupgrade.bought]
        maxFishes = [maxFishes, hookupgrade.bought]
        fishSpawnCap = [fishSpawnCap, spawncapupgrade.bought]
        fishScaredRange = [fishScaredRange, scaredrangeupgrade.bought]
        catchTimer = [catchTimer, catchtimeupgrade.bought]
        fishRarity = [fishRarity, fishrarityupgrade.bought]
        upgradeLines = [f'{reelTime}\n', f'{maxFishes}\n', f'{fishSpawnCap}\n', f'{fishScaredRange}\n', f'{catchTimer}\n', f'{fishRarity}\n']
        f.writelines(upgradeLines)

    with open('settings.philooxy', 'w') as f:
        lines = [f'{int(fullscreen)}\n', f'{int(lowGraphicsMode)}\n', f'{float(volume)}\n', f'\n', f'{int(wideMode)}\n', f'{int(fishSFX)}\n', f'{int(fastSun)}\n']
        f.writelines(lines)

def renderText(text, font):
    text = font.render(text, False, (0,0,0))
    rect = text.get_rect()

    return text,rect

#achievement-related variables
scaredCounter = 0
outranFish = False
clickFish = False
realisticFishing = False

def updateAchs():
    global scaredCounter, outranFish, clickFish, realisticFishing, fishScaredRange
    ach_realistic_check.update(realisticFishing)
    ach_scared_check.update(scaredCounter >= 5)
    #ach_outrun_check.update(outranFish) #removed because it was buggy
    ach_click_check.update(clickFish)
    ach_notscared_check.update(fishScaredRange == 16)

def drawAchs():
    homebutton_down.update((WIDTH-120-640+startTransitionX*6.4, HEIGHT-60-1200+startTransitionY*6, 100, 40))
    global achs
    for i in range(len(achs)):
        achs[i].draw( pygame.Rect((1+i%4)*(WIDTH/5)-640+startTransitionX*6.4, (1+int(i/4))*(HEIGHT/5)+(-1200+startTransitionY*6), 32, 32 ) )

def transition(transitionVar, lerpMin, lerpMax, easing, a):
    global lowGraphicsMode
    finishedTransition = False

    if a:
        check3 = transitionVar < lerpMax
    else:
        check3 = lerpMax < transitionVar

    if check3:
        transitionVar = pygame.math.lerp(lerpMin, lerpMax, ease(easing))
        easing += 0.01

        finishedTransition = False

        if a:
            check2 = lerpMax-0.3 <= transitionVar < lerpMax
        else:
            check2 = (lerpMax <= transitionVar < lerpMax+0.3)
        if check2:
            transitionVar = lerpMax

    elif transitionVar == float(lerpMax):
        easing = 0
        finishedTransition = True

    if lowGraphicsMode == True:
        transitionVar = lerpMax


    return transitionVar, easing, finishedTransition

startAnim = True
startTransitionX = 100

class bobber():
    global bobbers, fishScaredRange
    def __init__(self, controls, fisherPos, fisherFlip, linePos, skin):
        self.pos = (0,0)
        self.tempPos = self.pos
        bobbers.append(self)
        self.reel = False
        self.cast = True
        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + 16 + self.pos[1], 32, 32)
        self.scaredRect = pygame.Rect(WIDTH/2 - fishScaredRange + self.pos[0], HEIGHT/2 - fishScaredRange + 16 + self.pos[1], 2*fishScaredRange, 2*fishScaredRange)
        self.fishCaughtArray = []
        self.moving = False
        self.castAnimCounter = 0
        self.reelAnimCounter = 0
        self.fisher_normal = fisherImage_normal
        self.fisher_pull = fisherImage_pull
        self.controls = controls
        self.fisherFlip = fisherFlip
        self.fisherPos = fisherPos
        self.linePos = linePos
        self.linePos2 = self.linePos
        self.exponent = 0
        self.fishCaughtArray = []
        self.moving2 = False
        self.skin = skin
        self.fishCount = 0
        self.upgrades = [[60, 0], [3, 0], [0, 0], [48, 0], [70, 0]]

    def update(self):
        global fishes, maxFishes, outranFish, moving, wideMode, sunsetCheck, sunriseCheck, nightCheck
        for i in fishes:
            if not(coop):
                check = len(self.fishCaughtArray) < maxFishes
            else:
                check = len(self.fishCaughtArray) < self.upgrades[1][0]
            if i.rect.colliderect(self.rect) and not(i.caught) and check:
                if not(-30 < i.catchTimer <= 0) and not(i.caught):
                    i.caught = True
                    self.fishCaughtArray.append(i)
                    outranFish = True
                    i.bobber = self
                    if not(coop):
                        check = catchTimer < catchtimeupgrade.cap
                    else:
                        check = self.upgrades[4][0] < catchtimeupgrade.cap
                    if check:
                        i.catchTimer = catchTimer + i.catchTime

            if i.rect.colliderect(self.scaredRect) and self.moving:
                i.scared = 30
                if not(i.caught):
                    i.bobber = self

        if len(self.fishCaughtArray) > 0 and self.pos[1] == 0:
            if not(self.fisherFlip):
                if self.fisherPos[0]+160-WIDTH/2-40 <= self.pos[0] <= self.fisherPos[0]+160+110-WIDTH/2:
                    self.reel = True
            elif self.fisherFlip:
                if self.fisherPos[0]-110-WIDTH/2 <= self.pos[0] <= self.fisherPos[0]-WIDTH/2+40:
                    self.reel = True

        bobberPos = (WIDTH/2+self.pos[0]-16+640-startTransitionX*6.4, HEIGHT/2+self.pos[1]-16+startTransitionY*6)

        fisherImage_normal = self.skin[0]
        fisherImage_pull = self.skin[1]

        if sunsetCheck or sunriseCheck:
            fisherImage_normal = self.skin[2]
            fisherImage_pull = self.skin[3]
        
        if nightCheck:
            fisherImage_normal = self.skin[4]
            fisherImage_pull = self.skin[5]


        fisherImage = fisherImage_normal
        if self.reel and not(wideMode):
            fisherImage = fisherImage_pull
        if wideMode:
            fisherImage = fisherImage_wide
        if self.fisherFlip:
            fisherImage = pygame.transform.flip(fisherImage, True, False)
        if not(wideMode):
            screen.blit(fisherImage, (self.fisherPos[0]+640-startTransitionX*6.4, startTransitionY*6+self.fisherPos[1]-100))
        else:
            screen.blit(fisherImage, (-100+640-startTransitionX*6.4, startTransitionY*6+self.fisherPos[1]-100))

        self.image = bobberImage

        if not(coop):
            tempScaredRange = fishScaredRange
        else:
            tempScaredRange = self.upgrades[3][0]

        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2-5 + self.pos[1], 32, 32)
        self.scaredRect = pygame.Rect(WIDTH/2 - tempScaredRange + self.pos[0], HEIGHT/2 - tempScaredRange + self.pos[1]+11, 2*tempScaredRange, 2*tempScaredRange)

        pygame.draw.line(screen, (0,0,0), (self.linePos[0]+640-startTransitionX*6.4, self.linePos[1]+startTransitionY*6), (bobberPos[0]+15, bobberPos[1]), width=2)
        screen.blit(self.image, bobberPos)

    def move(self):
        global moving, bobberSpeed, moving2, realisticFishing
        pressed_keys = pygame.key.get_pressed()

        self.moving = False

        if pressed_keys[self.controls[2]] and self.pos[0] > -200:
            self.moving = True
            self.pos = (self.pos[0] - 1*bobberSpeed, self.pos[1])
        if pressed_keys[self.controls[3]] and self.pos[0] < 200:
            self.moving = True
            self.pos = (self.pos[0] + 1*bobberSpeed, self.pos[1])
        if pressed_keys[self.controls[0]] and self.pos[1] > 0:
            self.moving = True
            self.pos = (self.pos[0], self.pos[1] - 1*bobberSpeed)
        if pressed_keys[self.controls[1]] and self.pos[1] < 200:
            self.moving = True
            self.pos = (self.pos[0], self.pos[1] + 1*bobberSpeed)

        if pressed_keys[self.controls[2]] and pressed_keys[self.controls[3]]:
            self.moving = False
        if pressed_keys[self.controls[0]] and pressed_keys[self.controls[1]]:
            self.moving = False

        if self.moving and not(self.cast):
            self.moving2 = True

        self.tempPos = self.pos

    def castAnim(self):
        global moving, moving2

        self.moving = True
        if self.castAnimCounter < 1:
            self.exponent = 10
        if self.castAnimCounter <= 97:
            if not(self.fisherFlip):
                self.pos = (self.pos[0] + 1, self.pos[1])
            else:
                self.pos = (self.pos[0] - 1, self.pos[1])
            self.exponent += 0.05
            self.pos = (self.pos[0], 100*math.sin(self.exponent)-70)
            self.castAnimCounter += 1
        else:
            self.pos = (self.pos[0], 0)
            self.cast = False
            self.moving2 = False
            self.castAnimCounter = 0

    def reelAnim(self):
        global reelTime, fishCaughtArray, xmove_temp, ymove_temp, fishCount, fishes, realisticFishing, coopFishCount
        if not(coop):
            tempReelTime = reelTime*(len(self.fishCaughtArray))/2
        else:
            tempReelTime = self.upgrades[0][0]*(len(self.fishCaughtArray))/2
        if not(self.fisherFlip):
            self.linePos = (self.linePos2[0]-10, self.linePos2[1]-10)
        else:
            self.linePos = (self.linePos2[0]+10, self.linePos2[1]-10)
        if self.reelAnimCounter == 0:
            xmove_temp = ((WIDTH/2-150-self.linePos[0]))/(tempReelTime-1)
            ymove_temp = ((HEIGHT/2-self.linePos[1]))/(tempReelTime-1)
            self.reelAnimCounter = 1
            if not(self.moving2):
                realisticFishing = True
        if self.reelAnimCounter < tempReelTime+1:
            self.pos = (pygame.math.lerp(self.tempPos[0], self.linePos[0]-WIDTH/2, self.reelAnimCounter/tempReelTime), pygame.math.lerp(self.tempPos[1], self.linePos[1]-HEIGHT/2+22, self.reelAnimCounter/tempReelTime))
            self.reelAnimCounter += 1
        if self.reelAnimCounter >= tempReelTime+1:
            self.castAnimCounter = 0
            self.reelAnimCounter = 0

            while len(self.fishCaughtArray) > 0:
                for i in fishes:
                    if i.caught == True and i in self.fishCaughtArray:
                        fishes.remove(i)
                        self.fishCaughtArray.remove(i)
                        i.caught == False
                        if not(coop):
                            fishCount += 1
                            fishesHeld.append(i.type)
                            fishesHeld2.append(i)
                        else:
                            if i.type == 1:
                                coopFishCount += 5
                            elif i.type == 2:
                                coopFishCount += 10
                            elif i.type == 3:
                                coopFishCount += 20
            self.linePos = self.linePos2
            self.reel = False
            self.cast = True
            self.reelAnimCounter = 0
            self.moving2 = False

bobber1 = bobber([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT], (0,0), False, (150, 101), skin_soday)
bobber2 = bobber([pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d], (WIDTH-150,0), True, (WIDTH-140, 101), skin_evilsoday)

def main():
    global area, bobberFallAnim, fishingMusic, reelAnim, menuMusic, startTransitionY, startTransitionX, offsetX, offsetY, bobberSpeed, bobberFall, bobberReel, exponent, waterOffset, fishCount, fishingrect, fishingrect2, moving, fishes, cloudOffset, cloudOffset2, reelTime, linePos, fishSpawnCap, fishCaughtArray, fishesHeld, balance, fisherImage, fishSFX, bobberPos, easingY, easingX, run, sunsetCheck, sunriseCheck, nightCheck, lowGraphicsMode, wideMode, fullscreen, startAnim, doRPC, moving2, coop, fishReq, coopShop
    drawbg()

    if area == "exit":
        run = False
        save()

    if area == "sell":
        while len(fishesHeld) > 0:
            for i in fishesHeld:
                if i == 1:
                    balance += 5
                elif i == 2:
                    balance += 10
                elif i == 3:
                    balance += 20
                fishesHeld.remove(i)
        area = "shop"

    if area == "coop":
        coop = True
        area = "fishing"

    if area == "single":
        coop = False
        area = "fishing"


    if area == "title":

        if menuMusic == False:
            while len(fishes) > 0:
                for i in fishes:
                    fishes.remove(i)

            menuMusic = True
            if not(sunsetCheck) and not(sunriseCheck):
                pygame.mixer.stop()
                mus_menu.play(loops=-1)
            bobberFallAnim = True
            reelAnim = False
            bobberFall = 0
            bobberReel = 0
            offsetX = 0
            offsetY = 0
            fishCaughtArray = []
            fishingMusic = False
            if sunsetCheck or sunriseCheck:
                fishingMusic = True

            if doRPC:
                RPC.update(
                    state="In Menus",
                    details=f'Balance: ${balance}',
                    name="Philooxy's Phishing",
                )

        coopShop = False
        fishReqCounter = 0

        for i in bobbers:
            i.fishCaughtArray = []

        drawTitle()

        startTransitionY, easingY, finishedTransition = transition(startTransitionY, 0, 100, easingY, True)
        if not(finishedTransition):
            if not(startAnim):
                drawFishing()
        else:
            startAnim = False

        startTransitionY, easingY, finishedTransition = transition(startTransitionY, 200, 100, easingY, False)
        if not(finishedTransition):
           drawAchs()

        startTransitionX, easingX, finishedTransition = transition(startTransitionX, 0, 100, easingX, True)
        if not(finishedTransition):
            drawShop()

        startTransitionX, easingX, finishedTransition = transition(startTransitionX, 200, 100, easingX, False)
        if not(finishedTransition):
            drawSettings()

    if area == "fishing":

        menuMusic = False

        if fishingMusic == False:
            fishingMusic = True
            if not(sunsetCheck) and not(sunriseCheck):
                pygame.mixer.stop()
                mus_fishing.play(loops=-1)
                menuMusic = False
            if sunsetCheck or sunriseCheck:
                menuMusic = True

            if doRPC:
                RPC.update(
                    state="Fishing",
                    details=f'Total Fish Caught: {fishCount}',
                    name="Philooxy's Phishing",
                )

        if lowGraphicsMode == True:
            startTransitionY = 0
            startTransitionX = 100
    
        startTransitionX, easingX, finishedTransition = transition(startTransitionX, 0, 100, easingX, True)
        if not(finishedTransition):
            drawShop()

        startTransitionY, easingY, finishedTransition = transition(startTransitionY, 100, 0, easingY, False)
        if not(finishedTransition):
            drawTitle()

        else:
            if not coop:
                tempSpawnCap = fishSpawnCap
            else:
                tempSpawnCap = coopMaxFishes
            if len(fishes) < tempSpawnCap:
                r = random.randint(1, 100)
                if r == 33:
                    if fishSFX == True:
                        ykwtm.play()
                    fish = fishy()

        drawFishing()

    if area == "shop":
      
        if lowGraphicsMode == True:
            startTransitionX = 0

        startTransitionX, easingX, finishedTransition = transition(startTransitionX, 100, 0, easingX, False)
        if not(finishedTransition):
            #drawTitle()
            drawFishing()
        
        drawShop()


    if area == "settings":

        drawSettings()

        startTransitionX, easingX, finishedTransition = transition(startTransitionX, 100, 200, easingX, True)
        if not(finishedTransition):
            drawTitle()

    if area == "achs":

        drawAchs()

        startTransitionY, easingY, finishedTransition = transition(startTransitionY, 100, 200, easingY, True)
        if not(finishedTransition):
            drawTitle()


def update():
    pressed_keys = pygame.key.get_pressed()

    clock.tick(60)

    if fullscreen != pygame.display.is_fullscreen():
        pygame.display.toggle_fullscreen()

    pygame.display.flip()

run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            save()

    pygame.mixer.music.set_volume(volume)

    screen.fill((255,255,255))

    hovering = False

    main()

    updateAchs()

    checkClick(True)

    if hovering == False:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    update()
