#!/usr/bin/python

from LDMX.Framework import ldmxcfg
from LDMX.Biasing import target
from LDMX.SimCore import generators
from LDMX.SimCore import simulator

# We need to create a process
#   this is the object that keeps track of all the files/processors/histograms/etc
#   the input name is a shortcode to distinguish this run
p=ldmxcfg.Process("SingleE")

# We need to tell the process what libraries are required
#   Here we are using a biased simulation, so we need both of those libraries
p.libraries.append("libSimCore.so")

# Single particle gun
myGun = generators.gun('myGun')
myGun.particle = 'e-' 
myGun.position = [ 0., 0., -1.2 ]  # mm
myGun.direction = [ 0., 0., 1] 
myGun.energy = 4.0 # GeV

myGen = myGun

# Instantiate the sim.
sim = simulator.simulator("SingleE")

# Set the path to the detector to use.
#   Also tell the simulator to include scoring planes
sim.setDetector( 'ldmx-det-v12' , True )

# Set run parameters
sim.runNumber = $run
sim.description = "Single electron gun"
sim.randomSeeds = [ $seed1, $seed2 ]
sim.beamSpotSmear = [20., 80., 0.] #mm

sim.generators.append(myGen)

# Put the simulation into the process sequence
p.sequence=[sim]

# Give a name for the output file
#p.outputFiles=['single_e.root']
p.outputFiles=[ "$outputEventFile" ]

# How many events should the process simulation?
p.maxEvents = 40*1000

# How frequently should the process print an update?
p.logFrequency = 10
