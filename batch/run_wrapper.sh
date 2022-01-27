echo pwd; pwd
echo ls -lh; ls -lh
export BATCH_NEVENTS=-1
export BATCH_NJOBS=80
export BATCH_SEEDOFFSET=0
fire cfg.py
echo ls -lh; ls -lh
