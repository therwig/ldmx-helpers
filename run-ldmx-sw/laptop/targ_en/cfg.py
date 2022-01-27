from LDMX.Framework import ldmxcfg
from LDMX.Biasing import target
from LDMX.SimCore import generators

# We need to create a process
#   this is the object that keeps track of all the files/processors/histograms/etc
#   the input name is a shortcode to distinguish this run
p=ldmxcfg.Process("targen")

# We need to tell the process what libraries are required
#   Here we are using a biased simulation, so we need both of those libraries
p.libraries.append("libSimCore.so")
p.libraries.append("libBiasing.so")

# We import the Ecal PN template, the two arguments allow you to specify the geometry
#   and the generator you wish to use
targ_en = target.electro_nuclear('ldmx-det-v12', generators.single_4gev_e_upstream_tagger())
targ_en.biasing_threshold = 3500.
targ_en.biasing_factor = 1
targ_en.biasing_particle = 'e-'

# set the name of the target volume
targ_en.actions[1].volume = 'target_PV'
targ_en.actions[1].recoilThreshold = 3500.

# Put the simulation into the process sequence
p.sequence=[targ_en]
print(targ_en)
for filter in targ_en.actions: print(filter)

# Give a name for the output file
p.outputFiles=['targ_en.root']

# How many events should the process simulation?
p.maxEvents = 10*1000*1000

# How frequently should the process print an update?
p.logFrequency = 100
