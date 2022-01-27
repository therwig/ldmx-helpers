#!/bin/python3

import os
import sys
import json

from LDMX.Framework import ldmxcfg

p=ldmxcfg.Process("v12")
p.run = 1

import LDMX.Ecal.EcalGeometry
import LDMX.Ecal.ecal_hardcoded_conditions

from LDMX.SimCore import simulator
from LDMX.SimCore import generators
# sim = simulator.simulator("mySim")
# sim.setDetector( 'ldmx-det-v12', True  )
# sim.description = "ECal photo-nuclear, xsec bias 450"
# sim.randomSeeds = [ 2*p.run , 2*p.run+1 ]
# sim.beamSpotSmear = [20., 80., 0]
# from LDMX.SimCore import generators
# sim.generators = [ generators.single_4gev_e_upstream_tagger() ]
# sim.biasingOn(True)
# sim.biasingConfigure('photonNuclear', 'ecal', 2500., 450)
# from LDMX.Biasing import filters
# sim.actions = [ filters.TaggerVetoFilter(),
#                 filters.TargetBremFilter(),
#                 filters.EcalProcessFilter(), 
#                 filters.TrackProcessFilter.photo_nuclear() ]

p.libraries.append("libSimCore.so")

nPart=1
gpsCmds=[
     "/gps/particle e-",
     "/gps/pos/type Plane",
     "/gps/direction 0 0 1",
     # Mono energy
     # "/gps/ene/mono 4 GeV",
     # Linear energy
     "/gps/ene/type Lin",
     "/gps/ene/min 0.5 GeV",
     "/gps/ene/max 4 GeV",
     "/gps/ene/gradient 0",
     "/gps/ene/intercept 1",
     # circle
     "/gps/pos/shape Circle",
     "/gps/pos/centre 0 0 240 mm",
     "/gps/pos/radius 50 mm",
     # Square
     # "/gps/pos/shape Square",
     # "/gps/pos/centre 0 0 0 mm",
     # "/gps/pos/halfx 1 m",
     # "/gps/pos/halfy 1 m",
     # angles
     # "/gps/ang/type cos",
     # "/gps/ang/type iso",
     # "/gps/ang/mintheta 1 rad", # = pi is down the beamline
     # number of particles
     #"/gps/number "+str(nPart), # shoots at same location
]
if nPart>1:
     gpsCmds += (nPart-1)*(['/gps/source/add 1']+gpsCmds)
     gpsCmds += ["/gps/source/multiplevertex True"]
    
myGPS = generators.gps( 'myGPS' , gpsCmds )

# myGun = generators.gun('myGun')
# myGun.particle = 'e-' 
# myGun.position = [ 0., 0., -1.2 ]  # mm
# myGun.direction = [ 0., 0., 1] 
# myGun.energy = 4.0 # GeV
# myGen = myGun

myGen = myGPS

sim = simulator.simulator("SingleE")
sim.setDetector( 'ldmx-det-v12' , True )
sim.runNumber = 0
sim.description = "Single electron gun"
sim.randomSeeds = [ 2*p.run , 2*p.run+1 ]
#sim.beamSpotSmear = [20., 80., 0.] #mm
sim.beamSpotSmear = [0., 0., 0.] #mm
#sim.beamSpotSmear = [10., 10., 0.] #mm
sim.generators.append(myGen)


# from LDMX.EventProc.trigScintDigis import TrigScintDigiProducer
# tsDigisUp   = TrigScintDigiProducer.up()
# tsDigisTag  = TrigScintDigiProducer.tagger()
# tsDigisDown = TrigScintDigiProducer.down()

# #set the PE response to 100 (default is 10, too low)
# tsDigisUp.pe_per_mip   = 100.
# tsDigisTag.pe_per_mip  = tsDigisUp.pe_per_mip
# tsDigisDown.pe_per_mip = tsDigisUp.pe_per_mip

from LDMX.Ecal import digi
from LDMX.Ecal import ecal_trig_digi
#from LDMX.Ecal import vetos
#from LDMX.EventProc import hcal
from LDMX.EventProc.simpleTrigger import simpleTrigger 
from LDMX.EventProc.trackerHitKiller import trackerHitKiller
p.sequence=[ sim, 
             digi.EcalDigiProducer(),
             ecal_trig_digi.EcalTrigPrimDigiProducer(),
             digi.EcalRecProducer(), 
             #        vetos.EcalVetoProcessor(),
             #hcal.HcalDigiProducer(),
             #hcal.HcalVetoProcessor(), 
             #tsDigisUp, tsDigisTag, tsDigisDown, 
             trackerHitKiller, 
             simpleTrigger, 
             ldmxcfg.Producer('finableTrack','ldmx::FindableTrackProcessor','EventProc'),
             ldmxcfg.Producer('trackerVeto' ,'ldmx::TrackerVetoProcessor'  ,'EventProc')
]

p.outputFiles=["simoutput_{}ecal_electron.root".format(nPart)]
p.maxEvents = 10*1000
p.maxEvents = 10*10
with open('parameterDump.json', 'w') as outfile:
     json.dump(p.parameterDump(),  outfile, indent=4)

