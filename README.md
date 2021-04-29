# Introduction

Generate CD+G files programmatically with Python (CD + Graphics)
By Casey Halverson (spaceneedle@gmail.com)

There are quite a few visual commercial CD+G applications, and even some open source applications, that generate CD+G files. HOWEVER, I wasn't able to find one that A) generated them programmatically B) supported some rarely used modes and techniques that are difficult to implement.

I have seen many great CD+G examples that really pushed the format in the late 1980's and early 1990's, so I decided to create a library that might be able to foster a demoscene for CD+G. With an unusual 20 years of experience with embedded python, I apologize for my brief nature of python scripting. Gotta keep stuff small with very minimal module support. This is even my first use of __init__.py.

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

# Private Functions

You shouldn't use these, but I will document them anyway.

* _makeCDGPacket(instruction, packet)

*Instruction* contains the actual instruction to be passed, in numerical format. 
*Packet* is the contents of the packet.

This returns an actual CD+G binary packet. There are all sorts of other things stuffed within the CD+G packet, including Q and P parity. No idea what this is about, but we have to do this.

