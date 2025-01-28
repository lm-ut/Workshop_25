#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import argparse
import os
import sys


# In[73]:


import plotly.offline as po
import plotly.express as px
import pandas as pd


# In[ ]:


def load_data(file_path):
    """Load PCA data from a file, return a formatted DataFrame."""
    try:
        pca_df = pd.read_csv(file_path, skiprows=1, header=None, sep=r"\s+|:|\t", engine="python")
        pcs_count = len(pca_df.columns) - 3
        pcs = ["PC" + str(i+1) for i in range(pcs_count)]  # PC indices should start from 1
        header = ['POP', 'ID'] + pcs + ['Projection']
        pca_df.columns = header
        
	# Replace '???' in the last column ('CC') with 'Scaffold'
        pca_df['Projection'] = pca_df['Projection'].replace('???', 'Scaffold')
        return pca_df
    except FileNotFoundError:
        sys.exit(f"Error: The file {file_path} was not found.")
    except pd.errors.ParserError:
        sys.exit("Error: The file could not be parsed. Please check the format.")
    except Exception as e:
        sys.exit(f"Error loading file: {e}")


# In[ ]:


def plot_pca(pca_df, output_file):
    """Generate and save an interactive PCA plot."""
    try:
        fig = px.scatter(
            pca_df,
            x='PC1',
            y='PC2',
            color='POP',
            symbol='Projection',
            title="PCA Plot",
            labels={"PC1": "Principal Component 1", "PC2": "Principal Component 2"}
        )
        po.plot(fig, filename=output_file, auto_open=False)
        print("Plot saved as: "+output_file)
    except KeyError:
        sys.exit("Error: Required columns for PCA plot (PC1, PC2) are missing.")
    except Exception as e:
        sys.exit(f"Error creating plot: {e}")


# In[ ]:


def main():
    parser = argparse.ArgumentParser(description="Create HTML interactive PCA plot.")
    parser.add_argument("--input_file", help="File name of the PCA to be plotted", type=str, required=True)
    parser.add_argument("--output_file", help="Output name for the plot (without .html extension)", type=str, required=True)
    args = parser.parse_args()

    # Prepare output filename with .html extension
    output_file = args.output_file+".html"
    
    # Load and process PCA data
    pca_df = load_data(args.input_file)
    
    
    # Generate PCA plot
    plot_pca(pca_df, output_file)


# In[ ]:


if __name__ == "__main__":
    main()

