#!/bin/bash
#SBATCH -J BEAGLE
#SBATCH --time=2:00:00
#SBATCH --mem=5g
#SBATCH --ntasks=1
#SBATCH -A ealloc_e7679_project1-tk-echo
#SBATCH --cpus-per-task 1
#SBATCH --output=BEAGLE.txt

module load any/java/1.8.0_265
module load tabix/2013-12-16 
module load bcftools/1.9

# Imputation with BEAGLE
# This script performs two-step imputation as described in Hui et al. 2020, https://www.nature.com/articles/s41598-020-75387-w
# Briefly, genotypes will be imputed first from GL with BEAGLE 4.1 followed by removal of sites with low GP and a BEAGLE 5.5 step to complete the gaps  

# BEAGLE4.1
# java [memory options] -jar /path/beagle4.1.jar input ref map output

refpan=/gpfs/helios/projects/echo_workshops/project.1.tk/data/chr22.1kg.phase3.v5a.vcf.gz
mapfile=/gpfs/helios/projects/echo_workshops/project.1.tk/data/plink.chr22.GRCh37.map
input=KOS028_GLc

for i in {22..22}
do
outgl=KOS028_gl_chr${i}
java -Xss5m -Xmx5g -jar /gpfs/helios/home/etais/hpc_tk_echo/BEAGLE/beagle.27Jan18.7e1.jar gl=${input}.vcf.gz ref=${refpan} map=${mapfile} out=${outgl} gprobs=true chrom=${i} window=5000 overlap=500
tabix ${outgl}.vcf.gz
# bcftools annotate -e 'GT="./."' ${outgl}.vcf.gz -Oz -o ${outgl}.GP99.vcf.gz
bcftools view -i 'MAX(GP)>=0.99' ${outgl}.vcf.gz -Oz -o ${outgl}_GP99.vcf.gz
tabix ${outgl}.GP99.vcf.gz
done

# BEAGLE5, http://faculty.washington.edu/browning/beagle/beagle_5.5_17Dec24.pdf manual
for i in {22..22}
do
java -Xss5m -Xmx5g -jar /gpfs/helios/home/etais/hpc_tk_echo/BEAGLE/beagle.17Dec24.224.jar gt=${outgl}_GP99.vcf.gz ref=${refpan} map=${mapfile} out=${outgl}.imputed impute=true gp=true
# also to get results on the variants called only
# java -Xss5m -Xmx5g -jar /gpfs/helios/home/etais/hpc_tk_echo/BEAGLE/beagle.17Dec24.224.jar gt=${outgl}_GP99chr${i}.vcf.gz ref=${refpan} map=${mapfile} out=${outgl}.imputed_onlycalled impute=false gp=true
tabix ${outgl}.imputed.vcf.gz
# tabix ${outgl}.imputed_onlycalled.vcf.gz
bcftools view -i 'MAX(GP)>=0.99' ${outgl}.imputed.vcf.gz -Oz -o ${outgl}_imputed_GP99.vcf.gz
tabix ${outgl}_imputed_GP99.vcf.gz
done
# took xx min with KOS028 chr22 1M region
