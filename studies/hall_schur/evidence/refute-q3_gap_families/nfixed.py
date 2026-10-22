import math
from math import comb
def K(n,m): return sum((-1)**j*comb(n,j)*(n+1-j)**m for j in range(n+1))
for n in (1,2,3):
    m=800; r = K(n,m)/math.perm(m,n) if False else None
    lr = math.log(K(n,m)) - math.log(math.perm(m,n))
    print(n, 'ratio^(1/m) at m=800:', round(math.exp(lr/m),3), ' ratio*m^n/(n+1)^m =', round(math.exp(lr + n*math.log(m) - m*math.log(n+1)),6))
for n in range(1,15):
    for m in range(n,200):
        mo=K(n,m); assert (n+1)**m - n*n**m <= mo <= (n+1)**m
print('Bonferroni OK n<15, m<200')
# summary-wording counterexample: K_{1,2} plus isolated hole
import sys; sys.path.insert(0,'.')
from exh import counts
print('K12+isolated hole:', counts(1,3,[1,1,0]))
