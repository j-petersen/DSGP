#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 23:18:31 2019

@author: jonpetersen
"""

import numpy as np
import tables



### With Pertubation
PERT    = False
### Perturbation with different initial states
INIT    = True


### pre setting
K = 8
J = 32
F = 10
h, c, b  = 1, 1, 1

d = 1e-9

title1 = "Lorenz96_XMode"
title2 = "Lorenz96_YMode"


### choose scheme
scheme = "RK"     # EF:Euler Forward, RK:Runge Kutta, RRK:Reduced Runge Kutta

def dX_val(X1,Y1,K1,J1):
    dX1 = np.zeros((K1+3))
    for k in range(2,K1+2):
        dX1[k] = - X1[k-1]*(X1[k-2]-X1[k+1]) - X1[k] + F - h*c/b * np.sum(Y1[(J1*(k-1)):k*J1])

    dX1[0] = dX1[-3]
    dX1[1] = dX1[-2]
    dX1[-1] = dX1[2]
    return(dX1)


def dY_val(X1,Y1,K1,J1):
    dY1= np.zeros(((K1*J1)+3))
    for j in range(1,(K1*J1)+1):
        dY1[j] = -c * b * Y1[j+1] * (Y1[j+2] - Y1[j-1]) - c * Y1[j] + (h * c)/b * X1[int((j-1)/J1)]
    dY1[0] = dY1[-1]
    dY1[-2] = dY1[1]
    dY1[-3] = dY1[2]
    return(dY1)

def dX_valred(X1,K1):
    dX1 = np.zeros((K1+3))
    ek = 0
    for k in range(2,K1+2):
        ek = 0.984 * ek + 1.74 * np.sqrt(1-0.984**2)*np.random.normal(0,1)
        gU = 0.275 + 1.59*X1[k] - 0.0190*(X1[k])**2 - 0.0130*(X1[k])**3 + 0.000707*(X1[k])**4 + ek
        dX1[k] = - X1[k-1]*(X1[k-2]-X1[k+1])-X1[k]+F-gU
    dX1[0]=dX1[-3]
    dX1[1]=dX1[-2]
    dX1[-1]=dX1[2]
    return(dX1)

### Calculating
#for different time steps t

    

if INIT:
    ni      = 20            # number of initial states
    runs    = range(0,ni) 
    t = 0.001                                  # delta t
    TU  = 10
    wpt = 100
    T = TU/t                                    # number of timesteps
    print('Die Berechnung läuft über ' + str(T) + ' Zeitschritte!')

else:
    init    = 0                      # time step of perturbation
    runs    = np.linspace(init,init,1)
    t = 0.001                                  # delta t
    TU  = 10
    wpt = 100
    T = TU/t                                    # number of timesteps
    print('Die Berechnung läuft über ' + str(T) + ' Zeitschritte!')   

# initial values for X and Y, vary for different initial states
X = np.zeros((K+3))+np.random.normal(size=K+3)
Y = np.zeros((J*K+3))+np.random.normal(size=J*K+3)

dX, dY = np.zeros((K+3)), np.zeros((J*K+3))
    


    
for init in runs:
    # initial values for X and Y, vary for different initial states
    np.random.seed(init*5)
    X = np.zeros((K+3))+np.random.normal(size=K+3)
    Y = np.zeros((J*K+3))+np.random.normal(size=J*K+3)

    dX, dY = np.zeros((K+3)), np.zeros((J*K+3))
    # open files to save
    fX = tables.open_file(f'data/pert_init/{title1}_{scheme}_Pert_{PERT}_INIT_{init}.h5', mode='w')
    fY = tables.open_file(f'data/pert_init/{title2}_{scheme}_Pert_{PERT}_INIT_{init}.h5', mode='w')
    atom = tables.Float64Atom()
    array_X = fX.create_earray(fX.root, 'array_X', tables.Float64Atom(), shape =(0,K), title='X for Lorenz96')#, expectedrows = int(T*t/wpt))
    array_Y = fY.create_earray(fY.root, 'array_Y', tables.Float64Atom(), shape =(0,J*K), title='Y for Lorenz96')#, expectedrows = int(T*t/wpt))
    array_X.append(X[2:-1].reshape((1, K)))
    array_Y.append(Y[1:-2].reshape((1, J*K)))
    T = TU/t
    for tt in range(1,int(T)):

        if (tt % (T/100)) == 0:
            print('Fortschritt: ' + str(int(tt*100/T)) + '%')


        if scheme == "EF":
            ## Euler forward
            X = X + dX_val * t
            Y = Y + dY_val * t

        elif scheme == "RK":
            ## Runge-Kutta scheme
            k1 = dX_val(X,Y,K,J)
            j1 = dY_val(X,Y,K,J)
                
            k2 = dX_val(X+t/2*k1,Y+t/2*j1,K,J)                           #dX + t/2 * k1
            j2 = dY_val(X+t/2*k1,Y+t/2*j1,K,J)
                
            k3 = dX_val(X+t/2*k2,Y+t/2*j2,K,J)
            j3 = dY_val(X+t/2*k2,Y+t/2*j2,K,J)
                
            k4 = dX_val(X+t*k3,Y+t*j3,K,J)
            j4 = dY_val(X+t*k3,Y+t*j3,K,J)
                
            X = X+ t/6 * (k1 + 2*k2 + 2*k3 + k4)
            Y = Y+ t/6 * (j1 + 2*j2 + 2*j3 + j4)

        elif scheme == "RRK":
            ## Reduced Runge-Kutta scheme
            k1 = dX_valred(X,K)
            k2 = dX_valred(X+t/2*k1,K)
            k3 = dX_valred(X+t/2*k2,K)
            k4 = dX_valred(X+t*k3,K)
            X = X + t/6 * (k1 + 2*k2 + 2*k3 + k4)

        else:
            print('Wähle ein implimentiertes scheme. (EF für Euler forward, RK für Runge Kutta scheme oder RRK für Reduced Runge Kutta)')

        if PERT:
            if (tt == 5000):
                X = X + d
                Y = Y + d


        if ((tt*t*wpt) % 1) == 0.:
            array_X.append(X[2:-1].reshape((1, K)))
            array_Y.append(Y[1:-2].reshape((1, J*K)))

    fX.close()
    fY.close()
