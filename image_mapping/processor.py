from PIL import Image # python image library
from envmap import *

# drawing the map
# pix[x,y] = value  # Set the RGBA Value of the image (tuple)
# im.save('output.png')  # Save the modified pixels as .png

# ------- RGBA cell mappings -----------
air = (255, 255, 255)       # white
dead = (0, 0, 0)            # black
surface = (128, 128, 128)   # gray
arrival = (67, 168, 77)     # green
handwash = (0, 148, 255)    # blue
door = (255, 0, 110)        # magenta
window = (176, 119, 255)    # lavender
other = (255, 220, 48)      # yellow
# --------------------------------------

def readImage(filename: str):
    """ Processes the image given by the specified filename and returns an
        EnvMap class object (see envmap.py). """
    im = Image.open(filename) # open image file
    pixel = im.load() # load image pixel data
    width, height = im.size # Get the width and height of the image to iterate over

    # empty lists to append to:
    airlist = []
    deadlist = []
    surfacelist = []
    arrivallist = []
    handwashlist = []
    doorlist = []
    windowlist = []
    otherlist = []

    for y in range(height): # for all rows:
        for x in range(width): # for all columns:
            rgba = pixel[x,y]  # get the RGBA Value of the specified pixel
            if rgba == air:
                airlist.append((x, y))
            elif rgba == dead:
                deadlist.append((x, y))
            elif rgba == surface:
                surfacelist.append((x, y))
            elif rgba == arrival:
                arrivallist.append((x, y))
            elif rgba == handwash:
                handwashlist.append((x, y))
            elif rgba == door:
                doorlist.append((x, y))
            elif rgba == window:
                windowlist.append((x, y))
            elif rgba == other:
                otherlist.append((x, y))
            else:
                print(f"error: unregistered color found at ({x}, {y})")
                return

    env = EnvMap(width, height, airlist, surfacelist, deadlist, doorlist,
                 windowlist, handwashlist, arrivallist, otherlist)

    return env

def draw(filename):
    """ debug: recreate the input image filename through unicode characters
        in the terminal. works best with images under 32x32 resolution. """
    im = Image.open(filename) # open image file
    pixel = im.load() # load image pixel data
    width, height = im.size # Get the width and height of the image to iterate over

    # print basic image info:
    print(f"{width}x{height}: '{filename}'")

    for y in range(height): # for all rows:
        for x in range(width): # for all columns:
            rgba = pixel[x,y]  # get the RGBA Value of the specified pixel

            if rgba == air:
                print('.', end=' ')
            elif rgba == dead:
                print('▮', end=' ')
            elif rgba == surface:
                print('▢', end=' ')
            elif rgba == arrival:
                print('◍', end=' ')
            elif rgba == handwash:
                print('▽', end=' ')
            elif rgba == door:
                print('▥', end=' ')
            elif rgba == window:
                print('◎', end=' ')
            elif rgba == other:
                print('◌', end=' ')
            else:
                print(f"error: unregistered color found at ({x}, {y})")
                return
        print()
    return

def main():
    readImage('map01.png')
    draw('map01.png')
    return


if __name__ == "__main__":
    main()
