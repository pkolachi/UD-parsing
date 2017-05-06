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
# mandatory variable defs PIPELINE_DIR, JAVA, MODELS_DIR
# options variables defs  CORES, MEM
LIB_DIR="${PIPELINE_DIR}/lib"
SCRIPT_DIR="${PIPELINE_DIR}/scripts"
MODELS_DIR="${PIPELINE_DIR}/models/v1.4"

if (( $# < 1)); then
  echo "Error: $0 lang-code [<tmp-dir>]"
  exit 1;
else
  LANG=$1;
fi
if (( $# >= 2)); then
  TMP_DIR=$2;
  if [[ ! -d "${TMP_DIR}" ]]; then
      mkdir -p "${TMP_DIR}";
  fi
else
  TMP_DIR="/tmp";
fi

function convert2conll09 {
  
  local sentsfile="$1";
  local taggerin="$2";
  local lexicon="$3";

  local cmd="${SCRIPT_DIR}/prepare_data.py totsv ${sentsfile} ${taggerin} ${lexicon}";
  echo $cmd >&2; 
  eval $cmd >&2;
}

function joint_tagger {
  m_mdlfile=$1;
  l_mdlfile=$2;
  infile=$3;
  outfile=$4;

  TAGGER_JAR="${LIB_DIR}/marmot-2017-04-18.jar";
  TDEPS="${LIB_DIR}/trove-3.1a1.jar:${LIB_DIR}/mallet.jar";

  local cmd="java -Xmx${MEM} -classpath ${TAGGER_JAR}:${TDEPS} \
         marmot.morph.cmd.Annotator \
         -model-file $m_mdlfile \
	 -lemmatizer-file $l_mdlfile \
	 -test-file form-index=1,token-feature-index=2,$infile \
	 -pred-file $outfile";
  echo $cmd >&2; 
  eval $cmd >&2;

}

function graph_parser {
  local mdlfile=$1;
  local infile=$2;
  local outfile=$3;

  PARSER_JAR="${LIB_DIR}/anna-3.3.jar";
  PDEPS="";

  local cmd="${JAVA} -Xmx${MEM} -classpath $PARSER_JAR:${PDEPS} \
          is2.parser.Parser \
          -model $mdlfile \
	  -test  $infile  \
	  -out   $outfile \
	  -cores $CORES" ;  
  echo "$cmd" >&2;
  eval $cmd   >&2;
}

function convert2conllu {
  local sentsfile=$1;
  local parserout=$2;
  
  local cmd="${SCRIPT_DIR}/prepare_data.py toconllu ${sentsfile} ${parserout}";
  echo "$cmd" >&2; 
  eval $cmd   ;
}

function add2conll09 {
  taggerout=$1;
  parserin=$2; 

  cmd="${SCRIPT_DIR}/prepare_data.py prepmate ${taggerout} ${parserin}";
  echo "$cmd" >&2; 
  eval $cmd   >&2;
}

function remove_tmp {
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
MDL_MTAGGER="${MODEL_DIR}/${MDL_MTAGGER}";
MDL_LTAGGER="${MODEL_DIR}/${MDL_LTAGGER}";
MDL_GPARSER="${MODEL_DIR}/${MDL_GPARSER}";
MDL_CLASSES="${MODEL_DIR}/${MDL_CLASSES}";
MDL_ABBREVS="${MODEL_DIR}/${MDL_ABBREVS}";

# -- temporary storage for stages in the pipeline ;
TMP_PREFIX="${TMP_DIR}/$$"
TMP_SENTSFILE="${TMP_PREFIX}.tok.sents";
TMP_TAGGERINFILE="${TMP_PREFIX}.taginp.tsv" ;
TMP_TAGGEDFILE="${TMP_PREFIX}.tagged.conll09";
TMP_PARSERINFILE="${TMP_PREFIX}.parsinp.conll09";
TMP_PARSEDFILE="${TMP_PREFIX}.parsed.conll09";

convert2conll09 $TMP_SENTSFILE $TMP_TAGGERINFILE $MDL_CLASSES;
joint_tagger    $MDL_MTAGGER $MDL_LTAGGER $TMP_TAGGERINFILE $TMP_TAGGEDFILE ;
add2conll09     $TMP_TAGGEDFILE $TMP_PARSERINFILE ;
graph_parser    $MDL_GPARSER $TMP_PARSERINFILE $TMP_PARSEDFILE ;
convert2conllu  $TMP_SENTSFILE $TMP_PARSEDFILE ;
remove_tmp      $TMP_SENTSFILE $TMP_TAGGERINFILE $TMP_TAGGEDFILE $TMP_PARSEDFILE ;
