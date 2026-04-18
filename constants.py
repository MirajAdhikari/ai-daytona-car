SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "AI Car - Procedural Track Navigation"

# Colors
GRASS        = (52, 140, 62)
GRASS_DARK   = (38, 115, 48)
GRASS_LIGHT  = (75, 160, 85)
ASPHALT      = (58, 60, 68)
ASPHALT_MID  = (72, 74, 82)
ASPHALT_EDGE = (230, 230, 235)
WHITE        = (255, 255, 255)

# Track geometry
TRACK_HALF_WIDTH = 38   # asphalt half-thickness; also used for collision radius

# Physics
MAX_SPEED      = 9.5
REVERSE_MAX    = -5.5
BASE_ACCEL     = 0.19
BRAKE_FORCE    = 0.45
REVERSE_ACCEL  = 0.12
FRICTION       = 0.955
TURN_RATE      = 0.055

# Car
CAR_WIDTH   = 36
CAR_HEIGHT  = 19
CAR_HALF_L  = 14
CAR_HALF_W  = 8

# Raycasting
NUM_RAYS    = 9
RAY_LENGTH  = 220
RAY_SPREAD  = 120.0
RAY_STEP    = 4.0