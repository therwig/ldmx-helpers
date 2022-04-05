import ROOT as r
import os

# constants
good_chans=list(range(16))
good_chans=list(range(8))+[9,12,14]
lyso_chans=list(range(4))+[9]
plastic_chans=[4,5,6,7,12,14]
maxEvents=-10000
maxDisplays=50
nSamples=30

# def printCanv(canv, path):
#     d = os.path.dirname(path)
#     print ('dir is ',d)
#     os.sys('mkdir -p '+d)
#     canv.Print(path)
    
# functions
def bookHist(hh,name,title,n,lo,hi):
    hh[name]=r.TH1F(name,title,n,lo,hi)
def bookHist2(hh,name,title,n,lo,hi,n2,lo2,hi2):
    hh[name]=r.TH2F(name,title,n,lo,hi,n2,lo2,hi2)

def arr2hist(arr,hname='dummy'):
    h = r.TH1F(hname,';sample',nSamples,-0.5,nSamples-0.5)
    for i in range(nSamples):
        h.SetBinContent(i+1,arr[i])
    return h

def make_display(c, chans, name='display',spam='',pd='./',single=False):
    hs=[]
    l=r.TLatex()
    l.SetNDC()
    if spam:  # clear the old spam
        c.cd(0)
        c.Clear()
        if not single: c.Divide(4,int((len(good_chans)+3)/4))
    if single:
        h = arr2hist(chans)
        # h.GetXaxis().SetLabelSize(0.08)
        # h.GetYaxis().SetLabelSize(0.08)
        hs+=[h]
        h.Draw("hist")
        l.DrawLatex(0.10,0.92,'#scale[0.4]{'+spam+'}')
    else:
        for i,ic in enumerate(good_chans):
            c.cd(i+1)
            # h = arr2hist(getattr(t,'chan'+str(i)),str(i))
            h = arr2hist(chans[ic],str(i))
            h.GetXaxis().SetLabelSize(0.08)
            h.GetYaxis().SetLabelSize(0.04)
            hs+=[h]
            h.Draw("hist")
            l.DrawLatex(0.2,0.8,'chan'+str(ic))
        c.cd(0)
        l.DrawLatex(0.005,0.005,'#scale[0.3]{'+spam+'}')
    c.Print(pd+'/'+name+'.pdf(')

def remove_spike_old(vals, disable=False):
    if disable: return -1
    ret=-1
    pred_thresh = 20
    abs_tol = 50
    abs_tol2 = 50
    for i in range(29):
        # single-bin spikes
        if i>0 and i<29: # in middle
            pred = 0.5*(vals[i-1]+vals[i+1])
        elif i==0 : pred=vals[0]
        else: pred=vals[29]
        if pred < pred_thresh and vals[i] > pred + abs_tol:
            ret=i
            
        # # consider spike on pedastal
        # if i>0 and i<29: # in middle
        #     pred = 0.5*(vals[i-1]+vals[i+1])
        #     diff = 0.5*(vals[i-1]-vals[i+1])
        #     if diff/(pred+1e-5)<0.1 and (vals[i] > pred+abs_tol) and (vals[i] > pred*3):
        #         ret=i
        
        # double-bin spikes
        if i>0 and i<28: # in middle
            pred = 0.5*(vals[i-1]+vals[i+2])
        if pred < pred_thresh and (vals[i]+vals[i+1])/2. > pred + abs_tol2:
            ret=i
    return ret

def fail_spike(vals, disable=False, tol=0.1):
    if disable or sum(vals)<1: return False, -1
    peak_frac = max(vals)/sum(vals)
    return peak_frac > 1-tol, peak_frac

def getRing4_Chi2(vals, disable=False):
    if disable or sum(vals)<1: return 9e9 # don't kill empties
    return sum([pow(vals[i]-vals[i+4],2) for i in range(nSamples-4)])

def getRing4_Chi2_rel(vals, disable=False):
    if disable or sum(vals)<1: return 9e9 # don't kill empties
    m = float(max(vals))
    norm = [x/m for x in vals]
    return sum([pow(norm[i]-norm[i+4],2) for i in range(nSamples-4)])

# def fail_saturation(vals):
#     nHigh=5
#     tolerance=0.2
#     satVal=525.
#     # sums = sum([vals[i] for i in range(15,15+nHigh)])
#     # avg = sums / nHigh
#     # relDiff = (avg/550 -1 )((sum([vals[i] for i in range(15,15+nHigh)])/nHigh) / 550. - 1.) < 0.1
#     fail=1
#     diffs=[]
#     # for i in range(15,15+nHigh):
#     for i in range(15,nSamples):
#         diffs.append( abs(vals[i]/satVal-1.) )
#         fail = (fail and diffs[-1] < tolerance)
#     nsat=0
#     reject=0
#     for i in range(15):
#         if diffs[i] < tolerance:
#             nsat += 1
#             if nsat>=nHigh: reject=1
#         else:
#             nsat = 0
#         # fail = (fail and diffs[-1] < tolerance)
#     # d = abs((sum([vals[i] for i in range(15,15+nHigh)])/nHigh) / 550. - 1.)
#     diffs = [round(d*100)/100 for d in diffs]
#     # return fail, diffs
#     return reject, diffs
#     # x=0
#     # cut = 20
#     # for i in range(nSamples-4):
#     #     x += pow(vals[i]-vals[i+4],2)
#     # return x


# def lyso_fail_sat5000(vals):
def fail_saturation(vals, nHigh=5, satVal=525, tolerance=0.2, firstSample=15, disable=False):
    if disable or sum(vals)<1: return False, []
    # nHigh=3
    # tolerance=0.2
    # satVal=5000.
    diffs=[]
    for i in range(firstSample,nSamples):
        diffs.append( abs(vals[i]/satVal-1.) )
    nsat=0
    reject=False
    for diff in diffs:
        if diff < tolerance:
            nsat += 1
            if nsat>=nHigh: reject=True
        else:
            nsat = 0
    diffs = [round(d*100)/100 for d in diffs]
    return reject, diffs
    
def fail_iso_bins(vals, nBins=1, tolerance=0.1, minVal=100, disable=False):
    if disable or sum(vals)<1: return False, 0
    
    for icenter in range(1,nSamples-nBins):
        peak=sum(vals[icenter:icenter+nBins])
        if peak < minVal: continue
        edges=vals[icenter-1] + vals[icenter+nBins]
        if peak+edges < 0.1: continue
        if (edges / (peak+edges)) < tolerance:
            #print(peak, edges, (edges / (peak+edges)) , tolerance)
            return True, edges / (peak+edges)
    return False, 0
