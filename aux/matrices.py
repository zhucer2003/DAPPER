from common import *

# Also recommend the package "rogues",
# which replicates Matlab's matrix gallery.

try:
  from magic_square import magic
except ImportError:
  pass


def randcov(m):
  """(Makeshift) random cov mat
  (which is missing from rogues)"""
  N = int(ceil(2+m**1.2))
  E = randn((N,m))
  return E.T @ E
def randcorr(m):
  """(Makeshift) random corr mat
  (which is missing from rogues)"""
  Cov  = randcov(m)
  Dm12 = diag(diag(Cov)**(-0.5))
  return Dm12@Cov@Dm12


def genOG(m):
  """Generate random orthonormal matrix."""
  Q,R = nla.qr(randn((m,m)))
  for i in range(m):
    if R[i,i] < 0:
      Q[:,i] = -Q[:,i]
  return Q

def genOG_1(N):
  """Random orthonormal mean-preserving matrix.
  Source: ienks code of Sakov/Bocquet."""
  e = ones((N,1))
  V = nla.svd(e)[0] # Basis whose first vector is e
  Q = genOG(N-1)     # Orthogonal mat
  return V @ sla.block_diag(1,Q) @ V.T



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



class CovMat:
  '''
  A positive-semi-def matrix class.
  '''
  def __init__(self,data,kind='C'):
    if kind in ('C12','sqrtm','ssqrt'):
      C = data.dot(data.T)
      kind = 'C'
    elif is1d(data) and data.size > 1:
      kind = 'diag'
    if kind is 'C':
      C    = data
      m    = data.shape[0]
      d,U  = eigh(data)
      d    = np.maximum(d,0)
      rk   = (d>0).sum()
    elif kind is 'diag':
      data  = asarray(data)
      assert is1d(data)
      #d,U = eigh(diag(data))
      C     = diag(data)
      m     = len(data)
      rk    = (data>0).sum()
      sInds = np.argsort(data)
      d,U   = zeros(m), zeros((m,m))
      for i in range(m):
        U[sInds[i],i] = 1
        d[i] = data[sInds[i]]
    else: raise TypeError

    self.C  = C
    self.U  = U
    self.d  = d
    self.m  = m
    self.rk = rk

  def transform_by(self,f,decomp='full'):
    if decomp is 'full':
      U = self.U
      d = self.d
    else:
      d = self.d[  -self.rk:]
      U = self.U[:,-self.rk:]
    return (U * f(d)) @ U.T

  @lazy_property
  def ssqrt(self):
    return self.transform_by(np.sqrt,'econ')

  @lazy_property
  def inv(self):
    return self.transform_by(lambda x: 1/x)

  @lazy_property
  def m12(self):
    return self.transform_by(lambda x: 1/np.sqrt(x),'econ')

  @property
  def cholL(self):
    # L = sla.cholesky(self.C,lower=True)
    # C = L @ L.T
    return self.ssqrt

  @property
  def cholU(self):
    # U = sla.cholesky(self.C,lower=False)
    # C = U.T @ U
    return self.ssqrt

  def __str__(self):
    return str(self.C)
  def __repr__(self):
      return self.__str__()

from scipy import sparse as sprs
class spCovMat():
  '''
  Sparse version of CovMat.
  Careful: if is_sprs it will yield sparse **matrices**,
           which interpret '*' as dot().
  '''
  def __init__(self,C=None,C12=None,ssqrtm=None,E=None,A=None,diagnl=None,trunc=0.99):

    inpt = [C,C12,ssqrtm,E,A,diagnl]
    has_no_None = False
    for arg in inpt:
      if arg is not None:
        if has_no_None:
          raise ValueError('Too many inputs')
        else:
          has_no_None = True
    assert 0 < trunc <= 1

    is_sprs  = False
    if E is not None:
      mu       = np.mean(E,0)
      A        = E - mu
    if A is not None:
      N        = A.shape[0]
      C12      = A.T / sqrt(N-1)
    if ssqrtm is not None:
      C12      = ssqrtm
    if C12 is not None:
      m        = C12.shape[0]
      U,d12,VT = svd(C12,full_matrices=False)
      d        = d12**2
    elif C is not None:
      C        = np.atleast_2d(C)
      m        = C.shape[0]
      assert     C.shape[1] == m
      d,U      = eigh(C)
      d        = np.flipud(d)
      U        = np.fliplr(U)
    elif diagnl is not None:
      is_sprs  = True
      d        = np.atleast_1d(diagnl)
      assert     is1d(d)
      m        = len(d)
      sInds    = arange(m) if np.all(d == d[0]) else np.argsort(d)[::-1] 
      d        = d[sInds]
      U        = sprs.csr_matrix((ones(m),(sInds,arange(m))))
    else: raise TypeError('Input missing')

    assert np.all(np.isreal(d)) and np.all(d>=0)
    assert np.all(np.isreal(U))

    rk = (d > 1e-13*mean(d)).sum()
    if trunc < 1:
      rk = 1 + find_1st_ind(np.cumsum(d)>=trunc*sum(d))

    self._U      = U[:,:rk]
    self._d      = d[  :rk]
    self.m       = m
    self.rk      = rk
    self.is_sprs = is_sprs

  def transform_by(self,fun):
    d  = self._d
    U  = self._U
    if self.is_sprs:
      return (U @ sprs.diags(fun(d))) @ U.T
    else:
      return (U * fun(d)) @ U.T

  @lazy_property
  def diagonal(self):
    d = zeros(self.m)
    for i in range(self.m):
      if self.is_sprs:
        d[i] = Uii_2 = self._U[i,:].power(2) * self._d
      else:
        d[i] = Uii_2 = self._U[i,:]**2       @ self._d
    return d

  @lazy_property
  def C(self):
    return self.transform_by(lambda x: x)

  @lazy_property
  def inv(self):
    return self.transform_by(lambda x: 1/x)

  @lazy_property
  def ssqrt(self):
    return self.transform_by(np.sqrt)

  @lazy_property
  def m12(self):
    return self.transform_by(lambda x: 1/np.sqrt(x))

  @property
  def cholL(self):
    # with sla.cholesky(self.C,lower=True) as L:
    #   C = L @ L.T
    d  = self._d
    U  = self._U
    if self.is_sprs:
      return U @ sprs.diags(np.sqrt(d))
    else:
      return U * np.sqrt(d)

  @property
  def cholU(self):
    # with sla.cholesky(self.C,lower=False) as U:
    #   C = U.T @ U
    return self.cholL.T

  def __repr__(self):
    repr_dict = { k: vars(self)[k] for k in ['m','rk','is_sprs'] }
    from pprint import pformat
    s = "<" + type(self).__name__ + ">\n" + pformat(repr_dict, width=1)
    s += '\ndiagonal: ' + str(self.diagonal)
    return s


# Rationale: __matmul__ works fine for myCovMat @ ndarray
# but not ndarray @ myCovMat.
def cvMult(A,B):
  is_transposed = False
  if type(B) is spCovMat and type(A) is np.ndarray:
    A, B = B, A.T
    # don't need to tranpose B, coz it's sym.
    is_transposed = True
  if type(A) is spCovMat:
    assert type(B) is np.ndarray
    U = A._U
    d = A._d
    if A.is_sprs:
      result =  U @ ( sprs.diags(d) @ (U.T @ B) )
    else:
      result = (U * d) @ (U.T @ B)
  else:
    raise TypeError
  if is_transposed:
    result = result.T
  return result





def funm_psd(a, fun, check_finite=False):
  """
  Matrix function evaluation for pos-sem-def mat.
  Adapted from sla.funm() doc.
  e.g.
  def sqrtm_psd(A):
    return funm_psd(A, np.sqrt)
  """
  w, v = eigh(a, check_finite=check_finite)
  w = np.maximum(w, 0)
  w = fun(w)
  return (v * w) @ v.T




