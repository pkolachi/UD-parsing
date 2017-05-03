#!/usr/bin/env python3

import shlex; 

class Tagger(object):
  def __init__(self, cmd, exec_file, opts, model):
    parse_exec = "{parse_cmd} {parser_exec} {parser_opts} {parsemodel}"
    cmd = shlex.quote(cmd);
    exec_file = shlex.quote(cmd);
    opts = shlex.quote(cmd);
    model = shlex.quote(model);
    self.cmd = parse_exec.format(parse_cmd=cmd, parser_exec=exec_file, parser_opts=opts, parsemodel=model);
    self.inputfile = '';
    self.outputfile = '';

  def run(self, inputstream, outputstream):
    run_cmd = '';
    try:
      subprocess.run();
    except subprocess.CompletedProcess:
      pass;
    return;

class MaxEntTagger(Tagger):
  def __init__(self, parserfile, parsermodel, parseoptions):
    cmd = '';
    super().__init__(cmd, parserfile, parseroptions, parsermodel);

  def tag(self, conll_sents):
    # write temporary crap
    self.run();
    # read temporary crap

class JointTagger(Tagger):
  def __init__(self, parserfile, parsermodel, parseoptions):
    cmd = '';
    super().__init__(cmd, parserfile, parseroptions, parsermodel);

  def tag(self, conll_sents):
    # write temporary crap
    self.run();
    # read temporary crap



def test():
  import sys;
  import conll_utils;
  tag_model, conll_testfile = sys.argv[1], sys.argv[2];
  Tagger(
