# CD+G Python Library
# Generate CD+Gs programmatically using Python
# By Casey Halverson (spaceneedle@gmail.com)
# Copyright 2021
# Based on the documentation found at: https://jbum.com/cdg_revealed.html
#
# The CD+G format makes use of a subcode channel within the Redbook Audio CD format.
# In addition to 16 bit stereo audio, there are a few other bytes within the stream that
# are used for error correction and other facilities. Within the byte that contains
# the Table of Contents and time coding are 6 additional unused bits that are used for
# the CD+G format. We will only make use of the lower 6 bits, so when the CD burner 
# makes our CD, it can populate the P and Q channels appropriately. 
# 
# The CD+G data is stored 24 byte packets and this Python library can generate packet 
# streams for most popular CD+G burning software where you provide this data file as 
# well as a audio wave file. Note that players like VLC can play these files -- which is
# extremely useful for getting immedate feedback from your program.
#
# This library works by filling a packet buffer that you can save to a file or stdout.
# 
# Library Requirements:
#
# Python 3
# PIL (Python Image Library)
#
# Technical Facts:
#
# CD+G Data Rate: 28800 bits per second
# CD+G Resolution: 300x216 ("Safe Area" is 294x204)
# Color Space: 4096 colors (4 bit per RGB channel, 12 bit total)
# Color Palette: 16 colors
# Tile Size: 6x12 pixels
# Tile Bits: 1 bit (2 colors) -- Can be XOR'ed for more colors per tile 
# Smooth scrolling available (rarely used)

import copy
import crapfont
from PIL import Image
from PIL import ImagePalette

# Constant values

_kBaseHeight = 216
_kBaseWidth = 300
UP = 2
DOWN = 1
LEFT = 2
RIGHT = 1
NO_WRAP = 0
WRAP = 1

# CD+G commands

_kScreenColor = 1
_kBorderColor = 2
_kTileBlock = 6
_kScrollPreset = 20
_kScrollCopy = 24
_kSetTransparentColor = 28
_kLoadColorTableL = 30
_kLoadColorTableH = 31
_kTileBlockXOR = 38

# Various variables

_curYPos = 10
_curXPos = 10
_vScrollCounter = 0
__buffer__ = ""


#### Packet Building Functions
#### 

# Clear the CD+G buffer

def newBuffer():
    __buffer__ = ""

# Export the buffer

def getBuffer():
    return __buffer__

# Internal command that is used to generate a CD+G packet. We wrap our instruction and packet payload inside this.

def _makeCDGPacket(instruction,packet):
    global __buffer__
    if len(packet) < 16:
       packet = packet + chr(0) * (16-len(packet))
    buffer = ""
    buffer += chr(9) 				# flag indicates a CD+G packet
    buffer += chr(instruction)			# CD+G instruction
    buffer += chr(0) * 2			# Blank data for Q parity (no idea what this is)
    buffer += packet  				# packet contents
    buffer += chr(0) * 4			# Blank data for P parity (no idea what this is)
    __buffer__ = __buffer__ + buffer
    return buffer

#### Delay routines 
#### These just create strings of nulls the same as the packet size

# Delay in seconds

def delaySeconds(seconds):
    global __buffer__
    padding = seconds * 3600
    __buffer__ += chr(0) * padding
    return chr(0) * padding

# Delay "Ticks": There are about 150 ticks in a second (6.6ms)

def delayTicks(ticks):
    global __buffer__
    padding = ticks * 24
    __buffer__ += chr(0) * padding
    return chr(0) * padding


#### Scrolling functions


# scroll()
#
# Scrolls the screen in a direction, at a specified step. Color is the color of the blank area to filled after the scrolling event.
# Leaving step blank will advance the typical column/row pixels, which is jumpy but fast. Specifying a step will produce smoother scrolling.
# When WRAP is provided, the display will actually wrap around itself when it scrolls (ie: stuff on the left appears on the right). Just like
# old video games. It can be used for a sort of marquee effect.

def scroll(direction, color, step=-1, wrap=NO_WRAP):

    hoffset = 0
    voffset = 0

    if direction == UP | direction == DOWN:		# set bounds for whats allowed for vertical scrolling
         if step > 11: raise Exception("Vertical scrolling can only have a maximum step of 11")
         if step >= 1: voffset = step


    if direction == LEFT | direction == RIGHT:		# set bounds for what is allowed for horizontal scrolling
         if step > 5: raise Exception("Horizontal scrolling can only have a maximum step of 5")
         if step < 0: step = 0  
         if step >= 1: hoffset = step

    if wrap == NO_WRAP: instruction = _kScrollPreset	# Select what type of scrolling instruction we should use
    else: wrap = _kScrollCopy;

    if step == 0: scmd = direction			# If the user didn't specify finer step, scroll tile size step
    else: scmd = 0

    if color > 15: raise Exception("Color must be between 0 and 15!")
    if color < 0: raise Exception("Color must be between 0 and 15!")
 
    buffer = chr(color)

    buffer += (chr(scmd << 4 | hoffset & 0x07)) + (chr(scmd << 4 | voffset & 0x07))  # put it all together

    return _makeCDGPacket(_kScrollPreset,buffer)
        

# multiScroll()
# TBD: Both H and V scrolling can be combined, so we should let the user do this
# Can be used for diagonal scrolling effects

# smoothScroll(direction)
# Smooth scrolling routine

def smoothScroll(direction):
    global _vScrollCounter
    _vScrollCounter = _vScrollCounter + 1
    buffer = ""
    buffer += chr(0)
    buffer += chr(0)
    if _vScrollCounter == 12: 
       buffer += chr(0x20)
       _vScrollCounter = 0
    else:
       buffer += chr(_vScrollCounter)
    return _makeCDGPacket(_kScrollPreset,buffer)

#### Palette, Cycling and Fading functions
#### Configures palettes, cycle animations and fading 

# screenColor(color)
# Change the screen color (hardware driven, not a fill operation)

def screenColor(color):
    buffer = ""
    buffer += chr(color)
    buffer += chr(0)
    buffer += chr(0) * 14
    return _makeCDGPacket(kScreenColor,buffer)

# borderColor(color)
# Change the border color (hardware driven, not a fill operation)

def screenColor(color):
    buffer = ""
    buffer += chr(color)
    buffer += chr(0)
    buffer += chr(0) * 14
    return _makeCDGPacket(kBorderColor,buffer)

# paletteLow(palette,duplicates)
# Set the low palette, send duplicates if you wish (people do this in case there are errors)

def paletteLow(palette,duplicates=1):
    buffer = ""
    for i in range(0,duplicates):
      for i in range(0,8):                # Low Palette
        v = palette[i]
        red = max(v[0],0)
        green = max(v[1],0)
        blue = max(v[2],0)
        hb = green >> 2 | red << 2
        lb = green << 4 & 0x3f | blue
        buffer += chr(hb)
        buffer += chr(lb)
    return _makeCDGPacket(_kLoadColorTableL,buffer)

# paletteLow(palette,duplicates)
# Set the high palette, send duplicates if you wish (people do this in case there are errors)

def paletteHigh(palette,duplicates=1):
    buffer = ""
    for i in range(0,duplicates):
      for i in range(8,16):                # High Palette
        v = palette[i]
        red = max(v[0],0)
        green = max(v[1],0)
        blue = max(v[2],0)
        hb = green >> 2 | red << 2
        lb = green << 4 & 0x3f | blue
        buffer += chr(hb)
        buffer += chr(lb)
    return _makeCDGPacket(_kLoadColorTableH,buffer)

# fadeIn(speed,palette)
# Speed is in ticks, image palette must be passed in function

def fadeIn(speed,imgpalette):
    buffer = ""
    fadepalette = copy.deepcopy(imgpalette)
    for i in range(0,16):
       fadepalette[i][0] = fadepalette[i][0] - 15
       fadepalette[i][1] = fadepalette[i][1] - 15
       fadepalette[i][2] = fadepalette[i][2] - 15
    scratchpalette = fadepalette
    for j in range(0,15):
          for i in range(0,16):
             fadepalette[i][0] = fadepalette[i][0] + 1
             fadepalette[i][1] = fadepalette[i][1] + 1
             fadepalette[i][2] = fadepalette[i][2] + 1
          buffer += paletteLow(fadepalette)
          buffer += paletteHigh(fadepalette)
          buffer += delayTicks(speed)
    return buffer

# fadeOut(speed,palette)
# Speed is in ticks, image palette must be passed in function

def fadeOut(speed,imgpalette):
    buffer = ""
    fadepalette = copy.deepcopy(imgpalette)
    for j in range(0,15):
          for i in range(0,16):
             if fadepalette[i][0] != 0: fadepalette[i][0] = fadepalette[i][0] - 1
             if fadepalette[i][1] != 0: fadepalette[i][1] = fadepalette[i][1] - 1
             if fadepalette[i][2] != 0: fadepalette[i][2] = fadepalette[i][2] - 1
          buffer += paletteLow(fadepalette)
          buffer += paletteHigh(fadepalette)
          buffer += delayTicks(speed)
    return buffer


# paletteCycle(color,sequence,delay,counter):
# TBD: palette animation helper
# This will be tricky as it needs to be interlaced and properly timed with the rest of the data
# I might made a tool where it goes through and fills in blanks with specific time stamps?

#### Tile manpulation 
#### Direct commands as well as a few helper ones

# tileBlock(color A, Color B, row, column, pixel data)
# Place a 1 bit color tile with the specified colors in row and column specified. Pixel data
# contains the raw binary 12 bytes of data of the pixels
# Note: Tiles can only have two colors, but there are tricks to add more adjacent colors

def tileBlock(colora,colorb,row,column,pixels):
    buffer = ""
    buffer += chr(colora)
    buffer += chr(colorb)
    buffer += chr(row)
    buffer += chr(column)
    for i in range(0,12):
       buffer += chr(ord(pixels[i]) & 0x3F)
    return _makeCDGPacket(_kTileBlock,buffer)

# tileBlockXOR(color A, Color B, row, column, pixel data)
# This function allows you to perform a XOR with th

# Place a 1 bit color tile with the specified colors in row and column specified. Pixel data
# contains the raw binary 12 bytes of data of the pixel
# Note that the pixels are XOR'ed to create new colors from the index
# I am stil trying to figure out how we can pack in max color data with XOR (I suspect it'll be super slow)

def tileBlockXOR(colora,colorb,row,column,pixels):
    buffer = ""
    buffer += chr(colora)
    buffer += chr(colorb)
    buffer += chr(row)
    buffer += chr(column)
    for i in range(0,12):
       buffer += chr(ord(pixels[i]) & 0x3F)
    return _makeCDGPacket(_kTileBlockXOR,buffer)

# Load an image with PIP 

def loadImage(filename):
   img = Image.open(filename)
   img = img.convert(mode='P',colors=16,palette=Image.ADAPTIVE)
   return img

# Get the 16 color palette from the pic

def getPalette(img):
   palette = img.getpalette()
   color = []
   for i in range(0,len(palette),3):
     if i/3 == 16: break
     color.append([palette[i] >> 4,palette[i+1] >> 4,palette[i+2] >> 4])
   return color

# Loads in an image and does a smooth scroll up as we print tiles. 
# This involves something I made up called "fast color". It's great for low complexity images.
# You can use complex images, but the results might look a bit weird and creepy.
# Basically, we figure out the dominant color in a tile and allow pixels of that color to be that color.
# Next, we figure out the second dominant color, and anything not the dominant color, no matter what the actual
# color is, becomes that color. As dumb as it sounds, it allows us to generate a "full color" image as fast 
# as a CD+G can possibly generate one. 

def scrollImageUp(image,speed):
    buffer = ""
    scroller = ""
    tileX = 0
    scanbuffer = ""
    px = image.load()
    width, height = image.size
    imageY = height
    for bY in range(0,imageY,12):
      if bY+12 > imageY: break
      tileX = 0
      for q in range(0,12): scroller = scroller + smoothScroll(UP)
      for bX in range(0,_kBaseWidth,6):
        buffer = ""
        color = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for y in range(0,12):
         for x in range(0,6):
           color[px[x+bX,y+bY]] = color[px[x+bX,y+bY]] + 1
        color_a = 0
        color_b = 0
        for z in range(0,16):
           if(color[z] > color[color_a]): 
                 color_a = z
        for z in range(0,16):
         if z != color_a:
           if(color[z] > color[color_b]):
                 color_b = z     
        for y in range(0,12):
          scanbuffer = "0b"
          for x in range(0,6):
           if px[x+bX,y+bY] == color_a: scanbuffer = scanbuffer + "1"
           else: scanbuffer = scanbuffer + "0"
          buffer = buffer + chr(int(scanbuffer,2))
        scroller = scroller + tileBlock(color_b,color_a,17,tileX,buffer)
        tileX = tileX + 1
    return scroller

# draw a character on the screen at position
# Makes use of our tile font
# Note that crapfont, the only supported font, is kinda crappy because I rushed through all the characters. Only caps are supported.

def textTile(text,cy,cx,xor=False):
    buffer = ""
    for y in range(0,12):
        buffer += chr(crapfont._font12x6[text][y])
    if xor == False: return tileBlock(15,1,cx,cy,buffer)
    if xor == True: return tileBlockXOR(15,1,cx,cy,buffer)

# print statement
# There are some bugs on newlines when its at the bottom

def printScreen(text,xor=False):
    global _curXPos
    global _curYPos
    for i in range(0,len(text)):
     if text[i] != "\n":
       if _curXPos == 49:
          _curYPos = _curYPos + 1
          _curXPos = 1
       if _curYPos == 17:
          for q in range(0,12): smoothScroll(UP)
          _curYPos = 16
       textTile(text[i],_curXPos,_curYPos)
       _curXPos = _curXPos + 1
     if text[i] == "\n":
        _curYPos = _curYPos + 1
        _curXPos = 1
        if _curYPos == 17:
          scroll(UP,15)
          _curYPos = 16

# set cursor

def setCursor(x,y):
    global _curXPos
    global _curYPos
    _curXPos = x
    _curYPos = y
    return

