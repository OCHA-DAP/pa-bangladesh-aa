import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import os
import datetime


def calc_extent(dirname):
    """
    Calculate the extent of flooding for ADM4 regions using the shapefiles output from GEE script.
    dirname = name of folder with the shapefiles output from
    """

    # Read in the shapefile for Bangladesh
    unions_shp = gpd.read_file(f'bdg_shp/bgd_admbnda_adm4_bbs_20180410.shp')
    # Select unions of interest
    unions_shp = unions_shp[unions_shp['ADM2_EN'].isin(['Bogra', 'Gaibandha', 'Jamalpur', 'Kurigram', 'Sirajganj'])]
    # Set the crs
    unions_shp = unions_shp.to_crs('ESRI:54009')
    # Get geom for the unions
    unions_shp.loc[:, 'union_area'] = unions_shp['geometry'].area
    # Get all of the dates from the shapefiles in the directory
    dirname = os.getcwd() + dirname
    dates = []
    for d in os.listdir(dirname):
        sp = d.split('-')
        if d.startswith('BGD') and d.endswith('shp'):
            dates.append((sp[1] + '-' + sp[2] + '-' + sp[3] + '-' + sp[4] + '-' + sp[5]).split('.')[0])
    # Create the output dataframe
    output_df = pd.DataFrame()
    # Loop through all shapefiles and calculate the flood extent
    for date in dates:
        print(date)
        fname = dirname + f'/BGD_Floods-{date}.shp'
        flood_shp = gpd.read_file(fname)
        flood_shp = flood_shp.to_crs('ESRI:54009')
        intersection = gpd.overlay(unions_shp, flood_shp, how='intersection')
        intersection = intersection.dissolve(by='ADM4_PCODE')
        flood_extent = intersection['geometry'].area
        flood_extent = flood_extent.rename('flooded_area')
        output_df_part = pd.merge(unions_shp, flood_extent.to_frame(), left_on='ADM4_PCODE', right_index=True)
        output_df_part.loc[:, 'date'] = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
        output_df = output_df.append(output_df_part)
    output_df.loc[:, 'flood_fraction'] = output_df['flooded_area'] / output_df['union_area']
    output_df.to_excel('Sentinel-1-BGD-Flooding-updated.xlsx')
    return(output_df)


def get_dates(data, sel_union, date_type):
    """
    Return list of the estimated flood start, end, or peak dates from the CDP interview data.
    data = dataframe with the flooding estimates over time for BGD admin-4 regions
    date_type = 'start', 'end', or 'pick'
    sel_union = name of ADM4 region
    """

    col_name = "flood_{}_date".format(date_type)
    # Get only the data for the selected union
    df_selected = data.loc[data['ADM4_EN'] == sel_union]
    # Select the rows from July that will have the estimates in the first row
    mask = (df_selected['date'] >= '2020-07-01') & (df_selected['date'] <= '2020-07-31')
    df_selected = df_selected.loc[mask]
    # Get the potential start date columns
    cols = df_selected.columns[df_selected.columns.str.contains(col_name)]
    # Get all of the start/peak dates within the columns
    # ASSUMPTION that the appropriate date will be in the first row
    dates = [pd.to_datetime(df_selected[col].iloc[0]) for col in cols if
             not pd.isna(pd.to_datetime(df_selected[col].iloc[0]))]
    return dates


def compare_estimates(data, sel_union):
    """
    Return a graph for the selected union, comparing Sentinel-1 estimates with interview estimates.
    data = dataframe with the flooding estimates over time for BGD admin-4 regions
    sel_union = name of ADM4 region
    """

    # Get only the data for the selected union
    df_selected = data.loc[data['ADM4_EN'] == sel_union]
    # Select the relevant flooding estimate data
    # Get the various estimates of flood extent by date (in %)
    flood_extent = df_selected[['flood_fraction', 'Interview_1', 'Interview_2', 'Interview_3', 'date']]
    # Melt data to long format for visualization
    flood_extent_long = flood_extent.melt(id_vars=['date'])
    # Colours for the line graph
    col_mapping = {
        'Interview_1': '#520057',
        'Interview_2': '#db00e8',
        'Interview_3': '#d096d4',
        'flood_fraction': '#ff9626'
    }
    # Get the start, end, and peak times
    start_dates = get_dates(data, sel_union, 'start')
    peak_dates = get_dates(data, sel_union, 'pick')
    end_dates = get_dates(data, sel_union, 'end')
    # Create simple line plot to compare the satellite estimates and interviewed estimates
    fig = plt.figure()
    ax = plt.axes()
    sns.lineplot(x='date', y='value', hue='variable', data=flood_extent_long, palette=col_mapping)
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Percent flooding estimate')
    plt.ylim([0, 110])
    plt.title('Estimates of flooding in {}, Bangladesh'.format(sel_union))

    for date in start_dates:
        plt.axvline(date, ls='--', color='#0fbd09', label='Flood Start', lw=0.75)
    for date in peak_dates:
        plt.axvline(date, ls='--', color='#f20a30', label='Flood Peak', lw=0.75)
    for date in end_dates:
        plt.axvline(date, ls='--', color='#032cfc', label='Flood End', lw=0.75)

    plt.legend(loc='lower right', bbox_to_anchor=(1.05, 1))
    leg = plt.legend()
    leg.get_texts()[1].set_text('Sentinel-1')
    leg.get_texts()[0].set_text('Legend')

    plt.tight_layout()
    plt.savefig("Results_images/{}.png".format(sel_union), bbox_inches='tight', pad_inches=0.2)
