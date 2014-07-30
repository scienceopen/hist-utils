#!/usr/bin/env python3
# plotting of closed-form energy flux distributions of Strickland 1993
# implemented by Michael Hirsch July 2014

from numpy import pi,exp,logspace
from matplotlib.pyplot import xlabel,ylabel,title,loglog,figure,clf,grid,gca

#%% user parameters
# phiE0 is electron flux at "top" of ionosphere
#incident energy flux Q0
Q0 = 1e7 #[erg cm^-2 sec^-1]
#characteristic energy E0
E0 = 2500

#%% build energy flux "base"
#Gaussian width parameter W
W = 0.15*E0 #per paper just above section 2.2
E = logspace(2,5,num=200,base=10)

#maxwellian
diffuseBase = ( Q0 / (2*pi*E0**3) ) * E * exp(-E/E0)
#gaussian
arcBase = ( Q0 / (pi**(3/2) * W * E0) ) * exp(-((E-E0)/W)**2)

#%% low energy tail
if E0 < 500:
    b = 1/(0.8*E0)
else: #E0 > 500
    b = 1/(0.1*E0 + 0.35)
B = 0.4*Q0/(2*pi*E0**2)*exp(-1)
print('B=' + str(B))
print('b=' + str(b))
philet = B * E0/E * exp(-b*E)
philet[E>E0] = 0
diffuse = diffuseBase + philet
arc = arcBase + philet

#high energy tail
phihet = B*(E/E0)**(-b)
phihet[E<E0] = 0
diffuse = diffuse + phihet
arc = arc + phihet
#%% plot
figure(1),clf()
loglog(E,diffuse)
grid(True,which='both')
xlabel('Electron Energy [eV]')
ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
title('Diffuse Aurora: driving precipitation')

figure(2),clf()
loglog(E,arc)
grid(True,which='both')
xlabel('Electron Energy [eV]')
ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
title('Auroral Arc: driving precipitation, No HET or LET')
#gca().set_ylim((1,1e9))
