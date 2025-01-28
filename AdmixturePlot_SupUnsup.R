# Script to plot ADMIXTURE results
# Usage Rscript script.R supervised/unsupervised prefix_admixture_output K_max pop_order

## What you will need:

## 1. Indicate whether the script will handle the admxiture results obtained from
## a 'supervised' admixture run
## or an 'unsupervised' admixture run

## 2. ADMIXTURE outputs
## write the file name without the K value and the suffix 
## ie. my_admixture_analysis_output.3.Q -> my_admixture_analysis_output 

## 2a. FAM file with Group and ID labels
## The script will look for the fam file, by adding '.fam' to the admixture file name
## my_admixture_analysis_output -> my_admixture_analysis_output.fam

## 3. Number of maximum k you ran
## if it is an 'unsupervised' admixture run, the script will look for all output files from 1 to k
## if it in a 'supervised' admixture run, the script will only look for the k given
## ie. Rscript script.R supervised prefix_admixture_output 2 PopA,PopB,PopC
## ie. > will look for prefix_admixture_output.2.Q
## ie. Rscript script.R unsupervised prefix_admixture_output 10 PopA,PopB,PopC
## ie. > will look for prefix_admixture_output.1.Q, prefix_admixture_output.N.Q, prefix_admixture_output.10.Q 

## 4. The list of the Populations in the specific order you want to plot them
## For now, please give the entire list in the cmd line, I'll add the option to read the list
## from a separate file/table later

###########################
##### PACKAGES CHECKS #####
###########################

## Checking if you have installed RColorBrewer and ggplot2

list.of.packages <- c("RColorBrewer", "ggplot2")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)

###########################
####### ARGS CHECKS #######
###########################

args = commandArgs(trailingOnly=TRUE)

approach = args[1]
admixture_file = args[2]
K_max = as.integer(args[3])
pop_order = unlist(strsplit(args[4],','))

##########################
####### FUNCTIONS ########
##########################

get_popnames <- function(current_K) {
  # Function to get population labels, ID names and relative admixture results
  fam_file = read.table(paste0(admixture_file,'.fam'))
  adm_file = read.table(paste0(admixture_file,".",current_K,".Q"))
  
  # Returns ID, Group, and ADMIXTURE proportions
  return(cbind(fam_file[,1:2],adm_file))
}



##########################
######## STARTING ########
##########################

if (approach == 'supervised') {
  print("Plotting Supervised ADMIXTURE")
  pdf("supADMXITURE_plot.pdf",width = 30,height = 15)
  
  pop_sadm_file = get_popnames(K_max)
  
  # split admixture results by group / value in first column
  adm.splitted = split(pop_sadm_file[,-c(1:2)], pop_sadm_file[,1])
  
  # Order file based on order list given, remove grouping
  adm.reordered <- adm.splitted[pop_order]
  adm.reordered <- do.call(rbind,adm.reordered)
  
  # Set Number of colors based on K
  colors <- (rainbow(K_max))
  
  # Plotting settings
  par(mar=c(20,3,3,1))
  barplot(t(adm.reordered),col=colors,border=NA,space = 0,
          names.arg = rep("",nrow(adm.reordered)),axes = F, main = paste0("K",K_max),
          cex.main = 2)
  
  axis(2,line=-0.1,las=2,cex=0.6)
  newrows <- gsub (replacement = "",pattern ="\\.[0-9]*" ,x =rownames(adm.reordered))
  pops=unique(newrows)
  labels <- sapply(pops,function(X) median(which(newrows==X)))
  lines <- sapply(pops,function(X) max(which(newrows==X)))
  abline(v=lines,col="white",lwd=2)
  text(x =labels,y = -0.02,labels = names(labels),
       cex=1.5, srt=70,xpd=NA,adj = 1) 
  dev.off()
  
} else if (approach == 'unsupervised') {
  print("Plotting Unsupervised ADMIXTURE")
  pdf("unsupADMXITURE_plot.pdf",width = 30,height = 15)
  
  for (current_k in 1:K_max) {
    pop_uadm_file.tmp = get_popnames(current_k)
    
    # split admixture results by group / value in first column
    adm.splitted = split(pop_uadm_file.tmp[,-c(1:2)], pop_uadm_file.tmp[,1])
    
    # Order file based on order list given, remove grouping
    adm.reordered <- adm.splitted[pop_order]
    adm.reordered <- do.call(rbind,adm.reordered)
    
    # Set Number of colors based on K
    colors <- (rainbow(current_k))
    
    # Plotting settings
    par(mar=c(20,3,3,1))
    barplot(t(adm.reordered),col=colors,border=NA,space = 0,
            names.arg = rep("",nrow(adm.reordered)),axes = F, main = paste0("K",current_k),
            cex.main = 2)
    
    axis(2,line=-0.1,las=2,cex=0.6)
    newrows <- gsub (replacement = "",pattern ="\\.[0-9]*" ,x =rownames(adm.reordered))
    pops=unique(newrows)
    labels <- sapply(pops,function(X) median(which(newrows==X)))
    lines <- sapply(pops,function(X) max(which(newrows==X)))
    abline(v=lines,col="white",lwd=2)
    text(x =labels,y = -0.02,labels = names(labels),
         cex=1.5, srt=70,xpd=NA,adj = 1) }
  dev.off()
} else {
  print('I do not recognize approach given, please write "supervised" or "unsupervised"')
}

