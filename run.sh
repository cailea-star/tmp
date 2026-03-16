#!/bin/bash
# run.hk to run highk, pack and gamlat
:

#for ((Z=40;Z<=50;Z=Z+2)); do
Z=110

for ((N=157;N<=157;N=N+2)); do

#N=74

run.hk $Z $Z $N $N Ds269-HKpr1n2p16



cd mp

run.mp $Z $Z $N $N Ds269-HKpr1n2p16



cd ..

done
 
