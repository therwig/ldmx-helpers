#include <iostream>
#include <vector>
#include "TFile.h"
#include "TTree.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TH3D.h"
#include "TCanvas.h"

void hcal_layer() {
    // Open the ROOT file
    TFile* file = TFile::Open("events_10k.root", "READ");
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
    TTreeReaderArray<float> energy(reader, "HcalRecHits_test.energy_");
    TTreeReaderArray<int>pdg(reader, "EcalScoringPlaneHits_test.pdgID_");
    TTreeReaderArray<float>y_pos(reader, "HcalRecHits_test.ypos_");
    TTreeReaderArray<float>z_pos(reader, "HcalRecHits_test.zpos_");
    TTreeReaderArray<float>x_pos(reader, "HcalRecHits_test.xpos_");
    TTreeReaderArray<float>z_ecal(reader, "EcalScoringPlaneHits_test.z_");
    TTreeReaderArray<int>ecal_track(reader, "EcalScoringPlaneHits_test.trackID_");
    TTreeReaderArray<int>hcal_track(reader, "HcalScoringPlaneHits_test.trackID_");
    TTreeReaderArray<int>hcal_sec(reader, "HcalRecHits_test.section_"); 
    TTreeReaderArray<int>hcal_strip(reader, "HcalRecHits_test.strip_"); 
    TTreeReaderArray<int>hcal_layer(reader, "HcalRecHits_test.layer_");
    TTreeReaderArray<float>e_ecal(reader, "EcalScoringPlaneHits_test.energy_"); 

    TH3D* hist = new TH3D("hist", "Hcal Rec Hits", 100, -17000, 7000,100, -7000, 7000, 100, -10000, 14000);
    TH1D* hist2 = new TH1D("hist2", "Hits in Hcal", 100, 0, 6);
    TH2D* hist3 = new TH2D("hist3", "Strips and Layers", 5, 1, 6, 48, 1, 49);
    while (reader.Next()) {
        // Check that pdg and x_pos arrays have entries before processing
        size_t pdgSize = pdg.GetSize();
        size_t xPosSize = x_pos.GetSize();
        size_t zEcalSize = z_ecal.GetSize();
        size_t energySize = energy.GetSize();
	int hits = 0;
	int group = 0;
	int layer = 0;
    
        // Loop through each entry within the arrays for this event
        for (size_t i = 0; i < pdgSize; i++) {
            if (pdg[i] == 13 && z_ecal[i] > 800 && e_ecal[i]/1000 <1) {
	       for (size_t j =0; j < xPosSize; j++) {
		   if (hcal_sec[j] ==0) {
		      hits++;
                      // Print each corresponding x_pos, energy, pdg, and z_ecal value
                      std::cout << "Position: " << x_pos[j] 
                                << " Energy: " << energy[j] 
                                << " PDG code: " << pdg[i] 
                                << " z_ecal: " << z_ecal[i] 
                                << std::endl;
		      //hist2->Fill(energy[j]);
		      group = (hcal_strip[j]/8) % 5 + 1;
		      layer = (hcal_layer[j]/2) % 48 + 1;
		      std::cout << "Strip: ," << hcal_strip[j] << " Group: " << group << std::endl;
		      hist3->Fill(group, layer);
		   }
	       }
            }
        }
	hist3->GetXaxis()->SetTitle("Strip");
	hist3->SetStats(kFALSE);
	hist3->Draw("colz");

    }

}


