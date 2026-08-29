import pygame

pygame.mixer.init()
pygame.font.init()

#window setup
WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED|pygame.RESIZABLE, vsync=1)
icon = pygame.image.load("assets/ui/icon.png").convert_alpha()
pygame.display.set_caption("Philooxy's Phishing")
pygame.display.set_icon(icon)
pygame.mixer.init()
clock = pygame.time.Clock()
arial = pygame.font.SysFont('arial', 20)
ut_b = pygame.font.Font('assets/font.ttf', 25)
ut = pygame.font.Font('assets/font.ttf', 20)
ut_s = pygame.font.Font('assets/font.ttf', 15)
ut_xs = pygame.font.Font('assets/font.ttf', 12)
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
cover = pygame.surface.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
cover.fill((0,0,25,100))

# flags
bobberFallAnim = False #bobber falling animation at start of fishing
fishingMusic = False #music only starts once on fishing area
reelAnim = False #reeling in animation
menuMusic = False #music only starts once on title 
startAnim = True

#not flags
startTransitionY = 0 #transition between menu and start
startTransitionX = 200 #same thing but horizontal
sunMove = 0

fullscreen = False
area = "title"
offsetX, offsetY = -169, -129
bobberSpeed = 2
bobberFall = 0
bobberReel = 0
waterOffset = 0
cloudOffset = -730
cloudOffset2 = -680
fishes = []
linePos = (150, 101)
isClicking = True
fishCaughtArray = []
easingY = 0
easingX = 0
bobberPos = (136, 100)
hovering = False
fishingrect = pygame.Rect(WIDTH/2 - 16 + offsetX, HEIGHT/2 - 16 + 16 + offsetY, 32, 32)
sunsetCheck = False
sunriseCheck = False
nightCheck = False
upgrade = False
achs = []
achs_unlocked = []
achs_showing = []
bobbers = []
fishesHeld2 = []
fishReq = 0
coopShop = False
upgradeList = []
coopUpgradeList = []
fishRarity = 5
fishReq = 5
coopLevel = 1
coopMaxFishes = 5
prevRandUpgrade = ""
randUpgrade = ""

#settings variables
volume = 1 #volume
lowGraphicsMode = False
theme = 0

#stupid
fishSFX = False
wideMode = False #wide sode
fastSun = False #this is for testing but you can turn it on if you want

if fastSun:
    hour, minute, = 1, 1

def loadify(img):
    return pygame.image.load(img).convert_alpha()

#images
#sunset/sunrise images
cloudsImage2_sunset = loadify("assets/bg/clouds2-sunset.png")
cloudsImage_sunset = loadify("assets/bg/clouds1-sunset.png")
dockImage_sunset = loadify("assets/bg/dock-sunset.png")
dockImageFull_sunset = loadify("assets/bg/dock2-sunset.png")
skyColor_sunset = (4, 99, 171)
waterImage_sunset = loadify("assets/bg/water-sunset.png")
sunImage_sunset = loadify("assets/bg/sun-sunset-full.png")
bobberImage_sunset = loadify("assets/fisher/bobber-sunset.png")
titleImage_sunset = loadify("assets/bg/title-sunset.png")
#normal images
cloudsImage2_noon = loadify("assets/bg/clouds2-noon.png")
cloudsImage_noon = loadify("assets/bg/clouds1-noon.png")
dockImage_noon = loadify("assets/bg/dock-noon.png")
dockImageFull_noon = loadify("assets/bg/dock2-noon.png")
skyColor_noon = (0, 175, 229)
waterImage_noon = loadify("assets/bg/water-noon.png")
sunImage_noon = loadify("assets/bg/sun-noon.png")
bobberImage_noon = loadify("assets/fisher/bobber-noon.png")
titleImage_noon = loadify("assets/bg/title-noon.png")
#night images
cloudsImage2_night = loadify("assets/bg/clouds2-night.png")
cloudsImage_night = loadify("assets/bg/clouds1-night.png")
dockImage_night = loadify("assets/bg/dock-night.png")
dockImageFull_night = loadify("assets/bg/dock2-night.png")
skyColor_night = (11, 20, 119)
waterImage_night = loadify("assets/bg/water-night.png")
sunImage_night = loadify("assets/bg/sun-noon.png")
bobberImage_night = loadify("assets/fisher/bobber-sunset.png")
titleImage_night = loadify("assets/bg/title-night.png")
stars = loadify("assets/bg/stars.png")
#other images
slider_bar = loadify("assets/ui/slider.png")
slider_ball = loadify("assets/ui/slider2.png")
toggle_on = loadify("assets/ui/toggle_on.png")
toggle_off = loadify("assets/ui/toggle_off.png")
ach_bg = loadify("assets/achs/bg.png")
ach_locked = loadify("assets/achs/ach_locked.png")

#skins
#soday
fisherImage_normal_noon = loadify("assets/fisher/soday/noon.png")
fisherImage_pull_noon = loadify("assets/fisher/soday/pull-noon.png")
fisherImage_normal_sunset = loadify("assets/fisher/soday/sunset.png")
fisherImage_pull_sunset = loadify("assets/fisher/soday/pull-sunset.png")
fisherImage_normal_night = loadify("assets/fisher/soday/night.png")
fisherImage_pull_night = loadify("assets/fisher/soday/pull-night.png")
skin_soday = [fisherImage_normal_noon, fisherImage_pull_noon, fisherImage_normal_sunset, fisherImage_pull_sunset, fisherImage_normal_night, fisherImage_pull_night]

#evil soday
evilFisherImage_normal_noon = loadify("assets/fisher/evilsoday/noon.png")
evilFisherImage_pull_noon = loadify("assets/fisher/evilsoday/pull-noon.png")
evilFisherImage_normal_sunset = loadify("assets/fisher/evilsoday/sunset.png")
evilFisherImage_pull_sunset = loadify("assets/fisher/evilsoday/pull-sunset.png")
evilFisherImage_normal_night = loadify("assets/fisher/evilsoday/night.png")
evilFisherImage_pull_night = loadify("assets/fisher/evilsoday/pull-night.png")
skin_evilsoday = [evilFisherImage_normal_noon, evilFisherImage_pull_noon, evilFisherImage_normal_sunset, evilFisherImage_pull_sunset, evilFisherImage_normal_night, evilFisherImage_pull_night]

skin_current = skin_soday

fisherImage_wide = pygame.transform.scale_by(fisherImage_normal_noon, (2.5, 1))

cloudsImage2 = cloudsImage2_noon
cloudsImage = cloudsImage_noon
fisherImage_normal = fisherImage_normal_noon
fisherImage_pull = fisherImage_pull_noon
dockImage = dockImage_noon
dockImageFull = dockImageFull_noon
skyColor = skyColor_noon
waterImage = waterImage_noon
sunImage = sunImage_noon
bobberImage = bobberImage_noon
titleImage = titleImage_noon

dockImage2 = pygame.transform.flip(dockImage, True, False)
waterImage2 = waterImage
fisherImage = fisherImage_normal
version = "0.7.0"
coop = False

#sounds
ykwtm = pygame.mixer.Sound("assets/sfx/fish.mp3")

#music
mus_hotel2 = pygame.mixer.Sound("assets/mus/hotel2.mp3")
mus_paradise = pygame.mixer.Sound("assets/mus/paradise.mp3")
mus_menu = mus_hotel2
