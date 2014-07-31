#!/usr/bin/env python3
# based on Strickland 1993

from numpy import pi,exp,logspace,sum,where
from matplotlib.pyplot import xlabel,ylabel,title,loglog,figure,clf,grid,gca

E0 = 2500
Wb=0.15*E0
Q0 = 8e11

E = logspace(2,5,num=200,base=10)
iE0 = where()

# Gaussian base
base = (Q0/(pi**(3/2)*Wb*E0)) * exp(-((E-E0)/Wb)**2)

# high energy tail
#Bh = 4.1e3
bh = 2.9
het = Bh*(E/E0)**(-bh)
het[E<E0] = 0

#low energy tail
# for LET, 1<b<2
Bl = 8200
bl = 1
let = Bl*(E/E0)**(-bl)
let[E>=E0] = 0

# "third tail"
B3 = 1.8e4
b3 = 3
mid = B3*(E/E0)**(b3)
mid[E>=E0] = 0
#%%
arc = base + het + let + mid
Q = sum(arc)
print('total flux Q=' + str(Q))
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