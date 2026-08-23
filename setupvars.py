import pygame

pygame.mixer.init()
pygame.font.init()

#window setup
WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED|pygame.RESIZABLE, vsync=1)
icon = pygame.image.load("assets/icon.png")
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

# flags
bobberFallAnim = False #bobber falling animation at start of fishing
fishingMusic = False #music only starts once on fishing area
reelAnim = False #reeling in animation
menuMusic = False #music only starts once on title screen

#not flags
startTransitionY = 0 #transition between menu and start
startTransitionX = 100 #same thing but horizontal
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
isClicking = False
fishCaughtArray = []
easingY = 0
easingX = 0
bobberPos = (136, 100)
hovering = False
fishingrect = pygame.Rect(WIDTH/2 - 16 + offsetX, HEIGHT/2 - 16 + 16 + offsetY, 32, 32)
sunsetCheck = False
sunriseCheck = False
upgrade = False

#settings variables
volume = 0 #volume
lowGraphicsMode = False
theme = 0

#stupid
fishSFX = False
wideMode = False #wide sode
fastSun = False #this is for testing but you can turn it on if you want

if fastSun:
    hour, minute, = 1, 1

#images
#sunset/sunrise images
cloudsImage2_sunset = pygame.image.load("assets/clouds2-sunset.png")
cloudsImage_sunset = pygame.image.load("assets/clouds1-sunset.png")
fisherImage_normal_sunset = pygame.image.load("assets/fisher-sunset.png")
fisherImage_pull_sunset = pygame.image.load("assets/fisherpull.png")
dockImage_sunset = pygame.image.load("assets/dock-sunset.png")
skyColor_sunset = (4, 99, 171)
waterImage_sunset = pygame.image.load("assets/water-sunset.png")
sunImage_sunset = pygame.image.load("assets/sun-sunset-full.png")
bobberImage_sunset = pygame.image.load("assets/bobber-sunset.png")
titleImage_sunset = pygame.image.load("assets/title-sunset.png")
#normal images
cloudsImage2_noon = pygame.image.load("assets/clouds2-noon.png")
cloudsImage_noon = pygame.image.load("assets/clouds1-noon.png")
fisherImage_normal_noon = pygame.image.load("assets/fisher-noon.png")
fisherImage_pull_noon = pygame.image.load("assets/fisherpull.png")
dockImage_noon = pygame.image.load("assets/dock-noon.png")
skyColor_noon = (0, 175, 229)
waterImage_noon = pygame.image.load("assets/water-noon.png")
sunImage_noon = pygame.image.load("assets/sun-noon.png")
bobberImage_noon = pygame.image.load("assets/bobber-noon.png")
titleImage_noon = pygame.image.load("assets/title-noon.png")

fisherImage_wide = pygame.transform.scale_by(fisherImage_normal_noon, (2.5, 1))

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

#sounds
ykwtm = pygame.mixer.Sound("assets/fish.mp3")

#music
mus_hotel2 = pygame.mixer.Sound("assets/hotel2.mp3")
mus_paradise = pygame.mixer.Sound("assets/paradise.mp3")
mus_menu = mus_hotel2