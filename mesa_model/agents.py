import mesa
import numpy as np
import numpy.linalg
import numpy.random
import random
#from mesa_model.model import * 
#from mesa_model.model import get_dimensions # for some reason when I try to use this helper funct I get errors from convert saying AirCell isn't defined 

grid_width = 31
grid_height = 31
#grid_width, grid_height = get_dimensions()

frames_per_day = 2

class BaseHuman(mesa.Agent):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=False, incubation_period=0, contagion_counter=0, immune=False, immunocompromised=False, susceptibility=1, caution_level = 1, schedule=[[0, 0, 0]], quarantined=False, recovered=False):
		super().__init__(unique_id, model)
		self.infected = infected
		self.masked = masked
		self.incubation_period = incubation_period 
		self.contagion_counter = contagion_counter
		self.immune = immune
		self.immunocompromised = immunocompromised
		self.susceptibility = np.double(susceptibility)
		self.caution_level = caution_level
		self.schedule = np.reshape(schedule, (-1, 3)) # Effectively a list of tuples representing (t, x, y)
		self.quarantined = quarantined
		self.recovered = recovered
		self.pos = pos

	def infect(self, contact, neighbor): 
		chance = 1.0
		if self.immune == True or self.infected == True:
			return # don't infect if we've recovered or already infected
		if self.caution_level == 0: # chance of infection based off of how caution agent is 
			if contact == "human": # varying chance based on how the agent came in contact with virus 
				chance = neighbor.contagion_counter / 14 # assumes infected people are most viral at start of infected period 
			else:
				chance = 0.1
		elif self.caution_level == 1:
			if contact == "human":
				chance = (neighbor.contagion_counter / 14) * 0.50
			else:
				chance = 0.01
		elif self.caution_level == 2:
			if contact == "human":
				chance = (neighbor.contagion_counter / 14) * 0.25
			else:
				chance = 0.001
		if random.random() < chance:
			self.infected = True
			self.contagion_counter = 14 # todo: find a distribution
		else:
			return 
	def update_infection(self):
		if self.infected == False:
			return
		self.contagion_counter -= 1 / frames_per_day
		if self.contagion_counter <= 0:
			self.infected = False
			self.contagion_counter = 0
			self.recovered = True
			self.immune = True

	# agents will move randomly to a sqaure next to their current square
	# To fix: some agents will move within the 1-thickness walls.
	def get_new_pos_near(self):
		possible_steps = self.model.grid.get_neighborhood(
			self.pos,
			moore=True, # can move diagonaly
			include_center=False)
		new_position = self.random.choice(possible_steps)	
		if True not in [isinstance(x, UnexposedCell) for x in self.model.grid.get_cell_list_contents(new_position)]:
			return new_position
		else:
			return self.get_new_pos_near()
	# agents will move randomly throughout grid
	def get_new_pos_far(self):
		new_position = random.randrange(grid_width), random.randrange(grid_height)  # get new position for agent w/in bounds of grid
		if True not in [isinstance(x, UnexposedCell) for x in self.model.grid.get_cell_list_contents(new_position)]: # Fixed it to work
			#say get_cell_list_contents is unexposed cell but agent will move there any way
			#print(new_position) # when converter used for environment doesn't get printed meaning get_new_pos isn't called
			return new_position
		else:
			return self.get_new_pos_far()

	def move(self):
		self.model.grid.move_agent(self, self.get_new_pos_far())
		for neighbor in self.model.grid.get_neighbors(self.pos, True, False, 2): # second arg Moore, thrid arg include center, thrid arg radius 
			if not self.infected: # what will happen to uninfected agents
				# contraction from other humans
				if neighbor.infected and isinstance(neighbor, BaseHuman):
					self.infect("human", neighbor) # let infect() determmine if they should move from recovered to another category
				# contraction from environment 
				elif neighbor.infected and isinstance(neighbor, InfectableCell):
					choice = random.randint(0, 4)
					if choice == 1:
						self.infect("environment", neighbor)
			if self.infected: # what will infected agents do
				if not neighbor.infected and isinstance(neighbor, InfectableCell):
					chance = 1.0
					if self.masked:
						chance = (self.contagion_counter / 14) * 0.01 # lower chance of infecting environment if masked 
					if not self.masked: 
						chance = (self.contagion_counter / 14) * 0.1
					if random.random() < chance: 
						neighbor.infect() # In the future, the initial amount may be important.


	def step(self):
		pass
		
	def advance(self):
		self.move()
		self.update_infection()

class Student(BaseHuman):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=True, incubation_period=0, contagion_counter=0, immune=False, immunocompromised=False, susceptibility=1, caution_level = 1, schedule=[[0, 0, 0]], quarantined=False, recovered=False):
		super().__init__(unique_id, pos, model, infected, masked, incubation_period, contagion_counter, immune, immunocompromised, susceptibility, caution_level, schedule, quarantined)

class Faculty(BaseHuman):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=True, incubation_period=0, contagion_counter=0, immune=False, immunocompromised=False, susceptibility=1, caution_level = 1, schedule=[[0, 0, 0]], quarantined=False, recovered=False):
		super().__init__(unique_id, pos, model, infected, masked, incubation_period, contagion_counter, immune, immunocompromised, susceptibility, caution_level, schedule, quarantined)

class BaseEnvironment(mesa.Agent):
	def __init__(self, unique_id, model, pos=(0,0)):
		super().__init__(unique_id, model)
		self.pos = pos
		self.infected = False # default

	def step(self):
		pass
	def advance(self):
		pass

# added 07/03 
class UnexposedCell(BaseEnvironment): # unreachable by agents 
	def __intit__(self, unique_id, model, pos=(0,0)):
		super().__init__(unique_id,model)
		self.infected = False

class InfectableCell(BaseEnvironment): # could contain particles, air, surfaces, etc
	# decay in all cases is how much is left after one iteratoin
	def __init__(self, unique_id, model, pos=(0,0), infected = np.double(0), contagion_counter=0, transmissionLikelihood = 1, decay = .50):
		super().__init__(unique_id, model, pos) 
		self.infected = infected
		self.contagion_counter = contagion_counter
		self.transmissionLikelihood = transmissionLikelihood
		self.decay = decay

	def step(self):
		pass
	def advance(self):
		self.decay_cell()
		self.infect_agents()


	def decay_cell(self):
		self.infected *= self.decay
		if self.infected < 0.1: # infected air only lasts for ~ 4 steps 
			self.infected = False
			pass
		# if CovidModel.schedule.steps % 14 == 0: 
			# self.cleanse()

		

	def infect(self, amount = 1.0):
		self.infected = min(self.infected + amount, 1.0) # Make sure we don't go past maximum capacity.
	

	def cleanse(self, percent = 1.0):
		self.infected *= (1 - percent)
		if self.infected < 0.001:
			self.infected == False

	def infect_agents(self):
		if not self.infected:
			return 
		else:
			for agent in self.model.grid.get_cell_list_contents(self.pos):
				if isinstance(agent, BaseHuman) and not agent.infected and not agent.recovered:
					if random.random() < self.infected:
  						agent.infect() # In the future, the initial amount may be important.

class SurfaceCell(InfectableCell): # interactable at edges, cannot be entered 
	def __init__(self, unique_id, model, pos=(0,0), infected = np.double(0), transmissionLikelihood = 1, decay = 1, cleaningInterval = -1, cleaned = True):
		super().__init__(unique_id, model, pos, infected, transmissionLikelihood, decay) 
		self.cleaningInterval = cleaningInterval
		self.lastCleaned = 0
		self.cleaned = cleaned

	def step(self):
		pass
	def advance(self):
		self.clean()

	def clean(self):
		self.lastCleaned += 1
		if self.cleaningInterval >= self.lastCleaned:
			self.lastCleaned = 0
			self.cleanse(1.0) # how effective are our cleaning measures?

class AirCell(InfectableCell): # can be traveled through 
	def __init__(self, unique_id, model, pos=(0,0), infected = np.double(0), transmissionLikelihood = 1, decay = 1, ventilationDirection = -1, ventilationDecay = 1):
		super().__init__(unique_id, model, pos, infected, transmissionLikelihood, decay) 
		self.ventilationDirection = ventilationDirection
		self.ventilationDecay = ventilationDecay

	def step(self):
		pass
	def advacne(self):
		super().advacne()
		self.ventilate()
	def ventilate(self):
		possible_steps = self.model.grid.get_neighborhood(
			self.pos,
			moore=True, # can move diagonaly
			include_center=False)
		rand = False # quick hack to allow random directions
		if self.ventilationDirection == -1:
			rand = True
			self.ventilationDirection = np.random.random() * np.pi * 2
		x, y = np.round(np.cos(self.ventilationDirection)) + self.pos[0], np.round(np.sin(self.ventilationDirection)) + self.pos[1]
		if rand == True:
			self.ventilationDirection = -1
		targets = [z for z in possible_steps if z == (x, y) in possible_steps]
		if len(targets) == 0:
			return # nothing to infect
		target = targets[0]
		for t in self.model.grid.get_cell_list_contents(target):
			if isinstance(t, InfectableCell):
				t.infect(self.infected * (1 - self.ventilationDecay)) # maybe make this so that the amount of particulates lost = particulate gains in other cells
			if isinstance(t, BaseHuman):
				t.infect()
		self.infected *= self.ventilationDecay

class Door(SurfaceCell): # upon interaction telleports agent to other side 
	def __init__(self, unique_id, model, pos=(0,0), infected = False, transmissionLikelihood = 1, decay = 1, cleaningInterval = 1, cleaned = True):
		super().__init__(unique_id, model, pos, infected, transmissionLikelihood, decay, cleaningInterval, cleaned)

class VentilatorCell(UnexposedCell):
	def __init__(self, unique_id, model, pos=(0,0), ventilationDecay=lambda rx, ry: 1 / (np.linalg.norm([rx, ry], 2)), maxRadius = 5):
		super().__init__(unique_id,model)
		self.ventilationDecay = ventilationDecay

	def step(self):
		pass
	def advance(self):
		self.ventilate()

	def ventilate(self):
		# rough outline complete later
		for x in range(grid_width):
			for y in range(grid_height):
				rx, ry = tuple(np.array(self.pos) - np.array((x, y)))
				cont = self.model.grid.get_cell_list_contents((x, y))
				cell.cleanse(self.ventilationDecay(rx, ry))