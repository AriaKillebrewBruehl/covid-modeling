import mesa_model.model
import mesa.batchrunner as br
import multiprocessing as mp
import itertools
import collections.abc
import traceback
import copy
import pandas as pd
import pickle

model_reporters = {
	"length": lambda x: x.schedule.steps
	"dataframe": mesa_model.model.get_dataframe
}


def run(fixed_params):
	global model_reporters
	print("Job: " + str(fixed_params.pop("job")))
	try:
		runner = br.BatchRunner(mesa_model.model.CovidModel, variable_parameters=fixed_params, iterations=5, max_steps=5000, model_reporters=model_reporters)
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
		"num_infec_agents": 1, #range(1, 5),
		"num_uninfec_agents": 20, #range(10, 100, 10),
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
	out = None
	with mp.Pool(processes=threads) as pool:
		res = pool.map_async(run, fixed_params_q)
		pool.close()
		pool.join()

	out = res.get()
	avg_frames = []
	for run_frame in out:
		# Each entry is a single frame with all results of BatchRunner with last column being frames of individual runs.
		avg_frame = pickle.loads(run_frame["dataframe"][0])
		avg_frame[:] = 0
		# Average of all datacollector frames
		params = list(run_frame.iloc[0][0:len(var_params)])
		dc_frames = [pickle.loads(run_frame["dataframe"][i]) for i in range(len(run_frame["dataframe"]))]
		max_len = max([x.shape[0] for x in dc_frames])
		avg_frame = avg_frame.append(avg_frame.iloc[[-1] * (max_len - avg_frame.shape[0])]).reset_index(drop=True)

		for dc_frame in dc_frames:
			# Question: what do we do with dataframes that have varying sizes?
			print(dc_frame.shape)
			dc_frame = dc_frame.append(dc_frame.iloc[[-1] * (max_len - dc_frame.shape[0])]).reset_index(drop=True)
			print(dc_frame.shape)
			avg_frame += dc_frame / len(dc_frames)
		avg_frames.append((params, avg_frame))

	frame = pd.concat(res.get())
	frame = frame.reset_index(drop=True)
	frame = frame.drop(["filename", "dataframe"], axis=1)
	res = False
	while res == False:
		try:
			with pd.ExcelWriter(input("Excel location: ")) as excel:
				frame.to_excel(excel, sheet_name=map_name)
				for x in avg_frames:
					x[1].to_excel(excel, sheet_name="-".join([str(y).replace("/", "_") for y in x[0][:-1]]))
			res = True
		except Exception as e:
			print(e)