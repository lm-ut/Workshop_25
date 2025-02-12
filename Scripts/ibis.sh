#!/bin/bash
#SBATCH -J ibis
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --mem=30gb
#SBATCH -A ealloc_e7679_project1-tk-echo
#SBATCH --cpus-per-task 3
#SBATCH --output=ibis.txt

module load any/plink/1.9
module load any/ibis/1.20.9
module load datamash/1.3

# IBD segment detection with IBIS (Seidman et al. 2020)
# https://github.com/williamslab/ibis

# prepare input1 from QUILT output
# plink --vcf /gpfs/helios/projects/echo_workshops/project.1.tk/data/QUILT_output/GT_corrected_imputed_data.vcf.gz --make-bed --out ADN_HAD_QUILT --double-id
# use simplified ID-s in the .fam, as in /gpfs/helios/projects/echo_workshops/project.1.tk/data/plink/ADN_HAD_QUILT.fam
# cp ADN_HAD_QUILT.bim ADN_HAD_QUILT.obim
# awk 'BEGIN{FS=OFS="\t"}{print $1, $1 "_" $4, $3, $4, $5, $6}' ADN_HAD_QUILT.obim >ADN_HAD_QUILT.bim
# extract a smaller set of MAF>0.05 variants, e.g. with plink --bfile ADN_HAD_QUILT --extract /gpfs/helios/projects/echo_workshops/project.1.tk/data/plink/em1k --make-bed --out ADN_HAD_QUILTsm
# map with: plink --bfile ADN_HAD_QUILTsm --cm-map /gpfs/helios/projects/echo_workshops/project.1.tk/data/B37maps/genetic_map_chr@_combined_b37.txt --make-bed --out ADN_HAD_QUILTsmapped
input1=/gpfs/helios/projects/echo_workshops/project.1.tk/data/plink/ADN_HAD_QUILTsmapped
input2=/gpfs/helios/projects/echo_workshops/project.1.tk/data/plink/em1k
ibis -bfile ${input1} -min_l 7 -a 0 -c 0.0001 -maxDist 0.1 -er .004 -2 -t 3 -noFamID -bin -printCoef -f tst7cM
# ibis -bfile /gpfs/helios/projects/echo_workshops/project.1.tk/data/em1k -min_l 5 -a 0 -c 0.0001 -maxDist 0.1 -er .004 -2 -t 3 -noFamID -bin -printCoef -f tst5cM
ibis -bfile ${input2} -min_l 5 -a 0 -c 0.0001 -maxDist 0.1 -er .004 -2 -t 3 -noFamID -bin -printCoef -f tst5cM

cut -f1-3 tst5cM.coef >t00.coef
sort -k1,1 t00.coef | join -1 1 -2 1 - indiv.txt -o 0,2.2,1.2,1.3,1.5,1.6 |sort -k 3,3 | join -1 3 -2 1 - indiv.txt -o 1.1,1.2,0,2.2,1.4,1.5,1.6 >tmp0m.txt
awk '{print $3,$4,$1,$2,$5,$6,$7}' tmp0m.txt >tempm.txt
cat tempm.txt >>tmp0m.txt
rm tempm.txt
datamash -W -s crosstab 1,4 sum 5 --filler 0 < tmp0m.txt >tmpm.txt
datamash -W -s crosstab 1,4 --filler 0 < tmp0m.txt >tmpm.txt
head -n 1 tmpm.txt >hdm.txt
awk '{print "ID" "\t" "Country" "\t" $1 "\t" $2 "\t" $3 "\t" $4 "\t" $5 "\t" $6 "\t" $7 "\t" $8 "\t" $9 "\t" $10 "\t" $11 "\t" $12 "\t" $13 "\t" $14 "\t" $15 "\t" $16 "\t" $17 "\t" $18 "\t" $19 "\t" $20 "\t" $21 "\t" $22 "\t" $23 "\t" $24 "\t" $25 "\t" $26  "\t" $27 "\t" $28 "\t" $29 "\t" $30 "\t" $31 "\t" $32 "\t" $33 "\t" $34 "\t" $35 "\t" $36 "\t" $37 "\t" $38 "\t" $39 "\t" $40 "\t" $41 "\t" $42 "\t" $43 "\t" $44 "\t" $45 "\t" $46 "\t" $47 "\t" $48 "\t" $49 "\t" $50 "\t" $51 "\t" $52 "\t" $53 "\t" $54 "\t" $55 "\t" $56 "\t" $57 "\t" $58 "\t" $59 "\t" $60 "\t" $61 "\t" $62 "\t" $63 "\t" $64 "\t" $65 "\t" $66 "\t" $67 "\t" $68 "\t" $69 "\t" $70 "\t" $71 "\t" $72 "\t" $73 "\t" $74  "\t" $75 "\t" $76 "\t" $77 "\t" $78 "\t" $79 "\t" $80}' hdm.txt >headerm.txt 
# sort -k1b: k1 says sort by column 1, b ignores spaces, ',1' specifies at which column to stop sorting, by default it would use all fields right of the start field
sort -k1b,1 tmpm.txt|join -1 1 -2 1 - indiv.txt -o 0,2.2,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10,1.11,1.12,1.13,1.14,1.15,1.16,1.17,1.18,1.19,1.20,1.21,1.22,1.23,1.24,1.25,1.26,1.27,1.28,1.29,1.30,1.31,1.32,1.33,1.34,1.35,1.36,1.37,1.38,1.39,1.40,1.41,1.42,1.43,1.44,1.45,1.46,1.47,1.48,1.49,1.50,1.51,1.52,1.53,1.54,1.55,1.56,1.57,1.58,1.59,1.60,1.61,1.62,1.63,1.64,1.65,1.66,1.67,1.68,1.69,1.70,1.71,1.72,1.73,1.74,1.75,1.76,1.77,1.78,1.79,1.80,1.81,1.82>tmp2m.txt
sort tmp2m.txt -k 2,2 >tmp3m.txt 
cat headerm.txt tmp3m.txt >SUM_EEMA_5cMcoef0.0001.txt
rm tmp*.*
