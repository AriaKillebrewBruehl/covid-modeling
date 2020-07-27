from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation #RandomActivation
from mesa import Model
import numpy as numpy
import numpy.linalg
from mesa_model.converter import *
from PIL import Image
import itertools
import random

# CONSTANTS --------------------
max_caution_level = 2
percent_immunocompromised = 0.05 # 5 % of population is immunocomprimised 
# ------------------------------
from PIL import Image

from mesa_model.agents import *
from mesa_model.converter import convert

def get_infected_agents(model):
	return len([x for x in model.humans if x.infected == True])

def get_recovered_agents(model):
	return len([x for x in model.humans if x.recovered == True])

def get_uninfected_agents(model):
	return len([x for x in model.humans if x.recovered == False and x.infected == False])

def get_quarantined_agents(model):
	return len([x for x in model.humans if x.quarantined == True])


# WARNING: VERY EXPENSIVE
def get_average_distance(model):
	acc = 0
	count = 0
	for x in itertools.product(model.humans, model.humans):
		if x[0].pos is None or x[1].pos is None:
			continue # Skip ones not on map
		count += 1
		acc += numpy.linalg.norm(numpy.array(x[0].pos) - numpy.array(x[1].pos))
	return acc / count

def get_avg_min_distance(model):
	mins = {}
	for x in itertools.product(model.humans, model.humans):
		if x[1].unique_id == x[0].unique_id:
			continue
		if x[0].pos is None or x[1].pos is None:
			continue # Skip ones not on map

		if x[0].unique_id not in mins:
			mins[x[0].unique_id] = numpy.inf
		if x[1].unique_id not in mins:
			mins[x[1].unique_id] = numpy.inf

		dist = numpy.linalg.norm(numpy.array(x[0].pos) - numpy.array(x[1].pos))
		if mins[x[0].unique_id] > dist:
			mins[x[0].unique_id] = dist
		if mins[x[1].unique_id] > dist:
			mins[x[1].unique_id] = dist
	vs = mins.values()
	return sum(x for x in vs) / len(vs)

class CovidModel(Model):
	def size(filename):
		return Image.open(filename).size

	def __init__(self, filename, num_infec_agents=20, num_uninfec_agents=20, num_rec_agents=20, mask_efficacy=95, passing = True, steps_per_hour = 600, hours = 0, days = 1):
		im = Image.open(filename) # open image file
		self.surfaces = []
		self.surface_pos = []
		self.entrances = []
		self.entrance_pos = []
		self.humans = []
		self.filename = filename
		self.width, self.height = im.size # Get the width and height of the image to iterate over
		self.schedule = RandomActivation(self) # Is this the best choice for agent activation? If not may need more implementation later.
		self.grid = MultiGrid(width=self.width, height=self.height, torus=False) # last arg prevents wraparound
		self.mask_efficacy = mask_efficacy / 100
		self.passing = passing
		self.steps_per_hour = steps_per_hour
		self.hours = hours
		self.days = days
		self.datacollector = DataCollector(
			model_reporters={
				"Uninfected": get_uninfected_agents,
				"Recovered": get_recovered_agents,
				"Infected": get_infected_agents,
				"Quarantined of Infected": get_quarantined_agents,
				"Average Distance": get_average_distance,
				"Average Nearest Distance": get_avg_min_distance
			},
			agent_reporters={
			#	"Uninfected": lambda x: x.infected == False and x.recovered == False,
			#	"Infected": lambda x: x.infected == True,
			#	"Recovered": (add later)
			}
			)

		convert(filename, self, self.surfaces, self.entrances) # convert environment, create position lists
		for surface in self.surfaces:
			self.surface_pos.append(surface.pos)
		for entrance in self.entrances:
			self.entrance_pos.append(entrance.pos)

		# Initialize agents here
		def setup_agent(ag_type):
			pos = random.choice(self.entrance_pos) # start agents at entrance
			seat = random.choice(self.surfaces) # get random goal postion for agent 
			self.surfaces.remove(seat) # make goal position unique
			next_pos = seat.pos
			new_human = Student(new_id(), self, pos=pos, next_pos = next_pos, seat = seat) # create new Student agent 
			if ag_type == "uninfec":
				new_human.infected, new_human.recovered = False, False # set state of agent 
			elif ag_type == "infec":
				new_human.init_infect() # needs deliberate setup
			elif ag_type == "rec":
				new_human.infected, new_human.recovered = False, True
			# new_human.quarantined = False
			new_human.caution_level = random.randint(0, max_caution_level) # create agents of different caution levels
			if new_human.caution_level == 0:
				new_human.masked = False
			elif new_human.caution_level == 1:
				new_human.masked = True
			elif new_human.caution_level == 2:
				new_human.masked = True
			if random.random() < percent_immunocompromised: # create immunocomprimised agents
				new_human.immunocompromised = True
			else:
				new_human.immunocompromised = False
			self.grid.place_agent(new_human, pos) # place agent on grid 
			self.schedule.add(new_human) # add agent to schedule
			self.humans.append(new_human)

		for agents in range(num_uninfec_agents):
			setup_agent("uninfec",)
		for agents in range(num_infec_agents):
			setup_agent("infec",)
		for agents in range(num_rec_agents):
			setup_agent("rec",)

		self.running = True
	
	def check_arrival(self, destination): # check if all agents are in seats
		arrived = False
		for human in self.humans:
			if not human.quarantined: # only check agents at class
					if destination == "seats":
						if not human.arrived or not human.pos in self.surface_pos:
							arrived = False
							break
						else:
							arrived = True
					elif destination == "exit":
						if not human.arrived or not human.pos in self.entrance_pos:
							arrived = False
							break
						else:
							arrived = True
		return arrived

	def check_agents(self): # check which agents will become quarantined 
		for human in self.humans:
			if human.infected and human.symptomatic and human.caution_level > 0 and not human.quarantined: # if cautious person and symptomatic quarantine
				human.quarantine()
				print("quarantined " + str(human.unique_id) + " on step" + str(self.schedule.steps)) 

	def leave(self): # update agents to leave classroom
		for human in self.humans:
			human.next_pos = random.choice(self.entrance_pos) # set scheduled position to entrance
	
	def clean_grid(self):
		for pos in self.surface_pos:
				for x in self.grid.get_cell_list_contents(pos):
					x.cleanse(1.0)
		for pos in self.entrance_pos:
				for x in self.grid.get_cell_list_contents(pos):
					if isinstance(x, BaseEnvironment):
						x.cleanse(1.0)
		print("cleaned")
	
	def reset(self): # reset scheduled position to seat
		for human in self.humans:
			human.next_pos = human.seat.pos

	def step(self):
		if self.check_arrival("seats"): # if all agents have arrived class has "started"
			self.passing = False # "passing period" ends, "class" begins 
		if self.passing:
			self.steps_per_hour = 600 # move every 6 sec during passing period
		else:
			self.steps_per_hour = 12 # move every 5 minutes during class 
		if not self.passing:
			self.hours += 1 / self.steps_per_hour # add time to class hours
			if self.hours % 3 < 0.001: # after a 3 hour class 
				self.leave() # move agents off grid
				self.passing = True # passing period begins again
		if self.check_arrival("exit"): # if all agents have left
			self.check_agents() # agents check selves for symptoms
			self.clean_grid() # clean grid
			self.hours = 0 # reset class hours
			self.days += 1 # number of days of class increases
			self.reset() # update scheduled position
		print("a(s): " + str(self.check_arrival("seats")) + " a(e): " + str(self.check_arrival("exit")) + ", s_p_h: " + str(self.steps_per_hour) + ", h: " + str(self.hours) + ", d: " + str(self.days) + ", s: " + str(self.schedule.steps))
		self.schedule.step()
		self.datacollector.collect(self)
	
	def run_model(self):
		#print("Rt: " + self.run_time)
		for i in range(self.run_time):
			self.step()

'''
		def rand_pos():
			pos = random.randrange(self.width), random.randrange(self.height)  # get new position for agent w/in bounds of grid
			if True not in [isinstance(x, UnexposedCell) for x in self.grid.get_cell_list_contents(pos)]:
				return pos
			else:
				return rand_pos()

		def create_pos(rows, cols): # create list of tuples of scheduled positions
			sched_pos = []
			base_X, base_Y = 4, 4 # (base_X, base_Y) is coordinate of upper-left most agent 
			sep = numpy.round((self.width - (2 * base_X) - cols) / (cols - 1))
			for i in range(rows): # for each row 
				for j in range(cols): # for each column 
					pos = (0, base_X + j*sep, 32 - base_Y - (i*sep)) # 32 - because upper left corner is (0, 32)
					sched_pos.append(pos)
			return sched_pos
'''