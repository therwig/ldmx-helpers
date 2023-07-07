#!/bin/pythoAAn3
import os
import json

from LDMX.Framework import ldmxcfg
p=ldmxcfg.Process("v12")

from LDMX.SimCore import simulator
from LDMX.SimCore import generators
p.libraries.append("libSimCore.so")

### Particle Gun
myGun = generators.gun('myGun')
myGun.particle = 'e-' 
myGun.particle = 'neutron' 
myGun.position = [ 0., 0., -1.2 ]  # mm
myGun.position = [ 0., 0., 240.4 ] # mm ecal face
# myGun.position = [ 0., 0., 690.6 ] # mm back hcal face before ecal SP
myGun.direction = [ 0., 0., 1] 
myGun.energy = 1.5 # GeV

### GPS
from gps_cmds import *
gpsCmds=ele_0e500_0deg20 #ele_500e4000_5deg20 #pro_50e4000_pt0 #ele_500e4000_5deg20 #pro_50e4000_pt0 #ele_50e4000_0pt800 #neu_50e4000_pt0 #pi_50e4000_60deg
nPart=1
if nPart>1:
     gpsCmds += (nPart-1)*(['/gps/source/add 1']+gpsCmds)
     gpsCmds += ["/gps/source/multiplevertex True"]    
myGPS = generators.gps( 'myGPS' , gpsCmds )

myGen = myGun

sim = simulator.simulator("LDMX")
sim.setDetector( 'ldmx-det-v12' , True )
sim.runNumber = 0
sim.description = "Single electron gun"
sim.beamSpotSmear = [20., 80., 0.] #mm
sim.generators.append(myGen)

from LDMX.Ecal import EcalGeometry
ecal_geom = EcalGeometry.EcalGeometryProvider.getInstance()
import LDMX.Ecal.ecal_hardcoded_conditions

from LDMX.Hcal import HcalGeometry
hcal_geom = HcalGeometry.HcalGeometryProvider.getInstance()
from LDMX.Hcal import hcal_hardcoded_conditions

from LDMX.Hcal import digi as hcal_digi
hcaldigi = hcal_digi.HcalDigiProducer()
hcaldigi.hgcroc.noise = False
hcalrec = hcal_digi.HcalRecProducer()

from LDMX.Hcal import hcal_trig_digi
from LDMX.Ecal import digi  as ecal_digi
from LDMX.Ecal import vetos as ecal_vetos
from LDMX.Ecal import ecal_trig_digi

from LDMX.Trigger import trigger_cfi
trigger_seq = trigger_cfi.trigger_seq
from LDMX.Trigger import dump_file_writer

from LDMX.TrigScint.trigScint import TrigScintDigiProducer

p.sequence=[sim,hcaldigi,
            hcal_trig_digi.HcalTrigPrimDigiProducer(),
            hcalrec,
            ecal_digi.EcalDigiProducer(),
            ecal_trig_digi.EcalTrigPrimDigiProducer(),
            ecal_digi.EcalRecProducer(),
            TrigScintDigiProducer.tagger(),
            TrigScintDigiProducer.up(),
            TrigScintDigiProducer.down(),
]
p.sequence += trigger_seq

### Configurable parameters
nEvents=1000
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

p.run = seed
sim.randomSeeds = [ 2*p.run , 2*p.run+1 ]
p.outputFiles=[outfile]
p.maxEvents = nEvents

with open('parameterDump.json', 'w') as out_pamfile:
     json.dump(p.parameterDump(),  out_pamfile, indent=4)

