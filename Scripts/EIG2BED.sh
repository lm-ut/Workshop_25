#!/bin/bash

Input=$1

Output=$2

echo "genotypename:    ${Input}.geno
snpname:         ${Input}.snp
indivname:       ${Input}.ind
outputformat:    PACKEDPED
genotypeoutname: ${Output}.bed
snpoutname:      ${Output}.bim
indivoutname:    ${Output}.fam
familynames:     YES" > convertf_${Output}.par

