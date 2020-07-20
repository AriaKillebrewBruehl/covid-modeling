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

id_counter = 0

def new_id():
    global id_counter
    id_counter += 1
    return id_counter

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
                environment = AirCell(new_id(), model, (x, y)) # create specified BaseEnvironment cell
            elif rgba == airInfec:
                environment = AirCell(new_id(), model, (x, y))
                environment.infect()
            elif rgba == inaccess:
                environment = UnexposedCell(new_id(), model,(x, y))
            elif rgba == inaccessInfec:
                environment = UnexposedCell(new_id(), model,(x, y))
                environment.infect()
            elif rgba == surface:
                environment = SurfaceCell(new_id(), model, (x, y))
            elif rgba == surfaceInfec:
                environment = SurfaceCell(new_id(), model, (x, y))
                environment.infect()
            elif rgba == arrival:
                environment = Door(new_id(), model, (x, y))
            elif rgba == handwash:
                environment = SurfaceCell(new_id(), model, (x, y))
            elif rgba == door:
                environment = Door(new_id(), model, (x, y))
            elif rgba == doorInfec:
                environment = Door(new_id(), model, (x, y))
                environment.infect()
            elif rgba == window:
                environment = VentilatorCell(new_id(), model, (x, y))
            elif rgba == other:
                environment = InfectableCell(new_id(), model, (x, y))
            else:
                print(f"error: unregistered color found at ({x}, {y})")
            model.grid.place_agent(environment, (x, y)) # place in environment
            model.schedule.add(environment) # add to schedule