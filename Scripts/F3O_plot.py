#!/usr/bin/env python
# coding: utf-8

# In[21]:


import argparse
import os
import sys


# In[22]:


import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# In[32]:


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


# In[30]:


def save_f3_plot_html(dataframe, output_path):
    """
    Creates an F3 plot and saves it as an interactive HTML file.

    Parameters:
        dataframe (pd.DataFrame): The input dataframe containing the data.
                                  Assumes columns: ['f_3', 'std_err', 'X'].
        output_path (str): The file path to save the HTML file.
    """
    # Sort the dataframe by f3 values in descending order
    dataframe_sorted = dataframe.sort_values(by="f_3", ascending=False)

    # Create the figure
    fig = go.Figure(go.Scatter(
        x=dataframe_sorted["f_3"].astype(float),
        y=list(range(len(dataframe_sorted))),
        error_x=dict(array=dataframe_sorted["std_err"].astype(float), visible=True),
        mode='markers',
        marker=dict(color='blue')
    ))

    # Update the layout
    fig.update_layout(
        title="F3(Target, X; Yoruba)",
        xaxis_title="F3(Target, X; Yoruba)",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(dataframe_sorted))),
            ticktext=dataframe_sorted["X"],
            autorange="reversed"  # Reverse the y-axis to show highest values at the top
        ),
        height=800,
        width=600
    )

    # Save the plot as an HTML file
    fig.write_html(output_path)
    print(f"Plot saved to {output_path}")


# In[ ]:


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process F3 results and generate an HTML plot.")
    parser.add_argument("pathtofile", type=str, help="Path to the F3 results file.")
    parser.add_argument("outputfile", type=str, help="Path to save the generated HTML plot.")
    
    args = parser.parse_args()

    # Validate the input file
    if not os.path.isfile(args.pathtofile):
        print(f"Error: The file '{args.pathtofile}' does not exist.")
        sys.exit(1)

    # Process the F3 results and save the plot
    f3o_res_sorted = process_f3_results(args.pathtofile)
    save_f3_plot_html(f3o_res_sorted, args.outputfile)

if __name__ == "__main__":
    main()

