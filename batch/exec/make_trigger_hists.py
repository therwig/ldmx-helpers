import EventTree
import sys, ROOT, ctypes, os, glob
ROOT.gROOT.SetBatch(1)
from array import array
from math import atan, hypot
import numpy as np
from collections import OrderedDict
from utils import *

#from LDMX.Trigger import TrigCaloCluster
from cppyy.gbl import trigger
from cppyy.gbl import ldmx

# default and local options
infiles = ['in.root']
if len(sys.argv)>1: infiles = [sys.argv[1]]
outfile='hist_'+infiles[0].split('/')[-1]
#batch overrides
env = os.environ
if 'LSB_JOBINDEX' in env:
    outfile = 'out.root' # will be renamed later
    infiles = glob.glob('input_files/*.root')
    
trees = [EventTree.EventTree(f) for f in infiles]
print('Running over trees from inputs:',infiles)
f_output = ROOT.TFile(outfile,'recreate')

hh=OrderedDict()
def bookTH1(h, name, title, n, a, b):
    h[name] = ROOT.TH1F(name, title, n, a, b)
def bookTH2(h, name, title, n, a, b, nn, aa, bb):
    h[name] = ROOT.TH2F(name, title, n, a, b, nn, aa, bb)
    
class ele():
    def __init__(self, ts, clus):
        self.ts=ts
        self.clus=clus
        self.isNull = (clus.energy()<1e-6 or t.getTrackID()<1)
        tsx, tsy = ts.getPosition()[0], ts.getPosition()[1]
        self.isNull |= (abs(tsx)<1e-3 and abs(tsy)<1e-3)
        self.clear()
        if not self.isNull:
            self.tsx=tsx
            self.tsy=tsy
            self.e = clus.e()
            self.dx = clus.x() - tsx
            # expected dx [mm], when initial px=0
            self.dx_hat = -( 2*(4000./clus.e()-1)+2.3 ) if clus.e() else 0 
            self.dy = clus.y() - tsy
            self.px = 17.8 * clus.e() / 4e3 * (self.dx - self.dx_hat)
            self.py = 17.8 * clus.e() / 4e3 * self.dy
            self.pt = hypot(self.px,self.py)
    def clear(self):
        self.e  = 0
        self.dx = 0
        self.dx_hat = 0
        self.dy = 0
        self.px = 0
        self.py = 0
        self.pt = 0
        self.tsx = 0
        self.tsy = 0

# ecalLayers=[5,10,15,20,25,30] # for sums ?
nEcalLayers=35
nHcalLayers=50
nHcalLayersSide=15
bookTH1(hh,'nEvents','',1,0,1)
bookTH1(hh,'Ecal_sumE',';total E [MeV]',200,0,8000)
bookTH1(hh,'Ecal_sumE_outer',';total E [MeV]',200,0,4000)
bookTH2(hh,'Ecal_layerSum',';layer number;total E [MeV]', nEcalLayers,-0.5,nEcalLayers-0.5, 400,0,4000,)
bookTH2(hh,'Ecal_minLayerSum',';layer number;total E [MeV]', nEcalLayers,-0.5,nEcalLayers-0.5, 400,0,8000,)
bookTH2(hh,'Ecal_maxLayerSum',';layer number;total E [MeV]', nEcalLayers,-0.5,nEcalLayers-0.5, 400,0,8000,)

bookTH1(hh,'Hcal_sumBackE',';total back HCal ADC [counts]',100,0,500)
bookTH1(hh,'Hcal_sumBackE2',';total back HCal ADC [counts]',100,0,50000)
bookTH1(hh,'Hcal_sumSideE',';total side HCal ADC [counts]',100,0,500)
bookTH1(hh,'Hcal_sumSideE2',';total side HCal ADC [counts]',100,0,50000)
bookTH1(hh,'Hcal_sumE',';total HCal ADC [counts]',100,0,500)
bookTH1(hh,'Hcal_sumE2',';total HCal ADC [counts]',100,0,50000)
bookTH2(hh,'Hcal_backLayerSum',';layer number;total ACD [counts]', nHcalLayers,-0.5,nHcalLayers-0.5, 200,0,10e3,)
bookTH2(hh,'Hcal_minBackLayerSum',';layer number;total ACD [counts]', nHcalLayers,-0.5,nHcalLayers-0.5, 200,0,20e3,)
bookTH2(hh,'Hcal_maxBackLayerSum',';layer number;total ACD [counts]', nHcalLayers,-0.5,nHcalLayers-0.5, 200,0,20e3,)
bookTH2(hh,'Hcal_sideLayerSum',';layer number;total ACD [counts]', nHcalLayersSide,-0.5,nHcalLayersSide-0.5, 200,0,5000,)
bookTH2(hh,'Hcal_minSideLayerSum',';layer number;total ACD [counts]', nHcalLayersSide,-0.5,nHcalLayersSide-0.5, 200,0,10e3,)
bookTH2(hh,'Hcal_maxSideLayerSum',';layer number;total ACD [counts]', nHcalLayersSide,-0.5,nHcalLayersSide-0.5, 200,0,10e3,)
# enum HcalSection { BACK = 0, TOP = 1, BOTTOM = 2, LEFT = 4, RIGHT = 3 };
## FYI
# pe_per_adc_{1.2/5}

bookTH1(hh,'Clus_e',';ECal cluster E [MeV]',200,0,8000)
bookTH1(hh,'Clus_nTP',';ECal cluster TP multiplicity',100,-0.5,99.5)
bookTH1(hh,'Clus_length',';ECal cluster length [#layers]',40,-0.5,39.5)
bookTH2(hh,'TS_xy',';x[mm];y[mm]', 40,-20,20,40,-50,50)
bookTH2(hh,'ECal_xy',';x[mm];y[mm]', 80,-100,100,80,-100,100)
bookTH2(hh,'ECal_xy2',';x[mm];y[mm]', 200,-300,300,200,-300,300)

bookTH1(hh,'Ele_dx',';Trigger electron dx [mm]',40,-50,50)
bookTH1(hh,'Ele_dx2',';Trigger electron dx [mm]',40,-200,200)
bookTH1(hh,'Ele_dx_raw',';Trigger electron dx (no corr.) [mm]',40,-50,50)
bookTH1(hh,'Ele_dx_raw2',';Trigger electron dx (no corr.) [mm]',40,-200,200)
bookTH1(hh,'Ele_dy',';Trigger electron dy [mm]',40,-50,50)
bookTH1(hh,'Ele_dy2',';Trigger electron dy [mm]',40,-200,200)
bookTH1(hh,'Ele_px',';Trigger electron p_{x} [MeV]',40,-600,600)
bookTH1(hh,'Ele_py',';Trigger electron p_{y} [MeV]',40,-600,600)
bookTH1(hh,'Ele_pyAbs',';Trigger electron |p_{y}| [MeV]',40,0,600)
bookTH1(hh,'Ele_pt',';Trigger electron p_{T} [MeV]',40,0,800)
bookTH1(hh,'Ele_e',';Trigger electron E [MeV]',200,0,8000)

bookTH1(hh,'nEle',';Trigger electron multiplicity',10,-0.5,9.5)
bookTH1(hh,'Ele1_pt',';Trigger electron p_{T} [MeV]',40,0,800)
bookTH1(hh,'Ele2_pt',';Trigger electron p_{T} [MeV]',40,0,400)
bookTH1(hh,'Ele3_pt',';Trigger electron p_{T} [MeV]',40,0,400)
bookTH1(hh,'Ele4_pt',';Trigger electron p_{T} [MeV]',40,0,400)
bookTH1(hh,'Ele1_e',';Trigger electron E [MeV]',200,0,8000)
bookTH1(hh,'Ele2_e',';Trigger electron E [MeV]',200,0,4000)
bookTH1(hh,'Ele3_e',';Trigger electron E [MeV]',200,0,4000)
bookTH1(hh,'Ele4_e',';Trigger electron E [MeV]',200,0,4000)

#E-capped
bookTH1(hh,'Ele_pyAbsCap',';Trigger electron |p_{y}| [MeV]',40,0,600)
bookTH1(hh,'Ele_ptCap',';Trigger electron p_{T} [MeV]',40,0,800)
#
bookTH1(hh,'Ele_ptTight',';Trigger electron p_{T} [MeV]',40,0,800)
bookTH1(hh,'Ele_ptTightCap',';Trigger electron p_{T} [MeV]',40,0,800)

#correlations for ele debugging
bookTH2(hh,'Ele_pt_vs_e',';Trigger electron p_{T} [MeV];energy [MeV]',40,0,800,60,0,6e3)
bookTH2(hh,'Ele_pt_vs_TSx',';Trigger electron p_{T} [MeV];TS x [mm]',40,0,800,40,-20,20)
bookTH2(hh,'Ele_pt_vs_TSy',';Trigger electron p_{T} [MeV];TS y [mm]',40,0,800,40,-50,50)
bookTH2(hh,'Ele_pt_vs_nTP',';Trigger electron p_{T} [MeV];nTP ',40,0,800,100,-0.5,99.5)
bookTH2(hh,'Ele_pt_vs_depth',';Trigger electron p_{T} [MeV];depth ',40,0,800,35,-0.5,34.5)
bookTH2(hh,'Ele_pt_vs_ze',';Trigger electron p_{T} [MeV];ze [mm] ',40,0,800,100,0,200)
bookTH2(hh,'EleCap_pt_vs_e',';Trigger electron p_{T} [MeV];energy [MeV]',40,0,800,60,0,6e3)
bookTH2(hh,'EleCap_pt_vs_TSx',';Trigger electron p_{T} [MeV];TS x [mm]',40,0,800,40,-20,20)
bookTH2(hh,'EleCap_pt_vs_TSy',';Trigger electron p_{T} [MeV];TS y [mm]',40,0,800,40,-50,50)
bookTH2(hh,'EleCap_pt_vs_nTP',';Trigger electron p_{T} [MeV];nTP ',40,0,800,100,-0.5,99.5)
bookTH2(hh,'EleCap_pt_vs_depth',';Trigger electron p_{T} [MeV];depth ',40,0,800,35,-0.5,34.5)
bookTH2(hh,'EleCap_pt_vs_ze',';Trigger electron p_{T} [MeV];ze [mm] ',40,0,800,100,0,200)
bookTH2(hh,'Ele300_pt_vs_e',';Trigger electron p_{T} [MeV];energy [MeV]',40,0,800,60,0,6e3)
bookTH2(hh,'Ele300_pt_vs_TSx',';Trigger electron p_{T} [MeV];TS x [mm]',40,0,800,40,-20,20)
bookTH2(hh,'Ele300_pt_vs_TSy',';Trigger electron p_{T} [MeV];TS y [mm]',40,0,800,40,-50,50)
bookTH2(hh,'Ele300_pt_vs_nTP',';Trigger electron p_{T} [MeV];nTP ',40,0,800,100,-0.5,99.5)
bookTH2(hh,'Ele300_pt_vs_depth',';Trigger electron p_{T} [MeV];depth ',40,0,800,35,-0.5,34.5)
bookTH2(hh,'Ele300_pt_vs_ze',';Trigger electron p_{T} [MeV];ze [mm] ',40,0,800,100,0,200)
bookTH2(hh,'Ele300_TSx_vs_TSy',';TS x [mm];TS y [mm]',40,-20,20,40,-50,50)
bookTH2(hh,'Ele300_Clusx_vs_Clusy',';Clus x [mm];Clus y [mm]',60,-150,150,60,-150,150)
bookTH2(hh,'Ele300_Clusx_vs_Clusy2',';Clus x [mm];Clus y [mm]',300,-150,150,300,-150,150)
bookTH2(hh,'Ele300_ECal_xy',';x[mm];y[mm]', 200,-300,300,200,-300,300)


# large and small ranges
bookTH1(hh,'Truth_px',';Truth particle p_{x} [MeV]',40,-100,100)
bookTH1(hh,'Truth_px2',';Truth particle p_{x} [MeV]',40,-800,800)
bookTH1(hh,'Truth_py',';Truth particle p_{y} [MeV]',40,-100,100)
bookTH1(hh,'Truth_py2',';Truth particle p_{y} [MeV]',40,-800,800)
bookTH1(hh,'Truth_pyAbs',';Truth particle p_{T} [MeV]',40,0,100)
bookTH1(hh,'Truth_pyAbs2',';Truth particle p_{T} [MeV]',40,0,1200)
bookTH1(hh,'Truth_pt',';Truth particle p_{T} [MeV]',40,0,100)
bookTH1(hh,'Truth_pt2',';Truth particle p_{T} [MeV]',40,0,1200)
bookTH1(hh,'Truth_e',';Truth particle E [MeV]',40,0,4000)
bookTH1(hh,'Truth_e2',';Truth particle E [MeV]',40,0,5000)
bookTH1(hh,'Truth_e3',';Truth particle E [MeV]',40,0,500)
bookTH1(hh,'Truth_ke',';Truth particle K.E. [MeV]',40,0,4000)
bookTH2(hh,'Truth_pt_vs_e',';Trigger electron p_{T} [MeV];energy [MeV]',40,0,1200,40,0,4e3)

# Ele trigger
bookTH1(hh,'Truth_e_Ele0',';Truth electron E [MeV]',40,0,4000)
bookTH1(hh,'Truth_e2_Ele0',';Truth electron E [MeV]',40,0,500)
bookTH1(hh,'Truth_pt_Ele0',';Truth electron p_{T} [MeV]',40,0,1200)
bookTH1(hh,'Truth_pt_Ele400',';Truth electron p_{T} [MeV]',40,0,1200)
bookTH1(hh,'Truth_pt_Ele500',';Truth electron p_{T} [MeV]',40,0,1200)
bookTH2(hh,'ECal_xy_pass400',';x[mm];y[mm]', 200,-300,300,200,-300,300)
bookTH2(hh,'ECal_xy_fail400',';x[mm];y[mm]', 200,-300,300,200,-300,300)
bookTH2(hh,'Truth_pt_vs_e_pass400',';Trigger electron p_{T} [MeV];energy [MeV]',40,0,1200,40,0,4e3)
bookTH2(hh,'Truth_pt_vs_e_fail400',';Trigger electron p_{T} [MeV];energy [MeV]',40,0,1200,40,0,4e3)
# HCal trigger
bookTH1(hh,'Truth_e_BackHcal50',';Truth E [MeV]',40,0,5000)
bookTH1(hh,'Truth_e_BackHcal300',';Truth E [MeV]',40,0,5000)
bookTH1(hh,'Truth_e_BackHcal1000',';Truth E [MeV]',40,0,5000)
bookTH1(hh,'Truth_e_BackHcal2000',';Truth E [MeV]',40,0,5000)
bookTH1(hh,'Truth_e_BackHcal4000',';Truth E [MeV]',40,0,5000)
bookTH1(hh,'Truth_e_BackHcal8000',';Truth E [MeV]',40,0,5000)
bookTH1(hh,'Truth_e_BackHcal12000',';Truth E [MeV]',40,0,5000)
bookTH1(hh,'Truth_ke_BackHcal50',';Truth K.E. [MeV]',40,0,4000)
bookTH1(hh,'Truth_ke_BackHcal300',';Truth K.E. [MeV]',40,0,4000)
bookTH1(hh,'Truth_ke_BackHcal1000',';Truth E [MeV]',40,0,4000)
bookTH1(hh,'Truth_ke_BackHcal2000',';Truth E [MeV]',40,0,4000)
bookTH1(hh,'Truth_ke_BackHcal4000',';Truth E [MeV]',40,0,4000)
bookTH1(hh,'Truth_ke_BackHcal8000',';Truth E [MeV]',40,0,4000)
bookTH1(hh,'Truth_ke_BackHcal12000',';Truth K.E. [MeV]',40,0,4000)

#
# produce 'ingredient' histograms from tree
#
for tree in trees:
    for ie, event in enumerate(tree):
        hh['nEvents'].Fill(0.5)
        # if ie > 1000: break
        
        # ecal sums
        ecal_layers = nEcalLayers*[0.]
        ecal_outer=0.
        for s in event.ecalTrigSums:
            ecal_layers[s.layer()] += s.energy()
            if s.module()!=0: ecal_outer += s.energy()
        for i in range(nEcalLayers):
            hh['Ecal_layerSum'].Fill(i, ecal_layers[i])        
        for i in range(nEcalLayers):
            hh['Ecal_minLayerSum'].Fill(i, sum(ecal_layers[i:]))
            hh['Ecal_maxLayerSum'].Fill(i, sum(ecal_layers[:i]))
        hh['Ecal_sumE'].Fill(sum(ecal_layers))
        hh['Ecal_sumE_outer'].Fill(ecal_outer)
    
        # hcal sums
        hcal_back_layers = nHcalLayers*[0.]
        hcal_side_layers = nHcalLayersSide*[0.]
        # layer sums
        for s in event.hcalTrigQuadsBackLayerSums:
            hcal_back_layers[s.layer()] += s.hwEnergy()
        for s in event.hcalTrigQuadsSideLayerSums:
            if s.layer() >= nHcalLayersSide: continue
            hcal_side_layers[s.layer()] += s.hwEnergy()
        for i in range(nHcalLayers):
            hh['Hcal_backLayerSum'].Fill(i, hcal_back_layers[i])
            hh['Hcal_minBackLayerSum'].Fill(i, sum(hcal_back_layers[i:]))
            hh['Hcal_maxBackLayerSum'].Fill(i, sum(hcal_back_layers[:i]))
        for i in range(nHcalLayersSide):
            hh['Hcal_sideLayerSum'].Fill(i, hcal_side_layers[i])
            hh['Hcal_minSideLayerSum'].Fill(i, sum(hcal_side_layers[i:]))
            hh['Hcal_maxSideLayerSum'].Fill(i, sum(hcal_side_layers[:i]))
        # totals
        hcal_back_sum=0
        hcal_side_sum=0
        for s in event.hcalTrigQuadsSectionSums:
            if s.module()==0: hcal_back_sum += s.energy()
            else: hcal_side_sum += s.energy()    
        hh['Hcal_sumBackE'].Fill(hcal_back_sum)
        hh['Hcal_sumSideE'].Fill(hcal_side_sum)
        hh['Hcal_sumE'].Fill(hcal_back_sum+hcal_side_sum)
        hh['Hcal_sumBackE2'].Fill(hcal_back_sum)
        hh['Hcal_sumSideE2'].Fill(hcal_side_sum)
        hh['Hcal_sumE2'].Fill(hcal_back_sum+hcal_side_sum)
        # hh['Hcal_sumE'].Fill(event.hcalTrigQuadsSum.hwEnergy())
    
        
        # ecal clusters
        clus = trigger.TrigCaloCluster()
        for c in event.ecalTrigClusters:
            # print (type(c))
            # if c.depth()<10: continue
            if c.e() > clus.e(): clus = c
        hh['Clus_e'].Fill(clus.e())
        hh['Clus_nTP'].Fill(clus.nTP())
        hh['Clus_length'].Fill(clus.depth())
    
        # TS hit
        ts=ldmx.SimTrackerHit()
        truth=ldmx.SimTrackerHit()
        for t in event.TargetScoringPlaneHits:
            if t.getTrackID()!=1: continue
            z=t.getPosition()[2]
            if z>0 and z<1: 
                truth=t
                if t.getPdgID()==11: ts=t
                    
        ecal=ldmx.SimTrackerHit()
        #ecal.setEdep(0)
        if hasattr(event,'EcalScoringPlaneHits'):
            for t in event.EcalScoringPlaneHits:
                if t.getTrackID()!=1: continue
                z=t.getPosition()[2]
                if z<240.4 or z>240.6: continue
                if t.getEdep() > ecal.getEdep():
                    ecal = t

        tsx, tsy = ts.getPosition()[0], ts.getPosition()[1]
        hh['TS_xy'].Fill(tsx, tsy)
        ecalx, ecaly = ecal.getPosition()[0], ecal.getPosition()[1]
        hh['ECal_xy'].Fill(ecalx, ecaly)
        hh['ECal_xy2'].Fill(ecalx, ecaly)
        
        # leading electron
        e = ele(ts, clus)
        if abs(e.tsx)>8: e.clear()
        if abs(e.tsy)>35: e.clear()

        
        hh['Ele_dx'].Fill(e.dx - e.dx_hat)
        hh['Ele_dx2'].Fill(e.dx - e.dx_hat)
        hh['Ele_dx_raw'].Fill(e.dx)
        hh['Ele_dx_raw2'].Fill(e.dx)
        hh['Ele_dy'].Fill(e.dy)
        hh['Ele_dy2'].Fill(e.dy)
        hh['Ele_px'].Fill(e.px)
        hh['Ele_py'].Fill(e.py)
        hh['Ele_pyAbs'].Fill(abs(e.py))
        hh['Ele_pt'].Fill(e.pt)
        hh['Ele_e'].Fill(e.e)

        hh['Ele_pt_vs_e'].Fill(e.pt, e.clus.e())
        hh['Ele_pt_vs_TSx'].Fill(e.pt, e.tsx) 
        hh['Ele_pt_vs_TSy'].Fill(e.pt, e.tsy) 
        hh['Ele_pt_vs_nTP'].Fill(e.pt, e.clus.nTP())
        hh['Ele_pt_vs_depth'].Fill(e.pt, e.clus.depth())
        hh['Ele_pt_vs_ze'].Fill(e.pt, e.clus.ze())

        if e.pt>300:
            hh['Ele300_pt_vs_e'].Fill(e.pt, e.clus.e())
            hh['Ele300_pt_vs_TSx'].Fill(e.pt, e.tsx) 
            hh['Ele300_pt_vs_TSy'].Fill(e.pt, e.tsy) 
            hh['Ele300_pt_vs_nTP'].Fill(e.pt, e.clus.nTP())
            hh['Ele300_pt_vs_depth'].Fill(e.pt, e.clus.depth())
            hh['Ele300_pt_vs_ze'].Fill(e.pt, e.clus.ze())
            hh['Ele300_TSx_vs_TSy'].Fill(e.tsx, e.tsy)
            hh['Ele300_Clusx_vs_Clusy'].Fill(e.clus.x(), e.clus.y())
            hh['Ele300_Clusx_vs_Clusy2'].Fill(e.clus.x(), e.clus.y())
            hh['Ele300_ECal_xy'].Fill(ecalx, ecaly)
            
        passTight=(e.clus.nTP()>=20 and e.clus.depth()>=10)
        hh['Ele_ptTight'].Fill(e.pt if passTight else 0)

        # all clusters
        eles = [ele(ts, clus) for clus in event.ecalTrigClusters]
        eles = list(filter(lambda e: abs(e.tsx)<8 and abs(e.tsy)<35, eles))
        hh['nEle'].Fill(len(eles))
        eles_pt = sorted(eles, key=lambda el:el.pt, reverse=True)
        for i in range(4):
            hh['Ele'+str(i+1)+'_pt'].Fill(eles_pt[i].pt if len(eles_pt)>i else 0)
        eles_e = sorted(eles, key=lambda el:el.e, reverse=True)
        for i in range(4):
            hh['Ele'+str(i+1)+'_e'].Fill(eles_e[i].e if len(eles_e)>i else 0)
            # print('post',[el.pt for el in eles])
        
        
        # energy-capped quantities
        e2=e
        if e.e>4e3:
            e.clus.setEnergy(4e3)
            e2 = ele(e.ts, e.clus)
            
        hh['Ele_pyAbsCap'].Fill(abs(e2.py))
        hh['Ele_ptCap'].Fill(e2.pt)
        hh['Ele_ptTightCap'].Fill(e.pt if passTight else 0)
        
        hh['EleCap_pt_vs_e'].Fill(e2.pt, e2.clus.e())
        hh['EleCap_pt_vs_TSx'].Fill(e2.pt, e2.tsx) 
        hh['EleCap_pt_vs_TSy'].Fill(e2.pt, e2.tsy) 
        hh['EleCap_pt_vs_nTP'].Fill(e2.pt, e2.clus.nTP())
        hh['EleCap_pt_vs_depth'].Fill(e2.pt, e2.clus.depth())
        hh['EleCap_pt_vs_ze'].Fill(e2.pt, e2.clus.ze())

        # truth, for the leading track
        truth_e = truth.getEnergy()
        truth_p = truth.getMomentum()
        truth_px = truth_p[0]
        truth_py = truth_p[1]
        truth_pt = hypot(truth_p[0],truth_p[1])
        truth_ke = sqrt(pow(truth_p[0],2)+pow(truth_p[1],2)+pow(truth_p[2],2))
        hh['Truth_pyAbs'].Fill(abs(truth_py))
        hh['Truth_py'].Fill(truth_py)
        hh['Truth_px'].Fill(truth_px)
        hh['Truth_pt'].Fill(truth_pt)
        hh['Truth_pyAbs2'].Fill(abs(truth_py))
        hh['Truth_py2'].Fill(truth_py)
        hh['Truth_px2'].Fill(truth_px)
        hh['Truth_pt2'].Fill(truth_pt)
        hh['Truth_e'].Fill(truth_e)
        hh['Truth_e2'].Fill(truth_e)
        hh['Truth_e3'].Fill(truth_e)
        hh['Truth_ke'].Fill(truth_ke)
        hh['Truth_pt_vs_e'].Fill(truth_pt,truth_e)

        # Ele trigger
        if e.e>0.1:
            hh['Truth_e_Ele0'].Fill(truth_e)
            hh['Truth_e2_Ele0'].Fill(truth_e)
            hh['Truth_pt_Ele0'].Fill(truth_pt)
        if e.pt>400: hh['Truth_pt_Ele400'].Fill(truth_pt)
        if e.pt>500: hh['Truth_pt_Ele500'].Fill(truth_pt)

        if truth_pt>500:
            if e.pt>400: hh['ECal_xy_pass400'].Fill(ecalx, ecaly)
            else: hh['ECal_xy_fail400'].Fill(ecalx, ecaly)
            if e.pt>400: hh['Truth_pt_vs_e_pass400'].Fill(truth_pt,truth_e)
            else: hh['Truth_pt_vs_e_fail400'].Fill(truth_pt,truth_e)
 
        # Neutron trigger
        if hcal_back_sum>50:
            hh['Truth_e_BackHcal50'].Fill(truth_e)
            hh['Truth_ke_BackHcal50'].Fill(truth_ke)
        if hcal_back_sum>300:
            hh['Truth_e_BackHcal300'].Fill(truth_e)
            hh['Truth_ke_BackHcal300'].Fill(truth_ke)
        if hcal_back_sum>1000:
            hh['Truth_e_BackHcal1000'].Fill(truth_e)
            hh['Truth_ke_BackHcal1000'].Fill(truth_ke)
        if hcal_back_sum>2000:
            hh['Truth_e_BackHcal2000'].Fill(truth_e)
            hh['Truth_ke_BackHcal2000'].Fill(truth_ke)
        if hcal_back_sum>4000:
            hh['Truth_e_BackHcal4000'].Fill(truth_e)
            hh['Truth_ke_BackHcal4000'].Fill(truth_ke)
        if hcal_back_sum>8000:
            hh['Truth_e_BackHcal8000'].Fill(truth_e)
            hh['Truth_ke_BackHcal8000'].Fill(truth_ke)
        if hcal_back_sum>12000:
            hh['Truth_e_BackHcal12000'].Fill(truth_e)
            hh['Truth_ke_BackHcal12000'].Fill(truth_ke)
    
    
        # # can calculate the initial px (and py) from E, dx
        #  E=recoil_e;
        #  x = recoil_dx;
        #  R = E*(11500/4000.); // convert 11.5m/4GeV (in mm/MeV)
        #  zd = 240.; // 240mm z detector                                                                                                                              
        #  a=x/zd;
        #  b=(x*x+zd*zd)/(2*R*zd);
        # pred_px = E*(-b+a*sqrt(1+a*a-b*b))/(1+a*a);
        # pred_py = recoil_dy * 16; //mev/mm    
    
        
        #     auto xyz = hit.getPosition();
        #     auto pxyz = hit.getMomentum();
        #     float pt = sqrt( pow(pxyz[0],2) + pow(pxyz[1],2) );
        # continue
    
#
# remove overflow
#
for h in hh:
    remove_overflow(hh[h])

# if False:
#   def MakeRateVsCut(h, reverse=False):
#       h2 = h.Clone("rate_"+h.GetName())
#       n = h2.GetNbinsX()
#       for i in range(1,n+1):
#           # h2.SetBinContent( h.Integral(i,n) )
#           # events from bin ib to max         
#           # e=ROOT.double(0)
#           e=ctypes.c_double(0)
#           if reverse:
#               val = h.IntegralAndError(0,i,e)
#           else:
#               val = h.IntegralAndError(i,n+1,e)
#           h2.SetBinContent(i,val)
#           h2.SetBinError(i,e.value)
              
#       return h2
  
#   hh['rate_Ecal_sumE'] = MakeRateVsCut(hh['Ecal_sumE'], reverse=True)
#   hh['rate_Ecal_sumE_outer'] = MakeRateVsCut(hh['Ecal_sumE_outer'])
#   hh['rate_Hcal_sumE'] = MakeRateVsCut(hh['Hcal_sumE'])
  
#   ecal_layer_energies = [1000,1500,2000,2500,3000,3500,4000]
#   for e in ecal_layer_energies:
#       b = h.GetYaxis().FindBin(e)
#       h = hh['Ecal_minLayerSum']
#       hh['Ecal_layerAbove{}MeV'.format(e)] = h.ProjectionX('Ecal_layerAbove{}MeV'.format(e),b,-1)
#       h = hh['Ecal_maxLayerSum']
#       hh['Ecal_layerBelow{}MeV'.format(e)] = h.ProjectionX('Ecal_layerBelow{}MeV'.format(e),0,b)
      
#   hcal_layer_adcs = [5,10,20,50,100]
#   for e in hcal_layer_adcs:
#       b = h.GetYaxis().FindBin(e)
#       h = hh['Hcal_minBackLayerSum']
#       hh['Hcal_backLayerAbove{}adc'.format(e)] = h.ProjectionX('Hcal_backLayerAbove{}adc'.format(e),b,-1)
#       h = hh['Hcal_maxBackLayerSum']
#       hh['Hcal_backLayerBelow{}adc'.format(e)] = h.ProjectionX('Hcal_backLayerBelow{}adc'.format(e),0,b)
    
#f_output.Write()
for h in hh:
    hh[h].Write()
f_output.Close()

#     sp = list(filter( lambda x : x.getTrackID()==1 and abs(x.getPosition()[2]-240)<5, event.EcalScoringPlaneHits))
#     if len(sp)==0: continue
#     sp=sp[0]
#     tmom = sp.getMomentum()
#     truth_dxdz = tmom[0] / tmom[2]
#     t_truth = atan(truth_dxdz) # angle from 'fwd'
    
#     hits=[None]*MAXHITS
#     for hit in event.EcalSimHits:
#         l = layer_from_id(hit.getID())

#         if l >= MAXHITS:
#             continue
#         elif not hits[l]:
#             hits[l] = hit
#         elif hit.getEdep() > hits[l].getEdep():
#             hits[l] = hit

#     thisBin = int(sp.getEnergy()/1e3) # e in GeV
#     if thisBin < bins[0]: thisBin=bins[0]
#     if thisBin > bins[-1]: thisBin=bins[-1]
#     h['energy'+str(thisBin)].Fill( sp.getEnergy() )
    
#     for nhits in nhitss:
#         xs=[]
#         zs=[]
#         for l in range(nhits):
#             if hits[l]:
#                 coords = hits[l].getPosition()
#                 xs += [coords[0]]
#                 zs += [coords[2]]
#         xs = array('d',xs)
#         zs = array('d',zs)
#         g = ROOT.TGraph(len(xs),zs,xs) # change in x versus z
#         # r = g.Fit("pol1","sq")
#         r = g.Fit("pol1","sq")
#         ps = r.GetParams()
#         dxdz = ps[1]
#         t = atan(dxdz) # angle from 'fwd'
        
#         h['dTheta'].Fill( t - t_truth )
#         h['dTheta'+str(thisBin)+'_tk'+str(nhits)].Fill( t - t_truth )
#         h['dTheta_tk'+str(nhits)].Fill( t - t_truth )

#     if ie < nDisplays:
#         xs=[]
#         zs=[]
#         for l in range(len(hits)):
#             if hits[l]:
#                 coords = hits[l].getPosition()
#                 xs += [coords[0]]
#                 zs += [coords[2]]
#         xs = array('d',xs)
#         zs = array('d',zs)
#         g = ROOT.TGraph(len(xs),zs,xs) # change in x versus z
#         g.SetName("Disp"+str(ie))
#         r = g.Fit("pol1","sq")
#         g.Write()
#         gDisplays += [g]
        
# for nhits in nhitss:
#     x=[]
#     xe=[]
#     y=[]
#     ye=[]
#     for b in bins[1:]:
#         x.append( h['energy'+str(b)].GetMean() )
#         xe.append( h['energy'+str(b)].GetRMS() )
#         r = h['dTheta'+str(b)+'_tk'+str(nhits)].Fit("gaus","sq")
#         ps = r.GetParams()
#         pe = r.GetErrors()
#         y.append(ps[2])
#         ye.append(pe[2])
    
#     c = ROOT.TCanvas()
#     g = ROOT.TGraphErrors(len(x), np.array(x), np.array(y), np.array(xe), np.array(ye) )
#     g.SetTitle('; Incoming muon energy [MeV];Scattering angle RMS [rad]')
#     g.SetName('AngleTk'+str(nhits))
#     g.Write()
#     g.Draw('ALP')
#     c.SaveAs('AngleTk'+str(nhits)+'.pdf')

# x=[]
# xe=[]
# y=[]
# ye=[]
# for nhits in nhitss:
#     x.append( nhits )
#     xe.append( 0.5)
#     r = h['dTheta_tk'+str(nhits)].Fit("gaus","sq")
#     ps = r.GetParams()
#     pe = r.GetErrors()
#     y.append(ps[2])
#     ye.append(pe[2])
# print(x, xe, y, ye)

# c = ROOT.TCanvas()
# g = ROOT.TGraphErrors(len(x), array('d',x), array('d',y), array('d',xe), array('d',ye) )
# g.SetTitle('; # tracklet hits;Scattering angle RMS [rad]')
# g.SetName('Angle_vs_Tk')
# g.Write()
# g.Draw('ALP')

# f1 = ROOT.TF1("f1","[0]+[1]/x/x",3,20)
# pams = g.Fit(f1,"s").GetParams()

# t = ROOT.TLatex()
# t.SetNDC()
# t.DrawLatex(0.5,0.2, 'y={:.3f}+{:.3f}/nHit^2'.format(pams[0], pams[1]))

# c.SaveAs('Angle_vs_Tk.pdf')

# # print(gDisplays)
# # for g in gDisplays: g.Write()

