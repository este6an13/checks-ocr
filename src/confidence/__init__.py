import pandas as pd

# To make sure both dfs have the same rows, in case one was removed from data.xlsx
# This assumes no rows are removed from confidence.xlsx without having removing them from data.xlsx
# which in case would be better to start with fresh new empty xlsx files.
def filter_confidence_df(confidence_df, df):
    # Merge to find common IDs
    merged_df = pd.merge(confidence_df, df[['ID']], on='ID', how='inner')

    # Filter confidence_df based on common IDs
    filtered_confidence_df = confidence_df[confidence_df['ID'].isin(merged_df['ID'])]

    return filtered_confidence_df