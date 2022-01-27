#!/usr/bin/env python

import argparse
import logging
import platform
import os
import sys
import subprocess
import time
import yaml
import uuid

#################################################################
# Parse Parameter File
#   Use yaml package to parse the parameters file
#   and return (effectively) a map of parameter names to values
def parse_parameters(parameters_file) :

    logging.info("Loading parameters from %s" % parameters_file)
    parameters = open(parameters_file, 'r')
    return yaml.safe_load(parameters)
    #return yaml.load(parameters)

###################################################################
# Main Program
def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("parameterFile", type=str, action='store',
                        help="Parameters file.")
    parser.add_argument("-t,--test", action='store_true', dest='test',
                        help="Don't submit the job to the batch.")
#    parser.add_argument("-v,--verbose", action='store_true', dest='verbose',
#                        help="Print logging messages to std out/err.")
    args = parser.parse_args()

    # If a parameters file was not specified, warn the user and exit.
    if not args.parameterFile :
        parser.error('A parameters file needs to be specified.')

    # Configure the logger
    logging.basicConfig(format='[ bsub ][ %(levelname)s ]: %(message)s', 
            level=logging.DEBUG)
   
    # Parse the parameters file.
    logging.info('Parsing parameters located at %s' % args.parameterFile.strip())
    parameters = parse_parameters(args.parameterFile)

    ##############################################################
    #   Check for required parameters

    jobs = 0

    inputFileList = []
    if 'InputFileList' in parameters :
        inputFileList = os.listdir( parameters['InputFileList'].strip() )
        logging.info('Getting input files from %s' % parameters['InputFileList'].strip())
        jobs = len(inputFileList)
    #end search for input files
    
    if 'Jobs' in parameters: 
        #jobs is minimum of available input files and number passed
        if 'InputFileList' in parameters : jobs = min( jobs , int(parameters['Jobs']) )
        else : jobs = int(parameters['Jobs'])
        logging.info('Submitting %s jobs.' % jobs)
    elif 'InputFileList' not in parameters : 
        logging.warning('Need to specify the number of jobs (Jobs) or a list of input files (InputFileList).')
        exit()

    configTemplate = ''
    if 'Config' in parameters:
        configTemplate = os.path.realpath(parameters['Config'].strip())
        logging.info('Config template located at \'%s\'' % configTemplate)
    else:
        logging.warning('A python config template for ldmx-app is required.')
        exit()

    if 'EventOutput' not in parameters and 'HistogramOutput' not in parameters:
        logging.warning('Either \'EventOutput\' or \'HistogramOutput\' must be given.')
        exit()

    ##############################################################
    #   Check for optional parameters and build command to run ldmx-app

    # Use the user specified run script if it has been specified instead.
    run_script = '%s/run_ldmx_app.py' % os.getcwd()
    if 'RunScript' in parameters: run_script = os.path.realpath(parameters['RunScript'])

    command = 'python %s %s ' %( run_script , configTemplate )

    if 'EnvScript' in parameters:
        command += '--envScript %s ' % ( os.path.realpath(parameters['EnvScript'].strip() ) )

    if 'DetectorPath' in parameters:
        command += '--detectorPath %s ' % ( os.path.realpath(parameters['DetectorPath'].strip() ) )

    #get detailed name for this sim run
    oprefix = ''
    if 'Prefix' in parameters:
        oprefix = parameters['Prefix'].strip()

    # Get the path where all files will be stored. If the path doesn't
    # exist, create it.
    if 'EventOutput' in parameters:
        eventDir = os.path.realpath(parameters['EventOutput'].strip()) + '/' + oprefix
        if not os.path.exists(eventDir): 
            logging.info('Output directory does not exist and will be created.')
            os.makedirs(eventDir)
        logging.info('All event files will be save to %s' % eventDir)
        command += '--eventOut %s ' % ( eventDir )
    else :
        logging.info( 'Event files will not be saved.' )

    if 'HistogramOutput' in parameters:
        histogramDir = os.path.realpath(parameters['HistogramOutput'].strip()) + '/' + oprefix
        if not os.path.exists(histogramDir): 
            logging.info('Output directory does not exist and will be created.')
            os.makedirs(histogramDir)
        logging.info('All histogram files will be save to %s' % histogramDir)
        command += '--histOut %s ' % ( histogramDir )
    else :
        logging.info( 'Histogram files will not be saved.' )

    #################################################################################
    # Define command to submit to batch
    #kisos = " ".join(["kiso{:0>4d}".format(i) for i in range(70)])
    kisos=" kiso0002 kiso0003  kiso0004 kiso0005 kiso0006  kiso0008 kiso0010 kiso0011  kiso0012 kiso0013 kiso0014  kiso0015 kiso0016 kiso0017  kiso0018 kiso0019 kiso0020  kiso0021 kiso0022 kiso0024  kiso0025 kiso0026 kiso0027  kiso0028 kiso0029 kiso0030  kiso0032 kiso0033 kiso0034  kiso0035 kiso0036 kiso0037  kiso0038 kiso0039 kiso0040  kiso0041 kiso0042 kiso0043  kiso0044 kiso0045 kiso0046  kiso0047 kiso0048 kiso0049  kiso0050 kiso0051 kiso0052  kiso0054 kiso0055 kiso0056  kiso0057 kiso0058 kiso0059  kiso0060 kiso0061 kiso0062  kiso0063 kiso0064 kiso0065  kiso0067 kiso0068"
    #batch_command = 'bsub -R "hname!=deft* select[centos7]" -q medium -W 2800 '
    #batch_command = 'bsub -R "select[centos7]" -m "kisofarm" -q medium -W 2800 '
    #batch_command = 'bsub -R "select[centos7]" -m "'+kisos+'" -q medium -W 2800 '
    #batch_command = 'bsub -R "hname != deft*" -q medium -W 2800 '
    #batch_command = 'bsub -q medium -W 2800 '
    batch_command = 'bsub -R "select[centos7]" -q medium -W 2800 '
    if 'BatchCommand' in parameters:
        batch_command = parameters['BatchCommand'].strip()

    # Turn off emailing about jobs
    email_command = ['bash', '-c', 'export LSB_JOB_REPORT_MAIL=N && env']
    proc = subprocess.Popen(email_command, stdout=subprocess.PIPE)

    for line in proc.stdout: 
        (key, _, value) = line.decode().partition('=')
        os.environ[key] = value.strip()

    proc.communicate()

    # CH note:
    # could rewrite with job arrays for more efficient submission
    # https://www.ibm.com/support/knowledgecenter/SSWRJV_10.1.0/lsf_admin/job_array_cl_args.html

    doJobArray=True
    #doJobArray=False

    # bsub -J "myArray[1-1000]" myJob -f input.\$LSB_JOBINDEX

    if doJobArray and len(inputFileList)==0:
        ofile = "%s_%s" % (oprefix, str(uuid.uuid4())[:8])
        specific_command = command + '--prefix %s ' % ( ofile )
        array_command = "-J jobArray[1-{}] ".format(jobs)
        #full_command = batch_command+array_command+specific_command
        wrapped_cmd = 'scl enable devtoolset-8 "{}"'.format(specific_command)
        full_command = batch_command+array_command+wrapped_cmd
        print("command:")
        print(full_command)
        #subprocess.Popen(full_command, shell=True).wait()
        # must catch the LSB_JOBINDEX env variable
        
    else:
        for job in range(0, jobs):
        
            # wait until the number of jobs pending is <= 5
            if not args.test:
                pendingCount = int(subprocess.check_output('bjobs -p 2> /dev/null | wc -l', shell=True))
                while pendingCount > 5 : 
                    sys.stdout.write( 'Total jobs pending: %s\r' % pendingCount )
                    sys.stdout.flush()
                    time.sleep(1)
                    pendingCount = int(subprocess.check_output('bjobs -p 2> /dev/null | wc -l',shell=True))
        
                if pendingCount > 0 :
                    time.sleep(10)
            #end if not test
        
            ofile = "%s_%s" % (oprefix, str(uuid.uuid4())[:8])
            specific_command = command + '--prefix %s ' % ( ofile )
            
            if 'InputFileList' in parameters:
                specific_command += '--inputFile %s ' % ( inputFileList[job] )
            #end attachment of input file
        
            if args.test: 
                logging.info( batch_command+specific_command )
                subprocess.Popen(specific_command + ' --test', shell=True).wait()
            else:
                subprocess.Popen(batch_command+specific_command, shell=True).wait()
                time.sleep(1)
            #end whether or not is a test
        #end loop through jobs

if __name__ == "__main__" : 
    main()
    
