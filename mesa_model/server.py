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
				port["Color"] = window
				shade = "(176, 119, 255"
			else:
				port["Color"] = inaccessible
				shade = "(252, 100, 24"
		elif isinstance(agent, InfectableCell):
			if isinstance(agent, SurfaceCell):
				if isinstance(agent, Door):
					port["Color"] = door
					shade = "(125, 70, 235"
				else:
					port["Color"] = surface 
					shade = "(128, 128, 128"
			elif isinstance(agent, AirCell):
				port["Color"] = air 
				shade = "(255, 0, 0"
			else:
				port["Color"] = other
				shade = "(255, 0, 0"
			if agent.infected:
				port["Color"] = [port["Color"], "rgba" + shade + ", " + str(agent.infected / 2) +  ")"]
	return port

canvas_element = CanvasGrid(canvas_repr, CovidModel.grid_width, CovidModel.grid_height, 500, 500)

chart_element = ChartModule(
		[
			{"Label": "Uninfected", "Color": UNINFECTED_COLOR},
			{"Label": "Infected", "Color": INFECTED_COLOR},
			{"Label": "Recovered", "Color": RECOVERED_COLOR}
		]
	)

model_params = {
	"num_infec_agents" : UserSettableParameter("number", "Initial Infected", 20, description="Initial Infected"),
	"num_uninfec_agents" : UserSettableParameter("number", "Initial Uninfected", 20, description="Initial Uninfected"),
	"num_rec_agents" : UserSettableParameter("number", "Initial Recovered", 20, description="Initial Recovered")
}

server = ModularServer(CovidModel, [canvas_element, chart_element], "COVID-19 Classroom Transmission Model", model_params=model_params)