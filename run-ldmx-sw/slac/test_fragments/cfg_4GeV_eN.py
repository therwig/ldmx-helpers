#!/bin/python3
import os
import json

from LDMX.Framework import ldmxcfg

p=ldmxcfg.Process("v12")

import LDMX.Ecal.EcalGeometry
import LDMX.Ecal.ecal_hardcoded_conditions

from LDMX.SimCore import simulator
from LDMX.SimCore import generators
from LDMX.Biasing import target
p.libraries.append("libSimCore.so")

targ_en = target.electro_nuclear('ldmx-det-v12', generators.single_4gev_e_upstream_tagger())
targ_en.biasing_threshold = 3500.
targ_en.biasing_factor = 1
targ_en.biasing_particle = 'e-'
targ_en.actions[1].volume = 'target_PV'
targ_en.actions[1].recoilThreshold = 3500.
sim = targ_en


from LDMX.Ecal import digi
from LDMX.Ecal import ecal_trig_digi
from LDMX.EventProc.simpleTrigger import simpleTrigger 
from LDMX.EventProc.trackerHitKiller import trackerHitKiller
p.sequence=[ sim,
             digi.EcalDigiProducer(),
             ecal_trig_digi.EcalTrigPrimDigiProducer(),
             digi.EcalRecProducer(),
             trackerHitKiller,
             simpleTrigger,
             ldmxcfg.Producer('finableTrack','ldmx::FindableTrackProcessor','EventProc'),
             ldmxcfg.Producer('trackerVeto' ,'ldmx::TrackerVetoProcessor'  ,'EventProc')
]


### Configurable parameters
 # 1M for 20 events in 10 minutes
nEvents=1000*1000
seed=1
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

