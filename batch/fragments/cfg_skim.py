#!/bin/python3
import os
import json
import glob

from LDMX.Framework import ldmxcfg

# Create a process with pass name "recon"
p=ldmxcfg.Process('skim')

p.sequence=[]

p.keep = [
    "drop Trigger.*",
    "drop Tagger.*",
    "drop Target.*",
    "drop Hcal.*",
    "drop Magnet.*",
    "drop Recoil.*",
    "drop Tracker.*",
]

def div_round_up(n,d): return (n+d-1)//d

nEvents=-1
outfile='skim.root'
nJobs=1
jobNo=0
infiles=[]
env = os.environ
if 'BATCH_NEVENTS' in env: nEvents = int(env['BATCH_NEVENTS'])
if 'BATCH_OUTFILE' in env: outfile = env['BATCH_OUTFILE']
if 'BATCH_NJOBS' in env: nJobs     = int(env['BATCH_NJOBS'])
if 'LSB_JOBINDEX' in env: jobNo    = int(env['LSB_JOBINDEX'])-1
infiles = glob.glob('input_files/*.root')

print("Running over",len(infiles),"files")
p.inputFiles    = infiles
p.maxEvents     = nEvents
p.outputFiles=[outfile]

with open('parameterDump.json', 'w') as out_pamfile:
     json.dump(p.parameterDump(),  out_pamfile, indent=4)
