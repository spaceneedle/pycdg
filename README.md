# Introduction

Generate CD+G files programmatically with Python (CD + Graphics)
By Casey Halverson (spaceneedle@gmail.com)

There are quite a few visual commercial CD+G applications, and even some open source applications, that generate CD+G files. HOWEVER, I wasn't able to find one that A) generated them programmatically B) supported some rarely used modes and techniques that are difficult to implement.

I have seen many great CD+G examples that really pushed the format in the late 1980's and early 1990's, so I decided to create a library that might be able to foster a demoscene for CD+G. With an unusual 20 years of experience with embedded python, I apologize for my brief nature of python scripting. Gotta keep stuff small with very minimal module support. *import pycdg* is all you need!

While I welcome you to read the CD+G Revealed file contained in this github, here is my summary:

The CD+G format makes use of a subcode channel within the Redbook Audio CD format. In addition to the usual 16 bit stereo audio we know about, there are a few other bytes within the stream that are used for error correction and other facilities. Within the byte that contains the Table of Contents and time coding are 6 additional unused bits that are used for the CD+G format. We will only make use of the lower 6 bits, so when the CD burner makes our CD, it can populate the P and Q channels appropriately.

The CD+G data is stored 24 byte packets and this Python library can generate packet streams for most popular CD+G burning software where you provide this data file as well as a audio wave file. Note that players like VLC can play these files -- which is extremely useful for getting immedate feedback from your program.

This library works by filling a packet buffer that you can save to a file or stdout.

The most important thing to learn from all of this is: CD+G data streams in at a slow, but steady rate. While each instruction is only 6.6ms, it all adds up, which means full screen images will take some time.

## Library Requirements

* Python 3
* PIL (Python Image Library)

## Technical Facts

* CD+G Data Rate: 28800 bits per second
* CD+G Resolution: 300x216 ("Safe Area" is 294x204)
* Color Space: 4096 colors (4 bit per RGB channel, 12 bit total)
* Color Palette: 16 colors
* Tile Size: 6x12 pixels
* Tile Bits: 1 bit (2 colors) -- Can be XOR'ed for more colors per tile
* Smooth scrolling available (rarely used)

## How to use this library

This library creates a buffer of bytes. It'll probably be kinda big when you are done. Modern computers will have no issue with this. You will probably write this buffer to a file, or perhaps, pipe it into another program.

# Functions

* newBuffer()

Creates a new buffer for CD+G data. If one exists, it will clear the buffer.

* getBuffer()

Returns the buffer as the result. Can be used to write a file or print into stdout.

* delaySeconds(*seconds*)

Delay seconds, pad stream with nulls for *seconds*

* delayTicks(*ticks*)

Delay for number of *ticks* -- each tick is 6.6ms or about 150 ticks per second. Pads stream with nulls.

* scroll(*direction*,*color*,[*step*],[*wrap*])

Scrolls the screen in a direction, at a specified step. Color is the color of the blank area to filled after the scrolling event.
Leaving step blank will advance the typical column/row pixels, which is jumpy but fast. Specifying a step will produce smoother scrolling.
When WRAP is provided, the display will actually wrap around itself when it scrolls (ie: stuff on the left appears on the right). Just like
old video games. It can be used for a sort of marquee effect.

* multiScroll() [TBD]

This future function will support (never used) diagonal scrolling

* smoothScroll(*direction*)

Smooth scrolling routine advances the screen scroll by just one pixel.

* screenColor(*color*)

Change the screen to the color specified as the *color* argument

* borderColor(*color*)

Change the screen border to the color specified as the *color* argument

* paletteLow(*palette*,[*duplicates*])

Configure the low palette (colors 0-7) with the 4096 color palette specified

* paletteHigh(*palette*,[*duplicates*])

Configure the low palette (colors 8-15) with the 4096 color palette specified

* fadeIn(*speed*,*palette*)

Fade in palette from black to max palette color, at speed measured in ticks.

* fadeOut(*speed*,*palette*)

Fade in palette from black to max palette color, at speed measured in ticks.

* paletteCycle(*color*,*sequence*,*delay*,*counter*) [TBD]

This future function will support palette cycles.

* tileBlock(*colora*,*colorb*,*row*,*column*,*pixels*)

Renders to the display a native 2 color, 1 bit tile, with the color indexs specified, at the position indicated. Pixels contains the binary 1 bit data of the tile pixel content.

* tileBlockXOR(*colora*,*colorb*,*row*,*column*,*pixels*)

Renders to the display a native 2 color, 1 bit tile, with the color indexs specified, XOR'ed to existing pixels at the position indicated. Pixels contains the binary 1 bit data of the tile pixel content.

* loadImage(*filename*)

Load an image and store in the variable speecified.

* getPalette(*image variable*)

Get the palette from the image that was loaded.\

* scrollImageUp(*image*,*speed*)

Do a smooth scroll of the specified image at the speed specified. This is a "fast color" image, a made up term, that involves a special tile processing technique. We take the most dominant color and allow it to be a pixel where specified. We then find the second dominant color and make it the color for the remaining pixels. For images of objects, it works fine. Human figures and fine details can look a bit creepy. This rendering, however, is the fastest a CD+G can make an image.

* textTile(*character*,*x*,*y*,*[xor]*)

Display one character at column X and row Y. With optional XOR function. 

* printScreen(*text*,*[xor]*)

Prints text of any length to the screen, following the rules and boundries of rows and columns visible on the screen. If the screen is full, it will scroll down. There are some weird bugs when text is at the bottom and a new line is found. Sometimes text is overwritten. Will fix this soon.

* setCursor**x*,*y*)

Position the cursor at column *x* and row *y*

# Private Functions

You shouldn't use these, but I will document them anyway.

* _makeCDGPacket(*instruction*, *packet*)

*Instruction* contains the actual instruction to be passed, in numerical format. 
*Packet* is the contents of the packet.

This returns an actual CD+G binary packet. There are all sorts of other things stuffed within the CD+G packet, including Q and P parity. No idea what this is about, but we have to do this.

