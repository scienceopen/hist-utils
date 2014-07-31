#!/usr/bin/env python3
# based on Strickland 1993

from numpy import pi,exp,logspace,sum,where
from matplotlib.pyplot import xlabel,ylabel,title,loglog,figure,clf,grid,gca
from findnearest import find_nearest

E0 = 2500.
Wb=0.15*E0
Q0 = 8.0e11

E = logspace(2,5,num=4000,base=10)
isimE0,simE0 = find_nearest(E,E0)

# Gaussian base
Qc = Q0/(pi**(3/2)*Wb*E0)
base = Qc * exp(-((E-E0)/Wb)**2)

#low energy tail
# for LET, 1<b<2
Bl = 8200.
bl = 1.
let = Bl*(E/E0)**(-bl)
let[E>E0] = 0.

# "third tail"
B3 = 1.8e4
b3 = 3.
mid = B3*(E/E0)**(b3)
mid[E>E0] = 0.
#%%
arc = base + let + mid
# now add high energy tail
# strickland 1993 said 0.2, but 0.145 gives better match to peak flux
Bh = 0.145*arc[isimE0] #4100.
print(Bh)
bh = 2.9
het = Bh*(E/E0)**(-bh)
het[E<E0] = 0.

arc += het

Q = sum(arc)
print('total flux Q=' + str(Q))
print('E0 flux =' + str(arc[isimE0]))
#%%
figure(1);clf()
loglog(E,het,'k:')
loglog(E,let,'k:')
loglog(E,mid,'k:')
loglog(E,arc)
grid(True,which='both')
xlabel('Electron Energy [eV]')
ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
title('arc flux [based on Strickland 1993]')
gca().set_ylim((1e2,1e6))