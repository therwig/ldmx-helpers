#include <iostream>
#include <vector>
#include "TFile.h"
#include "TTree.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TH3D.h"
#include "TCanvas.h"

class TP {
public:
  int strip=-1;
  int layer=-1;
  float pe=0;
  TP() {}
  TP (int s, int l, float e) : strip(s), layer(l), pe(e) {}
};
int get_idx(int s, int l){
  return s*100+l;
}

void runIt(TString fname="v3.3.6-1e_100PE_241008.root", TString procName="sim", TString oname="hist.root") {
    // Open the ROOT file
    TFile* file = TFile::Open(fname, "READ");
    if (!file || file->IsZombie()) {
        std::cerr << "Error opening file!" << std::endl;
        return;
    }

    // Get the TTree
    TTree* tree = (TTree*)file->Get("LDMX_Events");
    if (!tree) {
        std::cerr << "Error: Tree not found!" << std::endl;
        return;
    }

    // Set up the TTreeReader
    TTreeReader reader(tree);
    TTreeReaderArray<float>truth_e(reader, "TargetScoringPlaneHits_"+procName+".energy_"); 
    TTreeReaderArray<int>hcal_sec(reader, "HcalRecHits_"+procName+".section_"); 
    TTreeReaderArray<int>hcal_strip(reader, "HcalRecHits_"+procName+".strip_"); 
    TTreeReaderArray<int>hcal_layer(reader, "HcalRecHits_"+procName+".layer_");
    TTreeReaderArray<float>hcal_pe(reader, "HcalRecHits_"+procName+".pe_"); 

    TFile* fo = new TFile(oname,"recreate");
    TH1F* deepestTP = new TH1F("deepestTP",";layer of the deepest Hcal tp",51,-0.5,50.5);
    TH1F* deepestNonIsoTP = new TH1F("deepestNonIsoTP",";layer of the deepest non-isolated Hcal tp",51,-0.5,50.5);
    TH2F* deepestTP_vs_energy = new TH2F("deepestTP_vs_energy",";layer of the deepest Hcal tp;truth energy",51,-0.5,50.5,16,0,8e3);
    
    long iEvt=0;
    while (reader.Next()) {
      //if(iEvt>100) break;
      iEvt++;
      if(iEvt%1000==0) cout << "processing events " << iEvt << endl;

      // build a list of TPs
      map<int,TP> tp_list;
      for (size_t i = 0; i < hcal_layer.GetSize(); i++) {
	if (hcal_sec[i]!=0) continue; // only consider back HCal hits
	if (hcal_pe[i]<50) continue; // only consider hits consistent with MIP energies
	int tp_layer = (hcal_layer[i]/2)+1; // count from layer 1
	int tp_strip = (hcal_strip[i]/8);
	int tp_idx = get_idx(tp_strip, tp_layer);
	if (tp_list.count(tp_idx)) tp_list[tp_idx].pe += hcal_pe[i];
	else {
	  TP tp(tp_strip, tp_layer, hcal_pe[i]);
	  tp_list[tp_idx] = tp;
	}
      }
      int lastLayer = 0;
      int lastNonIsoLayer = 0;
      for(auto tp_pair : tp_list){
	auto tp = tp_pair.second;
	bool isIsolated = true;
	//look for a nearby TP
	for(int s=tp.strip-1; s<=tp.strip+1; s++){
	  if (s<0 || s>4) continue;
	  for(int l=tp.layer-1; l<=tp.layer+1; l++){
	    if (l<0 || l>48) continue;
	    if (tp_list.count(get_idx(s,l))) isIsolated = false;
	    if (!isIsolated) break;
	  }
	  if (!isIsolated) break;
	}
	if (tp.layer > lastLayer) lastLayer = tp.layer;
	if (!isIsolated && tp.layer > lastNonIsoLayer) lastNonIsoLayer = tp.layer;
      }
      deepestTP->Fill(lastLayer);
      deepestNonIsoTP->Fill(lastNonIsoLayer);
      if (truth_e.GetSize()){
	deepestTP_vs_energy->Fill(lastLayer, truth_e[0]);
      }
    }
    fo->Write();
    fo->Close();
    file->Close();
}

void hcal_layer(bool doBkg=false){
  if(doBkg){
    // run with the background file arguments
    runIt("v3.3.6-1e_100PE_241008.root", "sim", "hist_bkg.root");
  } else {
    // run with the signal file arguments
    runIt("muGun_1energy8.root", "test", "hist_sig.root");
  }
}



