from LDMX.Framework import ldmxcfg
p = ldmxcfg.Process('test')

from LDMX.SimCore import simulator as sim
mySim = sim.simulator( "mySim" )
mySim.setDetector( 'ldmx-det-v14' )
from LDMX.SimCore import generators as gen
mySim.generators.append( gen.single_4gev_e_upstream_tagger() )
mySim.beamSpotSmear = [20.,80.,0.]
mySim.description = 'Basic test Simulation'

p.sequence = [ mySim ]

##################################################################
# Below should be the same for all sim scenarios

import os
import sys

p.run = 1 #int(os.environ['LDMX_RUN_NUMBER'])
p.maxEvents = 10 #int(os.environ['LDMX_NUM_EVENTS'])

p.histogramFile = 'hist.root'
p.outputFiles = ['events.root']

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
trigger_seq = [
    trigger_energy_sums.EcalTPSelector(),
    trigger_energy_sums.TrigEcalEnergySum(),
    trigger_energy_sums.TrigHcalEnergySum(),
    trigger_energy_sums.TrigEcalClusterProducer(),
]

# from LDMX.Hcal import hcal # HcalTestProcessor

p.sequence.extend([
        ecal_digi.EcalDigiProducer(),
        ecal_trig_digi.EcalTrigPrimDigiProducer(),
        ecal_digi.EcalRecProducer(), 
        ecal_vetos.EcalVetoProcessor(),
        hcal_digi.HcalDigiProducer(),
        hcal_trig_digi.HcalTrigPrimDigiProducer(),
        hcal_digi.HcalRecProducer(),
        # trigger_energy_sums.TrigEcalEnergySum(),
        # trigger_energy_sums.Tester(), #
        # trigger_energy_sums.TriggerTestProcessor(), 
        # hcal_trig_digi.HcalTestProcessor(), # this works
        # hcal.HcalTestProcessor(),
        # trigger_energy_sums.Tester(), #
        # trigger_energy_sums.TrigEcalEnergySum(), #
        # *ts_digis,
        # TrigScintClusterProducer.pad1(),
        # TrigScintClusterProducer.pad2(),
        # TrigScintClusterProducer.pad3(),
        # trigScintTrack,
        # count, TriggerProcessor('trigger')
        ] + trigger_seq ) # + dqm.all_dqm + trigger_seq)

p.pause()
