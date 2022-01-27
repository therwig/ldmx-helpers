#!/bin/env python
import optparse
import shutil
import os

def setupJob(opts,args):
    '''
    write a submission diretory
    copy the log wrapper and other cfg files there
    amend the cfg with the job configs (files, events, etc...)
    submit the jobs
    '''

    # setup directories (submit + output)
    wd = os.getcwd()
    subDir = wd + "/submissions/" + opts.name
    outDir = opts.output
    os.makedirs(subDir,exist_ok=False)
    os.makedirs(outDir,exist_ok=False)
    os.makedirs(outDir+"/logs",exist_ok=False)
    os.makedirs(outDir+"/pams",exist_ok=False)

    # populate the submission directory
    shutil.copy(wd+"/scripts/setup_ldmx.sh", subDir)

    # write the runwrapper (everything we'd like to log)
    run_wrapper = subDir+"/run_wrapper.sh"
    with open(run_wrapper,'w') as f:
        # run
        f.write("echo pwd; pwd")
        f.write("echo ls -lh; ls -lh")
        f.write("fire cfg.py")
        f.write("echo ls -lh; ls -lh")
        
    # write a logging wrapper
    log_wrapper = subDir+"/log_wrapper.sh"
    with open(log_wrapper,'w') as f:
        # worker tmp directory
        user=os.getlogin()
        f.write("tmpdir=/tmp/"+user+"/lsf${LSB_JOBID}/job${LSB_JOBINDEX}")
        f.write("mkdir -p $tmpdir")
        f.write("cd $tmpdir")
        # copy inputs
        f.write('subDir="{}"'.format(subDir))
        f.write("cp $subDir/setup_ldmx.sh .")
        f.write("cp $subDir/cfg.py .")
        # run the payload with logging
        f.write("SECONDS=0")
        f.write(runcmd+" 2>err.log 1>out.log")
        f.write('echo "TIME ELAPSED: ${SECONDS} seconds" >> out.log')
        f.write('echo "Or $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds." >> out.log')
        # copy outputs
        f.write('outDir="{}"'.format(outDir))
        f.write("cp out.log  $outDir/logs/out.$LSB_JOBINDEX.log")
        f.write("cp err.log  $outDir/logs/err.$LSB_JOBINDEX.log")
        f.write("cp out.root $outDir/out.$LSB_JOBINDEX.root")
        f.write("cp parameterDump.json  $outDir/pams/parameterDump.$LSB_JOBINDEX.json")
        f.write("rm -r $tmpdir/*")
    

    cfgFile = opts.fragment

    

    # bsub -R "select[centos7]" -q medium -W 2800 -J jobArray[1-100]  \
    # scl enable devtoolset-8 "bash test_logwrap.sh ${outDir}/${name}"
    
def write_log_wrapper(fname, runcmd):

if __name__== "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-f',"--fragment", type="string", default='', help="fragment to run with 'fire [fragment]'")
    parser.add_option('-i',"--input", type="string", default='', help="input files")
    parser.add_option('-n',"--name", type="string", default='', help="job name")
    parser.add_option('-o',"--output", type="string", default='', help="path to output files")
    parser.add_option("--nFilesPerJob", type="int", default=1, help="number of input files per job")
    parser.add_option("--test", action='store_true', default=False, help="run 3x100 event test jobs")
    (opts, args) = parser.parse_args()

    if !len(opts.name): exit("Job name required! --name [name]")

    setupJob(opts,args)

