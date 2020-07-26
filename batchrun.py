import mesa_model.model
import mesa.batchrunner as br
import multiprocessing as mp
import itertools
import collections.abc
import traceback
import copy
import pandas as pd

model_reporters = {
	"Uninfected": mesa_model.model.get_infected_agents,
	"Recovered": mesa_model.model.get_recovered_agents,
	"Infected": mesa_model.model.get_uninfected_agents,
	"Quarantined of Infected": mesa_model.model.get_quarantined_agents
}


def run(fixed_params):
	global model_reporters
	print("Job: " + str(fixed_params.pop("job")))
	try:
		runner = br.BatchRunner(mesa_model.model.CovidModel, variable_parameters=fixed_params, iterations=1, max_steps=150, model_reporters=model_reporters)
		runner.run_all()
		# Note: Will return in correct order, first keys up to 'Run' will not be in correct order
		frame = runner.get_model_vars_dataframe()
		frame_v = frame.columns.values
		frame_v[0:len(fixed_params.keys())] = list(fixed_params.keys())
		frame.columns = frame_v
		return frame
	except Exception as e:
		traceback.print_exc()

def reduce(x):
	if type(x) == range:
		return list(x)
	return [x]


if __name__ == "__main__":
	threads = int(input("How many processes would you like to run: "))


	from os import listdir
	from os.path import isfile, join, splitext
	root = "mesa_model/maps/"
	maps = [x for x in listdir(root) if isfile(join(root, x)) and splitext(x)[1] == ".png"]
	print("=== Maps ===")
	for idx, x in enumerate(maps):
		print(str(idx) + ". " + x)
	map_name = maps[int(input("Map: "))]
	map_option = join(root, map_name)


	var_params = {
		"num_infec_agents": range(1, 5),
		"num_uninfec_agents": range(10, 100, 10),
		"num_rec_agents": 0,
		"mask_efficacy": 95,
		"filename": map_option
		#"mask_efficacy": range(0, 100, 5)			
			}

	# Generate all possible fixed parameters.
	fixed_params_q = []

	# Cartesian product of all values. Generate dicts with each possible k/v pair.
	n = 0
	for comb in itertools.product(*[reduce(x) for x in var_params.values()]):
		new = {}
		n += 1
		new["job"] = n
		for key, v in zip(var_params.keys(), comb):
			new[copy.deepcopy(key)] = [copy.deepcopy(v)]
		fixed_params_q.append(new)
	#

	print("Total: " + str(len(fixed_params_q)))
	with mp.Pool(processes=threads) as pool:
		res = pool.map_async(run, fixed_params_q)
		res.wait()
		frame = pd.concat(res.get())
		frame = frame.reset_index(drop=True)
		frame = frame.drop(["filename"], axis=1)
		frame.to_excel(input("Excel location: "), sheet_name=map_name)
		while True:
			try:
				print(eval(input(">>> ")))
			except Exception as e:
				traceback.print_exc()