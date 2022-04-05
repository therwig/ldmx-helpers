import ROOT as r
r.gROOT.SetBatch(True)
from sys import argv
from math import floor
from itertools import chain
from struct import unpack
from QIE import targetScint
from array import array

chan_map=[0,
          2,  #1
          10, #2
          4,  #3
          3,  #4
          1,  #5
          5,  #6
          11, #7
          12, #8
          6,  #9
          13, #10
          8,  #11
          7,  #12
          14, #13
          9,  #14
          15] #15

class qie_frame:

    def __init__(self,label):
        self.label=label
        self.adcs=[]
        self.tdcs=[]
        self.capid=0
        self.ce=0
        self.bc0=0

    def decode(self,frame):
        if len(frame) != 22 :
            #print("[[qie_frame]]  ERROR: was expecting 22 characters")
            return
        else :
            self.capid = (int(frame[:2],16)>>2)&3
            self.ce = (int(frame[:2],16)>>1)&1
            self.bc0 = (int(frame[:2],16))&1
            #print('line',frame)
            for i in range(8):
                #print('i',i)
                #print('hex',frame[(i+1)*2:(i+2)*2])
                #print('dec',int(frame[(i+1)*2:(i+2)*2],16))
                temp_adc=int(frame[(i+1)*2:(i+2)*2],16)
                self.adcs.append(temp_adc)
            tdc_bytes_03=int(frame[-4:-2],16)
            tdc_bytes_48=int(frame[-2:],16)
            for i in range(3,-1,-1):
                temp_tdc=(tdc_bytes_03>>(i*2))&3
                self.tdcs.append(temp_tdc)
            for i in range(3,-1,-1):
                temp_tdc=(tdc_bytes_48>>(i*2))&3
                self.tdcs.append(temp_tdc)

    def print(self):
        print('-----QIE FRAME-------')
        print(self.label)
        print('CADID: {0} CE: {1} BC0: {2}'.format(self.capid,self.ce,self.bc0))
        print('adcs: ',' '.join(map(str,self.adcs)))
        print('tdcs: ',' '.join(map(str,self.tdcs)))

    def trigger(self):
        nzero=0
        for adc,tdc in zip(self.adcs,self.tdcs):
            if (adc > 50 and adc < 255) :
                print('[[qie_frame]] Trigger')
                self.print()
                return
            if adc==0 :
                nzero=nzero+1
        if nzero>3 :
            print('[[qie_frame]] Trigger')
            self.print()
            return

hist_hit_mult = r.TH1F("hit_mult","hit multiplicity;channel;multiplicity",13,-0.5,12.5)
        
hist_pulse=[]
for i in range(16):
    hist_pulse.append(r.TH2F("pulse_ch{0}".format(i),"pulse_ch{0};time sample;ADC".format(i),64,-0.5,63.5,256,-0.5,255.5))

hist_pulseQ=[]
for i in range(16):
    hist_pulseQ.append(r.TH2F("pulseQ_ch{0}".format(i),"pulseQ_ch{0};time sample;ADC".format(i),64,-0.5,63.5,3000,0.5,100000))

hist_adc_tdc=[]
for i in range(16):
    hist_adc_tdc.append(r.TH2F("adc_tdc{0}".format(i),"adc_tdc{0};TDC;ADC".format(i),4,-0.5,3.5,256,-0.5,255.5))

hist_adc=[]
for i in range(16):
    hist_adc.append(r.TH1F("adc{0}".format(i),"adc{0};ADC;Arbitrary".format(i),256,-0.5,255.5))
    
hist_tdc=[]
for i in range(16):
    hist_tdc.append(r.TH1F("tdc{0}".format(i),"tdc{0};ADC;Arbitrary".format(i),3,-0.5,3.5))

hist_tdc=[]
for i in range(16):
    hist_tdc.append(r.TH1F("tdc{0}".format(i),"tdc{0};TDC;Arbitrary".format(i),3,-0.5,3.5))

hist_sumQ=[]
for i in range(16):
    hist_sumQ.append(r.TH1F("sumQ{0}".format(i),"sumQ{0};Q [fC];Events".format(i),100,0,100000))

hist_sumQallTop = r.TH1F("hist_sumQallTop","SumQ all top;Q [fC];Events",100,0,100000)
hist_sumQallBot = r.TH1F("hist_sumQallBot","SumQ all bot;Q [fC];Events",100,0,100000)

hist_sumQ_noise=[]
for i in range(16):
    hist_sumQ_noise.append(r.TH1F("sumQ_noise{0}".format(i),"sumQ_noise{0};Q [fC];Events".format(i),400,-800,2000))

#hist_max_adc = r.TH1F("max_adc","max(max(ADC));max(ADC);Events",40,0,1)

def clean_kchar(data):
    return data.replace('F7FB','')

def clean_BC7C(data):
    return data.replace('BC7C','')

def remove_partial_events(data):
    return  data[data.find('BC'):data.rfind('BC')]

def read_string_from_file(filename):
    data=""
    with open(filename) as f:
        data+= ''.join(f.readlines())
    return data.split('192.168.1.30')

def load_data(file):
  data = open(file, "r") #loads file
  data=data.read()       #reads file
  data=data.split("\n") #turn one giant string into a list of line strings. The last line is "" and drops it.
  return data

def sort_into_events(data):
  processed_data=[]
  processed_event=[]
  for line in data:
    try:
      if line[0] == 'r':
        processed_data.append(processed_event)
        # print("appended", 1)
        processed_event=[]
      if line[0] != 's' and line[:4] != 'recv' and line[0] != '\r':
        processed_event.append(line) 
    except: pass #blank lines in data that would otherwise crash program
  return processed_data

######### = = = = = = = = = = = = = = = = = 

fTree = r.TFile(argv[1]+'_tree.root','recreate')
evtTree = r.TTree("Events","Events")
chanArr=[]
for i in range(16):
    chanArr.append(array('d',[0]*30))
    b=evtTree.Branch('chan'+str(i),chanArr[-1],'chan'+str(i)+'[30]/D')
    

######### = = = = = = = = = = = = = = = = = 

qie = targetScint()

data = load_data('../data/'+argv[1]+'.txt')
data = sort_into_events(data)
data = list(chain.from_iterable(data))
events=[]
timestamps=[]
start_index=0
#print("Data len", len(data))
for i in range(len(data)):
    if i+1 >= len(data):
        break
    if data[i]== 'FFFFFFFFFFFFFFFF' : #and data[i+1] == 'FFFFFFFFFFFFFFFF':
        if i != 0 :
            events.append(data[start_index:i-1])
            temp = bytes.fromhex(data[i+1][8:])
            decoded = unpack('<I', temp)[0]
            #print(decoded)
            timestamps.append(decoded)
            #timestamps.append(int(data[i+1],16)&(0xFFFFFFFF))
        start_index=i+2
#print(timestamps)
ievent=-1
for event in events:
    ievent = ievent+1
    #if ievent>1000: break
    if ievent%1000 == 0 : 
        print('=========== NEW EVENT {0} ========'.format(ievent))
    fiber2=""
    fiber1=""
    event = event[1:]
    for word in event:
        fiber1+=word[:8]
        fiber2+=word[8:]

    fiber1 = clean_kchar(fiber1)
    fiber1 = clean_BC7C(fiber1)
    #fiber1 = remove_partial_events(fiber1)
    fiber2 = clean_kchar(fiber2)
    fiber2 = clean_BC7C(fiber2)
    #fiber2 = remove_partial_events(fiber2)
        
    fiber1 = fiber1.split('BC')
    fiber2 = fiber2.split('BC')
    #print(fiber1)
    #continue
    sum_from=0
    sum_to=29
    sums=[0]*16
    sums_n=[0]*16
    sum_top=0
    sum_bot=0
    #max_max_adc=0
    for i,z in enumerate(zip(fiber1,fiber2)):
        #print('---------- NEW TIME SAMPLE ({0}) ----------'.format(i))
        #print(z)
        f1 = qie_frame('fiber 1')
        f1.decode(z[0])
        #max_adc = max(f1.adc)
        if i<30:
            for j in range(16): chanArr[j][i]=0 # reset            
        for j,codes in enumerate(zip(f1.adcs,f1.tdcs)):
            #hist_pulse[(ievent-1)*16+j].Fill(i,codes[0])
            hist_pulse[j].Fill(i,codes[0])
            hist_pulseQ[j].Fill(i,qie.ADCtoQ(codes[0]))
            if i<30: chanArr[j][i]=qie.ADCtoQ(codes[0])
            hist_adc[j].Fill(codes[0])
            hist_tdc[j].Fill(codes[1])
            hist_adc_tdc[j].Fill(codes[1],codes[0])
            if i >= sum_from and i <= sum_to :
                sums[j]+=qie.ADCtoQ(f1.adcs[j])
            elif i>= 0 and i <= 14 :
                sums_n[j]+=qie.ADCtoQ(f1.adcs[j])
        #f1.trigger()
        #f1.print()
        f2 = qie_frame('fiber 2')
        f2.decode(z[1])
        #max_adc = max(f2.adc)        
        for j,codes in enumerate(zip(f2.adcs,f2.tdcs)):
            #hist_pulse[(ievent-1)*16+j+8].Fill(i,codes[0])
            hist_pulse[j+8].Fill(i,codes[0])
            hist_pulseQ[j+8].Fill(i,qie.ADCtoQ(codes[0]))
            if i<30: chanArr[j+8][i]=qie.ADCtoQ(codes[0])
            hist_adc[j+8].Fill(codes[0])
            hist_tdc[j+8].Fill(codes[1])
            hist_adc_tdc[j+8].Fill(codes[1],codes[0])
            if i >= sum_from and i <= sum_to :
                #print('adc',f2.adcs[j])
                #print('q',qie.ADCtoQ(f2.adcs[j]))
                sums[j+8]+=qie.ADCtoQ(f2.adcs[j])
            elif i>= 10	and i <= 17 :
                sums_n[j+8]+=qie.ADCtoQ(f2.adcs[j])
        #max_adc = max_adc/sum
    evtTree.Fill()
    for i_s,s in enumerate(sums):
        if s > 15000 :
            hist_hit_mult.Fill(chan_map[i_s])
        #f2.trigger()
        #f2.print()
    sum_top = sums[0]+sums[1]+sums[3]+sums[9]+sums[11]+sums[2]
    sum_bot = sums[5]+sums[4]+sums[6]+sums[12]+sums[7]
    hist_sumQallTop.Fill(sum_top)
    hist_sumQallBot.Fill(sum_bot)
    for i in range(16):
        hist_sumQ[i].Fill(sums[i])
        hist_sumQ_noise[i].Fill(sums[i])

fOut = r.TFile(argv[1]+'.root','recreate')
def saveCanv(canv, canvName, exts=['png']):
    can.SetName(canvName)
    can.Write()
    for ext in exts:
        can.SaveAs(canvName+'.'+ext)

can = r.TCanvas('can','can',500,500)
for i,h in enumerate(hist_pulse):
    h.Draw("colz")
    saveCanv(can, argv[1]+'pulse_ch{0}'.format(i))
can.SetLogy(True)
for i,h in enumerate(hist_pulseQ):
    h.Draw("colz")
    saveCanv(can, argv[1]+'pulseQ_ch{0}'.format(i))
can.SetLogy(False)
for i,h in enumerate(hist_adc):
    h.Draw()
    can.SetLogy()
    saveCanv(can, argv[1]+'adc{0}'.format(i))
for i,h in enumerate(hist_tdc):
    h.Draw()
    saveCanv(can, argv[1]+'tdc{0}'.format(i))
for i,h in enumerate(hist_sumQ):
    h.Draw()
    saveCanv(can, argv[1]+"sumQ{0}".format(i))

hist_sumQallTop.SetLineColor(4)
hist_sumQallBot.SetLineColor(2)
hist_sumQallTop.Draw()
hist_sumQallBot.Draw("same")
saveCanv(can, argv[1]+"SumQallChan")

hist_sumQ_allbotchan = hist_sumQ[0].Clone("hist_sumQ_allchan");
hist_sumQ_allbotchan.SetTitle("All channels");
hist_sumQ_allbotchan.SetLineColor(2)
hist_sumQ_alltopchan = hist_sumQ[0].Clone("hist_sumQ_allchan");
hist_sumQ_alltopchan.SetTitle("All channels");
hist_sumQ_alltopchan.SetLineColor(4)

hist_sumQ_allbotchan.Add(hist_sumQ[5])
hist_sumQ_allbotchan.Add(hist_sumQ[4])
hist_sumQ_allbotchan.Add(hist_sumQ[6])
hist_sumQ_allbotchan.Add(hist_sumQ[12])
hist_sumQ_allbotchan.Add(hist_sumQ[7])
hist_sumQ_allbotchan.Draw()
#saveCanv(can, argv[1]+'sumQallbotchan')

hist_sumQ_alltopchan.Add(hist_sumQ[0])
hist_sumQ_alltopchan.Add(hist_sumQ[1])
hist_sumQ_alltopchan.Add(hist_sumQ[3])
hist_sumQ_alltopchan.Add(hist_sumQ[9])
hist_sumQ_alltopchan.Add(hist_sumQ[11])
hist_sumQ_alltopchan.Add(hist_sumQ[2])
hist_sumQ_alltopchan.Draw("same")
saveCanv(can, argv[1]+'sumHitsallChan')

for i,h in enumerate(hist_sumQ_noise):
    h.Draw()
    saveCanv(can, argv[1]+"sumQ_noise{0}".format(i))
can.SetLogy(False)
for i,h in enumerate(hist_adc_tdc):
    h.Draw('colz')
    saveCanv(can, argv[1]+"adc_tdc{0}".format(i))

hist_hit_mult.Draw()
saveCanv(can, argv[1]+"_hits")

fOut.Close()
fTree.cd()    
evtTree.Write()
fTree.Close()    
