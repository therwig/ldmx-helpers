#!/bin/env python
import argparse
import shlex, subprocess
import shutil
import os
import glob
from math import ceil

def div_round_up(n,d): return (n+d-1)//d

def setupJob(args):
    '''
    write a submission diretory
    copy the log wrapper and other cfg files there
    amend the cfg with the job configs (files, events, etc...)
    submit the jobs
    '''

    # setup directories (submit + output)
    wd = os.getcwd()
    subDir = wd + "/job_submissions/" + args.name
    outDir = args.output + "/" + args.name
    os.makedirs(subDir,exist_ok=False)
    os.makedirs(outDir,exist_ok=False)
    os.makedirs(outDir+"/logs",exist_ok=False)
    os.makedirs(outDir+"/pams",exist_ok=False)

    # load args (may be modified by inFile loading)
    nEventsPerJob = args.nEventsPerJob
    nFilesPerJob = args.nFilesPerJob
    nJobs = args.nJobs
    testRun = args.test
    seedOffset = args.seedOffset
    filelist = args.input

    # collect input files
    if filelist:
        print('Collected',len(filelist),'inputs (truncating after first ten entries):',filelist[:10])
        if type(filelist) is str and '*' in filelist:
            filelist = glob.glob(filelist)
            print('Expanded WC to',len(filelist),'inputs')
        if testRun:
            nJobs=min(3,len(filelist))
            filelist = filelist[:nJobs]
            nEventsPerJob = 100
            nFilesPerJob = 1
        nFiles=len(filelist)
        if nFilesPerJob: nJobs = ceil(float(nFiles)/nFilesPerJob)
        else: nFilesPerJob = div_round_up(nFiles,nJobs)
        print('Splitting into',nJobs,'jobs')
        os.makedirs(subDir+"/filelists",exist_ok=False)
        with open(subDir+'/filelists/filelist.py','w') as f:
            f.write( 'filelist = '+filelist.__repr__() )
        for ijob in range(nJobs):
            flist = filelist[ijob*nFilesPerJob:(ijob+1)*nFilesPerJob]
            with open(subDir+'/filelists/filelist.{}.txt'.format(ijob+1),'w') as f:
                for fi in flist:
                    f.write(fi+'\n')
    else:
        if testRun:
            nJobs=3
            nEventsPerJob=100
        if(nJobs==0): exit("must provide nJobs or input list!")
        if nEventsPerJob <=0: exit("Must specify nEventsPerJob!")


    # write the run script (e.g. everything that we'd like to log)
    run_wrapper = subDir+"/run_wrapper.sh"
    with open(run_wrapper,'w') as f:
        # run
        f.write("echo pwd; pwd\n")
        f.write("echo ls -lh; ls -lh\n")
        f.write("export BATCH_NEVENTS={}\n".format(nEventsPerJob))
        #f.write("export BATCH_NFILES={}\n".format(nFilesPerJob)) #not needed
        f.write("export BATCH_NJOBS={}\n".format(nJobs))
        f.write("export BATCH_SEEDOFFSET={}\n".format(seedOffset))
        if args.pyExec: f.write("python3 cfg.py\n")
        else: f.write("fire cfg.py\n")
        f.write("echo ls -lh; ls -lh\n")

    # write a logging wrapper
    log_wrapper = subDir+"/log_wrapper.sh"
    with open(log_wrapper,'w') as f:
        # worker tmp directory
        user=os.getlogin()
        f.write('tmpdir=/tmp/'+user+'/lsf${LSB_JOBID}/job${LSB_JOBINDEX}\n')
        f.write('mkdir -p $tmpdir\n')
        f.write('cd $tmpdir\n')
        # copy inputs
        f.write('subDir="{}"\n'.format(subDir))
        f.write('cp $subDir/setup_ldmx.sh .\n')
        f.write('cp $subDir/run_wrapper.sh .\n')
        for fi in args.include: f.write('cp $subDir/'+os.path.basename(fi)+' .\n')
            # shutil.copy(wd+"/"+f, subDir+"/")
        # f.write('let "LSB_JOBINDEX_ZERO_IDX = LSB_JOBINDEX-1"\n')
        #f.write('if [ -f $subDir/filelist.py ]; then cp $subDir/filelist.py .; fi\n')
        #f.write('if [ -f $subDir/filelists/filelist.${LSB_JOBINDEX_ZERO_IDX}.py ]; then cp $subDir/filelists/filelist.${LSB_JOBINDEX_ZERO_IDX}.py filelist.py; fi\n')
        ### COPY INPUT FILES
        f.write('mkdir ./input_files\n')
        f.write('if [ -f $subDir/filelists/filelist.${LSB_JOBINDEX}.txt ]; then cp $subDir/filelists/filelist.${LSB_JOBINDEX}.txt input_files/filelist.txt; fi\n')
        f.write('if [ -f input_files/filelist.txt ]; then while read line; do   cp "$line" input_files/; done < input_files/filelist.txt; fi\n')
        f.write('cp $subDir/cfg.py .\n')
        f.write('source setup_ldmx.sh\n')
        # run the payload with logging
        f.write('SECONDS=0\n')
        f.write('bash run_wrapper.sh 2>err.log 1>out.log\n')
        f.write('echo "TIME ELAPSED: ${SECONDS} seconds" >> out.log\n')
        f.write('echo "Or $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds." >> out.log\n')
        # copy outputs
        f.write('outDir="{}"\n'.format(outDir))
        f.write('cp out.log  $outDir/logs/out.$LSB_JOBINDEX.log\n')
        f.write('cp err.log  $outDir/logs/err.$LSB_JOBINDEX.log\n')
        f.write('cp out.root $outDir/out.$LSB_JOBINDEX.root\n')
        f.write('cp parameterDump.json  $outDir/pams/parameterDump.$LSB_JOBINDEX.json\n')
        f.write('rm -r $tmpdir/*\n')
    

    # populate the submission directory
    shutil.copy(wd+"/scripts/setup_ldmx.sh", subDir)
    shutil.copy(wd+"/"+args.fragment, subDir+"/cfg.py")
    for f in args.include: 
        shutil.copy(wd+"/"+f, subDir+"/")

    queue = args.queue
    walltime = args.walltime
    if args.test:
        queue = "short"
        walltime = "59"

    print("Run command:")
    cmd  = 'bsub -R "select[centos7]" '
    cmd += '-q {} -W {} -J jobArray[1-{}] '.format(queue, walltime, nJobs)
    cmd += 'scl enable devtoolset-8 "bash {}/log_wrapper.sh"'.format(subDir)
    print(cmd)
    split_args = shlex.split(cmd)
    if not args.noSubmit: subprocess.run(split_args)

    # os.system('cd '+subDir)
    # os.system('pwd ')

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',"--fragment", default='', help="fragment to run with 'fire [fragment]'")
    parser.add_argument('-i',"--input", nargs='*', default='', help="input files")
    parser.add_argument('-n',"--name", default='', help="job name")
    parser.add_argument('-o',"--output", default='', help="path to output files")
    parser.add_argument("--nFilesPerJob", type=int, default=0, help="number of input files per job")
    parser.add_argument("--nEventsPerJob", type=int, default=-1, help="number of events per job")
    parser.add_argument("--nJobs", type=int, default=0, help="number of jobs to send")
    parser.add_argument("--seedOffset", type=int, default=0, help="offset to be applied to each of the job random seeds")
    parser.add_argument("--test", action='store_true', default=False, help="run 3x100 event test jobs")
    parser.add_argument("--pyExec", action='store_true', default=False, help="instead of 'fire cfg.py' run 'python cfg.py'")
    parser.add_argument("--include", nargs='*', default='', help="extra files to copy to the run directory")
    parser.add_argument("--queue", type=str, default='medium')
    parser.add_argument("--walltime", type=str, default='2800')
    parser.add_argument("--noSubmit", action='store_true')
    
    args = parser.parse_args()

    if not len(args.name): exit("Job name required! --name [name]")

    setupJob(args)

