import sys, os, ROOT, ctypes
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(ROOT.kCMYK)
from array import array
from math import atan, hypot
from collections import OrderedDict
from utils import *

infiles = 'hist.root'
if len(sys.argv)>1: infile = sys.argv[1]
outfile='plot_'+infile.split('/')[-1]

f_input = ROOT.TFile(infile,'read')
f_output = ROOT.TFile(outfile,'recreate')

hh=OrderedDict()
for k in f_input.GetListOfKeys():
    n = k.GetName()
    hh[n] = f_input.Get(n)

rand = ROOT.TRandom3()

def bookTH1(h, name, title, n, a, b):
    h[name] = ROOT.TH1F(name, title, n, a, b)
def bookTH2(h, name, title, n, a, b, nn, aa, bb):
    h[name] = ROOT.TH2F(name, title, n, a, b, nn, aa, bb)

    
#
# remove overflow
#
for h in hh:
    remove_overflow(hh[h])
    
def MakeRateVsCut(h, reverse=False):
    h2 = h.Clone("rate_"+h.GetName())
    n = h2.GetNbinsX()
    for i in range(1,n+1):
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
hh['rate_Hcal_sumE'] = MakeRateVsCut(hh['Hcal_sumE2'])
hh['rate_Hcal_sumBackE'] = MakeRateVsCut(hh['Hcal_sumBackE'])
hh['rate_Hcal_sumBackE2'] = MakeRateVsCut(hh['Hcal_sumBackE2'])
hh['rate_Hcal_sumSideE'] = MakeRateVsCut(hh['Hcal_sumSideE2'])
hh['rate_nEle'] = MakeRateVsCut(hh['nEle'])
hh['rate_Ele_pt'] = MakeRateVsCut(hh['Ele_pt'])
hh['rate_Ele_ptCap'] = MakeRateVsCut(hh['Ele_ptCap'])
hh['rate_Ele_ptTight'] = MakeRateVsCut(hh['Ele_ptTight'])
hh['rate_Ele_ptTightCap'] = MakeRateVsCut(hh['Ele_ptTightCap'])
hh['rate_Ele_pyAbs'] = MakeRateVsCut(hh['Ele_pyAbs'])
for i in range(1,5):
    hh['rate_Ele{}_pt'.format(i)] = MakeRateVsCut(hh['Ele{}_pt'.format(i)])
    hh['rate_Ele{}_e'.format(i)] = MakeRateVsCut(hh['Ele{}_e'.format(i)])
    
ecal_layer_energies = [1000,1500,2000,2500,3000,3500,4000]
for e in ecal_layer_energies:
    h = hh['Ecal_minLayerSum']
    b = h.GetYaxis().FindBin(e)
    hh['Ecal_layerAbove{}MeV'.format(e)] = h.ProjectionX('Ecal_layerAbove{}MeV'.format(e),b,-1)
ecal_layer_veto_energies = [100,200,500,1000,2000,3000]
for e in ecal_layer_veto_energies:
    h = hh['Ecal_maxLayerSum']
    b = h.GetYaxis().FindBin(e)
    hh['Ecal_layerBelow{}MeV'.format(e)] = h.ProjectionX('Ecal_layerBelow{}MeV'.format(e),0,b)
    
#hcal_layer_adcs = [5,10,20,50,100,1000,5000,10000]
hcal_layer_adcs = [100,1000,5000,10000]
for e in hcal_layer_adcs:
    h = hh['Hcal_minBackLayerSum']
    b = h.GetYaxis().FindBin(e)
    hh['Hcal_backLayerAbove{}adc'.format(e)] = h.ProjectionX('Hcal_backLayerAbove{}adc'.format(e),b,-1)
    h = hh['Hcal_maxBackLayerSum']
    b = h.GetYaxis().FindBin(e)
    hh['Hcal_backLayerBelow{}adc'.format(e)] = h.ProjectionX('Hcal_backLayerBelow{}adc'.format(e),0,b)
hcal_side_layer_adcs = [100,500,1000,2000,4000]
for e in hcal_side_layer_adcs:
    h = hh['Hcal_minSideLayerSum']
    b = h.GetYaxis().FindBin(e)
    hh['Hcal_sideLayerAbove{}adc'.format(e)] = h.ProjectionX('Hcal_sideLayerAbove{}adc'.format(e),b,-1)
    h = hh['Hcal_maxSideLayerSum']
    b = h.GetYaxis().FindBin(e)
    hh['Hcal_sideLayerBelow{}adc'.format(e)] = h.ProjectionX('Hcal_sideLayerBelow{}adc'.format(e),0,b)

pDir='plots'
os.system('mkdir -p '+pDir)    

def plot(n, hs_, pDir, hEvts=None, xtitle='',ytitle='',
         xmin=None, xmax=None, ymin=None, ymax=None
         ,legs=None, logy=False):
    if type(hs_)!=list: hs_=[hs_]
    legCoords=(.70,.62, 0.92,.92)
    isGraph = hs_[0].InheritsFrom('TGraph')
    if isGraph:
        legCoords=(.12,.68, 0.34,.92)
    else:
        legCoords=(.70,.62, 0.92,.92)

    c = ROOT.TCanvas('c','',400,400)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    if hEvts:
        c.SetLogy()
        c.SetGrid()
    if logy: c.SetLogy()
    hs=[]
    if legs:
        leg = ROOT.TLegend(*(legCoords)) 
        leg.SetTextFont(42);
        #leg.SetHeader("");
        leg.SetNColumns(1);
    if isGraph:
        mg=ROOT.TMultiGraph()
        for i,h in enumerate(hs_):
            g = h.Clone()
            mg.Add(g)
            if legs: leg.AddEntry(g,legs[i],'le')
        # for h in hs_: mg.Add(h.Clone())
        # if legs:
        #     for i,h in enumerate(hs_): 
        mg.Draw("ALP plc")
        if xtitle: mg.GetHistogram().GetXaxis().SetTitle(xtitle)
        if ytitle: mg.GetHistogram().GetYaxis().SetTitle(ytitle)
        mg.GetHistogram().GetYaxis().SetRangeUser(0,1.05)
    else:
        for i,h_ in enumerate(hs_):
            h = h_.Clone()
            hs+=[h]
            if hEvts:
                h.Scale(40e6/hEvts.GetBinContent(1))
            if i==0:
                if hEvts:
                    h.GetYaxis().SetTitle('Rate [hz]')
                    h.SetMinimum(ymin if ymin else 1)
                if xtitle: h.GetXaxis().SetTitle(xtitle)
                if ytitle: h.GetYaxis().SetTitle(ytitle)
                if xmax or xmin:
                    if xmin==None: xmin=0
                    if xmax==None: xmax=h.GetXaxis().GetXmax()
                    h.GetXaxis().SetRangeUser(xmin,xmax)
            if h.InheritsFrom('TH1'):
                h.Draw('e1 plc pfc'+(' same' if (i>0) else ''))
            else: # graph
                h.Draw('ALP')
            if legs: leg.AddEntry(h,legs[i],'le')
            # h.Draw('same plc' if (i>0) else 'plc')
            # h.Draw('same plc hist')
    if legs:
        leg.SetFillStyle(1001) #solid
        leg.SetFillColor(0)
        #leg.SetTextAlign(12) # left center
        leg.SetBorderSize(0)
        leg.Draw()
        
    c.SaveAs(pDir+'/'+n+'.pdf')

###
### Rates
###

hEvts=hh['nEvents']

# energy sums
plot('ecalMissingEnergy', hh['rate_Ecal_sumE'], pDir, hEvts=hEvts, xtitle='Maximum Total ECal Energy [MeV]',xmax=4e3)
plot('ecalMissingEnergyLong', hh['rate_Ecal_sumE'], pDir, hEvts=hEvts, xtitle='Maximum Total ECal Energy [MeV]')
plot('ecalOuterEnergy', hh['rate_Ecal_sumE_outer'], pDir, hEvts=hEvts, xtitle='ECal Energy in outer modules [MeV]')
plot('hcalEnergy', hh['rate_Hcal_sumE'], pDir, hEvts=hEvts, xtitle='Total HCal ADC counts', xmax=25e3)
plot('hcalBackEnergyZoom', hh['rate_Hcal_sumBackE'], pDir, hEvts=hEvts, xtitle='Total Back HCal ADC counts', ymin=1e4)
plot('hcalBackEnergy', hh['rate_Hcal_sumBackE2'], pDir, hEvts=hEvts, xtitle='Total Back HCal ADC counts', xmax=20e3)
plot('hcalSideEnergy', hh['rate_Hcal_sumSideE'], pDir, hEvts=hEvts, xtitle='Total Side HCal ADC counts', xmax=10e3)


# layer sums
hs = [hh['Hcal_backLayerAbove{}adc'.format(e)] for e in hcal_layer_adcs]
leg=['Sum(ADC)>{}'.format(e) for e in hcal_layer_adcs]
plot('hcalBackLayers', hs, pDir, hEvts=hEvts, xtitle='Back HCal trigger layer',legs=leg)
hs = [hh['Hcal_sideLayerAbove{}adc'.format(e)] for e in hcal_side_layer_adcs]
leg=['Sum(ADC)>{}'.format(e) for e in hcal_side_layer_adcs]
plot('hcalSideLayers', hs, pDir, hEvts=hEvts, xtitle='Side HCal trigger layer',legs=leg)
hs = [hh['Ecal_layerAbove{}MeV'.format(e)] for e in ecal_layer_energies]
leg=['Sum(MeV)>{}'.format(e) for e in ecal_layer_energies]
plot('ecalLayers', hs, pDir, hEvts=hEvts, xtitle='ECal trigger layer',legs=leg)

hs = [hh['Hcal_backLayerBelow{}adc'.format(e)] for e in hcal_layer_adcs]
leg=['Sum(ADC)<{}'.format(e) for e in hcal_layer_adcs]
plot('hcalBackLayersVetoFront', hs, pDir, hEvts=hEvts, xtitle='Back HCal trigger layer',legs=leg)
hs = [hh['Hcal_sideLayerBelow{}adc'.format(e)] for e in hcal_side_layer_adcs]
leg=['Sum(ADC)<{}'.format(e) for e in hcal_side_layer_adcs]
plot('hcalSideLayersVetoFront', hs, pDir, hEvts=hEvts, xtitle='Side HCal trigger layer',legs=leg)
hs = [hh['Ecal_layerBelow{}MeV'.format(e)] for e in ecal_layer_veto_energies]
leg=['Sum(MeV)<{}'.format(e) for e in ecal_layer_veto_energies]
plot('ecalLayersVetoFront', hs, pDir, hEvts=hEvts, xtitle='ECal trigger layer',legs=leg)

# electron
labs=['pt','ptCap','ptTight','ptTightCap']
plot('elePt', [hh['rate_Ele_'+x] for x in labs], pDir, hEvts=hEvts, xtitle='Trigger electron p_{T} [MeV]',legs=labs)
plot('elePy', hh['rate_Ele_pyAbs'], pDir, hEvts=hEvts, xtitle='Trigger electron |p_{y}| [MeV]')
plot('elePtOrPy', [hh['rate_Ele_pt'],hh['rate_Ele_pyAbs']], pDir, hEvts=hEvts, xtitle='Trigger electron momentum [MeV]',legs=['p_{T} cut', '|p_{y}| cut'])

plot('nEle', hh['rate_nEle'], pDir, hEvts=hEvts, xtitle='Trigger electron multiplicity')

# print( [hh['rate_Ele{}_pt'.format(i)] for x in range(1,5)])
plot('elePt_multi', [hh['rate_Ele{}_pt'.format(i)] for i in range(1,5)], pDir, hEvts=hEvts, xtitle='Trigger electron p_{T} [MeV]',legs=['ele'+str(i) for i in range(1,5)])
plot('eleE_multi', [hh['rate_Ele{}_e'.format(i)] for i in range(2,5)], pDir, hEvts=hEvts, xtitle='Trigger electron energy [MeV]',legs=['ele'+str(i) for i in range(2,5)])
    # hh['rate_Ele_pt'+str(i)] = MakeRateVsCut(hh['Ele_pt'+str(i)])
    # hh['rate_Ele_e'+str(i)] = MakeRateVsCut(hh['Ele_e'+str(i)])

def make_eff(num, den, rebin=1, zeroBelow=None):
    g = ROOT.TGraphAsymmErrors()
    num = num.Clone()
    den = den.Clone()
    if zeroBelow: #truncate low bins
        for i in range(num.FindBin(zeroBelow)+1):
            num.SetBinContent(i,0)
            num.SetBinError(i,0)
            den.SetBinContent(i,0)
            den.SetBinError(i,0)
    if rebin>1:
        num.Rebin(rebin)
        den.Rebin(rebin)
    g.Divide(num, den, "b(1,1) mode")
    g.SetName(num.GetName()+'_OVER_'+den.GetName())
    return g
    
# g = ROOT.TGraphAsymmErrors()
# g.BayesDivide(hh['Truth_pt_Ele400'],hh['Truth_pt2'])
# plot('eff_Ele400', g, pDir, xtitle='Truth electron p_{T} [MeV]')
#print (hh['Truth_pt_Ele400'],hh['Truth_pt2'])
# e1=make_eff(hh['Truth_pt_Ele400'],hh['Truth_pt2'], rebin=4)
# e2=make_eff(hh['Truth_pt_Ele500'],hh['Truth_pt2'], rebin=4)
# print([e1,e2])
# plot('eff_Ele400', [e1,e2], pDir, xtitle='Truth electron p_{T} [MeV]',ytitle="efficiency",legs=['p_{T}>400 MeV','p_{T}>500 MeV'])
zeroBelow=50 # MeV
plot('eff_ele_e2_Ele0', make_eff(hh['Truth_e2_Ele0'],hh['Truth_e3'], rebin=2), pDir, xtitle='Truth electron E [MeV]',ytitle="efficiency")
plot('eff_ele_e_Ele0', make_eff(hh['Truth_e_Ele0'],hh['Truth_e'], rebin=2), pDir, xtitle='Truth electron E [MeV]',ytitle="efficiency")
plot('eff_ele_pt_Ele0', make_eff(hh['Truth_pt_Ele0'],hh['Truth_pt2'], rebin=2), pDir, xtitle='Truth electron p_{T} [MeV]',ytitle="efficiency")
plot('eff_ele_pt_Ele400', make_eff(hh['Truth_pt_Ele400'],hh['Truth_pt2'], rebin=2, zeroBelow=zeroBelow), pDir, xtitle='Truth electron p_{T} [MeV]',ytitle="efficiency")
plot('eff_ele_pt_Ele500', make_eff(hh['Truth_pt_Ele500'],hh['Truth_pt2'], rebin=2, zeroBelow=zeroBelow), pDir, xtitle='Truth electron p_{T} [MeV]',ytitle="efficiency")

if 'Truth_e_BackHcal12000' in hh:
    zeroBelow=10 # MeV
    hh['eff_e_BackHcal12000'] = make_eff(hh['Truth_e_BackHcal12000'],hh['Truth_e2'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_e_BackHcal8000'] = make_eff(hh['Truth_e_BackHcal8000'],hh['Truth_e2'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_e_BackHcal4000'] = make_eff(hh['Truth_e_BackHcal4000'],hh['Truth_e2'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_e_BackHcal2000'] = make_eff(hh['Truth_e_BackHcal2000'],hh['Truth_e2'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_e_BackHcal1000'] = make_eff(hh['Truth_e_BackHcal1000'],hh['Truth_e2'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_e_BackHcal300']   = make_eff(hh['Truth_e_BackHcal300'],hh['Truth_e2'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_e_BackHcal50']    = make_eff(hh['Truth_e_BackHcal50'],hh['Truth_e2'], rebin=2, zeroBelow=zeroBelow)
    effs=[hh['eff_e_BackHcal12000'], hh['eff_e_BackHcal8000'], hh['eff_e_BackHcal4000'], hh['eff_e_BackHcal2000'], hh['eff_e_BackHcal1000'], hh['eff_e_BackHcal300'], hh['eff_e_BackHcal50']]
    labs = ['12000 ADCs', '8000 ADCs', '4000 ADCs', '2000 ADCs','1000 ADCs','300 ADCs', '50 ADCs']
    plot('eff_Hcal_vs_e', effs, pDir, xtitle='Truth particle E [MeV]',ytitle="efficiency", legs=labs)
    #plot('eff_Hcal12k', eff1, pDir, xtitle='Truth neutron E [MeV]',ytitle="efficiency")
    #plot('eff_Hcal300', eff2, pDir, xtitle='Truth neutron E [MeV]',ytitle="efficiency")
    #plot('eff_Hcal50',  eff3, pDir, xtitle='Truth neutron E [MeV]',ytitle="efficiency")
    
    hh['eff_ke_BackHcal12000'] = make_eff(hh['Truth_ke_BackHcal12000'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_ke_BackHcal8000'] = make_eff(hh['Truth_ke_BackHcal8000'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_ke_BackHcal4000'] = make_eff(hh['Truth_ke_BackHcal4000'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_ke_BackHcal2000'] = make_eff(hh['Truth_ke_BackHcal2000'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_ke_BackHcal1000'] = make_eff(hh['Truth_ke_BackHcal1000'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_ke_BackHcal300']   = make_eff(hh['Truth_ke_BackHcal300'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    hh['eff_ke_BackHcal50']    = make_eff(hh['Truth_ke_BackHcal50'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    effs=[hh['eff_ke_BackHcal12000'], hh['eff_ke_BackHcal8000'], hh['eff_ke_BackHcal4000'], hh['eff_ke_BackHcal2000'], hh['eff_ke_BackHcal1000'], hh['eff_ke_BackHcal300'], hh['eff_ke_BackHcal50']]
    labs = ['12000 ADCs', '8000 ADCs', '4000 ADCs', '2000 ADCs','1000 ADCs','300 ADCs', '50 ADCs']
    plot('eff_Hcal_vs_ke', effs, pDir, xtitle='Truth particle K.E. [MeV]',ytitle="efficiency", legs=labs)
    # if False:
    #     #zeroBelow=100 # MeV
    #     eff1 = make_eff(hh['Truth_ke_BackHcal12000'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    #     eff2 = make_eff(hh['Truth_ke_BackHcal300'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    #     eff3 = make_eff(hh['Truth_ke_BackHcal50'],hh['Truth_ke'], rebin=2, zeroBelow=zeroBelow)
    #     effs=[eff1, eff2, eff3]
    #     labs = ['12000 ADCs', '300 ADCs', '50 ADCs']
    #     plot('eff_Hcal_vs_ke', effs, pDir, xtitle='Truth neutron K.E. [MeV]',ytitle="efficiency", legs=labs)

# g.BayesDivide(hh['Truth_pt_Ele500'],hh['Truth_pt2'])
# plot('eff_Ele500', g, pDir, xtitle='Truth electron p_{T} [MeV]')
#TGraphAsymErrors
# ecal_layer_energies = [1000,1500,2000,2500,3000,3500,4000]
# for e in ecal_layer_energies:
#     h = hh['Ecal_minLayerSum']
#     b = h.GetYaxis().FindBin(e)
#     hh['Ecal_layerAbove{}MeV'.format(e)] = h.ProjectionX('Ecal_layerAbove{}MeV'.format(e),b,-1)

#f_output.Write()

def resample_and_fill(hSamp, hFill, nResample, nEntries=-1, func=lambda x:x):
    if nEntries<0: nEntries = int(hSamp.GetEntries())
    for i in range(nEntries):
        x=0
        for j in range(nResample): x += hSamp.GetRandom()
        hFill.Fill(func(x))

nResamples=int(1e4)
for i in range(1,5):
    hname = 'Ecal_sumE_resample'+str(i)
    bookTH1(hh,hname,';total E [MeV]',200,0,4e3+i*4e3)
    resample_and_fill(hh['Ecal_sumE'], hh[hname],i, nEntries=nResamples)
    remove_overflow(hh[hname])
    hh[hname].Scale( hh['Ecal_sumE'].GetEntries() / float(hh[hname].GetEntries()) )
    #print("filled Ecal_sumE_resample",i)
    
nResamples=int(1e6)
nResamples=int(1e4)
for i in range(1,5):
    hname = 'Ecal_missingE_resample'+str(i)
    # bookTH1(hh,hname,';total E [MeV]',400,-4e3,4e3)
    bookTH1(hh,hname,';total E [MeV]',200,0,4e3)
    resample_and_fill(hh['Ecal_sumE'], hh[hname],i, nEntries=nResamples, func = lambda x: i*4e3-x)
    remove_overflow(hh[hname])
    hh['rate_'+hname] = MakeRateVsCut(hh[hname])
    print("filled missing e resample",i)
    
# hh['Ecal_missingE'] = hh['Ecal_sumE'].Clone()
# bBeam=hh['Ecal_sumE'].FindBin(4e3)
# for b in range(1,hh['Ecal_missingE'].GetNbinsX()+2):
#     hh['Ecal_missingE'].SetBinContent(b, hh['Ecal_missingE'].GetBinContent(bBeam-b))
#     hh['Ecal_missingE'].SetBinError(b, hh['Ecal_missingE'].GetBinError(bBeam-b))
# hh['rate_Ecal_missingE'] = MakeRateVsCut(hh['Ecal_missingE'])
# plot('ecalMissingEnergy', hh['rate_Ecal_sumE'], pDir, hEvts=hEvts, xtitle='Maximum Total ECal Energy [MeV]')

hs = [hh['Ecal_sumE_resample'+str(i)] for i in [4,3,2,1]]+[hh['Ecal_sumE']]
leg=['{}e resample'.format(e) for e in [4,3,2,1]]+['1e sim.']
plot('ecalTotalEnergyResample', hs, pDir, hEvts=None, xtitle='',legs=leg, logy=True)

hs = [hh['rate_Ecal_missingE_resample'+str(i)] for i in range(1,5)] #+ [hh['rate_Ecal_missingE']]
leg=['{}e, resampled'.format(e) for e in range(1,5)] #+ ['1e']
plot('ecalMissingEnergyResample', hs, pDir, hEvts=None, xtitle='Missing energy [MeV]',legs=leg, logy=True, xmin=0)

for h in hh:
    hh[h].Write()
f_output.Close()

