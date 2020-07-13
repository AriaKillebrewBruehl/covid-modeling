from PIL import Image # python image library
from mesa_model.agents import * 
# ------- RGBA cell mappings -----------
arrival = (67, 168, 77)       # green
inaccess = (0, 0, 0)          # black
inaccessInfec = (252, 100, 24) # red
surface = (128, 128, 128)     # gray
surfaceInfec = (235, 70, 180) # magenta
other = (255, 220, 48)        # yellow
air= (255, 255, 255)          # white
airInfec = (255, 0, 0)        # red
handwash = (0, 148, 255)      # blue
door = (122, 45, 45)          # brown
doorInfec = (125, 70, 235)    # purple
window = (70, 235, 125)       # mint

# --------------------------------------
def convert(filename, model):
    im = Image.open(filename) # open image file
    pixel = im.load() # load image pixel data
    width, height = im.size # Get the width and height of the image to iterate over

    # print basic image info:
    print(f"{width}x{height}: '{filename}'")

    for y in range(height): # for all rows:
        for x in range(width): # for all columns:
            rgba = pixel[x,y]  # get the RGBA Value of the specified pixel
            if rgba == air:
                environment = AirCell(10*y + x, model, (x, y)) # create specified BaseEnvironment cell
                #environment.infect()
            elif rgba == airInfec:
                environment = AirCell(10*y + x, model, (x, y)) # create specified BaseEnvironment cell
                environment.infect()
            elif rgba == inaccess:
                environment = UnexposedCell(10*y + x, model,(x, y))
            elif rgba == inaccessInfec:
                environment = UnexposedCell(10*y + x, model,(x, y))
                environment.infect()
            elif rgba == surface:
                environment = SurfaceCell(10*y + x, model, (x, y))
            elif rgba == surfaceInfec:
                environment = SurfaceCell(10*y + x, model, (x, y))
                environment.infect()
            elif rgba == arrival:
                environment = Door(10*y + x, model, (x, y))
            elif rgba == handwash:
                environment = SurfaceCell(10*y + x, model, (x, y))
            elif rgba == door:
                environment = Door(10*y + x, model, (x, y))
            elif rgba == doorInfec:
                environment = Door(10*y + x, model, (x, y))
                environment.infect()
            elif rgba == window:
                environment = Door(10*y + x, model, (x, y))
            elif rgba == other:
                environment = InfectableCell(10*y + x, model, (x, y))
            else:
                print(f"error: unregistered color found at ({x}, {y})")
            model.grid.place_agent(environment, (x, y)) # place in environment
            model.schedule.add(environment) # add to schedule