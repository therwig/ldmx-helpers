#!/bin/python3
import os
import json

from LDMX.Framework import ldmxcfg

# Create a process with pass name "recon"
p=ldmxcfg.Process('TriggerAna')

import LDMX.Ecal.EcalGeometry
import LDMX.Ecal.ecal_hardcoded_conditions

from LDMX.Analysis import trigger
trigger_ana = trigger.TriggerAnalyzer("TriggerNtuplizer")

from LDMX.Analysis import clusterConfigs
ccfg = clusterConfigs.allConfigs
trigger_ana.AddConfigs(ccfg)

trigger_ana.nEle=1
trigger_ana.storeTargetSPHit  = True
trigger_ana.storeECalSPHit    = True
trigger_ana.storeECalTrigDigi = False
trigger_ana.storeECalRecHit   = False
trigger_ana.storeECalSimHit   = False
trigger_ana.runAnalysis       = False

# Define the order in which the analyzers will be executed.
p.sequence=[trigger_ana]

def div_round_up(n,d): return (n+d-1)//d

nEvents=100
outfile='out.root'
nJobs=1
jobNo=0
infiles=[]
env = os.environ
if 'BATCH_NEVENTS' in env: nEvents = int(env['BATCH_NEVENTS'])
if 'BATCH_OUTFILE' in env: outfile = env['BATCH_OUTFILE']
if 'BATCH_NJOBS' in env: nJobs     = int(env['BATCH_NJOBS'])
if 'LSB_JOBINDEX' in env: jobNo    = int(env['LSB_JOBINDEX'])-1
if os.path.exists("filelist.py"):
    from filelist import filelist
    files_per_job = div_round_up(len(filelist),nJobs)
    infiles = filelist[jobNo*files_per_job: (jobNo+1)*files_per_job]

p.inputFiles    = infiles
p.histogramFile = outfile
p.maxEvents     = nEvents

with open('parameterDump.json', 'w') as out_pamfile:
     json.dump(p.parameterDump(),  out_pamfile, indent=4)
