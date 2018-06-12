# -*- coding: UTF-8 -*-

from spl.fem.basic   import FemField
from spl.fem.splines import SplineSpace
from spl.fem.tensor  import TensorFemSpace
from spl.fem.vector  import VectorFemSpace

from numpy import linspace


def test_1d_1():
    print ('>>> test_1d_1')

    knots = [0., 0., 0., 1., 1., 1.]
    p = 2
    V = SplineSpace(p, knots=knots)
    print (V)
    F = FemField(V,'F')

def test_1d_2():
    print ('>>> test_1d_2')

    p = 2
    grid = linspace(0., 1., 5)
    V = SplineSpace(p, grid=grid)
    print (V)
    F = FemField(V,'F')

def test_1d_3():
    print ('>>> test_1d_3')

    p = 2
    grid = linspace(0., 1., 5)
    V1 = SplineSpace(p, grid=grid)
    V2 = SplineSpace(p+1, grid=grid)
    V = VectorFemSpace(V1, V2)
    print (V)

def test_2d_1():
    print ('>>> test_2d_1')

    knots_1 = [0., 0., 0., 1., 1., 1.]
    knots_2 = [0., 0., 0., 0.5, 1., 1., 1.]
    p_1 = 2
    p_2 = 2
    V1 = SplineSpace(p_1, knots=knots_1)
    V2 = SplineSpace(p_2, knots=knots_2)

    V = TensorFemSpace(V1, V2)
    print (V)
    F = FemField(V,'F')

def test_2d_2():
    print ('>>> test_2d_2')

    p_1 = 2
    p_2 = 2
    grid_1 = linspace(0., 1., 3)
    grid_2 = linspace(0., 1., 5)
    V1 = SplineSpace(p_1, grid=grid_1)
    V2 = SplineSpace(p_2, grid=grid_2)

    V = TensorFemSpace(V1, V2)
    print (V)
    F = FemField(V,'F')

def test_2d_3():
    print ('>>> test_2d_3')

    p = 2
    grid_1 = linspace(0., 1., 3)
    grid_2 = linspace(0., 1., 5)

    # ... first component
    V1 = SplineSpace(p-1, grid=grid_1)
    V2 = SplineSpace(p, grid=grid_2)

    Vx = TensorFemSpace(V1, V2)
    # ...

    # ... second component
    V1 = SplineSpace(p, grid=grid_1)
    V2 = SplineSpace(p-1, grid=grid_2)

    Vy = TensorFemSpace(V1, V2)
    # ...

    V = VectorFemSpace(Vx, Vy)
    print (V)

def test_3d_1():
    print ('>>> test_3d_1')

    knots_1 = [0., 0., 0., 1., 1., 1.]
    knots_2 = [0., 0., 0., 0.5, 1., 1., 1.]
    knots_3 = [0., 0., 0.5, 1., 1.]
    p_1 = 2
    p_2 = 2
    p_3 = 1
    V1 = SplineSpace(p_1, knots=knots_1)
    V2 = SplineSpace(p_2, knots=knots_2)
    V3 = SplineSpace(p_3, knots=knots_3)

    V = TensorFemSpace(V1, V2, V3)
    print (V)
    F = FemField(V,'F')

def test_3d_2():
    print ('>>> test_3d_2')

    p_1 = 2
    p_2 = 2
    p_3 = 1
    grid_1 = linspace(0., 1., 3)
    grid_2 = linspace(0., 1., 5)
    grid_3 = linspace(0., 1., 7)
    V1 = SplineSpace(p_1, grid=grid_1)
    V2 = SplineSpace(p_2, grid=grid_2)
    V3 = SplineSpace(p_3, grid=grid_3)

    V = TensorFemSpace(V1, V2, V3)
    print (V)
    F = FemField(V,'F')

def test_3d_3():
    print ('>>> test_3d_3')

    p = 2
    grid_1 = linspace(0., 1., 3)
    grid_2 = linspace(0., 1., 5)
    grid_3 = linspace(0., 1., 7)

    # ... first component
    V1 = SplineSpace(p-1, grid=grid_1)
    V2 = SplineSpace(p, grid=grid_2)
    V3 = SplineSpace(p, grid=grid_3)

    Vx = TensorFemSpace(V1, V2, V3)
    # ...

    # ... second component
    V1 = SplineSpace(p, grid=grid_1)
    V2 = SplineSpace(p-1, grid=grid_2)
    V3 = SplineSpace(p, grid=grid_3)

    Vy = TensorFemSpace(V1, V2, V3)
    # ...

    # ... third component
    V1 = SplineSpace(p, grid=grid_1)
    V2 = SplineSpace(p, grid=grid_2)
    V3 = SplineSpace(p-1, grid=grid_3)

    Vz = TensorFemSpace(V1, V2, V3)
    # ...

    V = VectorFemSpace(Vx, Vy, Vz)
    print (V)


###############################################
if __name__ == '__main__':

    test_1d_1()
    test_1d_2()
    test_1d_3()

    test_2d_1()
    test_2d_2()
    test_2d_3()

    test_3d_1()
    test_3d_2()
    test_3d_3()
