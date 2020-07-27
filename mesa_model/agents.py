import mesa
import numpy as np
import numpy.linalg
import numpy.random
import random
#frames_per_hour = 2
# immuno_increase = 1.5       # how much more likely are immunocompromised people to get sick 
c_l0_mult = 1.0             # how much more likely are c_l0 people to get sick
c_l1_mult = 0.5             # how much more likely are c_l1 people to get sick
c_l2_mult = 0.25            # how much more likely are c_l2 people to get sick
percent_asymptomatic = 0.38 # what percent of people will show symptoms
masked_infect_rate = 0.01   # how likey is a masked person to infect a cell 
unmasked_infect_rate = 0.10 # how likely is an unmasked person to infect a cell
infection_duration = 14      # how long are symptomatic people contagious 
contagion_symp = 14
contagion_asymp = 28        # how long are asymptomatic people contagious 
hours = 0
days = 0
# ------------------------------
class BaseHuman(mesa.Agent):
	def __init__(self, unique_id, model, pos=(0,0), caution_level = 1, masked=False, severity = 0.5, infected=False, symptomatic = False, incubation_period=0, contagion_counter=14, quarantined=False, recovered=False, immune=False, next_pos=(0, 0), seat = (0, 0), arrived = False):
		super().__init__(unique_id, model)
		self.caution_level = caution_level
		self.masked = masked
		'''
		self.immunocompromised = immunocompromised
		self.susceptibility = np.double(susceptibility)
		'''
		self.severity = np.double(severity)
		self.infected = infected
		self.symptomatic = symptomatic 
		self.incubation_period = incubation_period 
		self.contagion_counter = contagion_counter
		self.recovered = recovered
		self.immune = immune
		#self.schedule = np.reshape(schedule, (-1, 3)) # Effectively a list of tuples representing (t, x, y)
		self.next_pos = next_pos
		self.seat = seat
		self.pos = pos
		self.last_pos = None
		self.arrived = arrived 
		self.unique_id = unique_id
		self.quarantined = False # LET 40-41 HANDLE QUARANTINING DO NOT CHANGE
		#print(caution_level, masked, severity, infected,  symptomatic, incubation_period, contagion_counter, recovered, immune, schedule, pos, unique_id, quarantined)
		if quarantined:
			self.quarantine(initialized=False)
		self.steps_per_hour = self.model.steps_per_hour

	def init_infect(self):
		self.infected = True
		# Fix later: this won't be feasible if we're doing 600 steps per hour
		self.contagion_counter = infection_duration  # * 24 * self.steps_per_hour # todo: find a distribution
		self.severity = random.random() # give agent random severity 
		if self.severity < percent_asymptomatic: # 38 % of people will be asymptomatic todo: find more reasonable numbers
			self.contagion_counter = contagion_asymp # todo: find a distribution
			self.symptomatic = False
		else: 
			# self.contagion_counter = contagion_symp # todo: find a distribution
			self.symptomatic = True

	def infect(self, contact="env", neighbor=None, amount=1.0): 
		chance = 1.0 # default chance 
		increase = amount # default increase in contraction 
		# if self.immunocompromised:
		#	increase = immuno_increase # immunocomprimised peopel have greater chance at infection 
		if self.immune == True or self.infected == True:
			return # don't infect if we've recovered or already infected
		if self.caution_level == 0: # chance of infection based off of how caution agent is 
			if contact == "human": # varying chance based on how the agent came in contact with virus 
				chance = (neighbor.contagion_counter / infection_duration) * c_l0_mult# assumes infected people are most viral at start of infected period 
			else:
				chance = 0.1
		elif self.caution_level == 1:
			if contact == "human":
				chance = (neighbor.contagion_counter / infection_duration) * c_l1_mult
			else:
				chance = 0.01
		elif self.caution_level == 2:
			if contact == "human":
				chance = (neighbor.contagion_counter / infection_duration) * c_l2_mult
			else:
				chance = 0.001
		if random.random() < chance * increase:
			self.init_infect()
		else:
			return

	def infect_cell(self, neighbor):
		chance = 1.0 # default chance of infecting cell 
		if self.masked:
			chance = 1#(self.contagion_counter / 14) * masked_infect_rate # lower chance of infecting environment if masked 
		if not self.masked: 
			chance = 1#(self.contagion_counter / 14) * unmasked_infect_rate
		if random.random() < chance:
			amt = 1
			if self.masked:
				amt *= (1 - self.model.mask_efficacy)
			neighbor.infect(amount = amt) # In the future, the initial amount may be important.

	def recover(self):
		self.infected = False
		self.contagion_counter = 0
		self.recovered = True
		self.immune = True
		if self.quarantined == True:
			self.pos = self.last_pos
			#print("Placed agent", self.unique_id)
			self.model.grid.place_agent(self, self.last_pos)
			self.quarantined = False

	def quarantine(self, initialized=True):
		self.last_pos = self.pos
		if initialized == True:
			self.model.grid.remove_agent(self)
			#print("Removed agent", self.unique_id)
		self.quarantined = True
		
	def update_infection(self):
		if not self.infected: # if not infected don't do anything 
			return
		self.contagion_counter -= 1 / self.steps_per_hour # reduce infection
		#if self.model.schedule.steps % 14 == 0:
		#	self.check_self()
		#if self.infected and self.symptomatic and self.caution_level > 0 and not self.quarantined: # if cautious person and symptomatic quarantine
		#	self.quarantine() # currently called even if already quarantined, is this okay?
		#	#print("quarantined") 
		if self.contagion_counter <= 0: # set as recovered 
			self.recover()

	# agents will move randomly to a sqaure next to their current square
	def get_new_pos_near(self):
		possible_steps = self.model.grid.get_neighborhood(
			self.pos,
			moore=True, # can move diagonaly
			include_center=False)
		new_position = self.random.choice(possible_steps)	
		if True not in [isinstance(x, UnexposedCell) or isinstance(x, SurfaceCell) for x in self.model.grid.get_cell_list_contents(new_position)]:
			if new_position is None:
				pass
				#print("new_pos of agent" + str(self.unique_id) + " is None")
			return new_position
		else:
			return self.get_new_pos_near()

	# agents will move randomly throughout grid
	def get_new_pos_far(self):
		new_position = random.randrange(self.model.width), random.randrange(self.model.height)  # get new position for agent w/in bounds of grid
		if True not in [isinstance(x, UnexposedCell) or isinstance(x, SurfaceCell) for x in self.model.grid.get_cell_list_contents(new_position)]: # Fixed it to work
			#say get_cell_list_contents is unexposed cell but agent will move there any way
			return new_position
		else:
			return self.get_new_pos_far()

	def check_new_pos(self, pos):
		X = pos[0]
		Y = pos[1]
		if True in [isinstance(x, BaseHuman) or isinstance(x, SurfaceCell) for x in self.model.grid.get_cell_list_contents((X, Y))]: # if obstacle in way
			if True in [isinstance(x, BaseHuman) or isinstance(x, SurfaceCell) for x in self.model.grid.get_cell_list_contents((self.pos[0], Y))]:
				new_pos = (self.pos[0] - 1, Y)
			elif True in [isinstance(x, BaseHuman) or isinstance(x, SurfaceCell) for x in self.model.grid.get_cell_list_contents((X, self.pos[1]))]:
				new_pos = (X, self.pos[1] + 1)
			else:
				choices = [(self.pos[0], self.pos[1] - 1), (self.pos[0] + 1, self.pos[1])]
				new_pos = random.choice(choices)
		if X < 0: # don't move off grid 
			X += 1
		elif X > 32:
			X -= 1
		if Y < 0:
			Y += 1
		elif Y > 32:
			Y -= 1
		new_pos = (X, Y)
		return new_pos

	def scheduled_move(self):
		goalX = self.next_pos[0]
		goalY = self.next_pos[1]
		X = self.pos[0]
		Y = self.pos[1]
		if goalX == X and goalY == Y: # if already arrived don't move 
			return
		elif goalX < X:
			X -= 1
		elif goalX > X:
			X += 1
		if goalY < Y:
			Y -= 1
		elif goalY > Y:
			Y += 1
		new_pos = (X, Y)
		if new_pos[0] != goalX and new_pos[1] != goalY: # if haven't arrived check for obstacles 
			new_pos = self.check_new_pos(new_pos)
		if new_pos[0] == self.next_pos[0] and new_pos[1] == self.next_pos[1]:
			self.arrived = True 
		self.model.grid.move_agent(self, new_pos)


	def move(self):
		if self.quarantined == True:
			return
		# self.model.grid.move_agent(self, self.get_new_pos_near())
		self.scheduled_move()
		# setting radius to 1 since it can pass through the walls
		for neighbor in self.model.grid.get_neighbors(self.pos, True, False): # second arg Moore, thrid arg include center, thrid arg radius 
			if not self.infected: # what will happen to uninfected agents
				# contraction from other humans
				if neighbor.infected and isinstance(neighbor, BaseHuman):
					self.infect("human", neighbor) # let infect() determmine if they should move from recovered to another category
				# contraction from environment 
				elif neighbor.infected and isinstance(neighbor, InfectableCell):
					self.infect("environment", neighbor)
			if self.infected: # what will infected agents do
				if not neighbor.infected and isinstance(neighbor, InfectableCell):
					self.infect_cell(neighbor)

	def step(self):
		self.move()
		self.update_infection()
		
class Student(BaseHuman):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=True, incubation_period=0, contagion_counter=14, immune=False, severity = 0.5, quarantined=False, caution_level = 1, next_pos=(0, 0), seat = (0, 0), recovered=False, arrived = False):
		super().__init__(unique_id, model, pos=pos, infected=infected, masked=masked, incubation_period=incubation_period, contagion_counter=contagion_counter, immune=immune, severity=severity, caution_level=caution_level, next_pos = next_pos, seat = seat, quarantined=quarantined, arrived = arrived)

class Faculty(BaseHuman):
	def __init__(self, unique_id, model, pos=(0,0), infected=False, masked=True, incubation_period=0, contagion_counter=14, immune=False, severity = 0.5, quarantined=False, caution_level = 1, next_pos=(0, 0), seat = (0, 0), recovered=False, arrived = False):
		super().__init__(unique_id, model, pos=pos, infected=infected, masked=masked, incubation_period=incubation_period, contagion_counter=contagion_counter, immune=immune, severity=severity, caution_level=caution_level, next_pos = next_pos, seat = seat, quarantined=quarantined, arrived = False)

class BaseEnvironment(mesa.Agent):
	def __init__(self, unique_id, model, pos=(0,0)):
		super().__init__(unique_id, model)
		self.pos = pos
		self.infected = False # default

	def step(self):
		pass

class UnexposedCell(BaseEnvironment): # unreachable by agents 
	def __init__(self, unique_id, model, pos=(0,0)):
		super().__init__(unique_id,model)
		self.infected = False

	def step(self):
		self.infected = False

class InfectableCell(BaseEnvironment): # could contain particles, air, surfaces, etc
	# decay in all cases is how much is left after one iteratoin
	def __init__(self, unique_id, model, pos=(0,0), infected = np.double(0), contagion_counter=0, transmissionLikelihood = 1, decay = .50):
		super().__init__(unique_id, model, pos) 
		self.infected = infected
		self.contagion_counter = contagion_counter
		self.transmissionLikelihood = transmissionLikelihood
		self.decay = decay

	def decay_cell(self):
		self.infected *= self.decay
		if self.infected < 0.1: # infected air only lasts for ~ 4 steps 
			self.infected = 0
			pass
		# if CovidModel.schedule.steps % infection_duration == 0: 
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
		for agent in self.model.grid.get_cell_list_contents(self.pos):
			if isinstance(agent, BaseHuman) and not agent.infected and not agent.recovered:
				if random.random() < self.infected:
					agent.infect("environment", self) # In the future, the initial amount may be important.

	def step(self):
		self.decay_cell()
		self.infect_agents()

class SurfaceCell(InfectableCell): # interactable at edges, cannot be entered 
	def __init__(self, unique_id, model, pos=(0,0), infected = np.double(0), transmissionLikelihood = 1, decay = 1, cleaningInterval = -1, cleaned = True):
		super().__init__(unique_id, model, pos, infected, transmissionLikelihood, decay) 
		self.cleaningInterval = cleaningInterval
		self.lastCleaned = 0
		self.cleaned = cleaned

	def step(self):
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
		super().step()
		self.ventilate()
		

	def ventilate(self):
		possible_steps = self.model.grid.get_neighborhood(
			self.pos,
			moore=True, # can move diagonaly
			include_center=False)
		targets = []
		dx, dy = 0, 0
		target = None
		while len(targets) == 0:
			rand = False # quick hack to allow random directions
			if self.ventilationDirection == -1:
				rand = True
				self.ventilationDirection = np.random.random() * np.pi * 2
			dx, dy = int(np.round(np.cos(self.ventilationDirection))), int(np.round(np.sin(self.ventilationDirection)))
			x, y = dx + self.pos[0], dy + self.pos[1]
			if rand == True:
				self.ventilationDirection = -1
			targets = [z for z in possible_steps if z == (x, y) in possible_steps]
			horiz = dx + self.pos[0], self.pos[1]
			vert = self.pos[0], self.pos[1] + dy
			if horiz not in possible_steps:
				horiz = self.pos
			if vert not in possible_steps:
				vert = self.pos
			if True in [isinstance(x, UnexposedCell) or isinstance(x, SurfaceCell) for x in self.model.grid.get_cell_list_contents(vert)] and True in [isinstance(x, UnexposedCell) or isinstance(x, SurfaceCell) for x in self.model.grid.get_cell_list_contents(horiz)]:
				targets = []
				continue
				# check to see that we aren't passing a corner.
		target = targets[0]

		part_total = 0 
		# this would make it so that amount ventilated proportional to number of agents in cell, bad idea?
		for t in self.model.grid.get_cell_list_contents(target):
			if isinstance(t, InfectableCell):
				part_total += self.infected * (1 - self.ventilationDecay)
				t.infect(self.infected * (1 - self.ventilationDecay)) # maybe make this so that the amount of particulates lost = particulate gains in other cells
			if isinstance(t, BaseHuman):
				t.infect("environment", self)
		self.infected -= part_total

class Door(SurfaceCell): # upon interaction telleports agent to other side 
	def __init__(self, unique_id, model, pos=(0,0), infected = False, transmissionLikelihood = 1, decay = 1, cleaningInterval = 1, cleaned = True):
		super().__init__(unique_id, model, pos, infected, transmissionLikelihood, decay, cleaningInterval, cleaned)

class VentilatorCell(UnexposedCell):
	def __init__(self, unique_id, model, pos=(0,0), ventilationDecay=lambda rx, ry: 1 / (np.linalg.norm([rx, ry], 2)), maxRadius = 5):
		super().__init__(unique_id,model)
		self.ventilationDecay = ventilationDecay

	def step(self):
		self.ventilate()
		

	def ventilate(self):
		# rough outline complete later
		for x in range(self.model.width):
			for y in range(self.model.height):
				rx, ry = tuple(np.array(self.pos) - np.array((x, y)))
				cont = self.model.grid.get_cell_list_contents((x, y))
				cell.cleanse(self.ventilationDecay(rx, ry))