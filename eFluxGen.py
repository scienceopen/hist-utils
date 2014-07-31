#!/usr/bin/env python3
# based on Strickland 1993

from numpy import pi,exp,logspace,spacing
from matplotlib.pyplot import xlabel,ylabel,title,loglog,figure,clf,grid,gca

E0 = 2500
Wb=0.15*E0
Q0 = 3e11

E = logspace(2,5,num=200,base=10)

# Gaussian base
base = (Q0/(pi**(3/2)*Wb*E0)) * exp(-((E-E0)/Wb)**2)

# high energy tail
Bh = 4.1e3
bh = 2.9
het = Bh*(E/E0)**(-bh)
het[E<E0] = spacing(1)

#low energy tail
Bl = 8200
bl = 1
let = Bl*(E/E0)**(-bl)
let[E>=E0] = spacing(1)

# "third tail"
B3 = 1.8e4
b3 = 3
tail3 = B3*(E/E0)**(b3)
tail3[E>=E0] = spacing(1)

#%% 
arc = base + het + let + tail3
#%% 
figure(1);clf()
loglog(E,het,'k:')
loglog(E,let,'k:')
loglog(E,tail3,'k:')
loglog(E,arc)
grid(True,which='both')
xlabel('Electron Energy [eV]')
ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
title('arc flux [based on Strickland 1993]')
gca().set_ylim((1e2,1e6))