
proc="ele_0p1_4GeV"
proc="piM_0p1_4GeV"
proc="pro_0p1_4GeV"
proc="neu_0p1_4GeV"
proc="pho_0p1_4GeV"

#for proc in "ele_0p1_4GeV" "piM_0p1_4GeV" "pro_0p1_4GeV" "neu_0p1_4GeV" "pho_0p1_4GeV"
for proc in "ele_0p1_4GeV"
do

d="pfSamples"
nEvents=10000
#sfx=".10k"
sfx=".10k.2part"
#sfx=".10k.HCal"
sfx=".10k.HCal.2part"
# sfx=".tmp"
# genRunner="  "
# pfRunner=""
# runner=genRunner

#time ldmx fire cfg/cfg_pfReco.py --step gen --output $d/gen/gen.$proc$sfx.root --proc $proc --gps -n $nEvents --zstart 830
time ldmx fire cfg/cfg_pfReco.py --step pf --input $d/gen/gen.$proc$sfx.root --output $d/pf/pf.$proc$sfx.root #-n 1000

done
