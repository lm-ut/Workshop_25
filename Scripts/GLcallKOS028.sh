#!/bin/bash
#SBATCH -J AngsdGLcall
#SBATCH --time=2:00:00
#SBATCH --mem=5g
#SBATCH -A ealloc_e7679_project1-tk-echo
#SBATCH --ntasks=1
#SBATCH --cpus-per-task 5
#SBATCH --output=AngsdOut.txt

module load angsd/0.917

bams=/gpfs/helios/projects/echo_workshops/project.1.tk/data/KOS028_0.1.bams
sites=/gpfs/helios/projects/echo_workshops/project.1.tk/data/uk10k_chr22_maf0.05.pos

# Genotype likelihood (GL) calling with ANGSD
# This script calls genotype likelihoods (GL) and genotype probabilities (GP) from a list of bams that in this case contains just one single individual. 
# The resulting outputfile of this script serves as the input for the next step of imputation with BEAGLE 4.1.
# More information about preparing BEAGLE input with ANGSD:
# https://www.popgen.dk/angsd/index.php/Genotype_Likelihoods
# http://www.popgen.dk/angsd/index.php/Beagle_input
# -dovcf generates a vcf, -GL generates genotype likelihoos, -doGlf creates a BEAGLE input file with GL

angsd -b ${bams} -dovcf 1 -GL 1 -dopost 1 -nThreads 10 -doGlf 2 -doMajorMinor 1 -doMaf 1 -CheckBamHeaders 0 -r chr22: -sites ${sites} -out KOS028_GL

# Variant range only works with indexed bams, for this:
# module load samtools/1.19
# samtools index 
# with indexed bam and range set to chr 22 the cpu time used was 2.4 sec
# output vcf field explanations, see:
# https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://samtools.github.io/hts-specs/VCFv4.1.pdf&ved=2ahUKEwi7weS2w4mLAxWsZqQEHZ1fJn8QFnoECBoQAQ&usg=AOvVaw0ZnB2AserlLAW4xV1PLTaY
# briefly, unphased GP and GL values are in order of REF/REF, HET, ALT/ALT
# beagle file with normalized genotype likelihoods (not probabilities) that sum to 1

# if a PROBLEM with chromosome reporting: Gretzinger derived files 'chr22', BEAGLE ref panel '22'
zcat KOS028_GL.vcf.gz|awk -F'\t' -vOFS='\t' '{ gsub("chr22", "22", $1) ; print }'|gzip >KOS028_GLc.vcf.gz

