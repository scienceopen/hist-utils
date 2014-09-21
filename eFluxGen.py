#!/usr/bin/env python3
''' Michael Hirsch
 based on Strickland 1993
'''
from numpy import (pi,exp,logspace,sum,argmin,array,newaxis,repeat,copy,
                   arange,zeros,atleast_1d,isscalar,set_printoptions)
from matplotlib.pyplot import figure, show
from findnearest import find_nearest



def fluxgen(E,E0,Q0,Wbc,Bm,bl,bm,bh):
    E0 = atleast_1d(E0)
    nE0 = E0.size
    Wb=Wbc*E0

    isimE0 = find_nearest(E,E0)[0]
    isimE0 -= 1 # FIXME to get left of E0
    E = repeat(E[:,newaxis],nE0,axis=1) #identical columns

    base = gaussflux(E,E0,nE0,Q0,Wb)
    arc = copy(base)

    low = letail(E,E0,Q0,bl)
    arc += low #intermediate result

    mid = midtail(Bm,E,E0,nE0,arc,isimE0,bm)
    arc += mid #intermediate result

    hi = hitail(E,E0,nE0,arc,isimE0,bh)
    arc += hi

    diprat(E,E0,nE0,arc,isimE0)

    Q = sum(arc,axis=0)
    #rint('total flux Q: ' + (' '.join(' {:.1e}'.format(*q) for q in enumerate(Q))))
    print('total flux Q:'+str(Q))
    #print('E0 flux =' + str(arc[isimE0]))

    return arc,low,mid,hi,base

def letail(E,E0,Q0,bl):
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

def plotflux(E,E0,hi,low,mid,arc,dbglvl):
    ax = figure(1).gca()
    if isscalar(E0):
        ax.loglog(E,hi,'k:')
        ax.loglog(E,low,'k:')
        ax.loglog(E,mid,'k:')
    ax.loglog(E,arc)
    ax.grid(True,which='both')
    ax.set_xlabel('Electron Energy [eV]')
    ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
    ax.set_title('arc flux, $E_0=$' + str(E0) + '[eV]')
    ax.set_ylim((1e2,1e6))
    ax.legend(list(map(str,E0)))
    #ax.set_xlim((1e2,1e4))

    if dbglvl>0:
        ax = figure(2).gca()
        ax.loglog(E,base)
        ax.set_ylim((1e2,1e6))
        #ax.set_xlim((1e2,1e4))
        ax.set_title('arc Gaussian base function, E0=' + str(E0)+ '[eV]')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
        ax.legend(str(E0))

        ax = figure(3).gca()
        ax.loglog(E,low)
        ax.set_ylim((1e2,1e6))
        ax.set_title('arc low (E<E0)')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')

        ax = figure(4).gca()
        ax.loglog(E,mid)
        ax.set_ylim((1e2,1e6))
        ax.set_title('arc mid')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')

        ax = figure(5).gca()
        ax.loglog(E,hi)
        ax.set_ylim((1e2,1e6))
        ax.set_title('arc hi (E>E0)')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')

    show()

def writeh5(arc,E,E0,Q0,Wbc,bl,bm,bh):
    from time import time
    import h5py

    progms = time() * 1000
    with h5py.File(str(progms) + '.h5', libver='latest') as fid:
        fid.create_dataset('/arc',data=arc)
        hE = fid.create_dataset('/E',data=E); hE.attrs['Units'] = 'eV'
        hE = fid.create_dataset('/params/E0',data=E0); hE.attrs['Units'] = 'eV'
        fid.create_dataset('/Q0',data=Q0)
        fid.create_dataset('/params/Wbc',data=Wbc)
        fid.create_dataset('/params/bl',data=bl)
        fid.create_dataset('/params/bm',data=bm)
        fid.create_dataset('/params/bh',data=bh)


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='generates diff. num flux based on Strickland 1993')
    p.add_argument('-d','--debug',help='set debugging verbosity',default=0,type=float)
    p.add_argument('--E0min',help='of preset scenarios, use only those with E0>',default=0,type=float)
    args = p.parse_args()

    set_printoptions(precision=2)
    E = logspace(2,4.35,num=200,base=10)
    #E0 = 2500.
    #Q0 = 8.e11
    E0 = array([500., 1000., 2500., 5000., 1e4])
    useE0 = E0>args.E0min
    E0 = E0[useE0]
    Q0 = array([8e10, 3.2e11, 1.0e12, 2.8e12, 5.0e12]); Q0 = Q0[useE0]
    Wbc = array([1, 0.75, 0.5, 0.375, 0.25]); Wbc = Wbc[useE0]
    bl = array([2., 1.5, 1.4, 1.2, 1.]); bl = bl[useE0]
    bm = array([3., 3.,  3.,   2.5,  2.]); bm = bm[useE0]
    bh = array([4., 4.,  4.,   3.5,  2.5]); bh = bh[useE0]
    Bm = array([2e3, 5e3, 6e3, 8e3, 5e3]); Bm = Bm[useE0]

    #E0 = array([2500., 5000., 7500., 10000.])
    #Q0 = array([8.0e11, 8.0e11, 8.0e11, 8.0e11])

    arc,low,mid,hi,base = fluxgen(E,E0,Q0,Wbc,Bm,bl,bm,bh)

    plotflux(E,E0,hi,low,mid,arc,args.debug)

    writeh5(arc,E,E0,Q0,Wbc,bl,bm,bh)