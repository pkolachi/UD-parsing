#!/usr/bin/env python3

from collections import Iterator; 
import itertools as it;

class JToolBackend(object):
  def __init__(toolpath, args, javabin="java", bufsize=1000):
    self.__cmd = javabin;
    self.__binpath = toolpath;
    self.__args = args;
    self.__proc = None;
    self.__bufSize = bufsize;

  def startProcess(self):
    # check that self.__proc is None
    try:
      assert(not self.__proc);
    except AssertionError:
      self.__proc.kill();
    # Create a process and load the model
    self.__proc = Popen(self.cmd, self.args, shell=False);
    return;

  def stopProcess(self):
    # check that process has not been killed already
    try:
      assert(self.__proc not None);
      self.__proc.kill();
    except AssertionError:
      # failed to kill the subprocess;
      pass;
    finally:
      self.__proc = None;

  def __enter__(self):
    self.startProcess();
    return self.__proc;

  def __exit__(self):
    self.stopProcess();

  def run(self, inputstream, insep='\n', outsep=''):
    if not isinstance(inputstream, Iterator):
      inputstream = iter(inputstream);
    while True:
      inbuf  = it.slice(inputstream, self.__bufSize);
      inbuf  = list(inbuf);
      inbufs = insep.join(inbuf);
      self.__proc.communicate(inbuf_str);
      yield (outbufs, errbufs);
      if len(inbuf) < self.__bufSize:
        break;
    retcode = self.wait();
    if retcode < 0:
      raise ProcessKilledError, retcode ;
                                                                                    
