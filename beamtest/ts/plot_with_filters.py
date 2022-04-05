import ROOT as rAA
from sys import argv
from array import array
from collections import OrderedDict
from utils import *
from copy import copy
import os
r.gStyle.SetOptStat(0)
debug=0

f = r.TFile(argv[1],'read')
t = f.Get('Events')
pdir='plots'
os.system('mkdir -p '+pdir)

# book histograms
hh=OrderedDict()
for cfg in ['nocut','nocut_zeroSupp','noSpike','ring','final']:
    for i in range(16):
        bookHist(hh,cfg+"_sumQhi_chan{0}".format(i),"sumQ{0};Q [fC];Events".format(i),100,0,200000)
        bookHist(hh,cfg+"_sumQ_chan{0}".format(i),"sumQ{0};Q [fC];Events".format(i),100,0,100000)
        bookHist(hh,cfg+"_sumQ15_chan{0}".format(i),"sumQ{0};Q [fC];Events".format(i),100,0,100000)
        bookHist(hh,cfg+"_sumQlo_chan{0}".format(i),"sumQ{0};Q [fC];Events".format(i),100,0,2000)
bookHist(hh,"nHit","nHit;hit multiplicity;Events",10,-0.5,9.5)
bookHist(hh,"nHit_lyso","nHit lyso;lyso hit multiplicity;Events",10,-0.5,9.5)
bookHist(hh,"sumQ_lyso",";total Q (all lyso channels);Events",100,0,1000000)
bookHist(hh,"sumQ_plastic",";total Q (all plastic channels);Events",100,0,200000)
bookHist(hh,"hit",";hit channel;hits",16,-0.5,15.5)
bookHist2(hh,"hitCorr",";hit channel;hit channel",16,-0.5,15.5,16,-0.5,15.5)
# neighbors
bookHist2(hh,"sumQ_corr01",";sumQ chan0;sumQ chan1",100,0,300000,100,0,300000)
bookHist2(hh,"sumQ_corr13",";sumQ chan1;sumQ chan3",100,0,300000,100,0,300000)
bookHist2(hh,"sumQ_corr39",";sumQ chan3;sumQ chan9",100,0,300000,100,0,300000)
# neighbors-neighbords
bookHist2(hh,"sumQ_corr03",";sumQ chan0;sumQ chan3",100,0,300000,100,0,300000)
bookHist2(hh,"sumQ_corr19",";sumQ chan1;sumQ chan9",100,0,300000,100,0,300000)
bookHist2(hh,"sumQ_corr92",";sumQ chan9;sumQ chan2",100,0,300000,100,0,300000)

dispCanv = r.TCanvas('c','',600,400)
dispCanv.Divide(4,int((len(good_chans)+3)/4))
ring4_chi2_cut = 10000 # abs
ring4_chi2_cut = 1.5 # rel

nBadChanSpike=0
nRing4=0
nSat=0
nGoodDisplaysNZS=0
nGoodDisplays=0
nLowSumDisplays=[0]*len(good_chans)
for ie, e in enumerate(t):
    if ie>maxEvents and maxEvents>0: break
    # unpack channels from tree and clean
    all_chans_nzs = [getattr(t,'chan'+str(ic)) for ic in range(16)]
    all_chans = copy(all_chans_nzs)
    spike_spam=''
    for i, ic in enumerate(good_chans):
        # zero-suppression (zero if no hits above 1 PE)
        if sum([samp > 300 for samp in all_chans[ic]])==0:
            if debug and nGoodDisplaysNZS<maxDisplays:
                print("Suppressing chan {}. Sum {} for {}".format(ic, sum([samp > 300 for samp in all_chans[ic]]),
                                                                  [samp for samp in all_chans[ic]]))
            all_chans[ic] = [0]*nSamples
        # spike filter
        all_chans[ic] = array('d',all_chans[ic])
        failSpike, spikeScore = fail_spike(all_chans[ic], disable=0)
        # failSpike, spikeScore = fail_spike(all_chans[ic], disable=0)
        if failSpike:
            spike_spam='Found spike in event {}, chan{}, max/sum: {}'.format(
                ie, ic, spikeScore)
            break
        # period noise filter
        ring4_chi2 = getRing4_Chi2_rel(all_chans[ic], disable=0)
        if ring4_chi2 < ring4_chi2_cut:
            ring4_spam='Found 4-sample ringing in event {}, chan{}. Too-low chi2: {:.2f}. Sum {:.0f}'.format(
                ie, ic, ring4_chi2, sum(all_chans[ic]))
            break
        # saturation filter
        satFail, satVal = fail_saturation(all_chans[ic], nHigh=2, satVal=5000.)
        satFailLo, satValLo = fail_saturation(all_chans[ic], nHigh=5, satVal=500.)
        isoFail1, isoFailVal1 = fail_iso_bins(all_chans[ic])
        isoFail2, isoFailVal2 = fail_iso_bins(all_chans[ic], nBins=2)
        satFail = satFail or satFailLo or isoFail1 or isoFail2
        if satFail:
            sat_spam='Found saturation in event {}, chan{}. RelDiffs={}. chi2: {:.2f}. Sum {:.0f}'.format(
                ie, ic, satVal, ring4_chi2, sum(all_chans[ic]))
            break
        if nLowSumDisplays[i]<maxDisplays and sum(all_chans[ic])>5e3 and sum(all_chans[ic])<20e3:
            nLowSumDisplays[i] += 1
            spam='event {}. SumQ = {}. Ring4 chi2={:.2f}. SatVal={}.'.format(
                ie, round(sum(all_chans[ic])),ring4_chi2, satVal)
            os.system('mkdir -p '+pdir+'/display_lowQ')
            make_display(dispCanv, all_chans[ic], name='display_lowQ/'+str(ic), pd=pdir, spam=spam,single=1)
            
    sum_nzs = sum([sum(all_chans_nzs[ic]) for ic in good_chans])
    sum_all = sum([sum(all_chans[ic]) for ic in good_chans])
    if failSpike>=0 and nBadChanSpike<maxDisplays and sum_all>0.01:
        nBadChanSpike += 1
        make_display(dispCanv, all_chans,name='display_spikes',pd=pdir, spam='event {}. {}'.format(ie,spike_spam))
    elif ring4_chi2 < ring4_chi2_cut and nRing4<maxDisplays and sum_all>0.01:
        nRing4 += 1
        make_display(dispCanv, all_chans,name='display_ring4',pd=pdir, spam='event {}. {}'.format(ie,ring4_spam))
    elif satFail and nSat<maxDisplays and sum_all>0.01:
        nSat += 1
        make_display(dispCanv, all_chans,name='display_sat',pd=pdir, spam='event {}. {}'.format(ie,sat_spam))
    else:
        if nGoodDisplaysNZS<maxDisplays and sum_nzs>0.01:
            nGoodDisplaysNZS += 1
            make_display(dispCanv, all_chans_nzs, name='display_noZS', pd=pdir, spam='event '+str(ie))
        if nGoodDisplays<maxDisplays and sum_all>0.01:
            nGoodDisplays += 1
            make_display(dispCanv, all_chans, name='display_good', pd=pdir, spam='event '+str(ie))
           
    # log some distributions
    for i, samples in enumerate(all_chans):
        samples = array('d',samples)
        cn='_chan'+str(i)
        hh['nocut_sumQ'+cn].Fill(sum(all_chans_nzs[i]))
        hh['nocut_sumQ15'+cn].Fill(sum([c for c in all_chans_nzs[i]][15:]))
        hh['nocut_sumQlo'+cn].Fill(sum(all_chans_nzs[i]))
        hh['nocut_sumQhi'+cn].Fill(sum(all_chans_nzs[i]))
        hh['nocut_zeroSupp_sumQ'+cn].Fill(sum(samples))
        hh['nocut_zeroSupp_sumQ15'+cn].Fill(sum(samples[15:]))
        hh['nocut_zeroSupp_sumQlo'+cn].Fill(sum(samples))
        hh['nocut_zeroSupp_sumQhi'+cn].Fill(sum(samples))
        if not failSpike:
            hh['noSpike_sumQ'+cn].Fill(sum(samples))
            hh['noSpike_sumQ15'+cn].Fill(sum(samples[15:]))
            hh['noSpike_sumQlo'+cn].Fill(sum(samples))
            hh['noSpike_sumQhi'+cn].Fill(sum(samples))
            if ring4_chi2 >= ring4_chi2_cut:
                hh['ring_sumQ'+cn].Fill(sum(samples))
                hh['ring_sumQ15'+cn].Fill(sum(samples[15:]))
                hh['ring_sumQlo'+cn].Fill(sum(samples))
                hh['ring_sumQhi'+cn].Fill(sum(samples))
                if not satFail:
                    hh['final_sumQ'+cn].Fill(sum(samples))
                    hh['final_sumQ15'+cn].Fill(sum(samples[15:]))
                    hh['final_sumQlo'+cn].Fill(sum(samples))
                    hh['final_sumQhi'+cn].Fill(sum(samples))
    # after all filters
    if not (failSpike or ring4_chi2 < ring4_chi2_cut or satFail):
        nHit=0
        good_hits= [ sum(all_chans[ic]) > 25000 for ic in good_chans ]
        lyso_hits= [ sum(all_chans[ic]) > 25000 for ic in lyso_chans ]
        hits= [ sum(samples) > 25000 for samples in all_chans ]        
        hh['nHit'].Fill(sum(good_hits))
        hh['nHit_lyso'].Fill(sum(lyso_hits))
        hh['sumQ_lyso'].Fill(sum([sum(all_chans[ic]) for ic in lyso_chans]))
        hh['sumQ_plastic'].Fill(sum([sum(all_chans[ic]) for ic in plastic_chans]))
        hh['sumQ_corr01'].Fill(sum(all_chans[0]), sum(all_chans[1]))
        hh['sumQ_corr13'].Fill(sum(all_chans[1]), sum(all_chans[3]))
        hh['sumQ_corr39'].Fill(sum(all_chans[3]), sum(all_chans[9]))
        hh['sumQ_corr03'].Fill(sum(all_chans[0]), sum(all_chans[3]))
        hh['sumQ_corr19'].Fill(sum(all_chans[1]), sum(all_chans[9]))
        hh['sumQ_corr92'].Fill(sum(all_chans[9]), sum(all_chans[2]))
        for i, hiti in enumerate(hits):
            if i not in good_chans: continue
            if hiti: hh['hit'].Fill(i,1)
            for j, hitj in enumerate(hits):
                if j not in good_chans: continue
                if hiti and hitj: hh['hitCorr'].Fill(i,j,1)
    
if nBadChanSpike: dispCanv.Print(pdir+'/display_spikes.pdf]')
if nRing4: dispCanv.Print(pdir+'/display_ring4.pdf]')
if nSat: dispCanv.Print(pdir+'/display_sat.pdf]')
if nGoodDisplaysNZS: dispCanv.Print(pdir+'/display_noZS.pdf]')
if nGoodDisplays: dispCanv.Print(pdir+'/display_good.pdf]')
for i, ic in enumerate(good_chans):
    if nLowSumDisplays[i]:
        dispCanv.Print(pdir+'/display_lowQ/'+str(ic)+'.pdf]')

dispCanv.Clear()
dispCanv.Divide(4,int((len(good_chans)+3)/4))
for hname in ['sumQ','sumQ15','sumQlo','sumQhi']:
    for cfg in ['nocut','nocut_zeroSupp','noSpike','ring','final']:
        for i, ic in enumerate(good_chans):
            dispCanv.cd(i+1)
            r.gPad.SetLogy()
            hh[cfg+'_'+hname+'_chan'+str(ic)].Draw('hist')
    
        os.system('mkdir -p '+pdir+'/'+cfg)
        dispCanv.Print(pdir+'/'+cfg+'/'+hname+'.pdf')

dispCanv.Clear()
dispCanv.cd(0)
r.gPad.SetLogy()
hh['sumQ_plastic'].Draw('hist')
dispCanv.Print(pdir+'/sumQ_plastic.pdf')
hh['sumQ_lyso'].Draw('hist')
dispCanv.Print(pdir+'/sumQ_lyso.pdf')

r.gPad.SetLogy(0)
hh['sumQ_corr01'].Draw('colz')
dispCanv.Print(pdir+'/corr_lyso.pdf(')
hh['sumQ_corr13'].Draw('colz')
dispCanv.Print(pdir+'/corr_lyso.pdf')
hh['sumQ_corr39'].Draw('colz')
dispCanv.Print(pdir+'/corr_lyso.pdf')
hh['sumQ_corr03'].Draw('colz')
dispCanv.Print(pdir+'/corr_lyso.pdf')
hh['sumQ_corr19'].Draw('colz')
dispCanv.Print(pdir+'/corr_lyso.pdf')
hh['sumQ_corr92'].Draw('colz')
dispCanv.Print(pdir+'/corr_lyso.pdf)')

r.gStyle.SetPaintTextFormat("8.0f");
dispCanv.Clear()
hh['nHit'].Draw("hist")
dispCanv.SetLogy(1)
dispCanv.Print(pdir+'/hit.pdf(')
hh['nHit_lyso'].Draw("hist")
dispCanv.Print(pdir+'/hit.pdf')
dispCanv.SetLogy(0)
hh['hit'].Draw("")
dispCanv.Print(pdir+'/hit.pdf')
hh['hitCorr'].Draw("colz text")
dispCanv.Print(pdir+'/hit.pdf)')

fout=r.TFile(pdir+'/histograms.root','recreate')
for n in hh:
    hh[n].Write()
fout.Close()

