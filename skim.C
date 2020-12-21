void progress(float f){
    // https://stackoverflow.com/questions/14539867/how-to-display-a-progress-indicator-in-pure-c-c-cout-printf
    int barWidth = 70;
    std::cout << "[";
    int pos = barWidth * f;
    for (int i = 0; i < barWidth; ++i) {
        if (i < pos) std::cout << "=";
        else if (i == pos) std::cout << ">";
        else std::cout << " ";
    }
    std::cout << "] " << int(f * 100.0) << " %\r";
    std::cout.flush();    
}

void skim(TString fname, TString cuts) {

    //Get old file, old tree and set top branch address
    TFile *oldfile = new TFile(fname,"read");
    TTree *oldtree = (TTree*)oldfile->Get("Events");
    Long64_t nentries = oldtree->GetEntries();

    oldtree->Draw(">>elist",cuts,"goff");
    TEventList *elist = (TEventList*)gDirectory->Get("elist");

    //Create a new file + a clone of old tree in new file
    TFile *newfile = new TFile("skim."+fname,"recreate");
    TTree *newtree = oldtree->CloneTree(0);

    for (Long64_t i=0;i<elist->GetN(); i++) {
        oldtree->GetEntry( elist->GetEntry(i) );
        newtree->Fill();
        if (i%100==0) progress(float(i)/elist->GetN());
    }
    cout << endl;
    newtree->AutoSave();
    delete oldfile;
    delete newfile;
    exit(0);
}
