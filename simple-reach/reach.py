import ROOT
import numpy as np
from array import array

def load_mA_vs_epsilon(fname, MeV=1e3):
    ma_vs_e = np.loadtxt(fname)
    chi_vs_y = np.zeros(ma_vs_e.shape)
    chi_vs_y[:,0] = ma_vs_e[:,0]/3 *MeV
    chi_vs_y[:,1] = ma_vs_e[:,1]*0.5/pow(3,4)
    return chi_vs_y
def load_chi_vs_y(fname, cols=(0,1), MeV=1e3, delim=None):
    dat = np.loadtxt(fname, delimiter=delim)
    chi_vs_y = np.zeros((dat.shape[0],2))
    chi_vs_y[:,0] = dat[:,cols[0]]*MeV
    chi_vs_y[:,1] = dat[:,cols[1]]
    return chi_vs_y
    
def get_min_graph(g1, g2, nSamples=100, lo=1, hi=1e3):
    xmin1=None
    xmax1=None
    xmin2=None
    xmax2=None
    for i in range(g1.GetN()):
        if xmin1==None or g1.GetX()[i] < xmin1: xmin1 = g1.GetX()[i]
        if xmax1==None or g1.GetX()[i] > xmax1: xmax1 = g1.GetX()[i]
    for i in range(g2.GetN()):
        if xmin2==None or g2.GetX()[i] < xmin2: xmin2 = g2.GetX()[i]
        if xmax2==None or g2.GetX()[i] > xmax2: xmax2 = g2.GetX()[i]
    # print xmin, xmax
    x1 = max(min(xmin1,xmin2), lo)
    x2 = min(max(xmax1,xmax2), hi)
    print x1, x2
    x1 = np.log(x1)
    x2 = np.log(x2)
    xvals = np.array([x1 + i*(x2-x1)/(nSamples-1) for i in range(nSamples)])
    xvals = np.exp(xvals)
    yvals=[]
    opt=''
    for x in xvals:
        print x,
        if x<xmin1 or x>xmax1:
            yvals.append( g2.Eval(x,0,opt) )
            print yvals[-1],'(0)'
        elif x<xmin2 or x>xmax2:
            yvals.append( g1.Eval(x,0,opt) )
            print yvals[-1],'(1)'
        else:
            yvals.append( min(g1.Eval(x,0,opt),g2.Eval(x,0,opt)) )
            print yvals[-1],'(2)'
    yvals = np.array( yvals )
    return ROOT.TGraph(nSamples, xvals, yvals)
    #g.Eval(3.5,0,"S")
    
arrs=[]
#theory
arrs.append(load_chi_vs_y('majorana.txt'))
arrs.append(load_chi_vs_y('pseudo.txt'))
arrs.append(load_chi_vs_y('scalar.txt'))

arrs.append(load_chi_vs_y('LSND_Patrick_y_mchi_R3_alphaD05_MeVunits.dat',MeV=1))
arrs.append(load_chi_vs_y('MiniBooNE2018_y_vs_mChi_alphaD05_ratio3.dat'))
arrs.append(load_chi_vs_y('babar.txt'))
arrs.append(load_chi_vs_y('NA64.csv', MeV=1, delim=','))
arrs.append(load_chi_vs_y('bkgd_best.txt', MeV=1))

arrs.append(load_chi_vs_y('eat_1e13.txt', cols=(0,1), MeV=1))
arrs.append(load_mA_vs_epsilon('Phase1Reach0p5_mA_vs_epsilon_Blue.dat'))
arrs.append(load_mA_vs_epsilon('Phase2AlReach0p5_mA_vs_epsilon_Red.dat'))

# arrs.append(load_chi_vs_y('meson_dark_photon.txt', cols=(0,1), MeV=1))
# arrs.append(load_chi_vs_y('meson_dark_photon.txt', cols=(0,3), MeV=1))
# arrs.append(load_chi_vs_y('meson_dark_photon.txt', cols=(0,4), MeV=1))
arrs.append(load_chi_vs_y('na64_best.txt', MeV=1))
arrs.append(load_chi_vs_y('phaseI_best.txt', MeV=1))
arrs.append(load_chi_vs_y('phaseII_best.txt', MeV=1))
#arrs.append(load_chi_vs_y('eat_meson_dark_photon.txt', cols=(0,5), MeV=1))
arrs.append(load_chi_vs_y('eat_best.txt', MeV=1))
# arrs.append(load_chi_vs_y('bkgd_best.txt', MeV=1))


# dat = np.loadtxt('NA64.csv',delimiter=',', )
# print dat

c = ROOT.TCanvas()
c.SetTopMargin(0.05)
c.SetRightMargin(0.05)
c.SetLogy()
c.SetLogx()

mg = ROOT.TMultiGraph()
leg = ROOT.TLegend(.70,.12, 0.94,.5)
leg.SetTextFont(42)
leg.SetNColumns(1)
colz= 3*[ROOT.kBlack]+[ROOT.kGray+1,ROOT.kGray+1,ROOT.kGray+1,ROOT.kGray+1, ROOT.kGray+1, ROOT.kGreen+2, ROOT.kRed, ROOT.kBlue, ROOT.kGray+1, ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2]+ [ROOT.kViolet]+ list(range(4,10))
shades=[3,4,5,6,7] #[0,1,2,3]
theorys=[0,1,2]
labs=["majorana","pseudo","scalar"]
labs+=['LSND','MiniBooNE','BaBar',"NA64 (brem)","all bkgd","LDMX ECal E_{miss}","LDMX Phase1","LDMX Phase2"]
labs+=['NA64 (meson)',#
       "Phase1 (meson)","Phase2 (meson)","LDMX ECal E_{miss} (meson)",]+['best']
# for i in theory:
#     arr=arrs[i]
#     xs = array('d',arr[:,0])
#     ys = array('d',arr[:,1])
#     g = ROOT.TGraph(arr.shape[0], xs, ys)
#     g.SetLineWidth(2)
#     g.SetLineColor(ROOT.kBlack)
#     mg.Add(g)
gshades=[]
for i in [7]: #total b only #shades:
    arr=arrs[i]
    xs = array('d',arr[:,0])
    ys = array('d',arr[:,1])
    g = ROOT.TGraph(arr.shape[0], xs, ys)
    g.SetLineWidth(8000)
    # g.SetFillColor(ROOT.kGray)
    g.SetFillColorAlpha(ROOT.kGray,0.5)
    # mg.Add(g)
    gshades+=[g]

gs=[]
for i,arr in enumerate(arrs):
    #if i in theory: continue
    xs = array('d',arr[:,0])
    ys = array('d',arr[:,1])
    g = ROOT.TGraph(arr.shape[0], xs, ys)
    g.SetName(labs[i])
    g.SetLineWidth(3)
    if i<3: # theory
        g.SetLineWidth(2)
    elif i<7: # bkgds
        g.SetLineWidth(0)
    if i>10: # meson
        g.SetLineStyle(2)
        g.SetLineWidth(2)
    if i==11: # na64 meson
        g.SetLineWidth(0)
    #     g.SetLineWidth(8003)
    #     g.SetFillColor(colz[i])
    g.SetLineColor(colz[i])
    gs.append(g)

# gs[-1].SetLineStyle(1)
# gs[-1].SetLineWidth(1)
# k=5
# for i in range(gs[k].GetN()):
#     print gs[k].GetX()[i], gs[k].GetY()[i]
        
# gg = get_min_graph(gs[6], gs[9], lo=1, hi=500)
# gg.SetLineColor(ROOT.kViolet)
# print gs[6].GetName(), gs[9].GetName()
# mg.Add(gg)

dummy1 = ROOT.TGraph()
dummy1.SetLineColor(ROOT.kBlack)
dummy1.SetLineWidth(3)
dummy2 = ROOT.TGraph()
dummy2.SetLineColor(ROOT.kBlack)
dummy2.SetLineWidth(2)
dummy2.SetLineStyle(2)
leg.AddEntry(dummy1,'Dark bremsstrahlung','l')
leg.AddEntry(dummy2,'Meson','l')

for i, g in enumerate(gs):
    if i in theorys:
        mg.Add(g)
    
for g in gshades: mg.Add(g)

for i, g in enumerate(gs):
    if i in theorys: continue
    if i in [8,9,10]: leg.AddEntry(g,labs[i],'l')
    #leg.AddEntry(g,labs[i],'l')
    mg.Add(g)

mg.Draw('AC ')
h = mg.GetHistogram()
# h.GetXaxis().SetRangeUser(1,500)
h.SetTitle(";m_{#chi} [MeV];y=#varepsilon^{2}#alpha_{D}(m_{#chi}/m_{A'})^{4}")
h.GetXaxis().CenterTitle()
h.GetYaxis().CenterTitle()
# h.SetTitleFont(12)
mg.GetXaxis().SetLimits(1,600)
mg.SetMinimum(2e-16)
mg.SetMaximum(8e-8)
# mg.GetXaxis().SetLimits(20,40)
# mg.SetMinimum(5e-11)
# mg.SetMaximum(5e-9)

leg.SetFillColor(0)
leg.SetBorderSize(0)
leg.SetTextFont(12)
leg.Draw()
h.Draw("axis same")

l = ROOT.TLatex()
l.SetTextFont(72)
xtext=0.15
ytext=0.89
l.DrawLatexNDC(xtext,ytext,"LDMX")
l.SetTextFont(52)
l.DrawLatexNDC(xtext+0.1,ytext,"Simulation")
#l.DrawLatexNDC(xtext+0.1,ytext,"Simulation Preliminary")
# l.SetTextFont(42)
# l.DrawLatexNDC(xtext,ytext-0.05,"Projected 1e13-1e16 EoT")
# l.DrawLatexNDC(xtext,ytext-0.1,"Dark Photon")
#t# l.DrawLatexNDC(xtext,ytext-0.05,"#scale[0.7]{m_{A'}=3m_{#chi}}")

# l3 = ROOT.TLatex()
l.SetTextFont(132)
xtext=0.15
ytext=0.78
l.DrawLatexNDC(xtext,ytext+0.05,"#scale[0.7]{Dark Photon}")
l.SetTextFont(12)
l.DrawLatexNDC(xtext,ytext,"#scale[0.7]{#alpha_{D}=0.5, m_{A'}=3m_{#chi}}")
# l3.DrawLatexNDC(xtext,ytext,"#scale[0.7]{#alpha_{D}=0.5}")
# l3.DrawLatexNDC(xtext,ytext-0.05,"#scale[0.7]{m_{A'}=3m_{#chi}}")

l.SetTextAngle(25)
l.SetTextFont(62)
l.DrawLatexNDC(0.40,0.575,"#scale[0.6]{Scalar}")
l.DrawLatexNDC(0.40,0.51,"#scale[0.6]{Majorana}")
l.DrawLatexNDC(0.40,0.41,"#scale[0.6]{Pseudo-Dirac}")
# l.DrawLatexNDC(0.20,0.445,"#scale[0.6]{Scalar}")
# l.DrawLatexNDC(0.29,0.44,"#scale[0.6]{Majorana}")
# l.DrawLatexNDC(0.50,0.48,"#scale[0.6]{Pseudo-Dirac}")

c.SaveAs('plot.pdf')
# c.SaveAs('plot.png')
    # x, y = arr[:,0], arr[:,1]
    # print x
    # print y

# ma_vs_e = np.loadtxt('Phase2AlReach0p5_mA_vs_epsilon_Red.dat')
# chi_vs_y = np.zeros(ma_vs_e.shape)
# chi_vs_y[:,0] = ma_vs_e[:,0]/3
# chi_vs_y[:,1] = ma_vs_e[:,1]*0.5/pow(3,4)
# # chi = ma_vs_e[:,0]/3
# # y = ma_vs_e[:,1]*0.5/pow(3,4)
# # chi_vs_y = np.vstack( (chi, y))
# # print ma_vs_e.shape, chi_vs_y.shape
# print chi_vs_y

# LSND_Patrick_y_mchi_R3_alphaD05_MeVunits.dat
# MiniBooNE2018_y_vs_mChi_alphaD05_ratio3.dat
# Phase1Reach0p5_mA_vs_epsilon_Blue.dat
# Phase2AlReach0p5_mA_vs_epsilon_Red.dat

