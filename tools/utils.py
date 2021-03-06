# Utilities (non-math)

from common import *

#########################################
# Progressbar
#########################################
def noobar(itrble, desc):
  """Simple progress bar. To be used if tqdm not installed."""
  L  = len(itrble)
  print('{}: {: >2d}'.format(desc,0), end='')
  for k,i in enumerate(itrble):
    yield i
    p = (k+1)/L
    e = '' if k<(L-1) else '\n'
    print('\b\b\b\b {: >2d}%'.format(int(100*p)), end=e)
    sys.stdout.flush()

# Get progbar description by inspecting caller function.
import inspect
def pdesc(desc):
  if desc is not None:
    return desc
  try:
    #stackoverflow.com/q/15608987
    DAC_name  = inspect.stack()[3].frame.f_locals['name_hook']
  except (KeyError, AttributeError):
    #stackoverflow.com/a/900404
    DAC_name  = inspect.stack()[2].function
  return DAC_name 

# Define progbar as tqdm or noobar
try:
  import tqdm
  if is_notebook:
    def progbar(inds, desc=None, leave=1):
      return tqdm.tqdm_notebook(inds,desc=pdesc(desc),leave=leave)
  else:
    def progbar(inds, desc=None, leave=1):
      return tqdm.tqdm(inds,desc=pdesc(desc),leave=leave,
          smoothing=0.3,dynamic_ncols=True)
except ImportError as err:
  install_warn(err)
  def progbar(inds, desc=None, leave=1):
    return noobar(inds,desc=pdesc(desc))




#########################################
# Console input / output
#########################################

#stackoverflow.com/q/292095
import select
def poll_input():
  i,o,e = select.select([sys.stdin],[],[],0.0001)
  for s in i: # Only happens if <Enter> has been pressed
    if s == sys.stdin:
      return sys.stdin.readline()
  return None

# Can't get thread solution working (in combination with getch()):
# stackoverflow.com/a/25442391/38281

# stackoverflow.com/a/21659588/38281
# (Wait for) any key:
def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch
    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    return _getch
getch = _find_getch()



# Terminal color codes. Use:
termcolors={
    'blue'      : '\033[94m',
    'green'     : '\033[92m',
    'OKblue'    : '\033[94m',
    'OKgreen'   : '\033[92m',
    'WARNING'   : '\033[93m',
    'FAIL'      : '\033[91m',
    'ENDC'      : '\033[0m' ,
    'header'    : '\033[95m',
    'bold'      : '\033[1m' ,
    'underline' : '\033[4m' ,
}

def print_c(*kargs,color='blue',**kwargs):
  s = ' '.join([str(k) for k in kargs])
  print(termcolors[color] + s + termcolors['ENDC'],**kwargs)


# Local np.set_printoptions. stackoverflow.com/a/2891805/38281
import contextlib
@contextlib.contextmanager
def printoptions(*args, **kwargs):
    original = np.get_printoptions()
    np.set_printoptions(*args, **kwargs)
    yield 
    np.set_printoptions(**original)


import tools.tabulate as tabulate_orig
tabulate_orig.MIN_PADDING = 0
def tabulate(data,headr=(),formatters=(),inds='nice'):
  """Pre-processor for tabulate().
  data:  list-of-lists, whose 'rows' will be printed as columns.
         This coincides with the output of Dict.values().
  headr: list or tuple.
  If 'data' is a dict, then the keys will be the headr.
  formatter: define formats to apply before relaying to pandas.
        Default: attr.__name__ (when applicable).
  Example:
  >>> print(tabulate(cfgs.distinct_attrs()))
  """

  # Extract headr/mattr
  if hasattr(data,'keys'):
    headr = list(data)
    data  = data.values()

  # Default formats
  if not formatters:
    formatters = ({
        'test'  : lambda x: hasattr(x,'__name__'),
        'format': lambda x: x.__name__
        },)
  # Apply formatting (if not applicable, data is just forwarded)
  for f in formatters:
    data = [[f['format'](j) for j in row] if f['test'](row[0]) else row for row in data]

  # Transpose
  data  = list(map(list, zip(*data)))

  # Generate nice indices
  if inds=='nice':
    inds = ['[{}]'.format(d) for d in range(len(data))]
  else:
    pass # Should be True or False

  return tabulate_orig.tabulate(data,headr,showindex=inds)



def repr_type_and_name(thing):
  """Print thing's type [and name]"""
  s = "<" + type(thing).__name__ + '>'
  if hasattr(thing,'name'):
    s += ': ' + thing.name
  return s

class MLR_Print:
  """
  Multi-Line, Recursive repr (print) functionality.
  Set class variables to change look:
   - 'indent': indentation per level
   - 'ch': character to use for "spine" (e.g. '|' or ' ')
   - 'ordr_by_linenum': 0: alphabetically, 1: linenumbr, -1: reverse
  """
  indent=3
  ch='.'
  ordr_by_linenum = 0

  # numpy print options
  threshold=10
  precision=None

  # Recursion monitoring.
  _stack=[] # Reference using MLR_Print._stack, ...
  # not self._stack or self.__class__, which reference sub-class "instance".

  # Reference using self.excluded, to access sub-class "instance".
  excluded = [] # Don't include in printing
  excluded.append(re.compile('^_')) # "Private"
  excluded.append('name') # Treated separately

  included = []
  aliases  = {}

  def __repr__(self):
    with printoptions(threshold=self.threshold,precision=self.precision):
      # new line chars
      NL = '\n' + self.ch + ' '*(self.indent-1)

      # Infinite recursion prevention
      is_top_level = False
      if MLR_Print._stack == []:
        is_top_level = True
      if self in MLR_Print._stack:
        return "**Recursion**"
      MLR_Print._stack += [self]

      # Use included or filter-out excluded
      keys = self.included or filter_out(vars(self), *self.excluded)

      # Process attribute repr's
      txts = {}
      for key in keys:
        t = repr(getattr(self,key)) # sub-repr
        if '\n' in t:
          # Activate multi-line printing
          t = t.replace('\n',NL+' '*self.indent) # other lines
          t = NL+' '*self.indent + t             # first line
        t = NL + self.aliases.get(key,key) + ': ' + t # key-name
        txts[key] = t

      def sortr(x):
        if self.ordr_by_linenum:
          return self.ordr_by_linenum*txts[x].count('\n')
        else:
          return x.lower()

      # Assemble string
      s = repr_type_and_name(self)
      for key in sorted(txts, key=sortr):
        s += txts[key]

      # Empty _stack when top-level printing finished
      if is_top_level:
        MLR_Print._stack = []

      return s


class AlignedDict(OrderedDict):
  """Provide aligned-printing for dict."""
  def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
  def __str__(self):
    L = max(len(s) for s in self.keys())
    s = " "
    for key in self.keys():
      s += key.rjust(L)+": "+repr(self[key])+"\n "
    s = s[:-2]
    return s
  def __repr__(self):
    return type(self).__name__ + "(**{\n " + str(self).replace("\n",",\n") + "\n})"
  def _repr_pretty_(self, p, cycle):
    # Is implemented by OrderedDict, so must overwrite.
    if cycle: p.text('{...}')
    else:     p.text(self.__repr__())
  
class Bunch(dict):
  def __init__(self,**kw):
    dict.__init__(self,kw)
    self.__dict__ = self


# From stackoverflow.com/q/22797580 and more
class NamedFunc():
  "Provides custom repr for functions."
  def __init__(self,_func,_repr):
    self._func = _func
    self._repr = _repr
    #functools.update_wrapper(self, _func)
  def __call__(self, *args, **kw):
    return self._func(*args, **kw)
  def __repr__(self):
    argnames = self._func.__code__.co_varnames[
      :self._func.__code__.co_argcount]
    argnames = "("+",".join(argnames)+")"
    return "<NamedFunc>"+argnames+": "+self._repr

class NameFunc():
  "Decorator version"
  def __init__(self,name):
     self.fn_name = name
  def __call__(self,fn):
      return NamedFunc(fn,self.fn_name)


#########################################
# Writing / Loading Independent experiments
#########################################

import glob
def find_last_v(dirpath):
  if not dirpath.endswith(os.path.sep):
    dirpath += os.path.sep
  ls = glob.glob(dirpath+'v*.npz')
  if ls == []:
    return 0
  #v = max([int(x.split(dirpath)[1].split('v')[1].split('_')[0]) for x in ls])
  v = max([int(re.search(dirpath + 'v([1-9]*).*\.npz',x).group(1)) for x in ls])
  return v

def rel_name(filepath,rel_to='./'):
  fn = os.path.relpath(filepath,rel_to)
  fn, ext = os.path.splitext(fn)
  return fn

from os import makedirs
def save_dir(filepath):
  """Make dir DAPPER/data/filepath_without_ext"""
  dirpath = 'data' + os.path.sep\
      + rel_name(filepath) + os.path.sep
  makedirs(dirpath, exist_ok=True)
  return dirpath

def parse_parallelization_args():
  """Get experiment version (v) and indices (inds) from command-line."""
  i_v    = sys.argv.index('save_path')+1
  i_inds = sys.argv.index('inds')+1
  assert i_v < i_inds
  save_path = sys.argv[i_v]
  inds   = sys.argv[i_inds:]
  inds   = [int(x) for x in inds]
  return save_path, inds

from subprocess import call
import time
def parallelize(script,inds,max_workers=4):
  save_path  = save_dir(script)
  v          = find_last_v(save_path) + 1
  v          = 'v' + str(v)
  save_path += v
  tmp        = 'tmp_' + v + '_t' + str(time.time())[-2:]
  with open(tmp,'w') as f:
    f.write('# Auto-generated for experiment parallelization.\n\n')
    f.write('source ~/.screenrc\n\n')
    for w in range(max_workers):
      iiw = [str(x) for x in inds[np.mod(inds,max_workers)==w]]
      f.write('screen -t exp_' + '_'.join(iiw) + ' python -i ' + script
          + ' save_path ' + save_path
          + ' inds ' + ' '.join(iiw) + '\n')
  sleep(0.2)
  call(['screen', '-S', v,'-c', tmp])
  sleep(0.2)
  os.remove(tmp)


def save_data(path,inds,**kwargs):
  path += '_inds_' + '_'.join([str(x) for x in inds])
  print('Saving to',path)
  np.savez(path,**kwargs)



#########################################
# Multiprocessing
#########################################
NPROC = 4
import multiprocessing, signal
def multiproc_map(func,xx,**kwargs):
  """
  Multiprocessing.
  Basically a wrapper for multiprocessing.pool.map(). Deals with
   - additional, fixed arguments.
   - KeyboardInterruption (python bug?)
  """
  # stackoverflow.com/a/35134329/38281
  orig = signal.signal(signal.SIGINT, signal.SIG_IGN)
  pool = multiprocessing.Pool(NPROC)
  signal.signal(signal.SIGINT, orig)
  try:
    # stackoverflow.com/a/5443941/38281
    f   = functools.partial(func,**kwargs)
    res = pool.map_async(f, xx)
    res = res.get(60)
  except KeyboardInterrupt as e:
    # Not sure why, but something this hangs,
    # so we repeat the try-block to catch another interrupt.
    try:
      traceback.print_tb(e.__traceback__)
      pool.terminate()
      sys.exit(0)
    except KeyboardInterrupt as e2:
      traceback.print_tb(e2.__traceback__)
      pool.terminate()
      sys.exit(0)
  else:
    pool.close()
  pool.join()
  return res



#########################################
# Tic-toc
#########################################

#import time
class Timer():
  """
  Usage:
  with Timer('<description>'):
    do_stuff()
  """
  def __init__(self, name=None):
      self.name = name

  def __enter__(self):
      self.tstart = time.time()

  def __exit__(self, type, value, traceback):
      #pass # Turn off timer messages
      if self.name:
          print('[%s]' % self.name, end='')
      print('Elapsed: %s' % (time.time() - self.tstart))





#########################################
# Misc
#########################################


def filter_out(orig_list,*unwanted):
  """
  Returns new list from orig_list with unwanted removed.
  Also supports re.search() by inputting a re.compile('patrn') among unwanted.
  """
  new = []
  for word in orig_list:
    for x in unwanted:
      try:
        # Regex compare
        rm = x.search(word)
      except AttributeError:
        # String compare
        rm = x==word
      # Insert
      if rm:
        break
    else:
      new.append(word)
  return new

def all_but_1_is_None(*args):
  "Check if only 1 of the items in list are Truthy"
  return sum(x is not None for x in args) == 1

# From stackoverflow.com/q/3012421
class lazy_property(object):
    '''
    Lazy evaluation of property.
    Should represent non-mutable data,
    as it replaces itself.
    '''
    def __init__(self,fget):
      self.fget = fget
      self.func_name = fget.__name__

    def __get__(self,obj,cls):
      value = self.fget(obj)
      setattr(obj,self.func_name,value)
      return value



class AssimFailedError(RuntimeError):
    pass

def raise_AFE(msg,time_index=None):
  if time_index is not None:
    msg += "\n(k,kObs,fau) = " + str(time_index) + ". "
  raise AssimFailedError(msg)


def vectorize0(f):
  """
  Vectorize f for its 1st (index 0) argument.

  Compared to np.vectorize:
    - less powerful, but safer to only vectorize 1st argument
    - doesn't evaluate the 1st item twice
    - doesn't always return array

  Example:
    @vectorize0
    def add(x,y):
      return x+y
    add(1,100)
    x = np.arange(6).reshape((3,-1))
    add(x,100)
    add([20,x],100)
  """
  @functools.wraps(f)
  def wrapped(x,*args,**kwargs):
    if hasattr(x,'__iter__'):
      out = [wrapped(xi,*args,**kwargs) for xi in x]
      if isinstance(x,np.ndarray):
        out = np.asarray(out)
      else:
        out = type(x)(out)
    else:
      out = f(x,*args,**kwargs)
    return out
  return wrapped


