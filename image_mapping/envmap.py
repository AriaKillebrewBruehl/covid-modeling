""" Environment Map Class for storing information about the simulation
    environment. Contains lists of environmental features in the form of
    (x, y) coordinate pairs. """

class EnvMap:
    """ Container entity for environmental features. """
    def __init__(self, width, height, air, surface, dead,
                doors, windows, handwash, arrival, other):
        self.width = width       # x resolution
        self.height = height     # y resolution
        self.air = air           # list of air cells
        self.surface = surface   # list of contactable surface cells
        self.dead = dead         # list of inaccessible environment cells
        self.doors = doors       # list of doors
        self.windows = windows   # list of windows
        self.handwash = handwash # list of handwashing stations
        self.arrival = arrival   # list of arrival/departure cells
        self.other = other       # list of unknown cells (errors?)
        return
