import mesa
import numpy as np
import random


grid_width = 20
grid_height = 20

frames_per_day = 2

def get_distance(agent_1, agent_2):
	xPos1 = agent_1.pos[0]
	yPos1 = agent_1.pos[1]
	xPos2 = agent_2.pos[0]
	yPos2 = agent_2.pos[1]

	return (((xPos1 - xPos2)**2 + (yPos1 - yPos2)**2)**0.5) 

class BaseHuman(mesa.Agent):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=True, incubation_period=0, contagion_counter=0, immune=False, immunocompromised=False, susceptibility=1, schedule=[[0, 0, 0]], quarantined=False, recovered=False):
		super().__init__(unique_id, model)
		self.infected = infected
		self.masked = masked
		self.incubation_period = incubation_period 
		self.contagion_counter = contagion_counter
		self.immune = immune
		self.immunocompromised = immunocompromised
		self.susceptibility = np.double(susceptibility)
		self.schedule = np.reshape(schedule, (-1, 3)) # Effectively a list of tuples representing (t, x, y)
		self.quarantined = quarantined
		self.recovered = recovered
		self.pos = pos

	def infect(self):
		if self.immune == True:
			return # don't infect if we've recovered
		self.infected = True
		self.contagion_counter = 14 # todo: find a distribution

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
		if True not in [isinstance(x, UnexposedCell) for x in self.model.grid.get_cell_list_contents(new_position)]: # isnt working see line 48
			return new_position
		else:
			return self.get_new_pos_near()
	# agents will move randomly throughout grid
	def get_new_pos_far(self):
		new_position = random.randrange(grid_width), random.randrange(grid_height)  # get new position for agent w/in bounds of grid
		if True not in [isinstance(x, UnexposedCell) for x in self.model.grid.get_cell_list_contents(new_position)]: # Fixed it to work
			#say get_cell_list_contents is unexposed cell but agent will move there any way
			return new_position
		else:
			return self.get_new_pos_far()

	def move(self):
		self.model.grid.move_agent(self, self.get_new_pos_far())
		
		for neighbor in self.model.grid.get_neighbors(self.pos, True, False, 2): # second arg Moore, thrid arg include center, thrid arg radius 
			if neighbor.infected == True and self.infected == False:
				self.infect()
				# let infect() determmine if they should move from recovered to another category

	def step(self):
		self.move()
		self.update_infection()

class Student(BaseHuman):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=True, incubation_period=0, contagion_counter=0, immune=False, immunocompromised=False, susceptibility=1, schedule=[[0, 0, 0]], quarantined=False, recovered=False):
		super().__init__(unique_id, pos, model, infected, masked, incubation_period, contagion_counter, immune, immunocompromised, susceptibility, schedule, quarantined)

class Faculty(BaseHuman):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=True, incubation_period=0, contagion_counter=0, immune=False, immunocompromised=False, susceptibility=1, schedule=[[0, 0, 0]], quarantined=False, recovered=False):
		super().__init__(unique_id, pos, model, infected, masked, incubation_period, contagion_counter, immune, immunocompromised, susceptibility, schedule, quarantined)

class BaseEnvironment(mesa.Agent):
	def __init__(self, unique_id, model, pos=(0,0)):
		super().__init__(unique_id, model)
		self.pos = pos
		self.infected = False # default

	def step(self):
		pass

# added 07/03 
class UnexposedCell(BaseEnvironment): # unreachable by agents 
	def __intit__(self, unique_id, model, pos=(0,0)):
		super().__init__(unique_id,model)
		self.infected = False

class InfectableCell(BaseEnvironment): # could contain particles, air, surfaces, etc
	# decay in all cases is how much is left after one iteratoin
	def __init__(self, unique_id, model, pos=(0,0), infected = np.double(0), transmissionLikelihood = 1, decay = .50):
		super().__init__(unique_id, model, pos) 
		self.infected = infected
		self.transmissionLikelihood = transmissionLikelihood
		self.decay = decay

	def step(self):
		self.decay_cell()
		self.infect_agents()

	def decay_cell(self):
		self.infected *= self.decay

	def infect(self, amount = 1.0):
		self.infected = max(self.infected + amount, 1.0) # Make sure we don't go past maximum capacity.

	def cleanse(self, percent = 1.0):
		self.infected *= percent

	def infect_agents(self):
		for agent in self.model.grid.get_cell_list_contents(self.pos):
			if isinstance(agent, BaseHuman):
				agent.infect() # In the future, the initial amount may be important.

class SurfaceCell(InfectableCell): # interactable at edges, cannot be entered 
	def __init__(self, unique_id, model, pos=(0,0), infected = np.double(0), transmissionLikelihood = 1, decay = 1, cleaningInterval = 1, cleaned = True):
		super().__init__(unique_id, model, pos, infected, transmissionLikelihood, decay) 
		self.cleaningInterval = cleaningInterval
		self.cleaned = cleaned

class AirCell(InfectableCell): # can be traveled through 
	def __init__(self, unique_id, model, pos=(0,0), infected = np.double(0), transmissionLikelihood = 1, decay = 1, ventilationDirection = 0, ventilationDecay = 1):
		super().__init__(unique_id, model, pos, infected, transmissionLikelihood, decay) 
		self.ventilationDirection = ventilationDirection
		self.ventilationDecay = ventilationDecay

	def step(self):
		super().step()
		self.ventilate()

	def ventilate(self):
		possible_steps = self.model.grid.get_neighborhood(
			self.pos,
			moore=True, # can move diagonaly
			include_center=False)
		x, y = np.round(np.cos(self.ventilationDirection)), np.round(np.sin(self.ventilationDirection))
		target = next(filter(lambda z: z.pos == (x, y), possible_steps))
		target.infect(self.infected * (1 - self.ventilationDecay))
		self.infected *= self.ventilationDecay


class Door(SurfaceCell): # upon interaction telleports agent to other side 
	def __init__(self, unique_id, model, pos=(0,0), infected = False, transmissionLikelihood = 1, decay = 1, cleaningInterval = 1, cleaned = True):
		super().__init__(unique_id, model, pos, infected, transmissionLikelihood, decay, cleaningInterval, cleaned)


# this one seemed a little complicated and I wasn't quite sure how to appraoch it 
class VentilatorCell(UnexposedCell):
	def __init__(self, unique_id, model, pos=(0,0), ventilationDecay=lambda rx, ry: 1 / (np.norm), maxRadius = 5):
		super().__init__(unique_id,model)
		self.ventilationDecay = ventilationDecay

	def step(self):
		self.ventilate()

	def ventilate(self):

		# rough outline complete later
		for cell in []:
			rx, ry = self.pos - cell.pos # rough idea
			cell.cleanse(self.ventilationDecay(rx, ry))
		pass