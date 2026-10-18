"""Reconstruction of the Schur(N,3) CNF described in the audit task."""


def var(i, c):
    return 3 * (i - 1) + c + 1


def schur_cnf(N, k=3):
    assert k == 3
    alo, amo, tri = [], [], []
    for i in range(1, N + 1):
        alo.append([var(i, 0), var(i, 1), var(i, 2)])
        for a in range(3):
            for b in range(a + 1, 3):
                amo.append([-var(i, a), -var(i, b)])
    for z in range(2, N + 1):
        for x in range(1, z // 2 + 1):
            y = z - x
            for c in range(3):
                cl = sorted({-var(x, c), -var(y, c), -var(z, c)})
                tri.append(cl)
    return 3 * N, alo, amo, tri


def all_clauses(N):
    nv, alo, amo, tri = schur_cnf(N)
    return nv, alo + amo + tri


def write_dimacs(path, nv, clauses):
    with open(path, "w") as f:
        f.write("p cnf %d %d\n" % (nv, len(clauses)))
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")
