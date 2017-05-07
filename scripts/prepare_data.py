#!/usr/bin/env python3

from collections import defaultdict;
from operator import itemgetter;
from sys import argv as sysargv, stdin, stdout, stderr, exit as sysexit;
import itertools as it;
import io;
import os.path as pathutils;
import re;
import argparse;


WSPAT  = re.compile('\s+', flags=re.U);
TABPAT = re.compile('\t',  flags=re.U);
BUF_SIZE = 10000;

def smart_open(filename='', mode='r', large=True):
  from bz2 import BZ2File;
  from gzip import GzipFile;
  
  bufferSize = ((2<<16)+8) if large == True else io.DEFAULT_BUFFER_SIZE;
  filename = filename.strip();
  if filename:
    _, ext = pathutils.splitext(filename);
    if ext == '.bz2':
      mode = 'rb' if mode in ['r', 'rb'] else 'wb';
      iostream = BZ2File(filename,  mode=mode, buffering=bufferSize);
    elif ext == '.gz':
      mode = 'rb' if mode in ['r', 'rb'] else 'wb';
      iostream = GzipFile(filename, mode=mode);
    else:
      mode = 'rb' if mode in ['r', 'rb'] else 'wb';
      iostream = io.open(filename,  mode=mode, buffering=bufferSize);
  else:
    iostream = stdin.buffer if mode in ['r', 'rb'] else stdout.buffer;

  return io.TextIOWrapper(iostream, encoding='utf-8');

def lines_from_file(filename, large=False, batchsize=0):
  with smart_open(filename, large=large) as infile:
    line_count = 0;
    for line_count, line in enumerate(infile, start=1):
      yield line.strip();
  return;

def lines_to_file(filename, lines, batchsize=0):
  with smart_open(filename, mode='w') as outfile:
    line_count = 0;
    for line_count, sent in enumerate(lines, start=1):
      print(sent.strip(), file=outfile);
  return True;

# These are the labels on the columns in the CoNLL 2007 dataset.
CONLL07_COLUMNS = (
    'id', 'form', 'lemma',
    'cpostag', 'postag', 'feats',
    'head', 'deprel',
    'phead', 'pdeprel',
    );
# These are the labels on the columns in the CoNLL 2009 dataset.
CONLL09_COLUMNS = (
    'id', 'form', 'lemma', 'plemma',
    'postag', 'ppostag', 'feats', 'pfeats',
    'head', 'phead', 'deprel', 'pdeprel', 'fillpred', 'sense', 
    );
# These are the labels on the columns in the ConllU format (UD treebanks).
CONLLU_COLUMNS = (
    'id', 'form', 'lemma',
    'postag', 'xpostag', 'feats',
    'head', 'deprel',
    'deps', 'misc', 
    );

# These are the labels on the columns when Berkeley parser 
# is given pre-tagged input
BERKELEY_COLUMNS = ('form', 'postag', );
# These are the labels on the output of morfette tagger
MORFETTE_COLUMNS = ('form', 'lemma', 'postag', );
TSV_INPUT = ('id', 'form', );

FIELDS = CONLLU_COLUMNS;

def words_from_conll(lines, fields=CONLLU_COLUMNS):
  '''Read words for a single sentence from a CoNLL text file.'''
  # using this with filter doubles parsing time 
  def isMultiWord(x): return re.match('^[0-9]+?-[0-9]+?$', x);
  def parseFeats(fstruc): 
    return tuple(
      tuple(x.split('=', 1)) for x in fstruc.split('|')
    );

  for line in lines:
    entries = re.split(TABPAT, line);
    if fields == CONLLU_COLUMNS and isMultiWord(entries[0]):
      continue;
    entries = zip(fields, entries);
    entry = defaultdict(lambda: u'_', entries);

    if 'feats' in fields and entry['feats'] != '_':
      entry['feats'] = parseFeats(entry['feats']);
    if 'pfeats' in fields and entry['pfeats'] != '_':
      entry['pfeats'] = parseFeats(entry['pfeats']);

    yield entry;

def words_to_conll(sent, fields=CONLLU_COLUMNS):
  str_repr = [];
  if type(sent) == type(()) and len(sent) == 2:
    str_repr.append(str(sent[0]));
    sent = sent[1];
  for token in sent:
    feat_repr = \
        '|'.join('{0}={1}'.format(feat, value) for feat, value in token['feats']) \
        if 'feats' in token and type(token['feats']) == type(()) \
        else token['feats'];
    token['feats'] = feat_repr if feat_repr.strip() else '_';
    if 'pfeats' in token:
      feat_repr = \
        '|'.join('{0}={1}'.format(feat, value) for feat, value in token['pfeats']) \
        if 'pfeats' in token and type(token['pfeats']) == type(()) \
        else token['pfeats'];
      token['pfeats'] = feat_repr if feat_repr.strip() else '_';
    str_repr.append('\t'.join(token[feat] for feat in fields));
  return '\n'.join(str_repr);

def lines_from_conll(lines):
  '''Read lines for a single sentence from a CoNLL text file.'''
  for line in lines:
    if not line.strip():
      return;
    yield line.strip();

def sentences_from_conll(stream, fields=None):
  '''Read sentences from lines in an open CoNLL file handle.'''
  global FIELDS;
  if not fields: 
    fields = FIELDS;
  sent_count = 0;
  while True:
    lines = tuple(lines_from_conll(stream));
    if not len(lines):
      break;
    sent_count += 1;
    comm_lines  = it.takewhile(lambda X: X.startswith('#'), lines);
    comm_lines  = '\n'.join(comm_lines); 
    conll_lines = it.dropwhile(lambda X: X.startswith('#'), lines);
    tree = list(words_from_conll(conll_lines, fields=fields));
    yield (comm_lines, tree);
  return;

def sentences_to_conll(sentences, fields=None):
  global FIELDS;
  if not fields:
    fields = FIELDS;
  for sent_count, sent in enumerate(sentences, start=1):
    yield words_to_conll(sent, fields=fields);
    yield "";

def swapConllFields(oldColumns, newColumns, remove=False):
  def worker(conll_sent):
    if type(conll_sent) == type(()) and len(conll_sent) == 2:
      meta_info  = conll_sent[0]
      conll_sent = conll_sent[1];
    else:
      meta_info  = '';
    for edge in conll_sent:
      for old, new in zip(oldColumns, newColumns):
        edge[new] = edge[old];
      if remove:
        for old in oldColumns:
          if old in edge:
            del edge[old];
    return (meta_info, conll_sent); 
  return worker ;

def toconll09(inputfile='', outputfile='', source='gold'):
  systemConv = swapConllFields(['postag', 'lemma', 'feats', 'head', 'deprel'], ['ppostag', 'plemma', 'pfeats', 'phead', 'pdeprel'], remove=True);
  goldConv   = swapConllFields(['postag', 'lemma', 'feats', 'head', 'deprel'], ['postag', 'lemma', 'feats', 'head', 'deprel'], remove=False);

  transformer  = goldConv if source == 'gold' else systemConv ;
  conll_sents  = sentences_from_conllfile(inputfile);
  nconll_sents = map(transformer, conll_sents);
  sentences_to_conllfile(outputfile, nconll_sents, fields=CONLL09_COLUMNS);
  return;

def toconll07(inputfile='', outputfile='', source=''):
  global FIELDS;
  if True or FIELDS == CONLL09_COLUMNS:
    systemConv = swapConllFields(['plemma', 'ppostag', 'ppostag', 'pfeats', 'phead', 'pdeprel'], ['lemma', 'postag', 'cpostag', 'feats', 'head', 'deprel'], remove=True);
    goldConv   = swapConllFields(['lemma', 'postag', 'postag', 'feats', 'head', 'deprel'], ['lemma', 'postag', 'cpostag', 'feats', 'head', 'deprel'], remove=False);
    blindConv  = swapConllFields(['plemma', 'ppostag', 'ppostag', 'pfeats'], ['lemma', 'postag', 'cpostag', 'feats'], remove=True);
  
  transformer  = goldConv if source == 'gold' else blindCov if source == 'blind' else systemConv ;
  conll_sents  = sentences_from_conllfile(inputfile);
  nconll_sents = map(transformer, conll_sents);
  sentences_to_conllfile(outputfile, nconll_sents, fields=CONLL07_COLUMNS);
  return;

def toconllu(inputfile='', outputfile='', source=''):
  global FIELDS;
  if FIELDS == CONLL09_COLUMNS:
    systemConv = swapConllFields(['plemma', 'ppostag', 'ppostag', 'pfeats', 'phead', 'pdeprel'], ['lemma', 'postag', 'xpostag', 'feats', 'head', 'deprel'], remove=True);
    goldConv   = swapConllFields(['lemma', 'postag', 'postag', 'feats', 'head', 'deprel'], ['lemma', 'postag', 'xpostag', 'feats', 'head', 'deprel'], remove=False);
    blindConv  = swapConllFields(['plemma', 'ppostag', 'ppostag', 'pfeats'], ['lemma', 'postag', 'xpostag', 'feats'], remove=True);
  elif FIELDS == CONLL07_COLUMNS:
    systemConv = swapConllFields(['cpostag', 'postag'], ['postag', 'xpostag'], remove=False);
    goldConv   = swapConllFields(['cpostag', 'postag'], ['postag', 'xpostag'], remove=False);
    blindConv  = swapConllFields(['cpostag', 'postag'], ['postag', 'xpostag'], remove=False);
  
  transformer  = goldConv if source == 'gold' else blindCov if source == 'blind' else systemConv ;
  conll_sents  = sentences_from_conllfile(inputfile);
  nconll_sents = map(transformer, conll_sents);
  sentences_to_conllfile(outputfile, nconll_sents, fields=CONLLU_COLUMNS);
  return;

def tokenized_to_sentences(sentences):
  global FIELDS;
  for sent_idx, sent in enumerate(sentences, start=1):
    if not sent.strip():
      continue;
    tokens = re.split('\s+', sent.strip());
    if not len(tokens):
      print('warning: empty sentence at %d' %(sent_idx), file=stderr);
      continue;
    conll_sent = [defaultdict(lambda: '_', {'form': tok, 'id': str(tok_idx)})
        for tok_idx, tok in enumerate(tokens, start=1)];
    yield ("#metainfo: {0}".format(sent.strip()), conll_sent);


# -- Higher-level functions to be accessed from other functions

def sentences_from_conllfile(filename, fields=None):
  if not fields:
    global FIELDS;
    fields = FIELDS;
  lines = lines_from_file(filename);
  return sentences_from_conll(lines, fields=fields);

def sentences_to_conllfile(filename, sentences, fields=None):
  if not fields:
    global FIELDS;
    fields = FIELDS;
  return lines_to_file(filename, sentences_to_conll(sentences, fields=fields));

def readLexicon(wordclasses):
  lines = lines_from_file(wordclasses);
  lexicon = map(lambda X: tuple(re.split(WSPAT, X, maxsplit=1)), lines);
  lexicon = map(lambda pair: (pair[0], re.sub('\s+', '#', pair[1]).replace(':', '_')), lexicon);
  lexicon = dict(lexicon);
  lexicon = defaultdict(lambda: lexicon['<RARE>'], lexicon);
  return lexicon;

def addClasses(lexicon):
  def worker(conll_sent):
    if type(conll_sent) == type(()) and len(conll_sent) == 2:
      meta_info  = conll_sent[0];
      conll_sent = conll_sent[1];
    else:
      meta_info  = '';
    
    for edge in conll_sent:
      edge['CLASS'] = lexicon[edge['form'].lower()];
    return (meta_info, conll_sent);
  return worker;

def prepare_lemming_data(inputfile='', sentsfile='', outputfile='', lexicon=''):
  conll_sents  = sentences_from_conllfile(inputfile);
  if lexicon.strip():
    classes = readLexicon(lexicon);
    transformer = addClasses(classes);
    nconll_sents = map(transformer, conll_sents);
  else:
    nconll_sents = conll_sents;

  with smart_open(outputfile, 'w') as cfile, smart_open(sentsfile, 'w') as sfile:
    while True:
      buf = it.islice(nconll_sents, BUF_SIZE);
      buf = list(buf);
      meta_info = [item.replace('\n', '_EOS_') for (item, sent) in buf];
      sents = [sent for (item, sent) in buf];
      for s in meta_info:
        print(s, file=sfile);
      for s in sentences_to_conll(sents, fields=('id', 'form', 'CLASS')):
        print(s, file=cfile);

      if len(buf) < BUF_SIZE:
        break;
  
  #sentences_to_conllfile(outputfile, nconll_sents, fields=('id', 'form', 'CLASS'));
  return;

def prepare_mate_data(inputfile='', outputfile=''):
  global CONLL09_COLUMNS;
  conll_sents = sentences_from_conllfile(inputfile, fields=CONLL09_COLUMNS);
  sentences_to_conllfile(outputfile, conll_sents, fields=CONLL09_COLUMNS);

def prepare_stanford_data(inputfile='', outputfile=''):
  global FIELDS;
  FIELDS = CONLL09_COLUMNS;
  toconllu(inputfile, outputfile, source='system');
  return;


def reorganize_data(inputfile='', sentsfile='', outputfile=''):
  global FIELDS;
  toconllu(inputfile, outputfile, source='system');
  return;

def prepare_lemming(inputfile='', outputfile='', lexicon=''):
  conll_sents  = sentences_from_conllfile(inputfile);
  if lexicon.strip():
    classes = readLexicon(lexicon);
    transformer = addClasses(classes);
    nconll_sents = map(transformer, conll_sents);
  else:
    nconll_sents = conll_sents;

  sentences_to_conllfile(outputfile, nconll_sents, fields=('id', 'form', 'lemma', 'postag', 'feats', 'CLASS'));
  return;

def prepare_conllinput(inputfile='', outputfile=''):
  sents = list(lines_from_file(inputfile));
  conll_sents = tokenized_to_sentences(sents);
  sentences_to_conllfile(outputfile, conll_sents, fields=CONLLU_COLUMNS);
  return;

def cmdLineParser():
  argparser = argparse.ArgumentParser(prog='prepare_data.py', description='');
  argparser.add_argument('-t', '--task', dest='task', required=True, help='');
  argparser.add_argument('-i', '--input', dest='inputfile', nargs='?', default='', help='');
  argparser.add_argument('-o', '--output', dest='outputfile', nargs='?', default='', help='');
  argparser.add_argument('-s', '--sents', dest='sentsfile', default='', help='');
  argparser.add_argument('-c', '--classes', dest='classesfile', default='', help='');
  return argparser;

if __name__ == '__main__':
  env = cmdLineParser().parse_args(sysargv[1:]);
  env.inputfile = '' if env.inputfile == '_NONE_' else env.inputfile;
  env.outputfile = '' if env.outputfile == '_NONE_' else env.outputfile;
  env.inputfile = '' if not env.inputfile else env.inputfile;
  env.outputfile = '' if not env.outputfile else env.outputfile;
  if env.task == 'totsv':
    prepare_lemming_data(inputfile=env.inputfile, \
        sentsfile=env.sentsfile, \
        outputfile=env.outputfile, \
        lexicon=env.classesfile);
  elif env.task == '9toconllu':
    FIELDS = CONLL09_COLUMNS;
    reorganize_data(inputfile=env.inputfile, \
        sentsfile=env.sentsfile, \
        outputfile=env.outputfile);
  elif env.task == '7toconllu':
    FIELDS = CONLL07_COLUMNS;
    reorganize_data(inputfile=env.inputfile, \
        sentsfile=env.sentsfile, \
        outputfile=env.outputfile);
  elif env.task == 'traintagger':
    prepare_lemming(inputfile=env.inputfile, \
        outputfile=env.outputfile, \
        lexicon=env.classesfile);
  elif env.task == 'prepmate':
    prepare_mate_data(inputfile=env.inputfile, \
        outputfile=env.outputfile);
  elif env.task == 'prepstan':
    prepare_stanford_data(inputfile=env.inputfile, \
        outputfile=env.outputfile);
  elif env.task == 'tokenize':
    prepare_conllinput(inputfile=env.inputfile, \
        outputfile=env.outputfile);
