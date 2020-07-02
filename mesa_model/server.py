from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter
import mesa
from mesa_model.agents import Student, Faculty

# Constants
UNINFECTED_COLOR = "#AAAAAA"
INFECTED_COLOR = "#FF0000"
RECOVERED_COLOR = "#00FF00"


canvas_element = CanvasGrid(lambda x: {}, 20, 20, 500, 500)

chart_element = ChartModule(
		[
			{"Label": "Uninfected", "Color": UNINFECTED_COLOR},
			{"Label": "infected", "Color": INFECTED_COLOR},
			{"Label": "Recovered", "Color": RECOVERED_COLOR}
		]
	)

server = ModularServer(mesa.Model, [canvas_element, chart_element], "COVID-19 Classroom Transmission Model", model_params={})