#!/bin/python3
import os
import json

from LDMX.Framework import ldmxcfg

p=ldmxcfg.Process("v12")
p.libraries.append("libSimCore.so")
p.libraries.append("libEcal.so")


from LDMX.SimCore import simcfg
from LDMX.SimCore import simulator
from LDMX.SimCore import generators
#from LDMX.Biasing import filters


### Particle Gun
myGun = generators.gun('myGun')
myGun.particle = 'e-' 
myGun.position = [ 0., 0., -1.2 ]  # mm
myGun.direction = [ 0., 0., 1] 
myGun.energy = 4.0 # GeV

sim = simulator.simulator("SingleE")

from LDMX.Detectors.makePath import makeDetectorPath
sim.detector = makeDetectorPath( "ldmx-det-v12" )

# sim.setDetector( 'ldmx-det-v12' , True )
# sim.runNumber = 0
sim.description = "Single electron gun"
sim.beamSpotSmear = [20., 80., 0.] #mm
sim.generators.append(myGun)

import LDMX.Ecal.EcalGeometry
import LDMX.Ecal.ecal_hardcoded_conditions

from LDMX.Ecal import digi
from LDMX.Ecal import vetos
from LDMX.Hcal import hcal
from LDMX.EventProc.simpleTrigger import simpleTrigger
from LDMX.EventProc.trackerHitKiller import trackerHitKiller
from LDMX.TrigScint.trigScint import TrigScintDigiProducer


tsDigisTag  =TrigScintDigiProducer.tagger()
#tsDigisTag.input_collection = tsDigisTag.input_collection
tsDigisUp  =TrigScintDigiProducer.up()
#tsDigisUp.input_collection = tsDigisUp.input_collection
tsDigisDown  =TrigScintDigiProducer.down()
#tsDigisDown.input_collection = tsDigisDown.input_collection

ecalDigi   =digi.EcalDigiProducer('EcalDigis')
ecalReco   =digi.EcalRecProducer('ecalRecon')
ecalVeto   =vetos.EcalVetoProcessor('ecalVetoBDT')

from LDMX.Hcal import HcalGeometry
geom = HcalGeometry.HcalGeometryProvider.getInstance()
from LDMX.Hcal import hcal_hardcoded_conditions
from LDMX.Hcal import digi
hcaldigi = digi.HcalDigiProducer()
hcaldigi.hgcroc.noise = False
hcalrec = digi.HcalRecProducer()

p.sequence=[ sim,
             ecalDigi, ecalReco, ecalVeto, 
             tsDigisTag, tsDigisUp, tsDigisDown,
             hcaldigi,hcalrec
]


### Configurable parameters
nEvents=100
seed=0
outfile='out.root'
env = os.environ
if 'BATCH_SEEDOFFSET' in env: seed += int(env['BATCH_SEEDOFFSET'])
if 'LSB_JOBINDEX' in env: seed += int(env['LSB_JOBINDEX'])
if 'BATCH_NEVENTS' in env: nEvents = int(env['BATCH_NEVENTS'])
if 'BATCH_OUTFILE' in env: outfile = env['BATCH_OUTFILE']
     
print('Setting random seed to:', seed)
print('Processing #events:', nEvents)
print('Writing output file to:', outfile)

#p.run = seed
#sim.randomSeeds = [ 2*p.run , 2*p.run+1 ]
p.outputFiles=[outfile]
p.maxEvents = nEvents

with open('parameterDump.json', 'w') as out_pamfile:
     json.dump(p.parameterDump(),  out_pamfile, indent=4)

