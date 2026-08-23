import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, sys, random, math, time, datetime, json
from setupvars import *

pygame.init()
pygame.font.init()
pygame.mixer.init()

def load(data):
    global fishesHeld, balance, reelTime, maxFishes, fishSpawnCap, fishScaredRange, catchTimer, fishCount
    with open('.saves/save.philooxy', 'r') as f:
        lines = f.readlines()
        if data == "var":
            fishesHeld = json.loads(lines[0])
            balance = int(lines[1])
            reelTime = json.loads(lines[2])[0]
            maxFishes = json.loads(lines[3])[0]
            fishSpawnCap = json.loads(lines[4])[0]
            fishScaredRange = json.loads(lines[5])[0]
            catchTimer = json.loads(lines[6])[0]
            fishCount = int(lines[7])
        elif data == "bought":
            reeltimeupgrade.shopItem.bought = json.loads(lines[2])[1]
            hookupgrade.shopItem.bought = json.loads(lines[3])[1]
            spawncapupgrade.shopItem.bought = json.loads(lines[4])[1]
            scaredrangeupgrade.shopItem.bought = json.loads(lines[5])[1]
            catchtimeupgrade.shopItem.bought = json.loads(lines[6])[1]

load("var")

#i have no idea what to name this
def buttonCheck(rect, image):
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
    if check:
        image = pygame.transform.scale(image, (rect[2]*1.2, rect[3]*1.2))
        rect = rect.inflate(rect[2]*0.2, rect[3]*0.2)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    return rect, image, check

def checkClick():
    global isClicking
    click = False
    if pygame.mouse.get_pressed()[0] == False and isClicking == True:
        isClicking = False
    if pygame.mouse.get_pressed()[0]:
        if isClicking == False:
            click = True
        isClicking = True
    return click

def updateButton(baseRect, image):
    update = False
    image = pygame.transform.scale(image, (baseRect[2], baseRect[3]))
    check = False

    rect, image, check = buttonCheck(baseRect, image)

    if check:
        click = checkClick()
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
        self.image_on = pygame.image.load("assets/toggle_on.png")
        self.image_off = pygame.image.load("assets/toggle_off.png")
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

class fishy():
    def __init__(self):
        global fishes, fishingrect, fishingrect2

        #print("You know what that means")

        self.pos = (random.randint(-200, 200), random.randint(20, 200))
        self.type = random.randint(1,5)
        if self.type == 3:
            self.type = 2
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

        self.imagepath = f'assets/fish{self.type}'
        self.image = pygame.image.load(f'{self.imagepath}_0.png')
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1], self.rect[2], self.rect[3])

        self.rotate = random.randint(0,4)*90

        fishes.append(self)

    def update(self):
        global moving, offsetX, offsetY, fishCount, bobberFallAnim, reelAnim, fishes, fishesHeld, maxFishes, fishCaughtArray, catchTimer

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


        if self.rect.colliderect(fishingrect2) and (moving == True or self.caught == True):
            self.scared = 30
        if self.scared > 0:
            self.speed = 3*self.speed2

            if self.caught == False:
                if self.pos[0] > offsetX:
                    self.dir = 1
                elif self.pos[0] < offsetX:
                    self.dir = 2

            self.scared -= 1

        if reelAnim == False:
            if -30 < self.catchTimer <= 0:
                self.caught = False

            if self.catchTimer == 0:
                fishCaughtArray.remove(self)
                self.pos = (self.pos[0], self.pos[1]+(16+-64*random.randint(0,1)))
                if self.pos[1] < 20:
                    self.pos = (self.pos[0], 20)

        if self.dir == 2:
            self.pos = (self.pos[0]-1*self.speed, self.pos[1])
        else:
            self.pos = (self.pos[0]+1*self.speed, self.pos[1])

        if self.rect.colliderect(fishingrect) and self.caught == False and len(fishCaughtArray) < maxFishes:
            if not(-30 < self.catchTimer <= 0) and catchTimer < catchtimeupgrade.cap:
                self.caught = True
                self.catchTimer = catchTimer + self.catchTime
                fishCaughtArray.append(self)

        if self.caught == True:
            self.pos = (offsetX, offsetY+24+11)
            if offsetY <= 0 and offsetX < -20 and bobberFallAnim == False:
                reelAnim = True

        if self.pos[0] > 320 or self.pos[0] < -320 or ((self.pos[1] > 200) and self.caught == False) or 0 < startTransitionY < 100:
            fishes.remove(self)

        self.rect[0], self.rect[1] = WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1]

        screen.blit(self.image, self.rect)

#basic upgrade item
class shopItem():
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
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

    def update(self, var, rect):
        global balance, hovering, startTransitionY, startTransitionX

        check = False
        click = False
        self.upgrade = False

        self.rect, self.image, check = buttonCheck(pygame.Rect(rect), self.image)

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

            click = checkClick()
            if click:
                if balance - self.cost >= 0:

                    if self.capCheck2:
                        self.bought += 1
                        self.upgrade = True
                        balance -= self.cost

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

                cost, costRect = renderText(f'Cost: ${self.cost}', ut_xs)
                costRect.center = (self.rect.center[0], self.rect.center[1] + self.rect[3]/2 + desc1Rect[3]/2 + 20 + 16)
                screen.blit(cost, costRect)

            else:
                desc2Text = f'MAX ({var})'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)

            desc2, desc2Rect = renderText(desc2Text, ut_xs)
            desc2Rect.center = (self.rect.center[0], self.rect.center[1] + self.rect[3]/2 + desc1Rect[3]/2 + 20 + 30)
            screen.blit(desc2, desc2Rect)

        name, nameRect = renderText(self.name, ut_s)
        nameRect.center = (self.rect.center[0], self.rect.bottom + 10)
        screen.blit(name, nameRect)

        screen.blit(self.image, self.rect)

        return self.upgrade

#upgrade types (i have no idea how to make this more efficient)

class hookUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global maxFishes
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(maxFishes, rect)
        if upgrade == True:
            maxFishes += self.increment
        if maxFishes >= self.cap:
            maxFishes = self.cap


class spawnCapUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        #shopItem.__init__(self, name, desc, image, rect, cost, increment, cap)
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global fishSpawnCap
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(fishSpawnCap, rect)
        if upgrade == True:
            fishSpawnCap += self.increment
        if fishSpawnCap >= self.cap:
            fishSpawnCap = self.cap


class reelTimeUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global reelTime
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(reelTime, rect)
        if upgrade == True:
            reelTime += self.increment
        if reelTime <= self.cap:
            reelTime = self.cap

class scaredRangeUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global fishScaredRange
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(fishScaredRange, rect)
        if upgrade == True:
            fishScaredRange += self.increment
        if fishScaredRange <= self.cap:
            fishScaredRange = self.cap

class catchTimeUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global catchTimer
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(catchTimer, rect)
        if upgrade == True:
            catchTimer += self.increment
        if catchTimer >= self.cap:
            catchTimer = self.cap

#upgrades
hookupgrade = hookUpgrade("Hook upgrade", "Increase how much fish you can hold", "assets/hookupgrade.png", (WIDTH/4 - 16, HEIGHT/4, 32, 32), 50, 25, 3, 50)
spawncapupgrade = spawnCapUpgrade("Max fish upgrade", "Increase how much fish spawn at a time", "assets/maxfishupgrade.png", (2*WIDTH/4 - 16, HEIGHT/4, 32, 32), 30, 20, 1, 20)
reeltimeupgrade = reelTimeUpgrade("Reel time upgrade", "Decrease the time to reel in fish", "assets/reelupgrade.png", (3*WIDTH/4 - 16, HEIGHT/4, 32, 32), 25, 15, -5, 10)
scaredrangeupgrade = scaredRangeUpgrade("Better lure", "Decrease the area where fish get scared", "assets/scaredrangeupgrade.png", (WIDTH/4 - 16, 2*HEIGHT/4, 32, 32), 55, 5, -4, 16)
catchtimeupgrade = catchTimeUpgrade("Hook glue", "Increase time that fish stay on hook", "assets/catchtimeupgrade.png", (2*WIDTH/4 - 16, 2*HEIGHT/4, 32, 32), 40, 20, 20, 200)
load("bought")
#buttons
startbutton = button("fishing", "assets/fishbutton.png")
shopbutton = button("shop", "assets/shopbutton.png")
settingsbutton = button("settings", "assets/settingsbutton.png")
exitbutton = button("exit", "assets/exitbutton.png")
sellbutton = button("sell", "assets/sellfishbutton.png")

homebutton = button("title", "assets/homebutton.png")
homebutton_up = button("title", "assets/homebutton-up.png")
homebutton_right = button("title", "assets/homebutton-right.png")

#functions
def checkSunset():

    global sunsetCheck, sunriseCheck, hour, minute, fastSun, theme

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

    if theme == 2:
        hour = 7
        minute = 30
    if theme == 1:
        hour = 12
        minute = 0
    sunsetCheck = 19 <= hour <= 23
    sunriseCheck = 0 <= hour <= 7

def checkSprites():
    global sunsetCheck, cloudsImage2, cloudsImage, fisherImage_normal, fisherImage_pull, fisherImage, dockImage, dockImage2, skyColor, waterImage, waterImage2, sunImage, bobberImage, titleImage

    if sunsetCheck or sunriseCheck:
        cloudsImage2 = cloudsImage2_sunset
        cloudsImage = cloudsImage_sunset
        fisherImage_normal = fisherImage_normal_sunset
        fisherImage_pull = fisherImage_pull_sunset
        dockImage = dockImage_sunset
        skyColor = skyColor_sunset
        waterImage = waterImage_sunset
        sunImage = sunImage_sunset
        bobberImage = bobberImage_sunset
        titleImage = titleImage_sunset
    else:
        cloudsImage2 = cloudsImage2_noon
        cloudsImage = cloudsImage_noon
        fisherImage_normal = fisherImage_normal_noon
        fisherImage_pull = fisherImage_pull_noon
        dockImage = dockImage_noon
        skyColor = skyColor_noon
        waterImage = waterImage_noon
        sunImage = sunImage_noon
        bobberImage = bobberImage_noon
        titleImage = titleImage_noon

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

if sunsetCheck or sunriseCheck:
    mus_menu.play(loops=-1)

#Thank you to my friend for teaching me how to ease
def ease(t):
    return 1 - ((1 - t) ** 9)

prevMin = minute
if 0 <= hour <= 11:
    sunLerp = 1-(hour/11)+(minute/60)/11
    print("a")
elif 12 <= hour <= 14:
    sunLerp = 0
    print("b")
elif 15 <= hour <= 23:
    sunLerp = ((hour-14)/11)+(minute/60)/11
    print("c")

def drawbg():
    global cloudOffset, cloudOffset2, waterOffset, startTransitionY, skyColor, fishes, bobberPos, sunsetCheck, fishingrect, linePos, sunMove, sunsetCheck, sunriseCheck, sunLerp, prevMin, minute, hour, lowGraphicsMode, wideMode

    checkSunset()

    checkMusic()

    checkSprites()

    screen.fill(skyColor)

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
    screen.blit(titleImage, (100+700-startTransitionX*7, 50-700+startTransitionY*7))
    startbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40))
    shopbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40))
    settingsbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40))
    exitbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40))

def drawShop():
    hookupgrade.update((WIDTH/4 - 16-startTransitionX*6, HEIGHT/4, 32, 32))
    spawncapupgrade.update((2*WIDTH/4 - 16-startTransitionX*6, HEIGHT/4, 32, 32))
    reeltimeupgrade.update((3*WIDTH/4 - 16-startTransitionX*6, HEIGHT/4, 32, 32))
    scaredrangeupgrade.update((WIDTH/4 - 16-startTransitionX*6, 2*HEIGHT/4, 32, 32))
    catchtimeupgrade.update((2*WIDTH/4 - 16-startTransitionX*6, 2*HEIGHT/4, 32, 32))
    homebutton_right.update((30-startTransitionX*6, 20, 100, 40))
    sellbutton.update((30-startTransitionX*6, HEIGHT - 60, 100, 40))

def drawFishing():
    global wideMode, fisherImage_wide
    screen.blit(dockImage, (-2, startTransitionY*6-100))
    screen.blit(dockImage2, (WIDTH - 158, startTransitionY*6-100))

    fisherImage = fisherImage_normal
    if reelAnim and not(wideMode):
        fisherImage = fisherImage_pull

    if wideMode:
        fisherImage = fisherImage_wide

    if not(wideMode):
        screen.blit(fisherImage, (0, startTransitionY*6-100))
    else:
        screen.blit(fisherImage, (-100, startTransitionY*6-100))

    bobberPos = (fishingrect[0], fishingrect[1]-11+startTransitionY*6)
    pygame.draw.line(screen, (0,0,0), linePos, (bobberPos[0]+15, bobberPos[1]), width=2)
    screen.blit(bobberImage, bobberPos)

    homebutton_up.update((20, 20+startTransitionY*6, 100, 40))

def drawSetting(text, coords, var, var_toggle):
    settings, settingsRect = renderText(text, ut)
    settingsRect.topright = coords
    screen.blit(settings, settingsRect)

    var = var_toggle.update(var, (coords[0]+10, coords[1]-2, 32, 32))
    
    return var

def drawSettings():
    global startTransitionX, fullscreen, wideMode, lowGraphicsMode, fishSFX, fastSun
    tempOffsetX = 1200-startTransitionX*6

    settings, settingsRect = renderText("Main Settings", ut_b)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 50)
    screen.blit(settings, settingsRect)

    fullscreen = drawSetting("Fullscreen:", (WIDTH+tempOffsetX-82, 100), fullscreen, fullscreen_toggle)

    lowGraphicsMode = drawSetting("Low Graphics Mode:", (WIDTH+tempOffsetX-82, 140), lowGraphicsMode, lowGraphicsMode_toggle)

    settings, settingsRect = renderText("silly settings", ut_b)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 300)
    screen.blit(settings, settingsRect)

    wideMode = drawSetting("W I D E M O D E :", (WIDTH+tempOffsetX-82, 350), wideMode, wideMode_toggle)

    fishSFX = drawSetting("fish spawn sfx:", (WIDTH+tempOffsetX-82, 390), fishSFX, fishSFX_toggle)

    fastSun = drawSetting("weird sun:", (WIDTH+tempOffsetX-82, 430), fastSun, fastSun_toggle)

    if wideMode:
        fisherImage_normal = fisherImage_wide

    homebutton.update((30+tempOffsetX, 20, 100, 40))

def save():
    global balance, reelTime, maxFishes, fishSpawnCap, fishScaredRange, catchTimer, fishCount, fishesHeld, reeltimeupgrade
    with open('.saves/save.philooxy', 'w') as f:
        reelTime = [reelTime, reeltimeupgrade.shopItem.bought]
        maxFishes = [maxFishes, hookupgrade.shopItem.bought]
        fishSpawnCap = [fishSpawnCap, spawncapupgrade.shopItem.bought]
        fishScaredRange = [fishScaredRange, scaredrangeupgrade.shopItem.bought]
        catchTimer = [catchTimer, catchtimeupgrade.shopItem.bought]
        lines = [f'{balance}\n', f'{reelTime}\n', f'{maxFishes}\n', f'{fishSpawnCap}\n', f'{fishScaredRange}\n', f'{catchTimer}\n', f'{fishCount}\n']
        f.write(f'{fishesHeld}\n')
        f.writelines(lines)

def bobberMove():
    global moving, offsetX, offsetY, bobberSpeed
    pressed_keys = pygame.key.get_pressed()

    if pressed_keys[pygame.K_LEFT] and offsetX > -200:
        moving = True
        offsetX -= 1*bobberSpeed
    if pressed_keys[pygame.K_RIGHT] and offsetX < 200:
        moving = True
        offsetX += 1*bobberSpeed
    if pressed_keys[pygame.K_UP] and offsetY > 0:
        moving = True
        offsetY -= 1*bobberSpeed
    if pressed_keys[pygame.K_DOWN] and offsetY < 200:
        moving = True
        offsetY += 1*bobberSpeed

    if pressed_keys[pygame.K_LEFT] and pressed_keys[pygame.K_RIGHT]:
        moving = False
    if pressed_keys[pygame.K_UP] and pressed_keys[pygame.K_DOWN]:
        moving = False

def doReelAnim():
    global reelTime, fishCaughtArray, linePos, bobberFall, bobberReel, xmove_temp, ymove_temp, offsetX, offsetY, fishCount, fishes, bobberFallAnim, reelAnim
    tempReelTime = reelTime*(len(fishCaughtArray))/2
    linePos = (140, 91)
    if bobberReel == 0:
        xmove_temp = ((WIDTH/2+offsetX)-142)/tempReelTime
        ymove_temp = ((HEIGHT/2+offsetY)-102)/tempReelTime
        bobberReel = 1
    if bobberReel < tempReelTime+1:
        offsetX -= xmove_temp
        offsetY -= ymove_temp
        bobberReel += 1
    if bobberReel >= tempReelTime+1:
        bobberFall = 0
        bobberReel = 0

        while len(fishCaughtArray) > 0:
            for i in fishes:
                if i.caught == True:
                    fishes.remove(i)
                    fishCaughtArray.remove(i)
                    i.caught == False
                    fishCount += 1
                    fishesHeld.append(i.type)
        linePos = (150, 101)
        reelAnim = False
        bobberFallAnim = True

def doCastAnim():
    global moving, bobberFall, offsetX, offsetY, exponent, bobberFallAnim
    moving = True
    if bobberFall < 1:
        offsetX = -169
        exponent = 10
        offsetY = -129
    if bobberFall <= 97:
        offsetX += 1
        exponent += 0.05
        offsetY = 100*math.sin(exponent)-70
        bobberFall += 1
    else:
        offsetY = 0
        bobberFallAnim = False

def renderText(text, font):
    text = font.render(text, False, (0,0,0))
    rect = text.get_rect()

    return text,rect

def main(area):
    global bobberFallAnim, fishingMusic, reelAnim, menuMusic, startTransitionY, startTransitionX, offsetX, offsetY, bobberSpeed, bobberFall, bobberReel, exponent, waterOffset, fishCount, fishingrect, fishingrect2, moving, fishes, cloudOffset, cloudOffset2, reelTime, linePos, fishSpawnCap, fishCaughtArray, fishesHeld, balance, fisherImage, fishSFX, bobberPos, easingY, easingX, run, sunsetCheck, sunriseCheck, lowGraphicsMode, wideMode, fullscreen

    if area == "exit":
        run = False
        save()

    if area == "sell":
        for i in fishesHeld:
            if i == 1:
                balance += 5
            elif i == 2:
                balance += 10
            fishesHeld.remove(i)
        area = "shop"

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

        drawbg()

        if lowGraphicsMode == True:
            startTransitionY = 100
            startTransitionX = 100
            linePos = (150, 101+startTransitionY*6)

        if startTransitionY < 100:
            startTransitionY = pygame.math.lerp(0, 100, ease(easingY))
            linePos = (150, 101+startTransitionY*6)
            easingY += 0.01

            drawFishing()

            if 99.7 <= startTransitionY < 100:
                startTransitionY = 100

        elif startTransitionY == 100:
            offsetX, offsetY = -169, -124
            easingY = 0


        if startTransitionX < 100: 
            startTransitionX = pygame.math.lerp(0, 100, ease(easingX))
            easingX += 0.01

            if 99.7 <= startTransitionX < 100:
                startTransitionX = 100

            drawShop()

        elif startTransitionX == 100:
            easingX = 0


        if startTransitionX > 100: 
            startTransitionX = pygame.math.lerp(200, 100, ease(easingX))
            easingX += 0.01

            if 100.3 >= startTransitionX > 100:
                startTransitionX = 100

            drawSettings()

        elif startTransitionX == 100:
            easingX = 0
        
        drawTitle()

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

        if reelAnim == True and startTransitionY == 0.0:
            doReelAnim()

        moving = False
        if bobberFallAnim == True and startTransitionY == 0.0:
            doCastAnim()

        if bobberFallAnim == False and reelAnim == False and startTransitionY == 0.0:
            bobberMove()

        fishingrect = pygame.Rect(WIDTH/2 - 16 + offsetX, HEIGHT/2 - 16 + 16 + offsetY, 32, 32)
        fishingrect2 = pygame.Rect(WIDTH/2 - fishScaredRange + offsetX, HEIGHT/2 - fishScaredRange + 16 + offsetY, 2*fishScaredRange, 2*fishScaredRange)

        drawbg()
        drawFishing()

        homebutton_up.update((20, 20+startTransitionY*6, 100, 40))

        if lowGraphicsMode == True:
            startTransitionY = 0
            linePos = (150, 101+startTransitionY*6)

        if startTransitionY > 0:

            drawTitle()

            linePos = (150, 101+startTransitionY*6)
            startTransitionY = pygame.math.lerp(100, 0, ease(easingY))
            easingY += 0.01

            if 0.3 >= startTransitionY > 0:
                startTransitionY = 0

        elif startTransitionY == 0:

            easingY = 0

            if len(fishes) < fishSpawnCap + len(fishCaughtArray):
                r = random.randint(1, 100)
                if r == 33:
                    if fishSFX == True:
                        ykwtm.play()
                    fish = fishy()
            
            fishCounter, fishCounterRect = renderText(f'Fish Caught: {fishCount}', ut)
            fishCounterRect.topright = (WIDTH - 20, 20)
            screen.blit(fishCounter, fishCounterRect)

            fishesHelder, fishesHelderRect = renderText(f'Fish Held: {len(fishCaughtArray)}/{maxFishes}', ut)
            fishesHelderRect.bottomright = (WIDTH - 20, HEIGHT - 20)
            screen.blit(fishesHelder, fishesHelderRect)

    if area == "shop":

        drawbg()

        drawShop()
      
        if lowGraphicsMode == True:
            startTransitionX = 0

        if startTransitionX > 0:
            drawTitle()

            startTransitionX = pygame.math.lerp(100, 0, ease(easingX))
            easingX += 0.01

        if 0.3 >= startTransitionX > 0:
            startTransitionX = 0

            easingX += 0.01
        if startTransitionX == 0:

            fishCounter, fishCounterRect = renderText(f'Fish: {len(fishesHeld)}', ut)
            fishCounterRect.topright = (WIDTH - 20, 20)
            screen.blit(fishCounter, fishCounterRect)

            balanceCounter, balanceCounterRect = renderText(f'Balance: ${balance}', ut)
            balanceCounterRect.topright = (WIDTH - 20, 60)
            screen.blit(balanceCounter, balanceCounterRect)

            easingX = 0
        
    if area == "settings":

        drawbg()

        drawSettings()

        if lowGraphicsMode == True:
            startTransitionX = 200

        if startTransitionX < 200:
            drawTitle()

            startTransitionX = pygame.math.lerp(100, 200, ease(easingX))
            easingX += 0.01

        if 199.7 <= startTransitionX < 200:
            startTransitionX = 200

            easingX += 0.01
        if startTransitionX == 200:
            easingX = 0



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

    main(area)

    if hovering == False:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    update()