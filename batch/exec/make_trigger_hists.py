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
    

# ecalLayers=[5,10,15,20,25,30] # for sums ?
nEcalLayers=35
nHcalLayers=50
nHcalLayersSide=15
bookTH1(hh,'nEvents','',1,0,1)
bookTH1(hh,'Ecal_sumE',';total E [MeV]',200,0,8000)
bookTH1(hh,'Ecal_sumE_outer',';total E [MeV]',200,0,4000)
bookTH2(hh,'Ecal_layerSum',';layer number;total E [MeV]', nEcalLayers,-0.5,nEcalLayers-0.5, 400,0,4000,)
bookTH2(hh,'Ecal_minLayerSum',';layer number;total E [MeV]', nEcalLayers,-0.5,nEcalLayers-0.5, 400,0,8000,)

bookTH1(hh,'Hcal_sumBackE',';total back HCal ADC [counts]',100,0,500)
bookTH1(hh,'Hcal_sumBackE2',';total back HCal ADC [counts]',100,0,50000)
bookTH1(hh,'Hcal_sumSideE',';total side HCal ADC [counts]',100,0,500)
bookTH1(hh,'Hcal_sumSideE2',';total side HCal ADC [counts]',100,0,50000)
bookTH1(hh,'Hcal_sumE',';total HCal ADC [counts]',100,0,500)
bookTH1(hh,'Hcal_sumE2',';total HCal ADC [counts]',100,0,50000)
bookTH2(hh,'Hcal_backLayerSum',';layer number;total ACD [counts]', nHcalLayers,-0.5,nHcalLayers-0.5, 200,0,10e3,)
bookTH2(hh,'Hcal_minBackLayerSum',';layer number;total ACD [counts]', nHcalLayers,-0.5,nHcalLayers-0.5, 200,0,20e3,)
bookTH2(hh,'Hcal_sideLayerSum',';layer number;total ACD [counts]', nHcalLayersSide,-0.5,nHcalLayersSide-0.5, 200,0,5000,)
bookTH2(hh,'Hcal_minSideLayerSum',';layer number;total ACD [counts]', nHcalLayersSide,-0.5,nHcalLayersSide-0.5, 200,0,10e3,)
# enum HcalSection { BACK = 0, TOP = 1, BOTTOM = 2, LEFT = 4, RIGHT = 3 };

bookTH1(hh,'Clus_e',';ECal cluster E [MeV]',200,0,8000)
bookTH1(hh,'Clus_nTP',';ECal cluster TP multiplicity',50,-0.5,49.5)
bookTH1(hh,'Clus_length',';ECal cluster length [#layers]',40,-0.5,39.5)
bookTH2(hh,'TS_xy',';x[mm];y[mm]', 40,-20,20,40,-50,50)

bookTH1(hh,'Ele_dx',';Trigger electron dx [mm]',40,-50,50)
bookTH1(hh,'Ele_dx_raw',';Trigger electron dx (no corr.) [mm]',40,-50,50)
bookTH1(hh,'Ele_dy',';Trigger electron dy [mm]',40,-50,50)
bookTH1(hh,'Ele_px',';Trigger electron p_{x} [MeV]',40,-600,600)
bookTH1(hh,'Ele_py',';Trigger electron p_{y} [MeV]',40,-600,600)
bookTH1(hh,'Ele_pyAbs',';Trigger electron |p_{y}| [MeV]',40,0,600)
bookTH1(hh,'Ele_pt',';Trigger electron p_{T} [MeV]',40,0,800)

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

# Ele trigger
bookTH1(hh,'Truth_pt_Ele400',';Truth electron p_{T} [MeV]',40,0,1200)
bookTH1(hh,'Truth_pt_Ele500',';Truth electron p_{T} [MeV]',40,0,1200)
# HCal trigger
bookTH1(hh,'Truth_e_BackHcal100',';Truth electron E [MeV]',40,0,4000)
bookTH1(hh,'Truth_e_BackHcal1000',';Truth electron E [MeV]',40,0,4000)
bookTH1(hh,'Truth_e_BackHcal10000',';Truth electron E [MeV]',40,0,4000)

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
        for i in range(nHcalLayersSide):
            hh['Hcal_sideLayerSum'].Fill(i, hcal_side_layers[i])
            hh['Hcal_minSideLayerSum'].Fill(i, sum(hcal_side_layers[i:]))
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
    
        # TS hit
        ts=ldmx.SimTrackerHit()
        truth=ldmx.SimTrackerHit()
        for t in event.TargetScoringPlaneHits:
            if t.getTrackID()!=1: continue
            z=t.getPosition()[2]
            if z<0 or z>1: continue
            truth=t
            # if t.getPdgID()!=11: continue
            # ts=t
            # p=ts.getMomentum()
            # hh['Truth_px'].Fill(p[0])
            # hh['Truth_py'].Fill(p[1])
            # hh['Truth_pt'].Fill(hypot(p[0],p[1]))
        hh['TS_xy'].Fill(ts.getPosition()[0], ts.getPosition()[1])
    
        # electron
        dx = clus.x() - ts.getPosition()[0]
        dx_hat = -( 2*(4000./clus.e()-1)+2.3 ) if clus.e() else 0 # expected dx [mm], when initial px=0
        dy = clus.y() - ts.getPosition()[1]
        px = 17.8 * clus.e() / 4e3 * (dx - dx_hat)
        py = 17.8 * clus.e() / 4e3 * dy
        pt = hypot(px,py)
        
        hh['Ele_dx'].Fill(dx - dx_hat)
        hh['Ele_dx_raw'].Fill(dx)
        hh['Ele_dy'].Fill(dy)
        hh['Ele_px'].Fill(px)
        hh['Ele_py'].Fill(py)
        hh['Ele_pyAbs'].Fill(abs(py))
        hh['Ele_pt'].Fill(pt)
    
        # truth, for the leading track
        truth_e = truth.getEnergy()
        truth_p = truth.getMomentum()
        truth_px = truth_p[0]
        truth_py = truth_p[1]
        truth_pt = hypot(truth_p[0],truth_p[1])
        hh['Truth_pyAbs'].Fill(abs(truth_py))
        hh['Truth_py'].Fill(truth_py)
        hh['Truth_px'].Fill(truth_px)
        hh['Truth_pt'].Fill(truth_pt)
        hh['Truth_pyAbs2'].Fill(abs(truth_py))
        hh['Truth_py2'].Fill(truth_py)
        hh['Truth_px2'].Fill(truth_px)
        hh['Truth_pt2'].Fill(truth_pt)
        hh['Truth_e'].Fill(truth_e)
    
        # Ele trigger
        if pt>400: hh['Truth_pt_Ele400'].Fill(truth_pt)
        if pt>500: hh['Truth_pt_Ele500'].Fill(truth_pt)
    
        # Neutron trigger
        if hcal_back_sum>100: hh['Truth_e_BackHcal100'].Fill(truth_e)
        if hcal_back_sum>1000: hh['Truth_e_BackHcal1000'].Fill(truth_e)
        if hcal_back_sum>10000: hh['Truth_e_BackHcal10000'].Fill(truth_e)
    
    
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
    
def MakeRateVsCut(h, reverse=False):
    h2 = h.Clone("rate_"+h.GetName())
    n = h2.GetNbinsX()
    for i in range(1,n+1):
        # h2.SetBinContent( h.Integral(i,n) )
        # events from bin ib to max         
        # e=ROOT.double(0)
        e=ctypes.c_double(0)
        if reverse:
            val = h.IntegralAndError(0,i,e)
        else:
            val = h.IntegralAndError(i,n+1,e)
        h2.SetBinContent(i,val)
        h2.SetBinError(i,e.value)
            
    return h2

hh['rate_Ecal_sumE'] = MakeRateVsCut(hh['Ecal_sumE'], reverse=True)
hh['rate_Ecal_sumE_outer'] = MakeRateVsCut(hh['Ecal_sumE_outer'])
hh['rate_Hcal_sumE'] = MakeRateVsCut(hh['Hcal_sumE'])

ecal_layer_energies = [1000,1500,2000,2500,3000,3500,4000]
for e in ecal_layer_energies:
    h = hh['Ecal_minLayerSum']
    b = h.GetYaxis().FindBin(e)
    hh['Ecal_layerAbove{}MeV'.format(e)] = h.ProjectionX('Ecal_layerAbove{}MeV'.format(e),b,-1)
    
hcal_layer_adcs = [5,10,20,50,100]
for e in hcal_layer_adcs:
    h = hh['Hcal_minBackLayerSum']
    b = h.GetYaxis().FindBin(e)
    hh['Hcal_backLayerAbove{}adc'.format(e)] = h.ProjectionX('Hcal_backLayerAbove{}adc'.format(e),b,-1)
    
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

