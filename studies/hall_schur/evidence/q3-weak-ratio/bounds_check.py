"""Check proven bounds for K_{n,2n} and K_{n,m} (fixed n) with exact integers."""
import math, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from weak_ratio import complete_models_formula as F
from fractions import Fraction
# K_{n,2n}: ((n+1)/4)^n <= ratio <= e*(n+1)^n, and models >= n!(n+1)^n
for n in range(1, 301):
    f, mt = F(n, 2*n), math.perm(2*n, n)
    assert f >= math.factorial(n) * (n+1)**n
    assert Fraction(f, mt) >= Fraction((n+1)**n, 4**n)
    assert f <= (n+1)**(2*n) and mt >= n**n
    assert math.log(f) - math.log(mt) <= 1 + n*math.log(n+1)
print("K_{n,2n} bounds OK n=1..300")
# fixed n: (n+1)^m - n*n^m <= models <= (n+1)^m
for n in range(1, 21):
    for m in range(n, 301):
        f = F(n, m)
        assert (n+1)**m - n*n**m <= f <= (n+1)**m
print("Bonferroni bounds OK n=1..20, m=n..300")
