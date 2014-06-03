#!/usr/bin/env python3
# Michael Hirsch
# we consider arbitrarily two worst case dates:
# Dec 21 worst-case heating need -- 10th percentile
# Sept 1 worst-case cooling need
import math

def worstHeat(Albedo,Aair,A,R,Qequip):
    # assume sun is below horizon 24 hours a day
    Qsolar = 0 #[W]
 #http://weatherspark.com/averages/32940/1/Fairbanks-Alaska-United-States 
    # 25th percentile -35C, 10th percentile -40C
    Tout = -40 #[C]
    Tin = -10 #[C]
    
    Qext = Qsolar*0
    Qxfer =  Aair/R*(Tout-Tin)

    Qcooler = Qext + Qxfer + Qequip #[W]
    
    print('10th percentile worst-case HEATing needs {:0.1f}'.format(-Qcooler) + ' watts / {:0.1f}'.format(-Qcooler*3.412) + ' BTU/hr.' )
    print('Contributions:')
    print('Qext [Watts]: {:0.1f}'.format(Qext))
    print('Qxfer [Watts]: {:0.1f}'.format(Qxfer))
    print('Qequip [Watts]: {:0.1f}'.format(Qequip))


def worstCool(Albedo,Aair,A,R,Qequip):
    #assume sun is at 45 degree elev, neglect cabinet albedo
    Qsun = 850 #[W]
 #http://weatherspark.com/averages/32940/1/Fairbanks-Alaska-United-States 
    # 25th percentile 18C, 10th percentile 21C  
    Tout = 20 #[C]
    Tin =  30 #[C]
    

    Qtop  = A['top']  * Qsun * math.sin(math.radians(35)) #max sun elev ~ 45 deg.
    Qside = A['side'] * Qsun * math.sin(math.radians(35)) #worst case(?)
    Qend  = 0 #A['end']  * Qsun * math.sin(math.radians(45)) #consistent with angle used for top,side
    Qsolar = Qtop + Qside + Qend #figure only 1 side, 1 end lit up
    

    Qext = Qsolar*(1-Albedo)        
    Qxfer =  Aair/R*(Tout-Tin)
    
    Qcooler = Qext + Qxfer + Qequip #[W]
    
    print('90th percentile worst-case COOLing needs {:0.1f}'.format(Qcooler) + ' watts / {:0.1f}'.format(Qcooler*3.412) + ' BTU/hr.' )
    print('Contributions:')
    print('Qext [Watts]: {:0.1f}'.format(Qext))
    print('Qxfer [Watts]: {:0.1f}'.format(Qxfer))
    print('Qequip [Watts]: {:0.1f}'.format(Qequip))

def SummerCool(Albedo,Aair,A,R,Qequip):
    #assume sun is at 45 degree elev, neglect cabinet albedo
    Qsun = 850 #[W]
 #http://weatherspark.com/averages/32940/1/Fairbanks-Alaska-United-States 
    # 25th percentile 18C, 10th percentile 21C  
    Tout = 35 #[C]
    Tin =  40 #[C]
    

    Qtop  = A['top']  * Qsun * math.sin(math.radians(45)) #max sun elev ~ 45 deg.
    Qside = A['side'] * Qsun * math.sin(math.radians(45)) #worst case(?)
    Qend  = 0 #A['end']  * Qsun * math.sin(math.radians(45)) #consistent with angle used for top,side
    Qsolar = Qtop + Qside + Qend #figure only 1 side, 1 end lit up
    

    Qext = Qsolar*(1-Albedo)        
    Qxfer =  Aair/R*(Tout-Tin)
    
    Qcooler = Qext + Qxfer + Qequip #[W]
    
    print('90th percentile Summer storage COOLing needs {:0.1f}'.format(Qcooler) + ' watts / {:0.1f}'.format(Qcooler*3.412) + ' BTU/hr.' )
    print('Contributions:')
    print('Qext [Watts]: {:0.1f}'.format(Qext))
    print('Qxfer [Watts]: {:0.1f}'.format(Qxfer))
    print('Qequip [Watts]: {:0.1f}'.format(Qequip))    
    
#------------------

A = {'side':0.45, 'end':0.35,'top':0.45}
Aair = 1*A['top'] + 2*A['side'] + 2*A['end'] #[m^2] roughly #neglect bottom side
Asun = A['top'] + A['side'] + A['end'] #[m^2] roughly 

print('enclosure area exposed to air is {:0.2f}'.format(Aair) +' m^2')
print('enclosure area exposed to sun is {:0.2f}'.format(Asun) +' m^2')
R = 0.18 #[m^2 C/W]
Qequip = { 'rest': 125, 'record': 175, 'compress': 250, 'off':5 } #[W]
Albedo = 0.7
print('Assuming albedo: {0:0.1f}'.format(Albedo))
#http://books.google.com/books?id=PePq7o6mAbwC&lpg=PA282&ots=gOYd86tmHh&dq=house%20paint%20albedo&pg=PA283#v=onepage&q=house%20paint%20albedo&f=false
print('Sign convention: negative watts is outgoing heat flux')
print('-------------------------------------------')
worstHeat(Albedo,Aair,A,R,Qequip['rest'])
print('-------------------------------------------')
worstCool(Albedo,Aair,A,R,Qequip['rest'])
print('-------------------------------------------')
SummerCool(Albedo,Aair,A,R,Qequip['off'])