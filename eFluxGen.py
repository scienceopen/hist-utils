#!/usr/bin/env python3
# based on Strickland 1993

from numpy import (pi,exp,logspace,sum,where,min,argmin,array,newaxis,repeat,
                   arange,zeros,all,atleast_1d,isscalar)
from matplotlib.pyplot import xlabel,ylabel,title,loglog,figure,clf,grid,gca,show,legend
from findnearest import find_nearest
from warnings import warn


def fluxgen(E0,Q0,Wbc,Bm,bl,bm,bh):
    E0 = atleast_1d(E0)
    nE0 = len(E0)
    Wb=Wbc*E0

    E = logspace(2,4.35,num=200,base=10)
    isimE0 = find_nearest(E,E0)[0]
    isimE0 += -1 # FIXME to get left of E0
    E = repeat(E[:,newaxis],nE0,axis=1) #identical columns

    base = gaussflux(E,E0,nE0,Q0,Wb)
    low = letail(E,E0,bl)
    arc = base + low #intermediate result
    mid = midtail(Bm,E,E0,nE0,arc,isimE0,bm)
    arc += mid #intermediate result
    hi = hitail(E,E0,nE0,arc,isimE0,bh)

    arc += hi

    diprat(E,E0,nE0,arc,isimE0)

    Q = sum(arc,axis=0).tolist()
    #rint('total flux Q: ' + (' '.join(' {:.1e}'.format(*q) for q in enumerate(Q))))
    print('total flux Q: ' + str(Q))
    #print('E0 flux =' + str(arc[isimE0]))

    return E,arc,low,mid,hi,base

def letail(E,E0,bl):
    # for LET, 1<b<2
    #Bl = 8200.   #820 (typo?)
    Bl = 0.4*Q0/(2*pi*E0**2)*exp(-1)
    #bl = 1.0     #1
    low = Bl*(E/E0)**(-bl)
    low[E>E0] = 0.
    print('Bl: ' + str(Bl))
    return low

def midtail(Bm,E,E0,nE0,arc,isimE0,bm):
    idip = zeros(nE0,dtype=int)
    #for iE0 in arange(nE0):
    #    idip[iE0] = argmin(arc[:isimE0[iE0],iE0],axis=0)
    #print(idip)
    #Bm = 1.8e4      #1.8e4
    #bm = 3.         #3
    mid = Bm*(E/E0)**(bm)
    mid[E>E0] = 0.

    return mid#,idip

def hitail(E,E0,nE0,arc,isimE0,bh):
    # strickland 1993 said 0.2, but 0.145 gives better match to peak flux at 2500 = E0
    Bh = zeros(nE0)
    for iE0 in arange(nE0):
        Bh[iE0] = 0.145*arc[isimE0[iE0],iE0]      #4100.
    #print('Bh = '+str(Bh))
    #bh = 4                   #2.9
    het = Bh*(E/E0)**(-bh)
    het[E<E0] = 0.

    return het

def diprat(E,E0,nE0,arc,isimE0):
    dipratio = zeros(nE0)
    for iE0 in arange(nE0):
        idip = argmin(arc[:isimE0[iE0],iE0],axis=0)
        dipratio[iE0] = arc[idip,iE0]/arc[isimE0[iE0],iE0]

    print('dipratio=' + str(dipratio))
    #if not all(0.2<dipratio<0.5):
    #    warn('dipratio outside of 0.2<dipratio<0.5')

def gaussflux(E,E0,nE0,Q0,Wb):
    Qc = Q0/(pi**(3/2)*Wb*E0)
    base = Qc * exp(-((E-E0)/Wb)**2)
    return base

if __name__ == '__main__':
    #E0 = 2500.
    #Q0 = 8.e11
    E0 = array([500., 1000., 2500., 5000., 1e4])
    Q0 = array([8e10, 3.2e11, 1.e12, 2.8e12, 5.e12])
    Wbc = array([1, 0.75, 0.5, 0.375, 0.25])
    bl = array([2., 1.5, 1.4, 1.2, 1.])
    bm = array([3., 3.,  3.,   2.5,  2.])
    bh = array([4., 4.,  4.,   3.5,  2.5])
    Bm = array([2e3, 5e3, 6e3, 8e3, 5e3])

    #E0 = array([2500., 5000., 7500., 10000.])
    #Q0 = array([8.0e11, 8.0e11, 8.0e11, 8.0e11])

    E,arc,low,mid,hi,base = fluxgen(E0,Q0,Wbc,Bm,bl,bm,bh)

    figure(1);clf()
    if isscalar(E0):
        loglog(E,hi,'k:')
        loglog(E,low,'k:')
        loglog(E,mid,'k:')
    loglog(E,arc)
    grid(True,which='both')
    xlabel('Electron Energy [eV]')
    ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
    title('arc flux, $E_0=$' + str(E0) + '[eV]')
    gca().set_ylim((1e2,1e6))
    legend(['500','1000','2500','5000','10000'])
    #gca().set_xlim((1e2,1e4))

    figure(2);clf()
    loglog(E,base)
    gca().set_ylim((1e2,1e6))
    #gca().set_xlim((1e2,1e4))
    title('arc Gaussian base function, E0=' + str(E0)+ '[eV]')
    xlabel('Electron Energy [eV]')
    ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
    legend(['500','1000','2500','5000','10000'])

    figure(3); clf()
    loglog(E,low)
    gca().set_ylim((1e2,1e6))

    show()