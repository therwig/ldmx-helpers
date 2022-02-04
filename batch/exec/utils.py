from math import sqrt

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
