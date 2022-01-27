float calcPx(float x_targ, float x_ecal, float e, float offset=0){
    float dx_exp = -2.0*(4000./e-1)-2.3; //mm 
    float dx=x_ecal-x_targ;
    return 17.8*(e/4000.)*(dx-dx_exp)+offset;
}
float calcPy(float y_targ, float y_ecal, float e, float offset=0){ return 17.8*(e/4000.)*(y_ecal-y_targ)+offset; }
float calcPt(float x_targ, float x_ecal, float y_targ, float y_ecal, float e, float offx=0, float offy=0){
    return sqrt(pow(calcPx(x_targ, x_ecal, e, offx),2)+calcPy(y_targ, y_ecal, e, offy));
}
const float CorrE(float e) {return e>4e3?4e3:e;}
const float PXOFF() {return 25;}
const float PYOFF() {return 0;}
const float TAIL() {return 200;}

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
    cout << "Skimming "+fname << endl;
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
