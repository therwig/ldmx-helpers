from LDMX.Framework import ldmxcfg
p = ldmxcfg.Process('trig')

# from LDMX.SimCore import simulator as sim
# mySim = sim.simulator( "mySim" )
# mySim.setDetector( 'ldmx-det-v14' )
# from LDMX.SimCore import generators as gen
# mySim.generators.append( gen.single_4gev_e_upstream_tagger() )
# mySim.beamSpotSmear = [20.,80.,0.]
# mySim.description = 'Basic test Simulation'

# p.sequence = [ mySim ]

##################################################################
# Below should be the same for all sim scenarios

import os, sys
from glob import glob

p.run = 1 #int(os.environ['LDMX_RUN_NUMBER'])
p.maxEvents = -1 #int(os.environ['LDMX_NUM_EVENTS'])
p.logFrequency = 1000
p.termLogLevel = 1 # default is 2 (WARNING); but then logFrequency is ignored. level 1 = INFO.

p.histogramFile = 'hist.root'
# p.outputFiles = ['/scratch/therwig/events.root']
p.outputFiles = ['events.root']
# p.outputFiles = [] 
p.inputFiles = ['input.root']
# p.inputFiles = ['data/trig/ele_500e4000_5deg20_50k.trig.root']
# p.inputFiles = glob('/scratch/therwig/events_*.root')
# print (p.inputFiles)
# p.inputFiles = ['/sdf/group/ldmx/data/validation/v14/4.0GeV/v3.2.0-1e-v14/mc_v14-4.0GeV-1e-inclusive_run10100_t1671176585.root']
# p.inputFiles = ['/sdf/group/ldmx/data/validation/v14/4.0GeV/Ap1GeV-1e-v3.2.0-v14/mc_v14-4.0GeV-1e-signal_W_noDecay_sim_run10000093_t1671224260.root']

import LDMX.Ecal.EcalGeometry
import LDMX.Ecal.ecal_hardcoded_conditions
import LDMX.Hcal.HcalGeometry
import LDMX.Hcal.hcal_hardcoded_conditions
import LDMX.Ecal.digi as ecal_digi
import LDMX.Ecal.vetos as ecal_vetos
import LDMX.Hcal.digi as hcal_digi

from LDMX.TrigScint.trigScint import TrigScintDigiProducer
from LDMX.TrigScint.trigScint import TrigScintClusterProducer
from LDMX.TrigScint.trigScint import trigScintTrack
ts_digis = [
        TrigScintDigiProducer.pad1(),
        TrigScintDigiProducer.pad2(),
        TrigScintDigiProducer.pad3(),
        ]
for d in ts_digis :
    d.randomSeed = 1

from LDMX.DQM import dqm

from LDMX.Recon.electronCounter import ElectronCounter
from LDMX.Recon.simpleTrigger import TriggerProcessor

count = ElectronCounter(1,'ElectronCounter')
count.input_pass_name = ''

# from LDMX.Trigger import trigger_cfi
# trigger_seq = trigger_cfi.trigger_seq

from LDMX.Hcal import hcal_trig_digi
from LDMX.Ecal import ecal_trig_digi
from LDMX.Trigger import trigger_energy_sums
ntup = trigger_energy_sums.NtupleWriter()
ntup.outPath='ntuple.root'
# ntup.outPath='/scratch/therwig/ntuple.root'

hcal_sum = trigger_energy_sums.TrigHcalEnergySum()
hcal_sum.inputProc = p.passName # use TPs from this step
# print("TAg IS", hcal_sum.inputProc)

trigger_preseq = [ # for wes' genie samples
    
]
trigger_seq = [
    # primitives
    ecal_trig_digi.EcalTrigPrimDigiProducer(),
    hcal_trig_digi.HcalTrigPrimDigiProducer(),
    trigger_energy_sums.EcalTPSelector(),
    trigger_energy_sums.TrigEcalEnergySum(),
    trigger_energy_sums.TrigEcalClusterProducer(),
    # hcal trigger
    hcal_sum,
    # trigger_energy_sums.TrigHcalEnergySum(),
    # global
    trigger_energy_sums.TrigElectronProducer(),
    ntup
    # trigger_energy_sums.NtupleWriter(outPath='/scratch/therwig/ntuple.root'),
]
p.sequence = trigger_seq
# p.sequence = [ntup]
# p.sequence = [ trigger_energy_sums.PropagationMapWriter() ]

p.keep = [ 
    "drop .*SimHits.*",
    "drop EcalDigi.*",
    "drop HcalDigi.*",
    "drop SimParticles_sim.*",
    # "drop .*Veto.*",
    # "drop .*Veto.*",
]

# # from LDMX.Hcal import hcal # HcalTestProcessor

# p.sequence.extend([
#         ecal_digi.EcalDigiProducer(),
#         ecal_digi.EcalRecProducer(), 
#         ecal_vetos.EcalVetoProcessor(),
#         hcal_digi.HcalDigiProducer(),
#         hcal_digi.HcalRecProducer(),
#         # trigger_energy_sums.TrigEcalEnergySum(),
#         # trigger_energy_sums.Tester(), #
#         # trigger_energy_sums.TriggerTestProcessor(), 
#         # hcal_trig_digi.HcalTestProcessor(), # this works
#         # hcal.HcalTestProcessor(),
#         # trigger_energy_sums.Tester(), #
#         # trigger_energy_sums.TrigEcalEnergySum(), #
#         # *ts_digis,
#         # TrigScintClusterProducer.pad1(),
#         # TrigScintClusterProducer.pad2(),
#         # TrigScintClusterProducer.pad3(),
#         # trigScintTrack,
#         # count, TriggerProcessor('trigger')
#         ] + trigger_seq ) # + dqm.all_dqm + trigger_seq)

# p.pause()
