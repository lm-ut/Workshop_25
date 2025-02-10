library(ggplot2)
library(reshape2)
library(argparse)
library(ggrepel)

# Argument parser
parser <- ArgumentParser()
parser$add_argument("--file1", required=TRUE, help="Prefix for first dataset")
parser$add_argument("--file2", required=TRUE, help="Prefix for second dataset")
parser$add_argument("--target", required=TRUE, help="Comma-separated list of target group names")
parser$add_argument("--k", required=TRUE, type="integer", help="Number of ancestral populations (K)")
args <- parser$parse_args()

# Read the .fam and .Q files for both runs
read_admixture_data <- function(fam_prefix, q_prefix, target_groups, k) {
  fam_file <- paste0(fam_prefix, ".fam")
  q_file <- paste0(q_prefix, ".", k, ".Q")
  
  fam_data <- read.table(fam_file, header=FALSE, stringsAsFactors=FALSE)
  q_data <- read.table(q_file, header=FALSE)
  
  colnames(fam_data) <- c("Group", "ID", "P3", "P4", "P5", "P6")
  
  # Filter by target groups
  target_fam <- fam_data[fam_data$Group %in% target_groups, ]
  
  # Extract ancestry proportions based on selected individuals
  target_q <- q_data[which(fam_data$Group %in% target_groups), 1]  # First ancestry component
  
  return(data.frame(ID=target_fam$ID, Ancestry=target_q))
}

# Convert target argument into a vector
target_groups <- unlist(strsplit(args$target, ","))

# Load both datasets
data1 <- read_admixture_data(args$file1, args$file1, target_groups, args$k)
data2 <- read_admixture_data(args$file2, args$file2, target_groups, args$k)

# Merge data for scatter plot
merged_data <- merge(data1, data2, by="ID", suffixes=c("_imputed", "_non_imputed"))

# Create scatter plot with labels
scatter_plot <- ggplot(merged_data, aes(x=Ancestry_imputed, y=Ancestry_non_imputed, label=ID)) +
  geom_point(alpha=0.7) +
  geom_text_repel(size=3, box.padding=0.5) +
  geom_abline(slope=1, intercept=0, linetype="dashed", color="red") +
  theme_minimal() +
  labs(x="Imputed Genomes", y="Non-Imputed Genomes", title="Scatter Plot of Ancestry Proportions")

# Save plot
ggsave("scatterplot.pdf", plot=scatter_plot, width=6, height=6)