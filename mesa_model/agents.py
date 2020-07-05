import mesa
import numpy as np
import random


grid_width = 20
grid_height = 20

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

	# agents will move randomly to a sqaure next to their current square
	def get_new_pos_near(self):
		possible_steps = self.model.grid.get_neighborhood(
			self.pos,
			moore=True, # can move diagonaly
			include_center=False)
		new_position = self.random.choice(possible_steps)	
		if self.model.grid.get_cell_list_contents(new_position) != UnexposedCell: # isnt working see line 48
			return new_position
		else:
			get_new_pos_near()
	# agents will move randomly throughout grid
	def get_new_pos_far(self):
		new_position = random.randrange(grid_width), random.randrange(grid_height) # get new position for agent w/in bounds of grid
		print(self.model.grid.get_cell_list_contents(new_position))
		if self.model.grid.get_cell_list_contents(new_position) != UnexposedCell: # isnt woking, above print statement will 
			#say get_cell_list_contents is unexposed cell but agent will move there any way
			return new_position
		else:
			get_new_pos_far()

	def move(self):
		self.model.grid.move_agent(self, self.get_new_pos_far())
		
		for neighbor in self.model.grid.get_neighbors(self.pos, True, False, 2): # second arg Moore, thrid arg include center, thrid arg radius 
			if neighbor.infected == True and self.infected == False:
				self.infected = True
				self.recovered = False

	def step(self):
		self.move()
class Student(BaseHuman):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=True, incubation_period=0, contagion_counter=0, immune=False, immunocompromised=False, susceptibility=1, schedule=[[0, 0, 0]], quarantined=False, recovered=False):
		super().__init__(unique_id, pos, model, infected, masked, incubation_period, contagion_counter, immune, immunocompromised, susceptibility, schedule, quarantined)

class Faculty(BaseHuman):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=True, incubation_period=0, contagion_counter=0, immune=False, immunocompromised=False, susceptibility=1, schedule=[[0, 0, 0]], quarantined=False, recovered=False):
		super().__init__(unique_id, pos, model, infected, masked, incubation_period, contagion_counter, immune, immunocompromised, susceptibility, schedule, quarantined)

class BaseEnvironment(mesa.Agent):
	def __init__(self, unique_id, model, pos=(0,0), infected = False):
		super().__init__(unique_id, model)
		self.pos = pos
		self.infected = infected

	def step(self):
		pass

# added 07/03 
class UnexposedCell(BaseEnvironment): # unreachable by agents 
	def __intit__(self, unique_id, model, pos=(0,0), infected = False):
		super().__init__(unique_id,model, infected)

class InfectableCell(BaseEnvironment): # could contain particles, air, surfaces, etc 
	def __init__(self, unique_id, model, pos=(0,0), infected = False, transmissionLikelyhood = 1, decay = 1):
		super().__init__(unique_id, model, pos, infected) 
		self.transmissionLikelyhood = transmissionLikelyhood
		self.decay = decay

class SurfaceCell(InfectableCell): # interactable at edges, cannot be entered 
	def __init__(self, unique_id, model, pos=(0,0), infected = False, transmissionLikelyhood = 1, decay = 1, cleaningInterval = 1, cleaned = True):
		super().__init__(unique_id, model, pos, infected, transmissionLikelyhood, decay) 
		self.cleaningInterval = cleaningInterval
		self.cleaned = cleaned

class AirCell(InfectableCell): # can be traveled through 
	def __init__(self, unique_id, model, pos=(0,0), infected = False, transmissionLikelyhood = 1, decay = 1, ventilationDirection = -1, ventilationDecay = 1):
		super().__init__(unique_id, model, pos, infected, transmissionLikelyhood, decay) 
		self.ventilationDirection = ventilationDirection
		self.ventilationDecay = ventilationDecay

class Door(SurfaceCell): # upon interaction telleports agent to other side 
	def __init__(self, unique_id, model, pos=(0,0), infected = False, transmissionLikelyhood = 1, decay = 1, cleaningInterval = 1, cleaned = True):
		super().__init__(unique_id, model, pos, infected, transmissionLikelyhood, decay, cleaningInterval, cleaned)

'''
this one seemed a little complicated and I wasn't quite sure how to appraoch it 
class VentilatorCell(UnexposedCell):
	def __intit__(self, unique_id, model, pos=(0,0), ventilationDecay):
		super().__init__(unique_id,model)
'''
