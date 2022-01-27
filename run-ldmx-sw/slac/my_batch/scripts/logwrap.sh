
# create a temporary working area
tmpdir=/tmp/therwig/lsf${LSB_JOBID}/job${LSB_JOBINDEX}
mkdir -p $tmpdir
cd $tmpdir

# copy the relevant scripts
subDir=$1
cp ${subDir}"/setup_ldmx.sh" .
cp ${subDir}"/test_run.sh" .
cp ${subDir}"/cfg.py" .

#run job and copy back an expected output: "out.root"
SECONDS=0
bash test_run.sh $tmpdir 2>err.log 1>out.log
echo "TIME ELAPSED: ${SECONDS} seconds" >> out.log
echo "Or $(($duration / 60)) minutes and $(($duration % 60)) seconds." >> out.log

#copy back to final dir
outDir=$1
mkdir -p $outDir/logs
mkdir -p $outDir/pams

cp out.log  $outDir/logs/out.$LSB_JOBINDEX.log
cp err.log  $outDir/logs/err.$LSB_JOBINDEX.log
cp out.root $outDir/out.$LSB_JOBINDEX.root
cp parameterDump.json $outDir/pams/parameterDump.$LSB_JOBINDEX.json

# cleanup tmp dir
rm -r $tmpdir/*
