#!/usr/bin/env python
# coding: utf-8

import argparse
import os
import sys

def write_command(o, comment, command):
    """Writes a shell command to the output file with an optional comment."""
    if comment:
        o.write(f"{comment}\n")
    o.write(f"{command}\n\n")

def create_eigenstrat_conversion_file(o, output_name):
    """Creates the parameter file for converting PLINK to EIGENSTRAT format."""
    write_command(o, "# Convert to EIGENSTRAT",
                  f"""echo 'genotypename: {output_name}.bed
snpname: {output_name}.bim
indivname: {output_name}.fam
outputformat: EIGENSTRAT
genotypeoutname: {output_name}.geno
snpoutname: {output_name}.snp
indivoutname: {output_name}.ind
familynames: YES' > convertf_{output_name}.par""")
    write_command(o, "", f"convertf -p convertf_{output_name}.par")

def prepare_pca_projection_yes(o, prune_output_name, pca_controls):
    """Prepares the .ind file for PCA projection by editing population labels."""
    write_command(o, "# Edit .ind file for PCA projection",
                  f"sed -r 's/:/ /g' {prune_output_name}.ind > tmp.ind")
    write_command(o, "", "awk '{print $2, $3, $1}' tmp.ind > tmp.2.ind")

    # Set control populations
    if pca_controls:
        for pop in pca_controls.split(','):
            write_command(o, f"# Set {pop.strip()} as Control",
                          f"awk -v param='{pop.strip()}' '{{if ($3 == param) $3 = \"Control\"; print }}' tmp.2.ind > tmp.3.ind")
            write_command(o, "", "mv tmp.3.ind tmp.2.ind")

    # Set other populations as Case
    write_command(o, "# Set other populations as Projected",
                  "awk '{if ($3 != \"Control\") $3 = \"Projected\"; print }' tmp.2.ind > tmp.3.ind")
    write_command(o, "", f"paste {prune_output_name}.ind tmp.3.ind | awk '{{split($1, a, \":\"); print $1, $2, $6}}' > {prune_output_name}_edit.ind")
    write_command(o, "# Create pop list file for smartpca", "echo 'Control' > pop_list.txt")

def create_smartpca_param_file_yes(o, output_name):
    """Creates the parameter file for running smartpca."""
    write_command(o, "# Prepare smartpca parameter file",
                  f"""echo 'genotypename: {output_name}.geno
snpname: {output_name}.snp
indivname: {output_name}_edit.ind
evecoutname: {output_name}.pca.evec
evaloutname: {output_name}.eval
altnormstyle: NO
numoutevec: 4
numoutlieriter: 0
numoutlierevec: 0
outliersigmathresh: 6.0
qtmode: 0
lsqproject: YES
poplistname: pop_list.txt' > smartpca_{output_name}.par""")

def create_smartpca_param_file_no(o, output_name):
    """Creates the parameter file for running smartpca."""
    write_command(o, "# Prepare smartpca parameter file",
                  f"""echo 'genotypename: {output_name}.geno
snpname: {output_name}.snp
indivname: {output_name}.ind
evecoutname: {output_name}.pca.evec
evaloutname: {output_name}.eval
altnormstyle: NO
numoutevec: 4
numoutlieriter: 0
numoutlierevec: 0
outliersigmathresh: 6.0
qtmode: 0' > smartpca_{output_name}.par""")

def main():
    parser = argparse.ArgumentParser(description="Converts VCF to PLINK to EIGENSTRAT and runs PCA with smartpca")

    parser.add_argument("--name", help="Bash .sh output filename", type=str, default='TEST')
    parser.add_argument("--input_file", help="Input file with prefix only of the VCF (will also be output prefix)", type=str, required=True)
    parser.add_argument("--maf", help="Minor allele frequency threshold for PLINK", type=str, required=True)
    parser.add_argument("--pruning", help="Pruning thresholds for PLINK, listed between commas ie '50 10 0.1'", type=str, default='50 10 0.1')
    parser.add_argument("--pca_project", help="Enable PCA projection in smartpca (YES/NO)", type=str, required=True, choices=['YES', 'NO'])
    parser.add_argument("--pca_controls", help="Comma-separated population names for PCA projection Control", type=str)

    args = parser.parse_args()

    with open(args.name+".sh", "w") as o:
        o.write("#!/bin/bash\n\n")
        o.write("#SBATCH -A ealloc_e7679_project1-tk-echo\n")
        o.write("#SBATCH --time=5:00:00\n")
        o.write("#SBATCH --mem=5000\n")
        o.write("#SBATCH --nodes=1\n")
        o.write("#SBATCH --cpus-per-task=1\n")
        o.write("#SBATCH --job-name="+args.name+"\n\n")

        # Convert VCF to PLINK
        write_command(o, "# VCF to PLINK", "plink --vcf "+args.input_file+".vcf --make-bed --out "+args.input_file)

        # MAF Filtering
        maf_output_name = args.input_file+"_maf"+args.maf
        write_command(o, "# MAF Filtering", "plink --bfile "+args.input_file+" --maf "+args.maf+" --make-bed --out "+maf_output_name)

        # Pruning
        prune_output_name = maf_output_name+"_pruned"
        write_command(o, "# Pruning",
                      "plink --bfile "+maf_output_name+" --indep-pairwise "+args.pruning+" --out pruning")
        write_command(o, "", "plink --bfile "+maf_output_name+" --exclude pruning.prune.out --make-bed --out "+prune_output_name)

        # Convert PLINK to EIGENSTRAT
        create_eigenstrat_conversion_file(o, prune_output_name)

	# Enforce that pca_controls can only be used if pca_project is 'YES'
        if not args.pca_controls and args.pca_project == 'YES':
            print("Error: --pca_project YES can only be used when a populations list is provided to --pca_controls.")
            sys.exit(1)
        
        # Process PCA Projection
        if args.pca_project == 'YES':
            prepare_pca_projection_yes(o, prune_output_name, args.pca_controls)
      	    # Prepare smartpca parameter file
            create_smartpca_param_file_yes(o, prune_output_name)
   	     
        elif args.pca_project == 'NO':
            create_smartpca_param_file_no(o, prune_output_name)   	

        # Run smartpca
        write_command(o, "# Run smartpca", "smartpca -p smartpca_"+prune_output_name+".par")

if __name__ == "__main__":
    main()
