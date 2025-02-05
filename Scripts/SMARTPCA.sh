#!/bin/bash

Input=$1

Output=$2

#OutName=$3

echo "genotypename:    ${Input}.geno
snpname:         ${Input}.snp
indivname:       ${Input}.ind
evecoutname:	${Input}.pca.evec
evaloutname:	${Input}.eval
altnormstyle: NO
numoutevec: 10
numoutlieriter: 0
numoutlierevec: 0
outliersigmathresh: 6.0
qtmode: 0
lsqproject: YES
poplistname: pop_list" > smartpca_${Output}.par

#convertf -p $Input.par
