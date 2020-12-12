
n=11
# python submitter.py \
#     -f fragments/cfg_4GeV_singleE.py \
#     -o /gpfs/slac/atlas/fs1/u/therwig/ldmx/sandbox/ldmx-helpers/batch/myOutDir$n \
#     -n myJobName$n \
#     --test

python submitter.py \
    -f fragments/cfg_ntuplizer.py \
    -i /gpfs/slac/atlas/fs1/u/therwig/ldmx/sandbox/ldmx-helpers/batch/myOutDir5/out.*root \
    -o /gpfs/slac/atlas/fs1/u/therwig/ldmx/sandbox/ldmx-helpers/batch/myNtupOutDir$n \
    -n myNtupJobName$n \
    --nEventsPerJob 100 \
    --nJobs=1 #--noSubmit
