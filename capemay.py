# Pans from top to bottom of the famous Cape May NJ lighthouse, then pauses for 30 seconds

import pycdg

pycdg.newBuffer()
lighthouse = pycdg.loadImage("capemaylighthouse.png")
palette = pycdg.getPalette(lighthouse)
pycdg.paletteLow(palette)
pycdg.paletteHigh(palette)
pycdg.scrollImageUp(lighthouse,10)
pycdg.delaySeconds(30)

file = open("./capemay.cdg","w")
file.write(pycdg.getBuffer())
file.close()



