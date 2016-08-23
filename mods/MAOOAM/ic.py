import numpy as np

# X0b=np.zeros(36)
# X0b[0]=0.1 # typ=A, NX0=0, Ny= 1
# X0b[1]=0.005 # typ=K, NX0=1, Ny= 1

# X0a=np.zeros(36)
# X0a[0]=0.03 # typ=A, NX0=0, Ny= 1
# X0a[1]=0.005 # typ=K, NX0=1, Ny= 1

# E=(X0a,X0b)
# E=array(E)

# X0b = f.model(X0b,0.1,0.1)
# X0a = f.model(X0a,0.1,0.1)
# E = f.model(E,0.1,0.1)

X0=np.zeros(36)

# X0c=np.zeros(36)
# X0c[0]=0.0003 # typ=A, NX0=0, Ny= 1
# X0c[1]=0.005 # typ=K, NX0=1, Ny= 1


# GRL ic after 268000=82.6 years
X1=np.array([  4.44820574e-02,  -5.93489980e-03,   6.72468803e-04,
        -2.01227570e-02,  -1.28684268e-02,  -3.55353681e-02,
         3.11341702e-04,  -1.27713098e-03,   1.80033730e-02,
        -2.20677433e-02,   5.07192810e-02,   9.35819375e-04,
         6.91712310e-03,   3.58538801e-04,  -1.94468955e-02,
        -1.61644623e-02,   3.60829852e-05,  -1.33859624e-03,
         5.51912074e-03,  -9.87924028e-03,   3.30184009e-06,
        -5.25653412e-05,  -1.35888046e-06,  -3.71654370e-07,
        -5.35765909e-06,   2.19891078e-05,  -6.03188797e-06,
         2.94608166e-07,   6.68573383e-03,   1.91002857e-01,
         2.45099679e-03,   1.03540875e-01,   3.69452384e-03,
        -5.39100765e-02,   1.06411054e-03,  -7.00209219e-05])



#GRL ic after moins de 10 years - 0.1 - python
# X1=np.array([  3.96282335e-02,  -1.17090354e-02,  -4.17830342e-02,
#          3.77819324e-02,  -9.83993620e-03,  -3.04146911e-03,
#          1.02147629e-02,   3.91911160e-03,   1.97539021e-02,
#          3.23147052e-02,   3.17206885e-02,  -6.25536744e-03,
#         -1.94112294e-02,   4.95809422e-03,  -9.07757336e-03,
#         -4.64571480e-05,   1.83484278e-03,   4.33499786e-03,
#          1.22257621e-02,   1.15499818e-02,  -7.82795976e-07,
#         -1.44505604e-05,   2.26732690e-07,  -3.20988502e-08,
#          2.45639934e-06,  -4.91550364e-06,  -6.66040970e-07,
#         -1.96839184e-08,  -2.28392595e-03,   2.18919847e-01,
#          2.19888119e-03,   7.20819584e-02,  -3.51634484e-04,
#         -9.02060876e-03,  -5.30086228e-05,   3.85312299e-06])
#psi variables
X0[0]=0.03 # typ=A, NX0=0, Ny= 1
X0[1]=0.005 # typ=K, NX0=1, Ny= 1
X0[2]=0 # typ=L, NX0=1, Ny= 1
X0[3]=0.0 # typ=A, NX0=0, Ny= 2
X0[4]=0.0 # typ=K, NX0=1, Ny= 2
X0[5]=0.0 # typ=L, NX0=1, Ny= 2
X0[6]=0.0 # typ=K, NX0=2, Ny= 1
X0[7]=0.0 # typ=L, NX0=2, Ny= 1
X0[8]=0.0 # typ=K, NX0=2, Ny= 2
X0[9]=0.0 # typ=L, NX0=2, Ny= 2

#theta variables
X0[10]=0.0 # typ=A, NX0=0, Ny= 1
X0[11]=0.0 # typ=K, NX0=1, Ny= 1
X0[12]=0.0 # typ=L, NX0=1, Ny= 1
X0[13]=0.0 # typ=A, NX0=0, Ny= 2
X0[14]=0.0 # typ=K, NX0=1, Ny= 2
X0[15]=0.0 # typ=L, NX0=1, Ny= 2
X0[16]=0.0 # typ=K, NX0=2, Ny= 1
X0[17]=0.0 # typ=L, NX0=2, Ny= 1
X0[18]=0.0 # typ=K, NX0=2, Ny= 2
X0[19]=0.0 # typ=L, NX0=2, Ny= 2

#A variables
X0[20]=0.0 # NX0=0.5, Ny= 1
X0[21]=0.0 # NX0=0.5, Ny= 2
X0[22]=0.0 # NX0=0.5, Ny= 3
X0[23]=0.0 # NX0=0.5, Ny= 4
X0[24]=0.0 # NX0=1.0, Ny= 1
X0[25]=0.0 # NX0=1.0, Ny= 2
X0[26]=0.0 # NX0=1.0, Ny= 3
X0[27]=0.0 # NX0=1.0, Ny= 4

#T variables
X0[28]=0.0 # NX0=0.5, Ny= 1
X0[29]=0.0 # NX0=0.5, Ny= 2
X0[30]=0.0 # NX0=0.5, Ny= 3
X0[31]=0.0 # NX0=0.5, Ny= 4
X0[32]=0.0 # NX0=1.0, Ny= 1
X0[33]=0.0 # NX0=1.0, Ny= 2
X0[34]=0.0 # NX0=1.0, Ny= 3
X0[35]=0.0 # NX0=1.0, Ny= 4