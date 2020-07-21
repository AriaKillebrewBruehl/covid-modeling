from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter
import mesa
from mesa_model.agents import *
from mesa_model.model import CovidModel

# Constants
UNINFECTED_COLOR = "#AAAAAA"
INFECTED_COLOR = "#FF0000"
RECOVERED_COLOR = "#00FF00"
QUARANTINING_COLOR = "#FFFF00"
# ------- RGBA cell mappings -----------
air = "#FFFFFF"          # white
inaccessible = "#000000" # black
surface = "#808080"      # gray 
arrival = "#43A84D"      #shade = (67, 168, 77)  # green
handwash = "#0094FF"     #shade = (0, 148, 255)  # blue
door = "#7A2D2D"         # brown
window = "46EB7D"        # mnit
other = "#EB46B4"        # yellow
# --------------------------------------

# How do we want to set up our grid?
def canvas_repr(agent):
	if agent is None:
		return

	port = {}
	if isinstance(agent, BaseHuman):
		port["Shape"] = "circle"
		port["r"] = 0.5
		port["Layer"] = 1
		port["Filled"] = "true"
		if agent.infected == False and agent.recovered == False:
			port["Color"] = UNINFECTED_COLOR
		elif agent.infected == True:
			port["Color"] = INFECTED_COLOR
		elif agent.infected == False and agent.recovered == True:
			port["Color"] = RECOVERED_COLOR
		port["text"] = ("S" if isinstance(agent, Student) else "F") + str(agent.unique_id)
		port["text_color"] = "#000000"
	elif isinstance(agent, BaseEnvironment):
		port["Shape"] = "rect" # add images later
		port["w"] = 1
		port["h"] = 1
		port["Layer"] = 0
		port["Filled"] = "true"
		
		# specify color of each environment aspect 
		if isinstance(agent, UnexposedCell):
			if isinstance(agent, VentilatorCell):
				color = window
				shade = "(176, 119, 255"
			else:
				color = inaccessible
				shade = "(252, 100, 24"
		elif isinstance(agent, InfectableCell):
			if isinstance(agent, SurfaceCell):
				if isinstance(agent, Door):
					color = door
					shade = "(125, 70, 235"
				else:
					color = surface 
					shade = "(128, 128, 128"
			elif isinstance(agent, AirCell):
				color = air 
				shade = "(255, 0, 0"
			else:
				color = other
				shade = "(255, 0, 0"
		port["Color"] = color
		if agent.infected:
				port["Color"] = [port["Color"], "rgba" + shade + ", " + str(agent.infected / 2) +  ")"]
				port["text"] = "{:.2f}".format(agent.infected) if agent.infected > 0.001 else ""
	return port


from os import listdir
from os.path import isfile, join, splitext
root = "mesa_model/maps/"
maps = [x for x in listdir(root) if isfile(join(root, x)) and splitext(x)[1] == ".png"]
print("=== Maps ===")
for idx, x in enumerate(maps):
	print(str(idx) + ". " + x)
map_name = maps[int(input("Map: "))]
map_option = join(root, map_name)

chart_element = ChartModule(
		[
			{"Label": "Uninfected", "Color": UNINFECTED_COLOR},
			{"Label": "Infected", "Color": INFECTED_COLOR},
			{"Label": "Recovered", "Color": RECOVERED_COLOR},
			{"Label": "Quarantined of Infected", "Color": QUARANTINING_COLOR}
		]
	)

model_params = {
	"num_infec_agents" : UserSettableParameter("number", "Initial Infected", 1, description="Initial Infected"),
	"num_uninfec_agents" : UserSettableParameter("number", "Initial Uninfected", 20, description="Initial Uninfected"),
	"num_rec_agents" : UserSettableParameter("number", "Initial Recovered", 0, description="Initial Recovered"),
	"mask_efficacy" : UserSettableParameter("number", "Mask Efficacy in %", 95, description="Mask effiacy in %"),
	"filename" : map_option
}

dist_chart_element = ChartModule(
	[
		{"Label": "Average Distance", "Color": UNINFECTED_COLOR},
		{"Label": "Average Nearest Distance", "Color": RECOVERED_COLOR}
	]
)

w, h = CovidModel.size(model_params["filename"])

canvas_element = CanvasGrid(canvas_repr, w, h, 500, 500)

ModularServer.verbose = False

server = ModularServer(CovidModel, [canvas_element, chart_element, dist_chart_element], "COVID-19 Classroom Transmission Model - " + splitext(map_name)[0], model_params=model_params)

print(type(server.model_cls), dir(server.model_cls))
