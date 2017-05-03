#!/usr/bin/env python3

from prepare_data import SentenceSplitter;

ALL_STAGES = ["tokenize", "ssplit", "xpos", "lemmatize", "tagandlemmatize", "morphtag", "tagandmanalyze", "parse"];

def train_pipeline(pipelineEnv, logger):
  return False;

def run_pipeline(test_conll, tag_model):  #def run_pipeline(pipelineEnv, logger):


  '''
  if pipelineEnv.sentSplit:
    # run SentenceSplitter
    ssplitter = SentenceSplitter();
    sents = ssplitter.process_text(inputstream);
    try:
      assert(not pipelineEnv.skip_tokenization);
    except AssertionError:
      logger.fdafads("Tokenization can not be if sentence splitting has been performed");

  else:
    sents = FileIO.lines_from_file(inputstream);

  if '''



def main():
  #pipe_env = commandline.....();
  #sane_pipe_env = sanitize(pipe_env);
  # find 
  if False:   #sane_pipe_env.train:
    ret_code = train_pipeline(sane_pipe_env);
  else:
    ret_code = run_pipeline(sane_pipe_env);
  return ret_code;

if __name__ == '__main__':
  return main();
