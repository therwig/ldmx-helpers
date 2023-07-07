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
outfile='histNeut_'+infiles[0].split('/')[-1]
#batch overrides
env = os.environ
if 'LSB_JOBINDEX' in env:
    outfile = 'out.root' # will be renamed later
    infiles = glob.glob('input_files/*.root')
    
trees = [EventTree.EventTree(f) for f in infiles]
print('Running over trees from inputs:',infiles)
f_output = ROOT.TFile(outfile,'recreate')

#HadHcalCalibFactor = 4e3/240 # standin for sampling faction correction (4GeV neutrons into hcal face)
#EMHcalCalibFactor = 4e3/225 # standin for sampling faction correction (4GeV neutrons into hcal face)
HCalCalibFactor = 4e3/238   # standin for sampling faction correction (4GeV neutrons into hcal face)
ECalCalibFactor = 1.19 # obtained from 4 GeV neutrons into ECal + HCal, with hcal calib already applied

hh=OrderedDict()
def bookTH1(h, name, title, n, a, b):
    h[name] = ROOT.TH1F(name, title, n, a, b)
def bookTH2(h, name, title, n, a, b, nn, aa, bb):
    h[name] = ROOT.TH2F(name, title, n, a, b, nn, aa, bb)
    
bookTH1(hh,'nEvents','',1,0,1)
bookTH1(hh,'Truth_e',';Truth particle E [MeV]',40,0,5000)
bookTH1(hh,'Truth_ke',';Truth particle K.E. [MeV]',50,0,5000)
bookTH1(hh,'Truth_e_hcal',';Sum(particle E) entering HCal [MeV]',40,0,5000)
bookTH1(hh,'Truth_ke_hcal',';Sum(particle KE) entering HCal [MeV]',40,0,5000)
bookTH1(hh,'Truth_ke_ecal',';Sum(particle KE) entering HCal [MeV]',40,0,5000)

bookTH1(hh,'Calib_e',';Calib E [MeV]',40,0,8000)
bookTH1(hh,'Calib_eh',';Calib EM/Total energies',41,-0.05,1)
bookTH1(hh,'Calib_e_fine',';Calib E [MeV]',12000,0,12000)
bookTH1(hh,'Calib_ecal_e',';Calib ECal E [MeV]',40,0,8000)
bookTH1(hh,'Calib_hcal_e',';Calib HCal E [MeV]',40,0,8000)
bookTH1(hh,'Calib_ecal_e_fine',';Calib ECal E [MeV]',12000,0,12000)
bookTH1(hh,'Calib_hcal_e_fine',';Calib HCal E [MeV]',12000,0,12000)
bookTH2(hh,'Calib_e_vs_ecal_e',';Calib E [MeV];ECal E [MeV];', 40,0,5000, 40,0,5000)
bookTH2(hh,'Calib_e_vs_hcal_e',';Calib E [MeV];HCal E [MeV];', 40,0,5000, 40,0,5000)

bookTH2(hh,'Calib_e_vs_Truth_e',';Calib E [MeV];Truth particle E [MeV];', 40,0,5000, 40,0,5000)
bookTH2(hh,'Calib_e_vs_Truth_ke',';Calib E [MeV];Truth particle KE [MeV];', 40,0,5000, 40,0,5000)
bookTH2(hh,'Calib_e_vs_eh',';Calib E [MeV];EM/Tot',40,0,8000, 41,-0.05,1)

# hh['calib_2d'] = ROOT.TProfile2D('calib2d','',10,0,1,10,0,1,0,8000)
# hh['calib_2d'].SetName('calib_2d')

nFineEnergyBins=50
nCoarseEnergyBins=10 # for fits
bookTH2(hh,'Truth_e_vs_e',';Truth particle E [MeV];', nFineEnergyBins,0,5000, nFineEnergyBins,0,5000)
bookTH2(hh,'Truth_e_vs_e_hcal',';Truth particle E [MeV];Sum(particle E) entering HCal [MeV]', nFineEnergyBins,0,5000, nFineEnergyBins,0,5000)
bookTH2(hh,'Truth_e_vs_ECal',';Truth particle E [MeV];total ECal E [MeV]', nFineEnergyBins,0,5000, 2000,0,1e4)
bookTH2(hh,'Truth_e_vs_HCal',';Truth particle E [MeV];total HCal E [MeV]', nFineEnergyBins,0,5000, 400,0,400)

bookTH2(hh,'Truth_ke_vs_ke',';Truth particle K.E. [MeV];', nFineEnergyBins,0,5000, nFineEnergyBins,0,5000)
bookTH2(hh,'Truth_ke_vs_ke_hcal',';Truth particle E [MeV];Sum(particle K.E.) entering HCal [MeV]', nFineEnergyBins,0,5000, nFineEnergyBins,0,5000)
bookTH2(hh,'Truth_ke_vs_ECal',';Truth particle K.E. [MeV];total ECal E [MeV]', nFineEnergyBins,0,5000, 2000,0,1e4)
bookTH2(hh,'Truth_ke_vs_HCal',';Truth particle K.E. [MeV];total HCal E [MeV]', nFineEnergyBins,0,5000, 400,0,400)

nFineEnergyBins=500
# nCoarseBins=10 # for fits
nEcalBins=1000
nHcalBins=400
bookTH2(hh,'Truth_ke1_vs_ke1',';Truth particle K.E. [MeV];', nFineEnergyBins,0,5000, nFineEnergyBins,0,5000)
bookTH2(hh,'Truth_ke2_vs_ke2',';Truth particle K.E. [MeV];', nFineEnergyBins,0,5000, nFineEnergyBins,0,5000)
bookTH2(hh,'Truth_ke1_vs_ECal',';Truth particle K.E. [MeV];total ECal E [MeV]', nFineEnergyBins,0,5000, nEcalBins,0,1e4)
bookTH2(hh,'Truth_ke2_vs_HCal',';Truth particle K.E. [MeV];total HCal E [MeV]', nFineEnergyBins,0,5000, nHcalBins,0,400)
bookTH2(hh,'Truth_ECal_vs_ECal',';total ECal E [MeV];total ECal E [MeV]', nEcalBins,0,1e4, nEcalBins,0,1e4)
bookTH2(hh,'Truth_HCal_vs_HCal',';total HCal E [MeV];total HCal E [MeV]', nHcalBins,0,400, nHcalBins,0,400)
bookTH1(hh,'ECal_e_fine',';Ecal E [MeV]',nEcalBins,0,5e3)
bookTH1(hh,'HCal_e_fine',';Hcal E [MeV]',nHcalBins,0,400)
bookTH1(hh,'ECal_e',';Ecal E [MeV]',80,0,1e4)
bookTH1(hh,'HCal_e',';Hcal E [MeV]',80,0,400)
bookTH2(hh,'ECal_e_vs_HCal_e',';Hcal E [MeV]',80,0,1e4,80,0,400)

hh['p2_e_h_truth'] = ROOT.TProfile2D('prof2d', '', 20,0,1e4, 20,0,400,0,5000)

#
# produce 'ingredient' histograms from tree
#
for tree in trees:
    for ie, event in enumerate(tree):
        hh['nEvents'].Fill(0.5)
        #if ie > 1000: break
        ecal=0
        for h in event.EcalRecHits: ecal += h.getEnergy()
        hcal=0
        for h in event.HcalRecHits: hcal += h.getEnergy()
    
        # truth neutron
        truth=ldmx.SimTrackerHit()
        for t in event.TargetScoringPlaneHits:
            if t.getTrackID()!=1: continue
            if t.getPdgID()!=2112: continue
            z=t.getPosition()[2]
            if z>0 and z<1: truth=t
        truth_e = truth.getEnergy()
        truth_p = truth.getMomentum()
        truth_ke = sqrt(pow(truth_p[0],2)+pow(truth_p[1],2)+pow(truth_p[2],2))
        hh['Truth_e'].Fill(truth_e)
        hh['Truth_ke'].Fill(truth_ke)

        truth_e_hcal = 0
        truth_ke_hcal = 0
        for t in event.EcalScoringPlaneHits:
            z=t.getPosition()[2]
            if z<690.5: continue
            truth_e_hcal += t.getEnergy()
            truth_p = t.getMomentum()
            truth_ke_hcal = sqrt(pow(truth_p[0],2)+pow(truth_p[1],2)+pow(truth_p[2],2))
        #truth_ke_hcal=max(0,truth_ke_hcal) enforce this to prevent weird stuff?
        hh['Truth_e_hcal'].Fill(truth_e_hcal)
        hh['Truth_ke_hcal'].Fill(truth_ke_hcal)
        truth_ke_ecal = truth_ke-truth_ke_hcal
        hh['Truth_ke_ecal'].Fill(truth_ke_ecal)
        hh['Truth_e_vs_e_hcal'].Fill(truth_e, truth_e_hcal)
        hh['Truth_ke_vs_ke_hcal'].Fill(truth_ke, truth_ke_hcal)
        
        
        hh['ECal_e'].Fill(ecal)
        hh['HCal_e'].Fill(hcal)
        hh['ECal_e_vs_HCal_e'].Fill(ecal, hcal)
        hh['ECal_e_fine'].Fill(ecal)
        hh['HCal_e_fine'].Fill(hcal)
        hh['Truth_e_vs_e'].Fill(truth_e, truth_e)
        hh['Truth_e_vs_ECal'].Fill(truth_e, ecal)
        hh['Truth_e_vs_HCal'].Fill(truth_e, hcal)
        
        hh['Truth_ke_vs_ke'].Fill(truth_ke, truth_ke)
        hh['Truth_ke_vs_ECal'].Fill(truth_ke, ecal)
        hh['Truth_ke_vs_HCal'].Fill(truth_ke, hcal)
        
        hh['Truth_ke1_vs_ke1'].Fill(truth_ke_ecal, truth_ke_ecal)
        hh['Truth_ke2_vs_ke2'].Fill(truth_ke_hcal,truth_ke_hcal)
        if ecal>0:
            hh['Truth_ECal_vs_ECal'].Fill(ecal, ecal)
            hh['Truth_ke1_vs_ECal'].Fill(truth_ke_ecal, ecal)
        if hcal>0:
            hh['Truth_HCal_vs_HCal'].Fill(hcal, hcal)
            hh['Truth_ke2_vs_HCal'].Fill(truth_ke_hcal, hcal)
        hh['p2_e_h_truth'].Fill(ecal, hcal, truth_ke)


        # ecal_calib = 1.49371e+03 + ecal * 1.13678e+00
        # hcal_calib = 2.17416e+01 + hcal * 3.63492e+00
        ecal_calib = ECalCalibFactor * ecal
        hcal_calib = HCalCalibFactor * hcal
        e_calib=ecal_calib+hcal_calib
        hh['Calib_ecal_e'].Fill(ecal_calib)
        hh['Calib_hcal_e'].Fill(hcal_calib)
        hh['Calib_ecal_e_fine'].Fill(ecal_calib)
        hh['Calib_hcal_e_fine'].Fill(hcal_calib)
        hh['Calib_e'].Fill(e_calib)
        hh['Calib_e_vs_ecal_e'].Fill(e_calib, ecal_calib)
        hh['Calib_e_vs_hcal_e'].Fill(e_calib, hcal_calib)
        hh['Calib_eh'].Fill(ecal_calib/e_calib if e_calib else 0)
        hh['Calib_e_fine'].Fill(e_calib)
        hh['Calib_e_vs_Truth_ke'].Fill(e_calib, truth_ke)
        hh['Calib_e_vs_Truth_e'].Fill(e_calib, truth_ke)
        hh['Calib_e_vs_eh'].Fill(e_calib, ecal_calib/e_calib if e_calib else 0)
#
# remove overflow
#
for h in hh:
    remove_overflow(hh[h])

energy  = array('d',nCoarseEnergyBins*[0])
energye = array('d',nCoarseEnergyBins*[0])
e1  = array('d',nCoarseEnergyBins*[0])
e1e = array('d',nCoarseEnergyBins*[0])
e2  = array('d',nCoarseEnergyBins*[0])
e2e = array('d',nCoarseEnergyBins*[0])
ecal    = array('d',nCoarseEnergyBins*[0])
ecale   = array('d',nCoarseEnergyBins*[0])
hcal    = array('d',nCoarseEnergyBins*[0])
hcale   = array('d',nCoarseEnergyBins*[0])

for ebin in range(nCoarseEnergyBins):
    nBins=nFineEnergyBins // nCoarseEnergyBins
    fineBinLow = ebin*nBins+1
    fineBinHigh = (ebin+1)*nBins
    # h=hh['Truth_ke_vs_ECal']
    h=hh['Truth_ke1_vs_ECal']
    hn='bin{}_ecal'.format(ebin)
    hh[hn] = h.ProjectionY(hn,fineBinLow,fineBinHigh)
    ecal[ebin] = hh[hn].GetMean()
    ecale[ebin] = hh[hn].GetRMS()
    
    # h=hh['Truth_ke_vs_HCal']
    h=hh['Truth_ke2_vs_HCal']
    hn='bin{}_hcal'.format(ebin)
    hh[hn] = h.ProjectionY(hn,fineBinLow,fineBinHigh)
    hcal[ebin] = hh[hn].GetMean()
    hcale[ebin] = hh[hn].GetRMS()
    
    h=hh['Truth_ke_vs_ke']
    hn='bin{}_energy'.format(ebin)
    hh[hn] = h.ProjectionX(hn,fineBinLow,fineBinHigh)
    energy[ebin] = hh[hn].GetMean()
    energye[ebin] = hh[hn].GetRMS()

    h=hh['Truth_ke1_vs_ke1']
    hn='bin{}_energy'.format(ebin)
    hh[hn] = h.ProjectionX(hn,fineBinLow,fineBinHigh)
    e1[ebin] = hh[hn].GetMean()
    e1e[ebin] = hh[hn].GetRMS()

    h=hh['Truth_ke2_vs_ke2']
    hn='bin{}_energy'.format(ebin)
    hh[hn] = h.ProjectionX(hn,fineBinLow,fineBinHigh)
    e2[ebin] = hh[hn].GetMean()
    e2e[ebin] = hh[hn].GetRMS()
    
hh['g_reversed_ecal'] = ROOT.TGraphErrors(nCoarseEnergyBins, e1, ecal, e1e, ecale)
hh['g_reversed_ecal'].SetTitle(';truth ECal energy [MeV]; ECal RecHit energy [MeV]')
hh['g_reversed_hcal'] = ROOT.TGraphErrors(nCoarseEnergyBins, e1, hcal, e1e, hcale)
hh['g_reversed_hcal'].SetTitle(';truth HCal energy [MeV]; HCal RecHit energy [MeV]')

hh['old_g_ecal'] = ROOT.TGraphErrors(nCoarseEnergyBins, energy, ecal, energye, ecale)
hh['old_g_hcal'] = ROOT.TGraphErrors(nCoarseEnergyBins, energy, hcal, energye, hcale)
hh['old_g_2d'] = ROOT.TGraph2DErrors(nCoarseEnergyBins, ecal, hcal, energy, ecale, hcale, energye)
hh['old_g_2d'].SetName('old_g_2d')


#
# Reverse axes -- fit 
#
nCoarseBins=20
ecal_bins = array('d',nCoarseBins*[0])
hcal_bins = array('d',nCoarseBins*[0])
quantiles = array('d',[float(i)/nCoarseBins for i in range(nCoarseBins+1)])
hh['ECal_e_fine'].GetQuantiles(nCoarseBins,ecal_bins,quantiles)
hh['HCal_e_fine'].GetQuantiles(nCoarseBins,hcal_bins,quantiles)
ecal_bins=[hh['ECal_e_fine'].FindBin(x) for x in ecal_bins]+[hh['ECal_e_fine'].GetNbinsX()+1]
ecal_bins=sorted(list(set(ecal_bins)))
hcal_bins=[hh['HCal_e_fine'].FindBin(x) for x in hcal_bins]+[hh['HCal_e_fine'].GetNbinsX()+1]
hcal_bins=sorted(list(set(hcal_bins)))
print ('ecal_bins',ecal_bins)
print ('hcal_bins',hcal_bins)

e1  = array('d',(len(ecal_bins)-1)*[0])
e1e = array('d',(len(ecal_bins)-1)*[0])
e2  = array('d',(len(hcal_bins)-1)*[0])
e2e = array('d',(len(hcal_bins)-1)*[0])
ecal    = array('d',(len(ecal_bins)-1)*[0])
ecale   = array('d',(len(ecal_bins)-1)*[0])
hcal    = array('d',(len(hcal_bins)-1)*[0])
hcale   = array('d',(len(hcal_bins)-1)*[0])

for ib,b1 in enumerate(ecal_bins):
    if ib+1>=len(ecal_bins): continue
    b2=ecal_bins[ib+1]
    # bins: [b1,b2)
    
    h=hh['Truth_ke1_vs_ECal']
    hn='ke1_ecal_bin{}'.format(ib)
    hh[hn] = h.ProjectionX(hn,b1,b2-1)
    e1[ib] = hh[hn].GetMean()
    e1e[ib] = hh[hn].GetRMS()
        
    h=hh['Truth_ECal_vs_ECal']
    hn='ecal_bin{}'.format(ib)
    hh[hn] = h.ProjectionY(hn,b1,b2-1)
    ecal[ib] = hh[hn].GetMean()
    ecale[ib] = hh[hn].GetRMS()

for ib,b1 in enumerate(hcal_bins):
    if ib+1>=len(hcal_bins): continue
    b2=hcal_bins[ib+1]
    # bins: [b1,b2)
    
    h=hh['Truth_ke2_vs_HCal']
    hn='ke1_hcal_bin{}'.format(ib)
    hh[hn] = h.ProjectionX(hn,b1,b2-1)
    e2[ib] = hh[hn].GetMean()
    e2e[ib] = hh[hn].GetRMS()
        
    h=hh['Truth_HCal_vs_HCal']
    hn='hcal_bin{}'.format(ib)
    hh[hn] = h.ProjectionY(hn,b1,b2-1)
    hcal[ib] = hh[hn].GetMean()
    hcale[ib] = hh[hn].GetRMS()


hh['g_ecal'] = ROOT.TGraphErrors(len(ecal_bins)-1, ecal, e1, ecale, e1e)
hh['g_ecal'].SetTitle(';ECal RecHit energy [MeV];truth ECal energy [MeV]')
hh['g_hcal'] = ROOT.TGraphErrors(len(hcal_bins)-1, hcal, e2, hcale, e2e)
hh['g_hcal'].SetTitle(';HCal RecHit energy [MeV];truth HCal energy [MeV]')

# hh['g_hcal']







# ecal_layer_energies = [1000,1500,2000,2500,3000,3500,4000]
# for e in ecal_layer_energies:
#     h = hh['Ecal_minLayerSum']
#     b = h.GetYaxis().FindBin(e)
#     hh['Ecal_layerAbove{}MeV'.format(e)] = h.ProjectionX('Ecal_layerAbove{}MeV'.format(e),b,-1)



    
#f_output.Write()
for h in hh:
    if hh[h].InheritsFrom('TGraph'): hh[h].SetName(h)
    hh[h].Write()
f_output.Close()


