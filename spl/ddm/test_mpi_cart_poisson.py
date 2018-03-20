import numpy as np
import h5py
from mpi4py   import MPI
from mpi_cart import MPICart2D

#===============================================================================
# INPUT PARAMETERS
#===============================================================================

# Number of elements
n1 = 20
n2 = 20

# Padding (ghost region size)
p1 = 2
p2 = 2

# number of derivatives
d1 = 1
d2 = 1

verbose = False
#verbose = True
# ...

# ...
npts    = [n1+1 ,n2+1 ]
pads    = [p1   ,p2   ]
periods = [False,False]
reorder =  False
# ...

# 2nd-order finite difference coefficients for Laplacian operator on uniform grid
hx = 1.0 / n1
hy = 1.0 / n2
coef = [(0.5*hx**2*hy**2)/(hx**2+hy**2), 1.0/hx**2, 1.0/hy**2]

# Manufactured solution for $\phi_{xx} + \phi_{yy} = -\rho$ with periodic BCs:
# Choose \phi and calculate \rho
phi = lambda x,y: np.sin( np.pi*x ) * np.sin( np.pi*y )
rho = lambda x,y: (-2*np.pi**2)*phi( x, y )

# Parameters for iterative solver: tolerance and maximum number of iterations
tol     = 1e-8
maxiter = 10000

#===============================================================================
# PARALLEL OBJECTS
#===============================================================================

# MPI Communicator
comm = MPI.COMM_WORLD

# New communicator with 2D Cartesian topology
mesh = MPICart2D( npts, pads, periods, reorder, comm )

# Local mesh information
s1,s2 = mesh.starts
e1,e2 = mesh.ends
p1,p2 = mesh.pads  # NOTE: we already have these values...

# Local 1D grids with ghost regions
x1 = np.arange( s1-p1, e1+p1+1 ) * hx
x2 = np.arange( s2-p2, e2+p2+1 ) * hy

# Number of elements in extended mesh
l1 = len( x1 )
l2 = len( x2 )

# Create local arrays
u     = np.zeros( (l1,l2) )  # satisfies BCs
u_new = np.zeros( (l1,l2) )  # satisfies BCs
u_ex  = phi( *np.meshgrid( x1, x2, indexing='ij' ) )
f     = rho( *np.meshgrid( x1, x2, indexing='ij' ) )

#===============================================================================
# DEBUG
#===============================================================================

# for k in range( comm.Get_size() ):
#     rank = comm.Get_rank()
#     if comm.Get_rank() == k:
#         print("==========================")
#         print( "RANK = {}".format( rank ) )
#         print("==========================")
#         print( " . l1 = ", l1 )
#         print( " . l2 = ", l2 )
#         print( " . x1 = ", x1 )
#         print( " . x2 = ", x2 )
#         print( " . r1 = ", list( mesh.grids[0] ) )
#         print( " . r2 = ", list( mesh.grids[1] ) )
#         print( " . r1_ext = ", list( mesh.extended_grids[0] ) )
#         print( " . r2_ext = ", list( mesh.extended_grids[1] ) )
#         print( "", flush=True )
#     comm.Barrier()

#===============================================================================
# SOLUTION: Jacobi iteration
#===============================================================================

n = 0
converged = False

while not converged and n < maxiter:

    # Increment counter
    n += 1

    # Swap references
    u_old = u
    u     = u_new
    u_new = u_old

    # Exchange data
    mesh.communicate( u )

    # Jacobi iteration
    for i1 in range(p1,l1-p1):
        for i2 in range(p2,l2-p2):
            u_new[i1,i2] = \
                coef[0] * ( coef[1] * (u[i1+1,i2  ] + u[i1-1,i2  ]) \
                          + coef[2] * (u[i1  ,i2+1] + u[i1  ,i2-1]) \
                          - f[i1,i2] )

    # Reinforce BCs
    if s1 == 0 :  u_new[ p1  ,:] = 0.0
    if e1 == n1:  u_new[-p1-1,:] = 0.0
    if s2 == 0 :  u_new[:, p2  ] = 0.0
    if e2 == n2:  u_new[:,-p2-1] = 0.0

    # Calculate maximum absolute difference between new and old solutions
    diff = abs( u[p1:-p1,p2:-p2] - u_new[p1:-p1,p2:-p2] ).max()
    diff = comm.allreduce( diff, op=MPI.MAX )
    converged = (diff <= tol)

    if verbose and comm.Get_rank() is 0:
        print( " {:4d} {:12.2e}".format( n, diff ) )

if comm.Get_rank() == 0:
    print()
    if converged:
        print( "Jacobi iteration converged after {} iterations.".format( n ) )
    else:
        print( "Jacobi iteration could not converge within {} iterations".format( maxiter ) )

u = u_new

#===============================================================================
# CHECK ERROR
#===============================================================================

error  = u[p1:-p1,p2:-p2] - u_ex[p1:-p1,p2:-p2]

error_max_norm = comm.allreduce( abs( error ).max(), op=MPI.MAX )
error_l2_norm  = np.sqrt( comm.allreduce( (error**2).sum(), op=MPI.SUM ) * hx*hy )

if comm.Get_rank() == 0:
    print( "Max-norm or error = {:.2e}".format( error_max_norm ) )
    print( "L_2-norm or error = {:.2e}".format( error_l2_norm  ) )
    print( "" )

#===============================================================================
# WRITE NUMERICAL AND EXACT SOLUTIONS TO FILE
#===============================================================================

# Master process removes all files
if comm.Get_rank() == 0:
    import glob
    import os
    filelist = glob.glob( "solution_(*).h5" )
    for f in filelist:
        os.remove( f )

comm.Barrier()

# Each process writes one file
h5 = h5py.File( "solution_({:d},{:d}).h5".format( *mesh.coords ), mode='w' )
h5['u']      = u   [p1:-p1,p2:-p2]
h5['u_ex']   = u_ex[p1:-p1,p2:-p2]
h5['starts'] = mesh.starts
h5['ends']   = mesh.ends
h5.close()
