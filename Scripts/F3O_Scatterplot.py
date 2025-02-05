#!/usr/bin/env python
# coding: utf-8

# In[1]:


import argparse
import os
import sys
import pandas as pd
import plotly.graph_objects as go


# In[3]:


def process_f3_results(file_path):
    """
    Processes the F3 results from a F3 output file and returns a sorted dataframe.

    Parameters:
        file_path (str): Path to the input file.

    Returns:
        pd.DataFrame: A sorted dataframe with processed F3 results.
                      Columns: ['Col1', 'X', 'Target', 'Outgroup', 'f_3', 'std_err', 'Zscore', 'SNPs']
    """
    # Load the file
    f3o_res = pd.read_csv(file_path)

    # Filter rows containing 'result' in the first column
    f3o_res2 = f3o_res[f3o_res.iloc[:, 0].str.contains('result')]

    # Split the first column on ':' and extract the second part
    f3o_res2 = f3o_res2.iloc[:, 0].str.split(':', expand=True)

    # Further split the second part into multiple columns
    f3o_res_cleaned = f3o_res2.iloc[:, 1].str.split(r'\s+', expand=True)

    # Rename the columns
    f3o_res_cleaned.columns = ['Col1', 'X', 'Target', 'Outgroup', 'f_3', 'std_err', 'Zscore', 'SNPs']

    # Sort the dataframe by the 'f_3' column in descending order
    f3o_res_sorted = f3o_res_cleaned.sort_values(by="f_3", ascending=False)

    # Return the sorted dataframe
    return f3o_res_sorted

def save_comparison_plot_html(df1, df2, output_path):
    """
    Creates a scatter plot comparing X values from two dataframes and saves it as an HTML file.

    Parameters:
        df1 (pd.DataFrame): Data from the first file.
        df2 (pd.DataFrame): Data from the second file.
        output_path (str): The file path to save the HTML file.
    """
    # Merge the dataframes on the 'X' column to ensure they have matching rows
    merged_df = pd.merge(df1, df2, on='X', suffixes=('_file1', '_file2'))

    # Create the scatter plot
    fig = go.Figure(go.Scatter(
        x=merged_df['f_3_file2'].astype(float),
        y=merged_df['f_3_file1'].astype(float),
        mode='markers+text',
        marker=dict(color='blue'),
        text=merged_df['X'],  # Add labels from the 'X' column
        textposition='top center'
    ))

    # Update the layout
    fig.update_layout(
        title="Comparison of F3 Values Between Two Files",
        xaxis_title="F3(Target, X; Yoruba) - File 2",
        yaxis_title="F3(Target, X; Yoruba) - File 1",
        height=800,
        width=800
    )

    # Save the plot as an HTML file
    fig.write_html(output_path+'.html')
    print(f"Comparison plot saved to {output_path}")


# In[2]:


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Compare F3 results from two files and generate a scatter plot.")
    parser.add_argument("file1", type=str, help="Path to the first F3 results file.")
    parser.add_argument("file2", type=str, help="Path to the second F3 results file.")
    parser.add_argument("outputfile", type=str, help="Path to save the generated HTML scatter plot.")

    args = parser.parse_args()

    # Validate the input files
    if not os.path.isfile(args.file1):
        print(f"Error: The file '{args.file1}' does not exist.")
        sys.exit(1)

    if not os.path.isfile(args.file2):
        print(f"Error: The file '{args.file2}' does not exist.")
        sys.exit(1)

    # Process the F3 results
    df1 = process_f3_results(args.file1)
    df2 = process_f3_results(args.file2)

    # Check for consistency in the 'X' column
    if not set(df1['X']).issubset(set(df2['X'])) or not set(df2['X']).issubset(set(df1['X'])):
        print("Error: The files do not have matching 'X' columns.")
        sys.exit(1)

    # Generate the scatter plot
    save_comparison_plot_html(df1, df2, args.outputfile)

if __name__ == "__main__":
    main()

