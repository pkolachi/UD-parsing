# UD-parsing
Parsing Pipelines for Universal Dependencies

This folder contains the scripts and models necessary for a UD parsing pipeline. 
The following pipelines have been included as of now
  - udjpipe:  A graph-based parser pipeline using classical statistical models

## INITALIZE pipeline

The following steps are necessary one-time to initialize the pipeline.

- The file "udjpipe/scripts/PIPE\_VARS.sh" contains environment variables
necessary for the pipeline. Check that these are consistent with your system
configuration. Variables defined here include- 
    - JAVA - path to the java executable on the system
    - MEM  - maximum allowable memory to be used by the pipeline
    - CORES - number of cores that the parser can use

- OBTAIN THE MODELS: The models for each language are quite big to be included
in the git repository. They need to be downloaded and placed in the right folder
before the pipeline can be used. The model archive should be downloaded from the
url listed below, and extracted into the udjpipe/models/v1.4/ folder.

The models for each language can be found at the below urls:
[English](http://www.grammaticalframework.org/~prakol/udjpipe/english-v1.4.tgz)
[Finnish](http://www.grammaticalframework.org/~prakol/udjpipe/finnish-v1.4.tgz)
[Swedish](http://www.grammaticalframework.org/~prakol/udjpipe/swedish-v1.4.tgz)

NEW: There is now a script init\_models.sh in udjpipe/models/. Executing it
will download the models and extract the models in the right place. 

## HOW TO

There are two scripts in the udjpipe/scripts folder included for direct use:
  Usage: ./pipeline.sh -l lang-code [-i <input>] [-o <conllu-output> ] [-t <tmp-dir>]
  Usage: ./pipeline\_conll.sh -l lang-code [-i <conll-input>] [-o <conllu-output> ] [-t <tmp-dir>]

These scripts accept input from stdin or an optional input file and produce the
output to stdout or a file specified using the "-o" option. 

The language codes are the same as used in Universal Dependencies project (and
not the ISO code used in Grammatical Framework). Thus listed below are the codes-

en -- English
fi -- Finnish
sv -- Swedish

Additionally, if the "-t" option is used, temporary files are written to the
folder and removed at the end of the pipeline.
  
## Directory structure

