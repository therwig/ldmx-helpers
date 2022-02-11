import sys, os, ROOT, ctypes
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(ROOT.kCMYK)
from array import array
from math import atan, hypot
from collections import OrderedDict
from utils import *

tags=['0p1','0p2','0p4','0p8','1','1p5','2','3','4']
# tags=['0p1','0p2','0p4','0p8','1','2','4']
es=[float(t.replace('p','.')) for t in tags]
# for t in tags:
#     print('ldmx python3 neutron_calib.py out_1k_neu_{}GeV_ECalFace.root'.format(t))

def getRMSeff(h):
    s=-1
    vals = array('d',101*[0])
    q = array('d',[0.01*i for i in range(101)])
    h.GetQuantiles(101,vals,q)
    # print 'rms', vals
    # print 'rms', q
    # check the possible 68% ranges
    for b1 in range(101-68):
        b2 = b1 + 68
        ss=vals[b2]-vals[b1]
        # print ss
        if s<0 or ss<s: s=ss
    # print 'returning', s
    return s

g1s=[]
g2s=[]
grs=[]
dets=['ECalFace', 'HCalFace']
for det in dets:
    fnames=['histNeut_out_1k_neu_{}GeV_{}.root'.format(t,det) for t in tags]
    #fnames=['histNeut_out_1k_neu_{}GeV_HCalFace.root'.format(t) for t in tags]
    files = [ROOT.TFile(fn) for fn in fnames]
    hs = [f.Get('Calib_e_fine') for f in files]
    
    qs=[]
    RMSs=[]
    for ih, h in enumerate(hs):
        vals = array('d',5*[0])
        q = array('d',[.023,.159,.5,.841,.977])
        h.GetQuantiles(5,vals,q)
        # print( vals)
        # to relative errors
        m=vals[2]
        vals[0] = m-vals[0]
        vals[1] = m-vals[1]
        vals[3] = vals[3]-m
        vals[4] = vals[4]-m
        for i in range(5): vals[i] = vals[i]/(es[ih]*1e3)
        #print( vals)
        qs.append(vals)
        rms = getRMSeff(h)
        RMSs.append(rms)
    
    vals=[ [q[i] for q in qs] for i in range(5) ]
    d2, d1, m, u1, u2 = vals
    d2 = array('d',d2)
    d1 = array('d',d1)
    m  = array('d',m)
    u1 = array('d',u1)
    u2 = array('d',u2)
    
    x = array('d',es)
    nulls = array('d',len(tags)*[0])
    
    g1 = ROOT.TGraphAsymmErrors(len(es),x,m,nulls,nulls,d1,u1)
    g2 = ROOT.TGraphAsymmErrors(len(es),x,m,nulls,nulls,d2,u2)
    g1s.append(g1)
    g2s.append(g2)
    
    x2 = array('d',es)
    r = array('d',RMSs)
    for i in range(len(r)): r[i] = r[i]/(x2[i]*m[i]*1e3) # response times energy
    # for i in range(len(r)): r[i] = r[i]/(m[i])
    # print 'm', m
    # print 'r', r
    
    gr = ROOT.TGraph(len(es),x2,r)
    grs.append(gr)

leg = ROOT.TLegend(.73,.77, 0.93,.92)
leg.SetTextFont(42);
leg.SetNColumns(1);

for ig,g in enumerate(g1s):
    g.SetMarkerStyle(20)
    g.SetMarkerColor(ROOT.kBlack)
    g.SetLineColor(ROOT.kBlack)
    leg.AddEntry(g,dets[ig],'le')
    if ig==1:
        g.SetMarkerStyle(22)
        g.SetMarkerColor(ROOT.kBlue)
        g.SetLineColor(ROOT.kBlue)
# g1s[0].SetMarkerStyle(20)
# g1s[0].SetMarkerColor(ROOT.kBlack)
# g1s[0].SetLineColor(ROOT.kBlack)
# g1s[1].SetMarkerStyle(22)
# g1s[1].SetMarkerColor(ROOT.kBlack)
# g1s[1].SetLineColor(ROOT.kBlack)

mg = ROOT.TMultiGraph()
for g1 in g1s:
    mg.Add(g1)
#mg.Add(g2)
mg.SetTitle(';Neutron energy [GeV];E_{reco}/E_{truth}')
# means = [h.GetMean() for h in hs]
# y = array('d',means)

c = ROOT.TCanvas()
c.SetTopMargin(0.05)
c.SetRightMargin(0.05)
c.SetGrid()
mg.Draw('AP')


#leg.SetFillStyle(1001) #solid
leg.SetFillColor(0)
#leg.SetTextAlign(12) # left center
leg.SetBorderSize(0)
leg.Draw()

# g = ROOT.TGraph(len(es),x,y)
c.SaveAs('response.pdf')


# return


leg = ROOT.TLegend(.53,.65, 0.93,.92)
#leg = ROOT.TLegend(.73,.17, 0.93,.32)
leg.SetTextFont(42);
leg.SetNColumns(1);

mgr = ROOT.TMultiGraph()

# for ig, g in enumerate(grs):
#     fn = ROOT.TF1('fn','[0]+[1]/sqrt(x)+[2]/x',0.1,4)
#     # fn = ROOT.TF1('fn','[0]/x+[1]/sqrt(x)',0.1,4)
#     fn.SetParLimits(0,0,100)
#     fn.SetParLimits(1,0,100)
#     fn.SetParLimits(2,0,100)
#     # fn = ROOT.TF1('fn','[0]+[1]/sqrt(x)',0.1,4)
#     # fn = ROOT.TF1('fn','[1]/sqrt(x)+[0]/x',0.1,4)
#     g.Fit(fn,'','',0.1,4)
#     g.GetFunction('fn').SetLineColor(ROOT.kBlue if ig else ROOT.kBlack)
#     g.GetFunction('fn').SetLineStyle(2)
#     g.GetFunction('fn').SetLineWidth(1)

for ig,g in enumerate(grs):
    g.SetMarkerStyle(20)
    g.SetMarkerColor(ROOT.kBlack)
    g.SetLineColor(ROOT.kBlack)
    leg.AddEntry(g,dets[ig],'lp')
    if ig==1:
        g.SetMarkerStyle(22)
        g.SetMarkerColor(ROOT.kBlue)
        g.SetLineColor(ROOT.kBlue)
        
    fn = ROOT.TF1('fn','[0]+[1]/sqrt(x)+[2]/x',0.1,4)
    # fn = ROOT.TF1('fn','[0]/x+[1]/sqrt(x)',0.1,4)
    fn.SetParLimits(0,0,100)
    fn.SetParLimits(1,0,100)
    fn.SetParLimits(2,0,100)
    # fn = ROOT.TF1('fn','[0]+[1]/sqrt(x)',0.1,4)
    # fn = ROOT.TF1('fn','[1]/sqrt(x)+[0]/x',0.1,4)
    g.Fit(fn,'','',0.1,4)
    fitfn = g.GetFunction('fn')
    fitfn.SetLineColor(ROOT.kBlue if ig else ROOT.kBlack)
    fitfn.SetLineStyle(2)
    fitfn.SetLineWidth(1)
    pars = [fitfn.GetParameters()[i] for i in range(fitfn.GetNpar())]
    # print pars
    lab = '{:.2f}+{:.2f}/sqrt(E)+{:.2f}/E'.format(*pars)
    leg.AddEntry(fitfn,lab,'lp')
    
    mgr.Add(g)
        
mgr.SetTitle(';Neutron energy [GeV];#sigma_{eff}(E_{reco})/E_{reco}')

c = ROOT.TCanvas()
c.SetTopMargin(0.05)
c.SetRightMargin(0.05)
c.SetGrid()
mgr.Draw('ALP')


#leg.SetFillStyle(1001) #solid
leg.SetFillColor(0)
#leg.SetTextAlign(12) # left center
leg.SetBorderSize(0)
leg.Draw()

# g = ROOT.TGraph(len(es),x,y)
c.SaveAs('resolution.pdf')
exit(0)
