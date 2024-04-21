mw = 20;
mc = 375;
kw = 100000;
ks = 10000;
b = 2000;
A = [0, 1, 0, 0; -(ks+kw)/mw, -b/mw, ks/mw, b/mw; 0, 0, 0, 1; ks/mc, b/mc, -ks/mc, -b/mc];
B1 = [0; 0; 0; 1/mc;];
C = [0, 0, 1, 0];
D1 = 0;

P = ss(A, B1, C, D1)

sisotool(P)