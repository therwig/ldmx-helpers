
### Example generation for eN events

Generate events from scratch (1000 x 2 hour jobs)
```
python submitter.py \
    -f fragments/cfg_4GeV_eN.py \
    -o /nfs/slac/g/ldmx/data/mc/v12/4_gev_incl_tp/ \
    -n 201212_njob_1000_nEvt_200_v1 \
    --nJobs 1000 --nEventsPerJob 10000000 
```

Run ntuplizer with eN inputs
```
python submitter.py \
    -f fragments/cfg_ntuplizer.py \
    -i /nfs/slac/g/ldmx/data/mc/v12/4_gev_incl_tp/201212_njob_1000_nEvt_200_v1/*root \
    -o /nfs/slac/g/ldmx/data/mc/v12/4_gev_incl_tp \
    -n 201212_njob_1000_nEvt_200_v1_NTUPv1 \
    --nFilesPerJob 10
```
