import os, sys, argparse
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--step", default='gen', choices=['gen','pf'], help="Processing step to run")
parser.add_argument("--proc", default='ele_4GeV', help="Process tag to simulate")
parser.add_argument("--gps", action='store_true', default=False, help="Use GPS in place of Particle Gun")
parser.add_argument("--check", action='store_true', default=False, help="Run checks")
parser.add_argument("-n","--nEvents", default=None, type=int, help="Number of events to process")
parser.add_argument("--histFile", default='histogram.root', help="Histogram file name")
parser.add_argument("--input", default=None, help="input file name")
parser.add_argument("--output", default=None, help="EDM output file name")
parser.add_argument("--zstart", default=1, type=float, help="start of the particle gun position, in mm from target")
args = parser.parse_args()
if args.step=='gen' and args.nEvents==None: args.nEvents=10
if args.step=='pf'  and args.nEvents==None: args.nEvents=-1
if args.step=='pf'  and args.input==None: args.input='gen.root'
if args.output==None: args.output = args.step+'.root'

from LDMX.Framework import ldmxcfg
p = ldmxcfg.Process(args.step)
p.termLogLevel = 1
p.logFrequency = 1000

from LDMX.SimCore import simulator
from LDMX.SimCore import generators
p.libraries.append("libSimCore.so")

from generators import *
if args.step=='gen':
     if args.gps:
          part, eMin, eMax = args.proc.split('_') #part_0p1_4GeV
          eMin = float(eMin.replace('p','.'))
          eMax = float(eMax[:-3].replace('p','.'))
          gpsCfg = gpsCmds( p=tag2part[part], eRange=(eMin, eMax), zpos=args.zstart )
          theCmds = gpsCfg.getCmds()
          nPart=2
          if nPart>1:
               theCmds += (nPart-1)*(['/gps/source/add 1']+theCmds)
               theCmds += ["/gps/source/multiplevertex True"]    
          myGen = generators.gps( 'myGPS' , theCmds )
     else:
          myGen = generators.gun('myGun')
          myGen.particle = tag2part[args.proc.split('_')[0]]
          myGen.position = [ 0., 0., args.zstart ]  # mm after target, all TS pads
          myGen.direction = [ 0., 0., 1] 
          myGen.energy = float(args.proc.split('_')[-1][:-3].replace('p','.')) # part_XpYGeV

     sim = simulator.simulator("mySim")
     sim.setDetector( 'ldmx-det-v14' , True )
     sim.description = args.proc
     sim.beamSpotSmear = [20., 80., 0.] #mm
     sim.generators.append(myGen)
     p.sequence = [ sim ]

##################################################################
# Below should be the same for all sim scenarios

p.run = 1 #int(os.environ['LDMX_RUN_NUMBER'])
p.maxEvents = args.nEvents #int(os.environ['LDMX_NUM_EVENTS'])

if args.input:
     p.inputFiles = [args.input]
p.histogramFile = args.histFile
p.outputFiles = [args.output]

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
# from LDMX.Trigger import trigger_energy_sums
# trigger_seq = [
#     trigger_energy_sums.EcalTPSelector(),
#     trigger_energy_sums.TrigEcalEnergySum(),
#     trigger_energy_sums.TrigHcalEnergySum(),
#     trigger_energy_sums.TrigEcalClusterProducer(),
# ]

# from LDMX.Hcal import hcal # HcalTestProcessor
# trigScintTrack.verbosity = 100

p.sequence.extend([
        ecal_digi.EcalDigiProducer(),
        ecal_digi.EcalRecProducer(), 
        hcal_digi.HcalDigiProducer(),
        hcal_digi.HcalRecProducer(),
        ]) # + trigger_seq ) # + dqm.all_dqm + trigger_seq)

if args.step == 'pf':
     p.setCompression(2, level=9) # LZMA
     from LDMX.Recon import pfReco
     ecalPF = pfReco.pfEcalClusterProducer()
     hcalPF = pfReco.pfHcalClusterProducer()
     trackPF = pfReco.pfTrackProducer()
     truthPF = pfReco.pfTruthProducer()

     # configure clustering options
     ecalPF.doSingleCluster = False #True
     ecalPF.logEnergyWeight = True

     hcalPF.doSingleCluster = False
     hcalPF.clusterHitDist = 200. # mm
     hcalPF.logEnergyWeight = True

     # hcalPF_v2 = pfReco.pfHcalClusterProducer()
     # hcalPF_v2.SetClusterParameters(minHits=5, eThresh=100)
     # hcalPF_v3 = pfReco.pfHcalClusterProducer()
     # hcalPF_v3.SetClusterParameters(minHits=5, eThresh=200)
     # hcalPF_v3.SetOutputCollectionName('Cluster_5_200')

     # from LDMX.Hcal import cluster
     # hcalPF = cluster.HcalNewClusterProducer()
     # hcalPF.cluster2d_coll_name = 'PFHcalClusters2D'
     # hcalPF.cluster3d_coll_name = 'PFHcalClusters'

     ecalPF_simple = pfReco.pfEcalClusterProducer()
     ecalPF_simple.clusterCollName += "Simple"
     ecalPF_simple.doSingleCluster = True
     hcalPF_simple = pfReco.pfHcalClusterProducer()
     hcalPF_simple.clusterCollName += "Simple"
     hcalPF_simple.doSingleCluster = True

     p.sequence = [
          #ecalPF_simple, 
          ecalPF, hcalPF, trackPF,
          pfReco.pfProducer(),
          truthPF,
        ]

if args.step == 'gen':
     p.keep = [ 
          # "drop .*SimHits.*",
          "drop EcalDigi.*",
          "drop HcalDigi.*",
          # "drop EcalRec.*",
          # "drop HcalRec.*",
          # "drop SimParticles_sim.*",
     ]
if args.step == 'pf':
     p.keep = [ 
          "drop .*SimHits.*",
          "drop EcalDigi.*",
          "drop HcalDigi.*",
          "drop EcalRec.*",
          "drop HcalRec.*",
          # slimmed into pfTruth collections instead
          "drop SimParticles.*",
          'drop TargetScoringPlaneHits.*',
          'drop TrackerScoringPlaneHits.*',
          'drop MagnetScoringPlaneHits.*',
          'drop EcalScoringPlaneHits.*',
          'drop HcalScoringPlaneHits.*',
          'drop TrigScintScoringPlaneHits.*',
     ]

allcols = [
     'stringParameters',
     'sampleOfInterest',
     'eventNumber',
     'TaggerSimHits',
     'EventHeader.floatParameters',
     'EventHeader.intParameters',
     'PFEcalClusters',
     'intParameters',
     'RecoilSimHits',
     'EventHeader.isRealData',
     'TriggerPad2SimHits',
     'TriggerPad1SimHits',
     'isRealData',
     'EventHeader.weight',
     'EventHeader.run',
     'TargetSimHits',
     'MagnetScoringPlaneHits',
     'EcalScoringPlaneHits',
     'HcalScoringPlaneHits',
     'TrigScintScoringPlaneHits',
     'version',
     'EventHeader',
     'HcalSimHits',
     'EcalDigis',
     'EventHeader.timestamp',
     'EventHeader.eventNumber',
     'timestamp',
     'numSamplesPerDigi',
     'HcalDigis',
     'EventHeader.stringParameters',
     'PFHcalClusters',
     'EcalSimHits',
     'PFTracks',
     'EcalRecHits',
     'weight',
     'samples',
     'floatParameters',
     'TriggerPad3SimHits',
     'run',
     'PFCandidates',
     'channelIDs',
     'SimParticles',
     'HcalRecHits',
]
