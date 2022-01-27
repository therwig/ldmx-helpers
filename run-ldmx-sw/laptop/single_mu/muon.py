from LDMX.Framework import ldmxcfg
p=ldmxcfg.Process("muon")
# p.libraries.append("libSimCore.so")
# p.libraries.append("libEcal.so")

nevents = 100*1000
energy = 4.
from LDMX.SimCore import simulator
from LDMX.SimCore import generators


myGun = generators.gun('myGun')
myGun.particle = 'mu-'
#myGun.position = [ 0., 0., -1.2 ]  # mm
myGun.position = [ 0., 0., 235 ]  # mm
myGun.direction = [ 0., 0., 1] 
myGun.energy = 4.0 # GeV

myGPS = generators.gps( 'myGPS' , [
    "/gps/particle mu-",
    "/gps/pos/type Plane",
    "/gps/pos/shape Square",
    "/gps/pos/centre 0 0 235 mm",
    "/gps/pos/halfx 0.001 m",
    "/gps/pos/halfy 0.001 m",
    # "/gps/ang/type cos",
    "/gps/ang/type iso",
    "/gps/ang/mintheta 2.356 rad", # = pi is down the beamline (3/4*pi)
    # "/gps/ang/mintheta 3.1415 rad", # = pi is down the beamline
    # "/gps/ene/mono 4 GeV",
    "/gps/ene/type Lin",
    "/gps/ene/min 1 GeV",
    "/gps/ene/max 16 GeV",
    "/gps/ene/gradient 0",
    "/gps/ene/intercept 1"
    ] )

myGen = myGPS
#myGen = myGun

sim = simulator.simulator("SingleE")
sim.setDetector( 'ldmx-det-v12' , True )
sim.runNumber = 0
sim.description = "Single electron gun"
#sim.beamSpotSmear = [20., 80., 0.] #mm
sim.beamSpotSmear = [20., 20., 0.] #mm
sim.generators.append(myGen)

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

p.outputFiles=['muon_%igev_test.root'%energy]
p.maxEvents = nevents
p.logFrequency = 1

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

from LDMX.Ecal import digi  as ecal_digi
from LDMX.Ecal import vetos as ecal_vetos
from LDMX.Ecal import ecal_trig_digi
# from LDMX.Hcal import hcal  as ecal_hcal
# from LDMX.EventProc.simpleTrigger import simpleTrigger
# from LDMX.EventProc.trackerHitKiller import trackerHitKiller
from LDMX.TrigScint.trigScint import TrigScintDigiProducer

tsDigisTag  =TrigScintDigiProducer.tagger()
    # #tsDigisTag.input_collection = tsDigisTag.input_collection
tsDigisUp  =TrigScintDigiProducer.up()
# #tsDigisUp.input_collection = tsDigisUp.input_collection
# tsDigisDown  =TrigScintDigiProducer.down()
#tsDigisDown.input_collection = tsDigisDown.input_collection

# ecalDigi   =digi.EcalDigiProducer('EcalDigis')
# ecalReco   =digi.EcalRecProducer('ecalRecon')
# ecalVeto   =vetos.EcalVetoProcessor('ecalVetoBDT')

p.sequence=[sim,
            # hcaldigi,hcalrec,
            # ecal_digi.EcalDigiProducer(),
            # ecal_trig_digi.EcalTrigPrimDigiProducer(),
            # ecal_digi.EcalRecProducer(),
            # TrigScintDigiProducer.tagger(),
            # TrigScintDigiProducer.up(),
            # TrigScintDigiProducer.down(),
            ### #ecal_vetos.EcalVetoProcessor(),
]

p.keep = [
    "drop Trigger.*",
    "drop Tagger.*",
    "drop Target.*",
    "drop Hcal.*",
    "drop Magnet.*",
    "drop Recoil.*",
    "drop Tracker.*",

    #"drop .*SimHits.*",
           # "drop ^((?!EcalScoringPlaneHits).)*$"
           # "keep EcalScoringPlaneHits.*"
            # "drop .*SimHits.*" #drop all sim hits 
            # ,"keep EcalSimHits.*" #except the ones in the ECal
         ]

#print( p)
