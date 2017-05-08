#!/bin/bash

OS=`uname`
# Some machines (older OS X, BSD, Windows environments) don't support readlink -e
if hash readlink 2>/dev/null; then
  scriptdir=`dirname $0`
else
  scriptpath=$(readlink -e "$0") || scriptpath=$0
  scriptdir=$(dirname "$scriptpath")
fi
WORK_DIR="$(cd "$scriptdir" && pwd -P)"

source "${WORK_DIR}/PIPE_VARS.sh"
PIPELINE_DIR="${WORK_DIR}/.."
# mandatory variable defs JAVA
# options variables defs  CORES, MEM
LIB_DIR="${PIPELINE_DIR}/lib"
SCRIPT_DIR="${PIPELINE_DIR}/scripts"
MODELS_DIR="${PIPELINE_DIR}/models/v1.4"

usage() {
    echo "Usage: $0 -l lang-code [-i <input>] [-o <output> ] [-t <tmp-dir>]" ;
    exit 1 ;
}

while getopts "l:i:o:t:h:" o; do
  case "${o}" in
    l)
      LANG=${OPTARG} ;
      ;;
    t)
      TMPDIR=${OPTARG} ;
      ;;
    i) 
      INPUTFILE=${OPTARG} ;
      ;;
    o)
      OUTPUTFILE=${OPTARG} ;
      ;;
    *)
      usage ;
      ;;
  esac
done
if [[ -z "${LANG}" ]] ; then
  usage ;  
  exit 1 ;
fi
if [[ -z "${TMPDIR}" ]] ; then
  TMPDIR="/tmp" ;
fi
if [[ ! -d "${TMPDIR}" ]]; then
    mkdir -p "${TMPDIR}";
fi

convert2conll09() {
  local inputconllfile="${INPUTFILE}"
  local sentsfile="$1";
  local taggerin="$2";
  local lexicon="$3";

  local cmd="${SCRIPT_DIR}/prepare_data.py -t totsv \
      -i ${inputconllfile} \
      -s ${sentsfile} -o ${taggerin} \
      -c ${lexicon}";
  echo $cmd >&2; 
  eval $cmd >&2;
}

joint_tagger() {
  local m_mdlfile=$1;
  local l_mdlfile=$2;
  local infile=$3;
  local outfile=$4;

  TAGGER_JAR="${LIB_DIR}/marmot-2017-04-18.jar";
  TDEPS="${LIB_DIR}/trove-3.1a1.jar:${LIB_DIR}/mallet.jar";
  local cmd="java -Xmx${MEM} -classpath ${TAGGER_JAR}:${TDEPS} \
         marmot.morph.cmd.Annotator \
         -model-file ${m_mdlfile} \
	 -lemmatizer-file ${l_mdlfile} \
	 -test-file form-index=1,token-feature-index=2,${infile} \
	 -pred-file ${outfile}";
  echo $cmd >&2; 
  eval $cmd >&2;
}

graph_parser() {
  local mdlfile=$1;
  local infile=$2;
  local outfile=$3;

  PARSER_JAR="${LIB_DIR}/anna-3.3.jar";
  PDEPS="";
  local cmd="${JAVA} -Xmx${MEM} -classpath ${PARSER_JAR}:${PDEPS} \
          is2.parser.Parser \
          -model ${mdlfile} \
	  -test  ${infile}  \
	  -out   ${outfile} \
	  -cores ${CORES}" ;  
  echo $cmd >&2;
  eval $cmd >&2;
}

nndep_parser() {
  local mdlfile=$1;
  local infile=$2;
  local outfile=$3;

  PARSER_JAR="${LIB_DIR}/stanford-corenlp-3.7.0.jar";
  PDEPS="";
  local cmd="${JAVA} -Xmx${MEM} -classpath ${PARSER_JAR}:${PDEPS} \
          edu.stanford.nlp.parser.nndep.DependencyParser \
	  -model ${mdlfile} \
	  -threads ${CORES} \
	  -testFile ${infile} \
	  -outFile ${outfile}" ;
  echo $cmd >&2;
  eval $cmd >&2;
}

add2conll09() {
  local taggerout=$1;
  local parserin=$2; 

  local cmd="${SCRIPT_DIR}/prepare_data.py -t prepmate \
      -i ${taggerout} \
      -o ${parserin}";
  echo "$cmd" >&2; 
  eval $cmd   >&2;
}

getconll07() {
  local taggerout=$1;
  local parserin=$2;

  local cmd="${SCRIPT_DIR}/prepare_data.py -t prepstan \
      -i ${taggerout} -o ${parserin}" ;
  echo "$cmd" >&2;
  eval $cmd   >&2;
}

convert092conllu() {
  local sentsfile=$1;
  local parserout=$2;
  
  local cmd="${SCRIPT_DIR}/prepare_data.py -t 9toconllu \
      -i ${parserout} -s ${sentsfile} -o ${OUTPUTFILE}";
  echo "$cmd" >&2; 
  eval $cmd   ;
}

convert072conllu() {
  local sentsfile=$1;
  local parserout=$2;
  
  local cmd="${SCRIPT_DIR}/prepare_data.py -t 7toconllu \
      -i ${parserout} -s ${sentsfile} -o ${OUTPUTFILE}";
  echo "$cmd" >&2; 
  eval $cmd   ;
}

remove_tmp() {
  for scratchfile in "$@"
  do
    if [[ -f "${scratchfile}" ]]; then
      cmd="rm -v ${scratchfile}";
      echo "$cmd" >&2;
      eval $cmd   >&2;
    fi
  done
}

# -- set variables based on variables defined in PIPE_VARS.sh
MODEL_DIR="${MODELS_DIR}/${LANG}"
source ${MODEL_DIR}/lang.sh  # this defines all necessary variables for language. 
# mandatory variable defs MDL_MTAGGER, MDL_LTAGGER, MDL_GPARSER, MDL_ABBREVS
# options variables defs  MDL_LEXICON

# -- temporary storage for stages in the pipeline ;
TMP_PREFIX="${TMPDIR}/$$"
TMP_SENTSFILE="${TMP_PREFIX}.tok.sents";
TMP_TAGGERINFILE="${TMP_PREFIX}.taginp.tsv" ;
TMP_TAGGEDFILE="${TMP_PREFIX}.tagged.conll09";

function PIPE1 {
  if [[ -z ${MDL_MTAGGER} || -z ${MDL_LTAGGER} ]]; then
      echo "Models not found for lemmatizer and morph tagger";
      echo "Check definitions in ${MODEL_DIR}/lang.sh";
      exit 1 ;
  fi
  if [[ -z ${MDL_GPARSER} ]]; then
      echo "Parsing model not found";
      echo "Check definitions in ${MODEL_DIR}/lang.sh";
      exit 1 ;
  fi
  MDL_MTAGGER="${MODEL_DIR}/${MDL_MTAGGER}";
  MDL_LTAGGER="${MODEL_DIR}/${MDL_LTAGGER}";
  MDL_GPARSER="${MODEL_DIR}/${MDL_GPARSER}";
  MDL_CLASSES="${MODEL_DIR}/${MDL_CLASSES}";
  MDL_ABBREVS="${MODEL_DIR}/${MDL_ABBREVS}";

  local TMP_PARSERINFILE="${TMP_PREFIX}.parsinp.conll09";
  local TMP_PARSEDFILE="${TMP_PREFIX}.parsed.conll09";
 
 
  convert2conll09 $TMP_SENTSFILE $TMP_TAGGERINFILE $MDL_CLASSES ;
  joint_tagger    $MDL_MTAGGER $MDL_LTAGGER $TMP_TAGGERINFILE $TMP_TAGGEDFILE ;
  add2conll09     $TMP_TAGGEDFILE $TMP_PARSERINFILE ;
  graph_parser    $MDL_GPARSER $TMP_PARSERINFILE $TMP_PARSEDFILE ;
  convert092conllu  $TMP_SENTSFILE $TMP_PARSEDFILE ;
  #remove_tmp $TMP_SENTSFILE $TMP_TAGGERINFILE $TMP_TAGGEDFILE $TMP_PARSERINFILE $TMP_PARSEDFILE ;
}

function PIPE2 {
  if [[ -z ${MDL_MTAGGER} || -z ${MDL_LTAGGER} ]]; then
      echo "Models not found for lemmatizer and morph tagger";
      echo "Check definitions in ${MODEL_DIR}/lang.sh";
      exit 1 ;
  fi
  if [[ -z ${MDL_NPARSER} ]]; then
      echo "Parsing model not found";
      echo "Check definitions in ${MODEL_DIR}/lang.sh";
      exit 1 ;
  fi
  MDL_MTAGGER="${MODEL_DIR}/${MDL_MTAGGER}";
  MDL_LTAGGER="${MODEL_DIR}/${MDL_LTAGGER}";
  MDL_NPARSER="${MODEL_DIR}/${MDL_NPARSER}";  # Stanford NNdep model
  MDL_CLASSES="${MODEL_DIR}/${MDL_CLASSES}";
  MDL_ABBREVS="${MODEL_DIR}/${MDL_ABBREVS}";

  local TMP_PARSER09INFILE="${TMP_PREFIX}.parsinp.conll09";
  local TMP_PARSER07INFILE="${TMP_PREFIX}.parsinp.conll07";
  local TMP_PARSEDFILE="${TMP_PREFIX}.parsed.conll07";
  
  
  convert2conll09 $TMP_SENTSFILE $TMP_TAGGERINFILE $MDL_CLASSES ;
  joint_tagger    $MDL_MTAGGER $MDL_LTAGGER $TMP_TAGGERINFILE $TMP_TAGGEDFILE ;
  add2conll09     $TMP_TAGGEDFILE $TMP_PARSER09INFILE ;
  getconll07      $TMP_PARSER09INFILE $TMP_PARSER07INFILE ;
  nndep_parser    $MDL_NPARSER $TMP_PARSER07INFILE $TMP_PARSEDFILE ;
  convert072conllu  $TMP_SENTSFILE $TMP_PARSEDFILE ;
  #remove_tmp $TMP_SENTSFILE $TMP_TAGGERINFILE $TMP_TAGGEDFILE $TMP_PARSERINFILE $TMP_PARSEDFILE ;
}


PIPE1 ;
# PIPE2 ;
