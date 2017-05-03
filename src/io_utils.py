#!/usr/bin/env python3

import itertools as it;
import re; 

class ConLLBuffer(object):
  CONLL07_COLUMNS = (
      'id', 'form', 'lemma',
      'cpostag', 'postag', 'feats',
      'head', 'deprel',
      'phead', 'pdeprel',
      );
  CONLL09_COLUMNS = (
      'id', 'form', 'lemma', 'plemma',
      'postag', 'ppostag', 'feats', 'pfeats',
      'head', 'phead', 'deprel', 'pdeprel', 
      'fillpred', 'sense',
      );
  CONLLU_COLUMNS = (
      'id', 'form', 'lemma', 
      'upostag', 'xpostag', 'feats', 
      'head', 'deprel', 
      'deps', 'misc',
      );
  CoNLLFormats = {
      'conll07': CONLL07_COLUMNS, 
      'conll09': CONLL09_COLUMNS, 
      'conllu' : CONLLU_COLUMNS
      }

  def __init__(self, cformat=None):
    if cformat in CoNLLFormats.keys():
      self.__fields = CoNLLFormats[cformat];
      self.__format = cformat;
      self.__buffer = [];
      self.__ibuffer = iter(self.__buffer);
    else:
      raise "FormatError", "Unknown CoNLL format";

  def addToBuffer(self, conll_sents, lazy=True):
    self.__ibuffer = it.chain(self.__ibuffer, conll_sents);
    if not lazy:
      self.__buffer = list(self.__ibuffer);
    else:
      self.__buffer = self.__ibuffer;

  def asconll07(self, system=True):
    if self.__format == 'conll07':
      return self.__ibuffer;
    else:
      if system:  # this is output from a system;
        cmap = [idx for f07 in CoNLLFormats['conll07'] for idx, f in enumerate(self.__fields) if f==f07];


      
      else:


class ConllIO(object):
  CONLLU_COLUMNS = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'];
  TAB_CHAR = '\t';

  def __init__(self, fields=None):
    self.__FIELDS = list(fields) if fields else CONLLU_COLUMNS;
    self.__C2I = dict((col, colidx) for colidx, col in enumerate(self.__FIELDS));
    self.__isConllu = True if fields == CONLLU_COLUMNS else False;  
  
  def __lines_from_conll(lines):
    for line in lines:
      if not line.strip():
        return;
      yield line.strip();

  def __nodes_from_conllu(self, lines):
    def isMultiWord(x): return re.match('^[0-9]+?-[0-9]+?$', x);
    for line in lines:
      entries = re.split(TAB_CHAR, line);
      if isMultiWord(entries[0]):
        continue;
      node = [None]*len(self.__FIELDS);
      for key, value in zip(self.__FIELDS, entries):
        node[self.__C2I[key]] = value if value != '_' else node[self.__C2I[key]];
      yield node;

  def __nodes_from_conll(self, lines):
    for line in lines:
      entries = re.split(TAB_CHAR, line);
      node = [None]*len(self.__FIELDS);
      for key, value in zip(self.__FIELDS, entries):
        node[self.__C2I[key]] = value if value != '_' else node[self.__C2I[key]];
      yield node;

  def __nodes_to_conllu(self, conll_sent):
    return '\n'.join('\t'.join(edge[self.__C2I[field]] for field in CONLLU_COLUMNS) for edge in conll_sent);

  def __nodes_to_conll(self, conll_sent, fields):
    return '\n'.join('\t'.join(edge[self.__C2I[field]] for field in fields) for edge in conll_sent);

  def sentences_from_conll(self, stream, comments=True):
    sent_count = 0;
    node_parser = self.__nodes_from_conllu if self.__FIELDS == CONLLU_COLUMNS else self.__nodes_from_conll ;
    while True:
      lines = tuple(lines_from_conll(stream));
      if not len(lines):
        break;
      sent_count += 1;
      if comments:
        comm_lines = it.takewhile(lambda X: X.startswith('#'), lines);
        comm_lines = '\n'.join(comm_lines);
        conll_lines = it.dropwhile(lambda X: X.startswith('#'), lines);
      else:
        comm_lines = '# ';
        conll_lines = lines;
      tree = list(node_parser(conll_lines));
      yield (comm_lines, tree);

  def sentences_to_conll(self, stream, conll_sents, comments=True, fields=CONLLU_COLUMNS):
    sent_count = 0;
    for meta_data, sent in conll_sents:
      yield meta_data;
      yield self.__nodes_to_conll(sent);
      yield "";

  def sentences_from_files(self, *filesList):
    for filepath in filesList:
      with open(filepath, mode='r', encoding='utf-8') as infile:
        for (meta_info, sentence) in self.sentences_from_conll(infile):
          yield (meta_info, sentence);

  def sentences_to_file(self, conll_sents, outputFile):
    with open(outputFile, mode='w', encoding='utf-8') as outfile:
      for str_buf in self.sentences_to_conll(conll_sents):
        print(str_buf, file=outfile);
    return;

class WordClasses(dict):
  def __init__(self, classes=None, classesfile=None):
    self.__embedding = classes if classes else {};
    if not classes and classesfile:
      with open(classesfile, mode='r', encoding='utf-8') as infile:
        for line in infile:
          word, classes = re.split('\s+', line, 1);
          self.__embedding[word] = tuple(re.split('\s+', classes));
