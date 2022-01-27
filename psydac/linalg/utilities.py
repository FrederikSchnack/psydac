# coding: utf-8

import numpy as np
from math                  import sqrt
from psydac.linalg.stencil import StencilVectorSpace, StencilVector
from psydac.linalg.block   import BlockVector, BlockVectorSpace

__all__ = ['array_to_stencil', '_sym_ortho']

def array_to_stencil(x, Xh):
    """ converts a numpy array to StencilVector or BlockVector format"""

    if isinstance(Xh, BlockVectorSpace):
        u = BlockVector(Xh)
        if isinstance(Xh.spaces[0], BlockVectorSpace):
            for d in range(len(Xh.spaces)):
                starts = [np.array(V.starts) for V in Xh.spaces[d].spaces]
                ends   = [np.array(V.ends)   for V in Xh.spaces[d].spaces]

                for i in range(len(starts)):
                    g = tuple(slice(s,e+1) for s,e in zip(starts[i], ends[i]))
                    shape = tuple(ends[i]-starts[i]+1)
                    u[d][i][g] = x[:np.product(shape)].reshape(shape)
                    x       = x[np.product(shape):]

        else:
            starts = [np.array(V.starts) for V in Xh.spaces]
            ends   = [np.array(V.ends)   for V in Xh.spaces]

            for i in range(len(starts)):
                g = tuple(slice(s,e+1) for s,e in zip(starts[i], ends[i]))
                shape = tuple(ends[i]-starts[i]+1)
                u[i][g] = x[:np.product(shape)].reshape(shape)
                x       = x[np.product(shape):]

    elif isinstance(Xh, StencilVectorSpace):

        u =  StencilVector(Xh)
        starts = np.array(Xh.starts)
        ends   = np.array(Xh.ends)
        g = tuple(slice(s, e+1) for s,e in zip(starts, ends))
        shape = tuple(ends-starts+1)
        u[g] = x[:np.product(shape)].reshape(shape)
    else:
        raise ValueError('Xh must be a StencilVectorSpace or a BlockVectorSpace')

    u.update_ghost_regions()
    return u

def petsc_to_stencil(x, Xh):
    """ converts a numpy array to StencilVector or BlockVector format"""
    x = x.array
    u = array_to_stencil(x, Xh)
    return u

def _sym_ortho(a, b):
    """
    Stable implementation of Givens rotation.
    This function was taken from the scipy repository
    https://github.com/scipy/scipy/blob/master/scipy/sparse/linalg/isolve/lsqr.py

    Notes
    -----
    The routine 'SymOrtho' was added for numerical stability. This is
    recommended by S.-C. Choi in [1]_.  It removes the unpleasant potential of
    ``1/eps`` in some important places (see, for example text following
    "Compute the next plane rotation Qk" in minres.py).

    References
    ----------
    .. [1] S.-C. Choi, "Iterative Methods for Singular Linear Equations
           and Least-Squares Problems", Dissertation,
           http://www.stanford.edu/group/SOL/dissertations/sou-cheng-choi-thesis.pdf
    """
    if b == 0:
        return np.sign(a), 0, abs(a)
    elif a == 0:
        return 0, np.sign(b), abs(b)
    elif abs(b) > abs(a):
        tau = a / b
        s = np.sign(b) / sqrt(1 + tau * tau)
        c = s * tau
        r = b / s
    else:
        tau = b / a
        c = np.sign(a) / sqrt(1+tau*tau)
        s = c * tau
        r = a / c
    return c, s, r
