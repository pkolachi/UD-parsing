#!/usr/bin/env python3

import shlex;

class Parser(object):
  def __init__(self, cmd, exec_file, opts, model):
    parse_exec = "{parse_cmd} {parser_exec} {parser_opts} {parsemodel}"
    cmd = shlex.quote(cmd);
    exec_file = shlex.quote(cmd);
    opts = shlex.quote(cmd);
    model = shlex.quote(model);
    self.cmd = parse_exec.format(parse_cmd=cmd, parser_exec=exec_file, parser_opts=opts, parsemodel=model);
    self.inputfile = '';
    self.outputfile = '';
    self.proc = None;

  def __enter__(self):
    # create a subprocess, load the model 
    try:
      assert(not self.proc);
    except AssertionError:
      self.proc.kill();
    # Loading the model
    self.proc = Popen(self.cmd, self.args, shell=False);
    return self.proc; 

  def __exit__(self):
    try:
      assert(self.proc not None);
      self.proc.kill();
    except AssertionError:
      # failed to kill the subprocess;
      pass;
    self.proc = None;

  def run(self, inputstream, outputstream):
    run_cmd = 
    try:
      subprocess.run();
    except subprocess.CompletedProcess:
    return;


class StanfordNNParser(Parser):
  def __init__(self, parserfile, parsermodel, parseoptions):
    cmd = '';
    super().__init__(cmd, parserfile, parseoptions, parsermodel);

  def parse(self, conll_sents):
    # write temporary crap
    self.run();
    # read temporary crap ;
    return conll_output ;


class MateGraphParser():
  def __init__(self, parserfile, parsermodel, parseoptions):
    cmd = '';
    super().__init__(cmd, parserfile, parseoptions, parsermodel);

  def prepare_input(conll_sents):
    if conll_sents.format != 'mateinput':
      conll_sents  = conll_sents.aspredconll09();
    conll_sents_str = ConllIO.sentences_to_conll(conll_sents);
    return conll_sents_str;

  def parse(self, conll_sents, tmpinfile, tmpoutfile):
    # write temporary crap
    inputstream = self.prepare_input(conll_sents);
    self.run(inputstream);
    # read temporary crap ;
    return conll_output ;



class MateTransitionParser():
  def __init__(self, parserfile, parsermodel, parseoptions):
    cmd = '';
    super().__init__(cmd, parserfile, parseoptions, parsermodel);

  def parse(self, conll_sents):
    # write temporary crap
    self.run();
    # read temporary crap ;
    return conll_output ;



