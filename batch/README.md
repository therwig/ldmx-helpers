```
scl enable devtoolset-8 bash
source ~/.bash_profile
source ~/ldmx/local_setup.sh

python run_ldmx_app.py /nfs/slac/g/ldmx/users/therwig/sandbox/ldmx-sw/run/batchtest/config.py.tpl --envScript /nfs/slac/g/ldmx/users/therwig/local_setup.sh --eventOut /nfs/slac/g/ldmx/users/therwig/sandbox/ldmx-sw/run/batchtest/ThisIsMyPrefix --histOut /nfs/slac/g/ldmx/users/therwig/sandbox/ldmx-sw/run/batchtest/ThisIsMyPrefix --prefix ThisIsMyPrefix_7052a46c

python ldmx_bsub.py sample.yml -t

python ldmx_bsub.py sample.yml
```

Something like 1k * 10k events.
