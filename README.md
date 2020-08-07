# altREU COVID-19 Modeling

<p align="center">
<img src="https://raw.githubusercontent.com/bcwarner/covid-modeling/master/docs/screenshot1.png" width="400px">
</p>

## Abstract

One of the foremost problems regarding the COVID-19 pandemic is the issue of reopening tertiary schools while minimizing the transmission of coronavirus. Limited options exist for evaluating the effectiveness of policies that might be utilized at tertiary institutions, as empirical data does not exist yet. Agent-based modeling, where various entities that would be found in an environment are simulated as agents, offers an opportunity to examine the effectiveness of various policies in a way that drastically minimizes the health and economic risks involved. In this project, we utilized agent-based modeling to examine the efficacy of various protocols that might be implemented to reduce the spread of SARS-CoV-2, such as mask adoption, limited classroom hours, cleaning, quarantining upon infection, and so on. From this we measured the amount of agents that were infected, the average basic reproduction number for agents, among several other basic measures. We found that reducing the number of people in the classroom, as well as the number of hours spent in the classroom had the strongest effects on reducing the basic reproduction number and the peak at which people were infected. Due to time constraints, several protocols were not tested, as well as several forms of measurement, which further agent-based research may be able to evaluate.

## Usage

This model primarily requires SciPy, Mesa and PIL to run, but for the entire repository, other packages are needed. Upon installation of the requisite packages, the graphical visualization can be run using `mesa runserver`. For batch runs, paramaters can be adjusted by modifying `batchrun.py` and then using `python batchrun.py`.

## Acknowledgements 

Special thanks to Christof Teuscher and MacKenzie Gray for making the Portland State altREU program possible, for without which this project would not have happened. Thanks to Lisa Marriott at OHSU for mentoring us as we developed this project. Finally, thanks to Wayne Wakeland, Alexander York, and Merlin Carson for assistance with the development of our model.
