from LDMX.Framework import ldmxcfg
p=ldmxcfg.Process("muon")
# p=ldmxcfg.Process("")
# p.libraries.append("libSimCore.so")
# p.libraries.append("libEcal.so")

nevents = 10
energy = 4.
from LDMX.SimCore import simulator
from LDMX.SimCore import generators


myGun = generators.gun('myGun')
#myGun.particle = 'mu-'
#myGun.particle = 'neutron'
#myGun.particle = 'e-'
myGun.particle = 'proton'
# myGun.particle = 'pi-'
# myGun.position = [ 0., 0., -1.2 ]  # mm target
myGun.position = [ 0., 0., 240.4 ]  # mm ecal face
#myGun.position = [ 0., 0., 690.6 ]  # mm back hcal face (before back ecal SP)
myGun.direction = [ 0., 0., 1] 
myGun.energy = 4.0 # GeV
#myGun.energy = 2.0 # GeV
#myGun.energy = 1.0 # GeV
# myGun.energy = 40. # GeV
sim = simulator.simulator("LDMX")
sim.setDetector( 'ldmx-det-v12' , True )
sim.runNumber = 0
sim.description = "Single electron gun"
sim.beamSpotSmear = [20., 80., 0.] #mm
sim.generators.append(myGun)

# sim = simulator.simulator("single_muon")
# sim.setDetector( 'ldmx-det-v12' , True )
# sim.runNumber = 0
# sim.description = "HCal muon"
# sim.beamSpotSmear = [20., 80., 0.] #mm  
# particle_gun = generators.gun( "single_muon_upstream_target")
# particle_gun.particle = 'mu-'
# particle_gun.position = [ 0., 0., 870. ]  # mm
# particle_gun.direction = [ 0., 0., 1]
# particle_gun.energy = energy #GeV

# myGen = particle_gun
# sim.generators.append(myGen)

p.outputFiles=['out_muon_%igev_test.root'%energy]
p.maxEvents = nevents
p.logFrequency = 1

from LDMX.Ecal import EcalGeometry
ecal_geom = EcalGeometry.EcalGeometryProvider.getInstance()
import LDMX.Ecal.ecal_hardcoded_conditions

from LDMX.Hcal import HcalGeometry
hcal_geom = HcalGeometry.HcalGeometryProvider.getInstance()
#print( 'hcal_geom', hcal_geom)
#hcal_tgeom = HcalGeometry.HcalTriggerGeometryProvider.getInstance()
#print( 'hcal_geom', hcal_tgeom)
from LDMX.Hcal import hcal_hardcoded_conditions


from LDMX.Hcal import digi as hcal_digi
hcaldigi = hcal_digi.HcalDigiProducer()
hcaldigi.hgcroc.noise = False
hcalrec = hcal_digi.HcalRecProducer()

from LDMX.Hcal import hcal_trig_digi

from LDMX.Ecal import digi  as ecal_digi
from LDMX.Ecal import vetos as ecal_vetos
from LDMX.Ecal import ecal_trig_digi
# from LDMX.Hcal import hcal  as ecal_hcal
# from LDMX.EventProc.simpleTrigger import simpleTrigger
# from LDMX.EventProc.trackerHitKiller import trackerHitKiller

# from LDMX.Trigger import trigger_energy_sums
from LDMX.Trigger import trigger_cfi
trigger_seq = trigger_cfi.trigger_seq
from LDMX.Trigger import dump_file_writer


from LDMX.TrigScint.trigScint import TrigScintDigiProducer

tsDigisTag  =TrigScintDigiProducer.tagger()
# tsDigisTag.input_collection = tsDigisTag.input_collection
tsDigisUp  =TrigScintDigiProducer.up()
# #tsDigisUp.input_collection = tsDigisUp.input_collection
# tsDigisDown  =TrigScintDigiProducer.down()
#tsDigisDown.input_collection = tsDigisDown.input_collection

# ecalDigi   =digi.EcalDigiProducer('EcalDigis')
# ecalReco   =digi.EcalRecProducer('ecalRecon')
# ecalVeto   =vetos.EcalVetoProcessor('ecalVetoBDT')

p.sequence=[sim,hcaldigi,
            hcal_trig_digi.HcalTrigPrimDigiProducer(),
            hcalrec,
            ecal_digi.EcalDigiProducer(),
            ecal_trig_digi.EcalTrigPrimDigiProducer(),
            ecal_digi.EcalRecProducer(),
            TrigScintDigiProducer.tagger(),
            TrigScintDigiProducer.up(),
            TrigScintDigiProducer.down(),
            #ecal_vetos.EcalVetoProcessor(),
            # trigger adds
            # trigger_energy_sums.TriggerEcalEnergySum(),
            # trigger_energy_sums.TriggerHcalEnergySum(),
            # trigger_energy_sums.TrigEcalClusterProducer(),
            # dump_file_writer.DumpFileWriter(),
]
p.sequence += trigger_seq
