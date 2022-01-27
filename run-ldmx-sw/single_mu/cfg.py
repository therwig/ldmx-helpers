from LDMX.Framework import ldmxcfg
from LDMX.Biasing import target
from LDMX.SimCore import generators
from LDMX.SimCore import simulator

# We need to create a process
#   this is the object that keeps track of all the files/processors/histograms/etc
#   the input name is a shortcode to distinguish this run
p=ldmxcfg.Process("HCal_Mu")

# We need to tell the process what libraries are required
#   Here we are using a biased simulation, so we need both of those libraries
p.libraries.append("libSimCore.so")

# Single particle gun
myGun = generators.gun('myGun')
myGun.particle = 'mu-' 
myGun.position = [ 0., 0., -1.2 ]  # mm
myGun.direction = [ 0., 0., 1] 
myGun.energy = 4.0 # GeV

# 3.1415 * 3/4 = 2.356
# http://geant4-userdoc.web.cern.ch/geant4-userdoc/UsersGuides/ForApplicationDeveloper/html/GettingStarted/generalParticleSource.html
myGPS = generators.gps( 'myGPS' , [
    "/gps/particle mu-",
    "/gps/pos/type Plane",
    "/gps/pos/shape Square",
    "/gps/pos/centre 0 0 0 mm",
    "/gps/pos/halfx 1 m",
    "/gps/pos/halfy 1 m",
    # "/gps/ang/type cos",
    "/gps/ang/type iso",
    "/gps/ang/mintheta 1 rad", # = pi is down the beamline
    "/gps/ene/mono 4 GeV",
    # "/gps/ene/type Lin",
    # "/gps/ene/min 3 GeV",
    # "/gps/ene/max 4 GeV",
    # "/gps/ene/gradient 1",
    # "/gps/ene/intercept 1"
    ] )

#myGen = myGPS
myGen = myGun
 
# Instantiate the sim.
sim = simulator.simulator("HCal_Single_Mu")

# Set the path to the detector to use.
#   Also tell the simulator to include scoring planes
sim.setDetector( 'ldmx-det-v12' , True )

# Set run parameters
sim.runNumber = 0
sim.description = "Single muon gun for hcal tests"
sim.randomSeeds = [ 1, 2 ]
sim.beamSpotSmear = [20., 80., 0.] #mm

sim.generators.append(myGen)


# # We import the Ecal PN template, the two arguments allow you to specify the geometry
# #   and the generator you wish to use
# targ_en = target.electro_nuclear('ldmx-det-v12', generators.single_4gev_e_upstream_tagger())
# targ_en.biasing_threshold = 3500.
# targ_en.biasing_factor = 1
# targ_en.biasing_particle = 'mu-'

# # set the name of the target volume
# targ_en.actions[1].volume = 'target_PV'
# targ_en.actions[1].recoilThreshold = 3500.

# Put the simulation into the process sequence
p.sequence=[sim]
print(sim)
for filt in sim.actions: print(filt)

# Give a name for the output file
p.outputFiles=['hcal_mu.root']

# How many events should the process simulation?
p.maxEvents = 100

# How frequently should the process print an update?
p.logFrequency = 100
