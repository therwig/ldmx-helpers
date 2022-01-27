
# Don't email batch job log
export LSB_JOB_REPORT_MAIL=N

export SOFTWARE_HOME=/nfs/slac/g/ldmx/software

#############
#   cmake   #
#############
export PATH=$SOFTWARE_HOME/cmake/cmake-3.16.0-rc3/install_gcc8/bin:$PATH

##############
#   python   #
##############
export PYTHONHOME=/nfs/slac/g/ldmx/software/Python-3.8.2/install_gcc8.3.1_cos7/
export PATH=$PYTHONHOME/bin:$PATH
export PYTHONPATH=$PYTHONHOME/lib:$PYTHONPATH
export LD_LIBRARY_PATH=$PYTHONHOME/lib:$LD_LIBRARY_PATH

##############
#   Xerces   #
##############
export XercesC_DIR=$SOFTWARE_HOME/xerces-c-3.2.2/install_gcc8.3.1_cos7
export LD_LIBRARY_PATH=$XercesC_DIR/lib:$LD_LIBRARY_PATH

#############
#   Boost   #
#############
export BOOST_ROOT=$SOFTWARE_HOME/boost_1_73_0/install_gcc8.3.0_cos7
export LD_LIBRARY_PATH=$BOOST_ROOT/lib:$LD_LIBRARY_PATH

##############
#   Geant4   #
##############
export G4DIR=$SOFTWARE_HOME/geant4/install_g10.2.3_v0.3_gcc8.3.1_cos7
source $G4DIR/bin/geant4.sh

############
#   ROOT   #
############
#export ROOTDIR=$SOFTWARE_HOME/root-6.18.04/install_gcc8.3.1_cos7
export ROOTDIR=$SOFTWARE_HOME/root-6.20.06/install_gcc8.3.1_cos7
source $ROOTDIR/bin/thisroot.sh

###################
#   ONNXRuntime   #
###################
export ONNXRUNTIME_DIR=$SOFTWARE_HOME/onnxruntime-linux-x64-1.2.0
export LD_LIBRARY_PATH=$ONNXRUNTIME_DIR/lib:$LD_LIBRARY_PATH

###############
#   ldmx-sw   #
###############
export LDMXSW_DIR=/nfs/slac/g/ldmx/users/$USER/sandbox/ldmx-sw/install
export PATH=$LDMXSW_DIR/bin:$PATH
export LD_LIBRARY_PATH=$LDMXSW_DIR/lib:$LD_LIBRARY_PATH
#export PYTHONPATH=$LDMXSW_DIR/lib/python:$LD_LIBRARY_PATH
export PYTHONPATH=$LDMXSW_DIR/python:$PYTHONPATH

