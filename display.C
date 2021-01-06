float calcPx(float x_targ, float x_ecal, float e, float offset=0){
    float dx_exp = -2.0*(4000./e-1)-2.3; //mm
    float dx=x_ecal-x_targ;
    return 17.8*(e/4000.)*(dx-dx_exp)+offset;
    //return 17.8*(e/4000.)*(dx-dx_exp) + (-61.2+6*(1-e/4000.));
}
float calcPy(float y_targ, float y_ecal, float e, float offset=0){ return 17.8*(e/4000.)*(y_ecal-y_targ)+offset; }
float calcPt(float x_targ, float x_ecal, float y_targ, float y_ecal, float e, float offx=0, float offy=0){
    return sqrt(pow(calcPx(x_targ, x_ecal, e, offx),2)+pow(calcPy(y_targ, y_ecal, e, offy),2));
}
void RunDisplay(int entry, int mode=0){
    TFile* f = new TFile("combo.root","read");
    auto t = (TTree*) f->Get("Events");
    TCanvas c("c","",600,400);
    gStyle->SetPalette(kInvertedDarkBodyRadiator);
    gStyle->SetOptStat(0);

    if(mode==3){
        t->Draw("ECalRecHit_x:ECalRecHit_y:ECalRecHit_z>>h3",Form("Entry$==%d",entry),"box");
        auto h = (TH3*) gDirectory->Get("h3");
        //h->SetTitle(";x [mm];y [mm];z [mm]"); // ordering is wrong!
        h->SetTitle("");
        c.SaveAs("plots/display3d.pdf");
        return;
    }
    
    gPad->SetTopMargin(0.15);
    gPad->SetRightMargin(0.15);
    

    // rechits
    TH2* h;
    // TH2F* h = new TH2F("h",";x [mm];y [mm];E [MeV]",200,-250,250,200,-250,250);
    if(mode==2) h = new TH2F("h",";x [mm];y [mm];RecHit E [MeV]",200,-250,250,200,-250,250);
    if(mode==0 || mode==2) t->Draw("ECalRecHit_y:ECalRecHit_x>>h",Form("Entry$==%d",entry),"colz");
    if(mode==1) t->Draw("ECalTrigDigi_y:ECalTrigDigi_x>>h",Form("Entry$==%d",entry),"colz");
    if(mode!=2){
        h = (TH2*) gDirectory->Get("h");
        h->SetTitle(";x [mm];y [mm];RecHit E [MeV]");
    }
    if(mode==1) h->SetTitle(";x [mm];y [mm];TP E [MeV]");
        
    // Clusters
    vector<float> *clus_x=0;
    vector<float> *clus_y=0;
    vector<float> *clus_e=0;
    vector<float> *clus_xe=0;
    vector<float> *clus_ye=0;
    t->SetBranchAddress("ECalTrigClus_3d_e",&clus_e);
    t->SetBranchAddress("ECalTrigClus_3d_x",&clus_x);
    t->SetBranchAddress("ECalTrigClus_3d_y",&clus_y);
    t->SetBranchAddress("ECalTrigClus_3d_xe",&clus_xe);
    t->SetBranchAddress("ECalTrigClus_3d_ye",&clus_ye);

    // Truth SPHits
    vector<float> *targ_x=0;
    vector<float> *targ_y=0;
    vector<float> *targ_z=0;
    vector<float> *targ_e=0;
    vector<int> *targ_pdgId=0;
    vector<int> *targ_trackID=0;
    t->SetBranchAddress("TargetSPHit_x",&targ_x);
    t->SetBranchAddress("TargetSPHit_y",&targ_y);
    t->SetBranchAddress("TargetSPHit_z",&targ_z);
    t->SetBranchAddress("TargetSPHit_e",&targ_e);
    t->SetBranchAddress("TargetSPHit_pdgID",&targ_pdgId);
    t->SetBranchAddress("TargetSPHit_trackID",&targ_trackID);

    vector<float> *ecal_x=0;
    vector<float> *ecal_y=0;
    vector<float> *ecal_z=0;
    vector<float> *ecal_e=0;
    vector<int> *ecal_pdgId=0;
    vector<int> *ecal_trackID=0;
    t->SetBranchAddress("ECalSPHit_x",&ecal_x);
    t->SetBranchAddress("ECalSPHit_y",&ecal_y);
    t->SetBranchAddress("ECalSPHit_z",&ecal_z);
    t->SetBranchAddress("ECalSPHit_e",&ecal_e);
    t->SetBranchAddress("ECalSPHit_pdgID",&ecal_pdgId);
    t->SetBranchAddress("ECalSPHit_trackID",&ecal_trackID);
        
    t->GetEntry(entry);

    TMarker* m_targ = new TMarker();
    m_targ->SetMarkerStyle(41);
    m_targ->SetMarkerColor(kRed);
    m_targ->SetMarkerSize(1);
    int itarg=-1;
    for(int i=0;i<targ_x->size();i++){
        if(targ_pdgId->at(i)!=11) continue;
        if(targ_trackID->at(i)!=1) continue;
        if(targ_z->at(i)<0 || targ_z->at(i)>1.) continue;
        itarg=i;
        // pointer so its not deleted
        // m_targ->SetX(targ_x->at(i));
        // m_targ->SetY(targ_y->at(i));
        // m_targ->Draw(); // draw
        m_targ->DrawMarker(targ_x->at(i), targ_y->at(i));
    }

    const int kECalPrimary=20;
    const int kECalSecondary=24;
    const int kECalPhoton=30;
    const int kECalOther=27;
    TMarker* m_ecal = new TMarker();
    m_ecal->SetMarkerColor(kBlue);
    m_ecal->SetMarkerStyle(kECalPrimary);// closed circle
    int iecal=-1;
    for(int i=0;i<ecal_x->size();i++){
        //if(dbg) cout << "ECA  e=" << ecal_x->at(i) << " (" << ecal_x->at(i) << ", " << ecal_y->at(i) << ")" << endl;
        if(ecal_e->at(i)<100) continue;
        if(ecal_z->at(i)<240) continue;
        if(ecal_z->at(i)>241) continue;
        if(ecal_trackID->at(i)==1 && ecal_pdgId->at(i)==11){ // primary recoil e
            m_ecal->SetMarkerStyle(kECalPrimary);// closed circle
            iecal=i;
            cout << "ECAL: primary, e=" << ecal_e->at(i) << " (" << ecal_x->at(i) << ", " << ecal_y->at(i) << ", " << ecal_z->at(i) << ")" << endl;
        } else if(abs(ecal_pdgId->at(i))==11){ // other e
            m_ecal->SetMarkerStyle(kECalSecondary); // open circle
            cout << "ECAL: other ele, e = " << ecal_e->at(i) << ", (x,y)=(" << ecal_x->at(i) << ", " << ecal_y->at(i) << ", " << ecal_z->at(i) << ")" << endl;
        } else if(ecal_pdgId->at(i)==22){ // gamma
            m_ecal->SetMarkerStyle(kECalPhoton);
            cout << "ECAL: photon, e = " << ecal_e->at(i) << ", (x,y)=(" << ecal_x->at(i) << ", " << ecal_y->at(i) << ", " << ecal_z->at(i) << ")" << endl;
        } else { // other
            m_ecal->SetMarkerStyle(kECalOther);
            cout << "ECAL: other PDG ID = "<< ecal_pdgId->at(i) << ", e = " << ecal_e->at(i) << ", (x,y)=(" << ecal_x->at(i) << ", " << ecal_y->at(i) << ", " << ecal_z->at(i) << ")" << endl;
        }
        m_ecal->DrawMarker(ecal_x->at(i), ecal_y->at(i));
    }
    
    TLine* m_clus = new TLine();
    m_clus->SetLineWidth(2);
    m_clus->SetLineColor(kGreen+2);
    
    for(int i=0;i<clus_x->size();i++){
        TLine* h = new TLine(clus_x->at(i)-clus_xe->at(i),clus_y->at(i),clus_x->at(i)+clus_xe->at(i),clus_y->at(i));
        TLine* v = new TLine(clus_x->at(i),clus_y->at(i)-clus_ye->at(i),clus_x->at(i),clus_y->at(i)+clus_ye->at(i));
        cout << Form("Cluster E=%.1f with (x, y) = (%.1f+/-%.1f, %.1f+/-%.1f)",clus_e->at(i),clus_x->at(i),clus_xe->at(i),clus_y->at(i),clus_ye->at(i)) << endl;
        //TEllipse* m = new TEllipse(clus_x->at(i), clus_y->at(i), clus_xe->at(i), clus_ye->at(i));
        //m->SetFillStyle(4000); // transparent
        // h->SetLineWidth(2);
        // v->SetLineWidth(2);
        // h->SetLineColor(kGreen+2);
        // v->SetLineColor(kGreen+2);
        // h->Draw();
        // v->Draw();
        m_clus->DrawLine(clus_x->at(i)-clus_xe->at(i),clus_y->at(i),clus_x->at(i)+clus_xe->at(i),clus_y->at(i));
        m_clus->DrawLine(clus_x->at(i),clus_y->at(i)-clus_ye->at(i),clus_x->at(i),clus_y->at(i)+clus_ye->at(i));
    }

    // Legend
    //auto hPad = gPad;
    c.cd();
    TLegend leg(.05,0.90,0.95,0.995);
    leg.SetTextFont(42);
    leg.SetHeader("");
    leg.SetNColumns(3);

    leg.AddEntry( m_targ ,"Target e","p");
    leg.AddEntry( m_clus ,"Cluster","le");

    m_ecal->SetMarkerStyle(kECalPrimary);
    leg.AddEntry( m_ecal ,"ECal primary e","p");

    auto m_ecal2 = (TMarker*) m_ecal->Clone();
    m_ecal2->SetMarkerStyle(kECalSecondary);
    leg.AddEntry( m_ecal2 ,"ECal other e","p");

    auto m_ecal3 = (TMarker*) m_ecal->Clone();
    m_ecal3->SetMarkerStyle(kECalPhoton);
    leg.AddEntry( m_ecal3 ,"ECal photon","p");

    auto m_ecal4 = (TMarker*) m_ecal->Clone();
    m_ecal4->SetMarkerStyle(kECalOther);
    leg.AddEntry( m_ecal4 ,"Other ECal","p");
    
    // TMarker* m_clus2 = new TMarker(0,0,2);
    // m_clus2->SetMarkerColor(kGreen-2);
    // const int kECalPrimary=20;
    // const int kECalSecondary=24;
    // const int kECalPhoton=30;
    // const int kECalOther=27;
    
    leg.SetFillStyle(0);
    leg.SetFillColor(0);
    leg.SetBorderSize(0);
    leg.Draw();

    //hPad->cd();
    TText tt;
    tt.SetTextAlign(12); // h:left v:center
    tt.SetNDC();
    tt.SetTextFont(42);
    tt.SetTextSize(0.04);

    float xtx=0.14;
    float ytx=0.82;
    //float calcPy(float y_targ, float y_ecal, float e, float offset=0){ return 17.8*(e/4000.)*(y_ecal-y_targ)+offset; }
    if(itarg>=0){
        tt.DrawText(xtx,ytx,Form("Target ele (x, y)=(%.1f, %.1f), e=%.1f",targ_x->at(itarg),targ_y->at(itarg),targ_e->at(itarg)));
        ytx -= 0.04;
    }
    if(iecal>=0 && itarg>=0){
        tt.DrawText(xtx,ytx,Form("ECal ele (x, y)=(%.1f, %.1f), e=%.1f, (px, py)=(%.1f, %.1f)",ecal_x->at(iecal),ecal_y->at(iecal),ecal_e->at(iecal),
                                 calcPx(targ_x->at(itarg), ecal_x->at(iecal), ecal_e->at(iecal)),
                                 calcPy(targ_y->at(itarg), ecal_y->at(iecal), ecal_e->at(iecal))));
        ytx -= 0.04;
    }
    for(int i=0;i<clus_x->size();i++){
        if (itarg<0) continue;
        //tt.DrawText(xtx,ytx,Form("Cluster (x, y, e)=(%.1f, %.1f, %.1f)",clus_x->at(i),clus_y->at(i),clus_e->at(i)));
        tt.DrawText(xtx,ytx,Form("Cluster ele (x, y)=(%.1f, %.1f), e=%.1f, (px, py)=(%.1f, %.1f)",clus_x->at(i),clus_y->at(i),clus_e->at(i),
                                 calcPx(targ_x->at(itarg), clus_x->at(i), clus_e->at(i)),
                                 calcPy(targ_y->at(itarg), clus_y->at(i), clus_e->at(i))));
        ytx -= 0.04;
    }
    
    // Entry$==0     
    // world boundaries
    // rechits
    //t->Draw("ECalRecHit_y:ECalRecHit_x>>hrec","Entry$==0","colz");
    // clusters
    // truth hits

    if(mode==0) c.SaveAs("plots/display2d_RecHit.pdf");
    else if (mode==1) c.SaveAs("plots/display2d_TP.pdf");
    else if (mode==2) c.SaveAs("plots/display2d_RecHitWide.pdf");
    else return;    
    

}

void display(int entry=0){
    RunDisplay(entry,0/* RecHit */);
    RunDisplay(entry,1/* TP Clusters */);
    RunDisplay(entry,2/* 3d */);
    RunDisplay(entry,3/* 3d */);
    exit(0);
}
