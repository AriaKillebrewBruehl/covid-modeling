from mesa_model.agents import *
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import SimultaneousActivation #RandomActivation
from mesa import Model
import numpy as numpy
from mesa_model.converter import convert
from PIL import Image

def setUp():
	global filename
	global num_infec_agents
	global num_agents
	global num_rec_agents
	#print("Enter name of environment file:")
	#filename = str(input())
	filename = 'mesa_model/maps/map01.png'
	# filename = 'mesa_model/maps/hallway.png'
	#print("Enter number of infected agents:")
	#num_infec_agents = int(input())
	print("Enter number of uninfected agents:")
	#num_agents = int(input())
	print("Enter number of recovered agents:")
	#num_rec_agents = int(input())
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
	#im = Image.open(filename) # open image file
	#grid_width, grid_height = im.size # Get the width and height of the image to iterate over
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
		for i in range(0, num_uninfec_agents):
			pos = rand_pos()
			test_human_1 = Student(1000 + i, pos, self)
			test_human_1.infected, test_human_1.recovered = False, False
			self.grid.place_agent(test_human_1, pos)
			self.schedule.add(test_human_1)
		for i in range(0, num_infec_agents):
			pos = rand_pos()
			test_human_1 = Student(1000 + num_uninfec_agents + i, pos, self)
			test_human_1.infected, test_human_1.recovered = True, False
			test_human_1.contagion_counter = 14
			self.grid.place_agent(test_human_1, pos)
			self.schedule.add(test_human_1)
		for i in range(0, num_rec_agents):
			pos = rand_pos()
			test_human_1 = Student(1000 + num_uninfec_agents + num_infec_agents + i, pos, self)
			test_human_1.infected, test_human_1.recovered = False, True
			self.grid.place_agent(test_human_1, pos)
			self.schedule.add(test_human_1)
		'''
		for i in range(0, grid_width):# when this is used to create environment everything works fine
			for j in range(10, grid_height):
				test_environment = AirCell(i * 10 + j * 10000, self, (i, j), ventilationDecay = .10)
				if i < 10:
					test_environment.infect()
				self.grid.place_agent(test_environment, (i, j))
				self.schedule.add(test_environment)
		# creating block of unexposed cells for test purposes
		for i in range(10):
			for j in range(grid_width):
				test_block = UnexposedCell(1, (j, i), self)
				self.grid.place_agent(test_block, (j,i))
		'''
		self.running = True
		self.datacollector.collect(self)
	def setUp(self):
		pass
	def step(self):
		self.schedule.step()
		self.datacollector.collect(self)
	def advance(self):
		pass

	def run_model(self):

		for i in range(self.run_time):
			self.step()
			self.advance()