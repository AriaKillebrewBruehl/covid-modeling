from mesa_model.agents import *
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa import Model
import numpy as numpy
from mesa_model.converter import convert


def get_infected_agents(model):
	return len([x for x in model.schedule.agents if isinstance(x, BaseHuman) and x.infected == True])

def get_recovered_agents(model):
	return len([x for x in model.schedule.agents if isinstance(x, BaseHuman) and x.recovered == True])

def get_uninfected_agents(model):
	return len([x for x in model.schedule.agents if isinstance(x, BaseHuman) and x.recovered == False and x.infected == False])

class CovidModel(Model):
	grid_width = 32
	grid_height = 32

	def __init__(self, height=grid_height, width=grid_width):
		self.height = height
		self.width = width
		self.schedule = RandomActivation(self) # Is this the best choice for agent activation? If not may need more implementation later.
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
		convert('mesa_model/map01.png', self) # when this is used to create environment agents don't work (humans don't move, air cells don't decay)# create specified BaseEnvironment cells from image, place
		# in environment and add to scheduler 
		# Initialize agents here
		for i in zip(range(0, 5), [(True, False), (False, True), (False, False), (False, False), (False, False)]):
			test_human_1 = Student(1000 + i[0], (10, 10 + i[0]), self)
			test_human_1.infected, test_human_1.recovered = i[1]
			if test_human_1.infected == True:
				test_human_1.contagion_counter = 14
			self.grid.place_agent(test_human_1, (10, 10 + i[0]))
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
		#print("in model step") # prints always (not affected by converter funct)
		self.schedule.step()
		self.datacollector.collect(self)
	def advnace(self):
		self.schedule.advance()
		


	def run_model(self):
		
		for i in range(self.run_time):
			self.step()
			self.advance()