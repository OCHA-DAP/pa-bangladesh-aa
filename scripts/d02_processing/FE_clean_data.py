import pandas as pd


def group_df(df, group):
    """

    Group flood extent estimates by admin area - takes the mean of the ADM4 calculations
    df: dataframe output from FE_flood_extent.py
    group: ADM4_EN, ADM3_EN, ADM2_EN, ADM1_EN

    """

    copy = df
    copy['date'] = pd.to_datetime(copy['date'], format="%Y-%m-%d").dt.strftime('%Y-%m-%d')
    # copy = copy.groupby(['date', group]).mean().reset_index()
    output = copy[[group, 'flood_fraction', 'date']]
    return output


def select_df(df, select):
    """

    Select single admin area from a grouped df
    df: dataframe output from group_df()
    group: name of the admin area to select

    """
    copy = df
    adm_col = copy.columns[0]  # Assuming that the column with the Admin area names is first in the dataframe
    return df.loc[df[adm_col] == select].reset_index()
