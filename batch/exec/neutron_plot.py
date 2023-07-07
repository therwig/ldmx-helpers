import sys, os, ROOT, ctypes
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(ROOT.kCMYK)
ROOT.gStyle.SetEndErrorSize(5)
from array import array
import numpy as np
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
def getRMSeffArr(arr):
    # assumes that arr is already SORTED!
    s=-1
    n=len(arr)
    wid = int(n*0.68)
    i=0
    while i+wid<n:
        ss = abs(arr[i+wid] - arr[i])
        if s<0 or ss<s: s=ss
        i += 1
    return s

g1s=[]
g2s=[]
grs=[]
dets=['ECalFace', 'HCalFace']
detPrints=['ECal+HCal', 'HCal only']
detPrints=['Passing through ECal+HCal', 'Passing through HCal only']
xdiff = 0.015
nStraps=100
for idet, det in enumerate(dets):
    fnames=['histNeut_out_1k_neu_{}GeV_{}.root'.format(t,det) for t in tags]
    #fnames=['histNeut_out_1k_neu_{}GeV_HCalFace.root'.format(t) for t in tags]
    files = [ROOT.TFile(fn) for fn in fnames]
    hs = [f.Get('Calib_e_fine') for f in files]
    
    meds=[]
    qs=[]
    RMSs=[]
    RMSs_BS=[]
    nSamples=[]
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
        qs.append(vals)
        rms = getRMSeff(h)
        RMSs.append(rms)
        meds.append(m)

        # bootstrapping
        vals=[] # original dataset
        rmss=[] # ensemble of rmss
        for b in range(1,h.GetNbinsX()+2):
            num = h.GetBinContent(b)
            if num:
                xval = h.GetBinCenter(b)
                vals += [xval]*int(num)
        vals = np.array(vals)
        nSamples.append( len(vals) )
        for iStrap in range(nStraps):
            indices = np.random.randint(0,len(vals),len(vals))
            dset = vals[indices] # the bootstrap dataset
            dset.sort()
            rmss.append( getRMSeffArr(dset) )
        rmss.sort()
        lo, med, hi = rmss[int(nStraps*0.16)], rmss[int(nStraps/2)], rmss[int(nStraps*0.84)]
        print '{} : ({}, {}, {})'.format(rms, lo, med, hi)
        RMSs_BS.append( (med-lo, med, hi-med) ) # send as absolute errors

        # print vals
        # print len(vals)
        
        # exit(0)
        
        
    
    vals=[ [q[i] for q in qs] for i in range(5) ]
    d2, d1, med, u1, u2 = vals
    d2 = array('d',d2)
    d1 = array('d',d1)
    m  = array('d',med)
    u1 = array('d',u1)
    u2 = array('d',u2)
    
    x = array('d',[e+(2*idet-1)*xdiff for e in es])
    nulls = array('d',len(tags)*[0])
    
    g1 = ROOT.TGraphAsymmErrors(len(es),x,m,nulls,nulls,d1,u1)
    g2 = ROOT.TGraphAsymmErrors(len(es),x,m,nulls,nulls,d2,u2)
    g1s.append(g1)
    g2s.append(g2)
    
    x2 = array('d',es)
    r = array('d',RMSs)
    print 'original r', RMSs
    for i in range(len(r)): r[i] = r[i]/(x2[i]*m[i]*1e3) # response times energy
    print 'new r', r
    # for i in range(len(r)): r[i] = r[i]/(m[i])
    # print 'm', m
    # print 'r', r

    # print "down", [d*e for d,e in zip(d1,es)]
    # print "med", [d*e for d,e in zip(m,es)]
    # print "up", [d*e for d,e in zip(u1,es)]
    
    # gr = ROOT.TGraph(len(es),x2,r)
    m2  = array('d',[med/1e3 for med in meds])
    u1mean = array('d',[u1Rel*eGen/sqrt(n) for n,u1Rel,eGen in zip(nSamples,u1,es)]) # error on the mean
    d1mean = array('d',[d1Rel*eGen/sqrt(n) for n,d1Rel,eGen in zip(nSamples,d1,es)]) # error on the mean
    # u1mean = array('d',[u1Rel*eGen for u1Rel,eGen in zip(u1,es)]) # spread of dist
    # d1mean = array('d',[d1Rel*eGen for d1Rel,eGen in zip(d1,es)]) # spread of dist
    
    vals=[ [q[i]/1e3 for q in RMSs_BS] for i in range(3) ]
    rmsLo, rmsMed, rmsHi = vals
    rmsLo  = array('d',[r/(genE*resp) for r,genE,resp in zip(rmsLo ,es,m)])
    rmsMed = array('d',[r/(genE*resp) for r,genE,resp in zip(rmsMed,es,m)])
    rmsHi  = array('d',[r/(genE*resp) for r,genE,resp in zip(rmsHi ,es,m)])
    print 'rmsLo', rmsLo
    print 'rmsMed', rmsMed
    print 'rmsHi', rmsHi
    # for i in range(len(r)): r[i] = r[i]/(x2[i]*m[i]*1e3) # response times energy
    
    # print meds
    #gr = ROOT.TGraph(len(es),m2,r) # no errors
    # print m2
    # print r
    # print d1mean
    # print u1mean
    # print rmsLo
    # print rmsHi
    nCrop=2
    m2     = array('d',[m2    [i] for i in range(nCrop,len(m2    ))])
    rmsMed = array('d',[rmsMed[i] for i in range(nCrop,len(rmsMed))])
    d1mean = array('d',[d1mean[i] for i in range(nCrop,len(d1mean))])
    u1mean = array('d',[u1mean[i] for i in range(nCrop,len(u1mean))])
    rmsLo  = array('d',[rmsLo [i] for i in range(nCrop,len(rmsLo ))])
    rmsHi  = array('d',[rmsHi [i] for i in range(nCrop,len(rmsHi ))])
    print m2
    print rmsMed
    print d1mean
    print u1mean
    print rmsLo
    print rmsHi
    gr = ROOT.TGraphAsymmErrors(len(es)-nCrop,m2,rmsMed,d1mean,u1mean,rmsLo,rmsHi) # with errors
    # for i in range(gr.GetN()):
    #     print gr.GetX()[i], gr.GetY()[i]
    grs.append(gr)

leg = ROOT.TLegend(.37,.20, 0.97,.38)
leg.SetTextFont(42);
leg.SetNColumns(1);

for ig,g in enumerate(g1s):
    # g.SetMarkerStyle(20)
    # g.SetMarkerSize(2)
    g.SetMarkerStyle(34)
    g.SetMarkerSize(1)
    g.SetMarkerColor(ROOT.kBlack)
    g.SetLineColor(ROOT.kBlack)
    g.SetLineWidth(2)
    leg.AddEntry(g,detPrints[ig],'ple')
    if ig==1:
        # g.SetMarkerStyle(22)
        # g.SetMarkerStyle(34)
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
mg.SetTitle(';Generated neutron energy [GeV];E_{reco}/E_{gen}')
# means = [h.GetMean() for h in hs]
# y = array('d',means)

c = ROOT.TCanvas()
c.SetTopMargin(0.07)
c.SetRightMargin(0.02)
c.SetBottomMargin(0.15)
c.SetLeftMargin(0.13)
#c.SetGrid()
mg.Draw('AP')
mg.GetHistogram().GetXaxis().SetTitleSize(0.065)
mg.GetHistogram().GetXaxis().SetTitleOffset(1.0)
mg.GetHistogram().GetXaxis().SetLabelSize(0.065)
mg.GetHistogram().GetYaxis().SetTitleSize(0.065)
mg.GetHistogram().GetYaxis().SetTitleOffset(0.95)
mg.GetHistogram().GetYaxis().SetLabelSize(0.065)

ll = ROOT.TLine()
ll.SetLineColor(ROOT.kBlack)
ll.SetLineStyle(ROOT.kDashed)
ll.SetLineWidth(2)
ll.DrawLine(mg.GetHistogram().GetXaxis().GetXmin(),1,
            mg.GetHistogram().GetXaxis().GetXmax(),1)


#leg.SetFillStyle(1001) #solid
leg.SetFillColor(0)
#leg.SetTextAlign(12) # left center
leg.SetBorderSize(0)
leg.Draw()

l = ROOT.TLatex()
l.SetTextFont(72)
l.SetTextSize(0.06)
xtext=0.69
ytext=0.945
l.DrawLatexNDC(xtext,ytext,"LDMX")
l.SetTextFont(52)
l.DrawLatexNDC(xtext+0.115,ytext,"Simulation")

# g = ROOT.TGraph(len(es),x,y)
c.SaveAs('response.pdf')


# return

ROOT.gStyle.SetEndErrorSize(0)

#leg = ROOT.TLegend(.44,.59, 0.93,.92)
# leg = ROOT.TLegend(.52,.59, 0.97,.92)
leg = ROOT.TLegend(.37,.59, 0.97,.92)
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
    g.SetMarkerSize(2)
    g.SetMarkerSize(0) #TMP
    g.SetMarkerStyle(34)
    g.SetMarkerSize(1)
    g.SetMarkerColor(ROOT.kBlack)
    g.SetLineColor(ROOT.kBlack)
    g.SetLineWidth(3)
    g.SetLineWidth(3) #TMP
    leg.AddEntry(g,detPrints[ig],'lpe')
    if ig==1:
        # g.SetMarkerStyle(22)
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
    fitfn.SetLineWidth(3)
    pars = [fitfn.GetParameters()[i] for i in range(fitfn.GetNpar())]
    # print pars
    lab = '{:.2f}+{:.2f}/sqrt(E)+{:.2f}/E'.format(*pars)
    lab = '{:.2f}+{:.2f}/sqrt(E)'.format(pars[0],pars[1])
    leg.AddEntry(fitfn,lab,'lp')
    
    mgr.Add(g)
        
mgr.SetTitle(';Reconstructed neutron energy [GeV];#sigma_{eff}(E_{reco})/E_{reco}')

c = ROOT.TCanvas()
# c.SetTopMargin(0.05)
# c.SetRightMargin(0.05)
# c.SetBottomMargin(0.15)
# c.SetLeftMargin(0.15)
c.SetTopMargin(0.07)
c.SetRightMargin(0.02)
c.SetBottomMargin(0.15)
c.SetLeftMargin(0.13)
#c.SetGrid()
mgr.Draw('AP')

# mgr.GetHistogram().GetXaxis().SetTitleSize(0.07)
# mgr.GetHistogram().GetXaxis().SetTitleOffset(1.0)
# mgr.GetHistogram().GetXaxis().SetLabelSize(0.07)
# mgr.GetHistogram().GetYaxis().SetTitleSize(0.07)
# mgr.GetHistogram().GetYaxis().SetTitleOffset(1.0)
# mgr.GetHistogram().GetYaxis().SetLabelSize(0.07)
mgr.GetHistogram().GetXaxis().SetTitleSize(0.065)
mgr.GetHistogram().GetXaxis().SetTitleOffset(1.0)
mgr.GetHistogram().GetXaxis().SetLabelSize(0.065)
mgr.GetHistogram().GetYaxis().SetTitleSize(0.065)
mgr.GetHistogram().GetYaxis().SetTitleOffset(0.95)
mgr.GetHistogram().GetYaxis().SetLabelSize(0.065)

#leg.SetFillStyle(1001) #solid
leg.SetFillColor(0)
#leg.SetTextAlign(12) # left center
leg.SetBorderSize(0)
leg.Draw()

l = ROOT.TLatex()
l.SetTextFont(72)
l.SetTextSize(0.06)
xtext=0.69
ytext=0.945
l.DrawLatexNDC(xtext,ytext,"LDMX")
l.SetTextFont(52)
l.DrawLatexNDC(xtext+0.115,ytext,"Simulation")

# g = ROOT.TGraph(len(es),x,y)
c.SaveAs('resolution.pdf')
exit(0)
