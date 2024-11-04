#!/usr/bin/env python
# coding: utf-8

# This script will create a .sh file that:
# will convert vcf to plink
# plink to eigenstrat format
# and run PCA with smartpca

#!/bin/python

import argparse
import os

parser = argparse.ArgumentParser(description="Converts vcf to plink to eigenstrat and runs smartpca")

parser.add_argument("--name", help="bash .sh namefile",type=str, default = 'TEST')
parser.add_argument("--input_file", help="Input file prefix, will be also output file prefix",type=str, default = None)
parser.add_argument("--maf", help="does minor allele freq step in plink, provide value",type=str, default = None)
parser.add_argument("--pruning", help="does pruning step in plink, provide three values",type=str, default = '50 10 0.1')
parser.add_argument("--pca_project", help="If YES will do projection in smartpca step, otherwise NO",type=str, default = None)
parser.add_argument("--pca_controls", help="List of pop names to use as scaffold in pca projection, comma sep",type=str, default = None)

args = parser.parse_args()

with open (args.name+".sh","w") as o:
    o.write("#!/bin/bash"+"\n")
    o.write("\n")


    # Converting VCF to PLINK
    o.write("#VCF to PLINK \n")
    o.write("plink --vcf "+args.input_file+'.vcf'+" --make-bed --out "+args.input_file+'\n')
    o.write("\n")

    # Filtering PLINK file

    ## MAF
    ### Output name will be called prefix_maf
    o.write("#MAF \n")
    maf_output_name = args.input_file+'_maf'+args.maf
    o.write("plink --bfile "+args.input_file+" --maf "+args.maf+" --out "+maf_output_name+'\n')    
    o.write("\n")


    ## Pruning
    ### Output name will be called prefix_maf_pruned
    o.write("#Pruning \n")
    prune_output_name = maf_output_name+'_pruned'
    o.write("plink --bfile "+maf_output_name+" --indep-pairwise "+args.pruning+" --out pruning"+'\n')
    o.write("plink --bfile "+maf_output_name+" --exclude pruning.prune.out"+" --make-bed --out "+prune_output_name+'\n')
    o.write("\n")
    
    # PLINK to EIGENSTRAT
    o.write("#Converting to EIGENSTRAT \n")
    o.write("echo 'genotypename: "+prune_output_name+".bed \n"+
        "snpname: "+prune_output_name+".bim \n"+
        "indivname: "+prune_output_name+".fam \n"+
        "outputformat: EIGENSTRAT \n"+
        "genotypeoutname: "+prune_output_name+".geno \n"+
        "snpoutname: "+prune_output_name+".snp \n"+
        "indivoutname: "+prune_output_name+".ind \n"+
        "familynames: YES' > convertf_"+prune_output_name+".par")
    o.write("\n")

    o.write("\n")
    o.write("#Editing .ind file \n")
    o.write("sed -r 's/:/ /g' "+prune_output_name+".ind > tmp.ind \n")
    o.write("awk '{print $2,$3,$1}' tmp.ind > tmp.2.ind \n")
    o.write("mv tmp.2.ind "+prune_output_name+"_edit.ind \n")
    o.write("\n")

    if args.pca_project == 'YES':  

        # Creating pop list file for smartpca
        o.write("#Creating pop list file for smartpca \n")
        for controls in args.pca_controls.split(','):
            POP = controls.strip()
            o.write("echo '"+POP+"' >> pop_list.txt \n")
        o.write("\n")

        # PLINK to EIGENSTRAT
        o.write("# Preparing .par file for smartpca \n")
        o.write("# altnormstyle: adjusts how eigenvectors are normalized. When set to NO (default), eigenvectors are normalized in the traditional way based on total variance.   \n")
        o.write("# numoutevec: specifies the number of eigenvectors (principal components) to be output  \n")
        o.write("# numoutevec: sets the number of iterations used to detect outliers in the dataset. Increase rigorous research but also runtime  \n")
        o.write("# numoutlierevec: control how many top principal components are included in the outlier detection process \n")
        o.write("# outliersigmathresh: \n")
        o.write("# qtmode: \n")
        o.write("# lsqproject: when set to YES will use projection \n")
        o.write("# poplistname: list of populations to be used as scaffold \n")
        o.write("\n")

        o.write("echo 'genotypeoutname: "+prune_output_name+".geno \n"+
            "snpoutname: "+prune_output_name+".snp \n"+
            "indivoutname: "+prune_output_name+"_edit.ind \n"+
            "evecoutname: "+prune_output_name+".pca.evec \n" +
            "evaloutname: "+prune_output_name+".eval \n" +
            "altnormstyle: NO\n" +
            "numoutevec: 4\n" +
            "numoutlieriter: 0\n" +
            "numoutlierevec: 0\n" +
            "outliersigmathresh: 6.0\n" +
            "qtmode: 0\n" +
            "lsqproject: YES\n" +
            "poplistname: pop_list.txt' > smartpca_prj_"+prune_output_name+".par")
        o.write("\n")

    elif args.pca_project == 'NO':  

        # PLINK to EIGENSTRAT
        o.write("# Preparing .par file for smartpca \n")
        o.write("# altnormstyle: adjusts how eigenvectors are normalized. When set to NO (default), eigenvectors are normalized in the traditional way based on total variance.   \n")
        o.write("# numoutevec: specifies the number of eigenvectors (principal components) to be output  \n")
        o.write("# numoutevec: sets the number of iterations used to detect outliers in the dataset. Increase rigorous research but also runtime  \n")
        o.write("# numoutlierevec: control how many top principal components are included in the outlier detection process \n")
        o.write("# outliersigmathresh: \n")
        o.write("# qtmode: \n")
        o.write("\n")

        o.write("echo 'genotypeoutname: "+prune_output_name+".geno \n"+
            "snpoutname: "+prune_output_name+".snp \n"+
            "indivoutname: "+prune_output_name+"_edit.ind \n"+
            "evecoutname: "+prune_output_name+".pca.evec \n" +
            "evaloutname: "+prune_output_name+".eval \n" +
            "altnormstyle: NO\n" +
            "numoutevec: 4\n" +
            "numoutlieriter: 0\n" +
            "numoutlierevec: 0\n" +
            "outliersigmathresh: 6.0\n" +
            "qtmode: 0' > smartpca_"+prune_output_name+".par")
        o.write("\n")
        
    # RUN SMARTPCA
    o.write("# Running smartpca \n")
    o.write("smartpca -p smartpca_"+prune_output_name+".par")
