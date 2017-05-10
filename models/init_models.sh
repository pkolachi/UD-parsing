#!/bin/bash

OS=`uname`
# Some machines (older OS X, BSD, Windows environments) don't support readlink -e
if hash readlink 2>/dev/null; then
  scriptdir=`dirname $0`
else
  scriptpath=$(readlink -e "$0") || scriptpath=$0
  scriptdir=$(dirname "$scriptpath")
fi
MODEL_DIR="$(cd "$scriptdir" && pwd -P)"

mkdir -p "${MODEL_DIR}/v1.4"
cd "${MODEL_DIR}/v1.4/"

curl -o "english-v1.4.tgz" \
    http://www.grammaticalframework.org/~prakol/udjpipe/english-v1.4.tgz
curl -o "swedish-v1.4.tgz" \
    http://www.grammaticalframework.org/~prakol/udjpipe/swedish-v1.4.tgz
curl -o "finnish-v1.4.tgz" \
    http://www.grammaticalframework.org/~prakol/udjpipe/finnish-v1.4.tgz

tar -xvzf english-v1.4.tgz
tar -xvzf swedish-v1.4.tgz
tar -xvzf finnish-v1.4.tgz

rm -v english-v1.4.tgz swedish-v1.4.tgz finnish-v1.4.tgz

cd -
