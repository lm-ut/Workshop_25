#!/usr/bin/env python
# coding: utf-8

# This script will create a .sh file that:
# will perform MAF and PRUNING on plink file
# Run unsupervised admixture or supervised admixture


import argparse
import os
import sys


def write_command(o, comment, command):
    """Writes a shell command to the output file with an optional comment."""
    if comment:
        o.write(f"{comment}\n")
    o.write(f"{command}\n\n")


def prepare_pop_file(o, prune_output_name, references):
    """ Prepares pop file for supervised ADMIXTURE. """    
    write_command(o, "# First step of editing pop file from fam file",
                  "awk '{print $0, \"-\"}' "+prune_output_name+".fam > tmp.pop")
    
    for pop in references.split(','):
            write_command(o, f"# Set {pop.strip()} as 7th column of pop file",
                          f"awk -v param='{pop.strip()}' '{{if ($1 == param) $7 = param; print }}'  tmp.pop > tmp.2.pop")
            write_command(o, "", "mv tmp.2.pop tmp.pop")
        
    write_command(o, "Final step of editing pop file", 
                  "awk '{print $7,$2,$3,$4,$5,$6,$7}' tmp.pop > "+prune_output_name+".pop")



def main():
    parser = argparse.ArgumentParser(description="Edit PLINK file and prepare the ADMIXTURE run")

    parser.add_argument("--name", help="Bash .sh output filename", type=str, default='TEST')
    parser.add_argument("--input_file", help="Input file prefix for PLINK file (also output prefix)", type=str, required=True)
    parser.add_argument("--maf", help="Minor allele frequency threshold for PLINK", type=str, required=True)
    parser.add_argument("--pruning", help="Pruning thresholds for PLINK", type=str, default='50 10 0.1')
    parser.add_argument("--approach", help="supervised or unsupervised, if unsupervised provide --K, if supervised provide --reference", type=str, required=True, choices=['supervised', 'unsupervised'])
    parser.add_argument("--k", help="Takes maximum number of K to run", type=str, required=False)
    parser.add_argument("--reference", help="Takes comma separated list of reference populations", required=False, type=str)

    args = parser.parse_args()
    
        # Check required arguments based on the approach
    if args.approach == 'unsupervised' and not args.k:
        parser.error("--k is required for unsupervised approach")
    if args.approach == 'supervised' and not args.reference:
        parser.error("--reference is required for supervised approach")

    with open(args.name+".sh", "w") as o:
        o.write("#!/bin/bash\n\n")

        # MAF Filtering
        maf_output_name = args.input_file+"_maf"+args.maf
        write_command(o, "# MAF Filtering", "plink --bfile "+args.input_file+" --maf "+args.maf+" --make-bed --out "+maf_output_name)

        # Pruning
        prune_output_name = maf_output_name+"_pruned"
        write_command(o, "# Pruning",
                      "plink --bfile "+maf_output_name+" --indep-pairwise "+args.pruning+" --out pruning")
        write_command(o, "", "plink --bfile "+maf_output_name+" --exclude pruning.prune.out --make-bed --out "+prune_output_name)

        # Prepare ADMIXTURE analysis
        if args.approach == 'unsupervised':
            # Run unsupervised ADMIXTURE for all Ks
            K_max = int(args.k)
            for k in range(K_max):
                k = k+1
                write_command(o, "# Run ADMIXTURE", "admixture "+prune_output_name+".bed "+str(k)+" --cv")
        
        elif args.approach == 'supervised':
            prepare_pop_file(o,prune_output_name,args.reference)
            n_refs = len(args.reference.split(','))
            write_command(o, "# Run ADMIXTURE", "admixture --supervised --cv "+prune_output_name+".bed "+str(n_refs))


if __name__ == "__main__":
    main()
