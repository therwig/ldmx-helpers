from math import sqrt
import ROOT

def add_bin_1d(h, x1, x2):
    h.SetBinContent(x1, h.GetBinContent(x1) + h.GetBinContent(x2))
    h.SetBinError(x1, sqrt(h.GetBinError(x1)**2 + h.GetBinError(x2)**2))
    h.SetBinContent(x2, 0)
    h.SetBinError(x2, 0)

def add_bin_2d(h, x1, y1, x2, y2):
    h.SetBinContent(x1,y1, h.GetBinContent(x1,y1) + h.GetBinContent(x2,y2))
    h.SetBinError(x1,y1, sqrt(h.GetBinError(x1,y1)**2 + h.GetBinError(x2,y2)**2))
    h.SetBinContent(x2,y2, 0)
    h.SetBinError(x2,y2, 0)

def remove_overflow_1d(h):
    add_bin_1d(h, 1, 0)
    add_bin_1d(h, h.GetNbinsX(), h.GetNbinsX()+1)

def remove_overflow_2d(h):
    for binx in range(h.GetNbinsX()+2):
        add_bin_2d(h, binx, h.GetNbinsY(), binx, h.GetNbinsY()+1)
        add_bin_2d(h, binx, 1, binx, 0)
    for biny in range(h.GetNbinsY()+2):
        add_bin_2d(h, h.GetNbinsX(), biny, h.GetNbinsX()+1, biny)
        add_bin_2d(h, 1, biny, 0, biny)
    
def remove_overflow(h):
        if h.InheritsFrom("TH2"): remove_overflow_2d(h)
        else: remove_overflow_1d(h)


def plot(n, hs_, pDir, hEvts=None, xtitle='',ytitle='',
         xmin=None, xmax=None, ymin=None, ymax=None
         ,legs=None, logy=False, spam=False):
    if type(hs_)!=list: hs_=[hs_]
    legCoords=(.70,.62, 0.92,.92)
    isGraph = hs_[0].InheritsFrom('TGraph')
    if isGraph:
        legCoords=(.12,.68, 0.34,.92)
    else:
        legCoords=(.70,.62, 0.92,.92)

    # spam
    legCoords=(.67,.52, 0.97,.92)
    c = ROOT.TCanvas('c','',500,400)
    c.SetRightMargin(0.02)
    c.SetTopMargin(0.07)
    c.SetLeftMargin(0.10)
    c.SetBottomMargin(0.11)
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
            #spam
            h.SetLineWidth(2)
            
            if hEvts:
                h.Scale(40e6/hEvts.GetBinContent(1))
            if i==0:
                if hEvts:
                    h.GetYaxis().SetTitle('Trigger rate [Hz]')
                    h.SetMinimum(ymin if ymin else 1)
                if xtitle: h.GetXaxis().SetTitle(xtitle)
                if ytitle: h.GetYaxis().SetTitle(ytitle)
                if xmax or xmin:
                    if xmin==None: xmin=0
                    if xmax==None: xmax=h.GetXaxis().GetXmax()
                    h.GetXaxis().SetRangeUser(xmin,xmax)
                #spam
                h.GetXaxis().SetTitleSize(0.05)
                h.GetXaxis().SetTitleOffset(1.0)
                h.GetXaxis().SetLabelSize(0.05)
                h.GetYaxis().SetTitleSize(0.05)
                h.GetYaxis().SetTitleOffset(0.95)
                h.GetYaxis().SetLabelSize(0.05)
            if h.InheritsFrom('TH1'):
                h.Draw('e1 plc pfc'+(' same' if (i>0) else ''))
            else: # graph
                h.Draw('ALP')
            if legs: leg.AddEntry(h,legs[i],'le')
            # h.Draw('same plc' if (i>0) else 'plc')
            # h.Draw('same plc hist')
    if legs:
        #leg.SetTextAlign(12) # left center
        leg.SetFillStyle(1001) #solid
        leg.SetFillColor(0)
        leg.SetBorderSize(0)
        leg.Draw()
        
    if spam:
        h.GetXaxis().SetTitleSize(0.065)
        h.GetXaxis().SetTitleOffset(1.0)
        h.GetXaxis().SetLabelSize(0.065)
        h.GetYaxis().SetTitleSize(0.065)
        h.GetYaxis().SetTitleOffset(0.95)
        h.GetYaxis().SetLabelSize(0.065)
        
        l = ROOT.TLatex()
        l.SetTextFont(72)
        l.SetTextSize(0.05)
        xtext=0.71
        ytext=0.945
        l.DrawLatexNDC(xtext,ytext,"LDMX")
        l.SetTextFont(52)
        # l.DrawLatexNDC(xtext+0.11,ytext,"Simulation Preliminary")
        l.DrawLatexNDC(xtext+0.11,ytext,"Simulation")
        
    c.SaveAs(pDir+'/'+n+'.pdf')
    
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
        
