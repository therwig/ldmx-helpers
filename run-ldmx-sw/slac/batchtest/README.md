# Batch at SLAC
This directory contains the basic files you need to submit batch jobs to SLAC through the bsub system.
The files you need to worry about editing to your specifc job are `config.py.tpl` and `sample.yml`.
`config.py.tpl` is a template configuratoin file that will be run through `ldmx-app` after certain parameters are substituted in.
The parameters that are searched for are

Parameter | Description
---|---
`inputFile` | The file that will be copied over before the run starts (e.g. LHE file or input root event file). Taken from the list given in `sample.yml`.
`output_events` | Name of output event file. Configured to by the running script attaching your prefix.
`output_hists` | Name of output histogram file. Configured to by the running script attaching your prefix.
`run` | Run Number. Generated in running script as a concatenation of the two seeds.
`seed1` and `seed2` | Random number seeds. Generated in running script.

You can make a copy of `config.py.tpl` and edit it to match your job that you want to do, keeping these parameters in mind.
I would advise running tests using the `run_ldmx_app.py` and your template to make sure everything runs smoothly before submitting loads of jobs.

After you are confident that the `config.py.tpl` is operating correctly, you can make a copy of `sample.yml` and edit it to point to your configuration and put it the other details you like.
Basic operation is simple but fragile.
```bash
python ldmx_bsub.py sample.yml
```
I say fragile because I don't totally understand how everything works.
All I can say, is be careful and try your best to understand the configuration script before submitting it to batch.
Good luck.
