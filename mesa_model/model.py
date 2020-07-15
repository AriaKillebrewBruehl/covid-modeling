from mesa_model.agents import *
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import SimultaneousActivation #RandomActivation
from mesa import Model
import numpy as numpy
from mesa_model.converter import convert
from PIL import Image

# CONSTANTS --------------------
max_caution_level = 2
percent_immunocompromised = 0.05 # 5 % of population is immunocomprimised 
# ------------------------------
def setUp():
	global filename
	#print("Enter name of environment file:")
	#filename = str(input())
	filename = 'mesa_model/maps/doors_simple.png'
	return filename #, num_infec_agents, num_agents, num_rec_agents

setUp()

def get_dimensions():
	global grid_width
	global grid_height
	im = Image.open(filename) # open image file
	grid_width, grid_height = im.size # Get the width and height of the image to iterate over
	return grid_width, grid_height

def get_infected_agents(model):
	return len([x for x in model.schedule.agents if isinstance(x, BaseHuman) and x.infected == True])

def get_recovered_agents(model):
	return len([x for x in model.schedule.agents if isinstance(x, BaseHuman) and x.recovered == True])

def get_uninfected_agents(model):
	return len([x for x in model.schedule.agents if isinstance(x, BaseHuman) and x.recovered == False and x.infected == False])

class CovidModel(Model):
	grid_width, grid_height = get_dimensions()

	def __init__(self, height=grid_height, width=grid_width, num_infec_agents=20, num_uninfec_agents=20, num_rec_agents=20):
		self.height = height
		self.width = width
		self.schedule = SimultaneousActivation(self) # Is this the best choice for agent activation? If not may need more implementation later.
		self.grid = MultiGrid(width=self.width, height=self.height, torus=False) # last arg prevents wraparound
		self.datacollector = DataCollector(
			model_reporters={
				"Uninfected": get_uninfected_agents,
				"Recovered": get_recovered_agents,
				"Infected": get_infected_agents
			},
			agent_reporters={
			#	"Uninfected": lambda x: x.infected == False and x.recovered == False,
			#	"Infected": lambda x: x.infected == True,
			#	"Recovered": (add later)
			}
			)

		convert(filename, self) # convert environment
		# Initialize agents here
		def rand_pos():
			pos = random.randrange(grid_width), random.randrange(grid_height)  # get new position for agent w/in bounds of grid
			if True not in [isinstance(x, UnexposedCell) for x in self.grid.get_cell_list_contents(pos)]:
				return pos
			else:
				return rand_pos()
		def set_up_agent(i, ag_type):
			pos = rand_pos() # get random position on grid 
			new_human = Student(1000 + i, pos, self) # create new Student agent 
			if ag_type == "uninfec":
				new_human.infected, new_human.recovered = False, False # set state of agent 
			elif ag_type == "infec":
				new_human.infected, new_human.recovered = True, False
			elif ag_type == "rec":
				new_human.infected, new_human.recovered = False, True
			new_human.caution_level = random.randint(0, max_caution_level) # create agents of different caution levels
			if new_human.caution_level == 0:
				new_human.masked = False
			else:
				new_human.masked = True
			if random.random() < percent_immunocompromised: # create immunocomprimised agents
				new_human.immunocompromised = True
			else:
				new_human.immunocompromised = False
			self.grid.place_agent(new_human, pos) # place agent on grid 
			self.schedule.add(new_human) # add agent to schedule

		for i in range(0, num_uninfec_agents):
			set_up_agent(i, "uninfec")
		for i in range(0, num_infec_agents):
			set_up_agent(i + num_uninfec_agents, "infec")
		for i in range(0, num_rec_agents):
			set_up_agent(i + num_uninfec_agents + num_infec_agents, "rec")

		self.running = True
		self.datacollector.collect(self)


	def step(self):
		self.schedule.step()
		self.datacollector.collect(self)
	def advance(self):
		pass

	def run_model(self):
		for i in range(self.run_time):
			self.step()
			self.advance()