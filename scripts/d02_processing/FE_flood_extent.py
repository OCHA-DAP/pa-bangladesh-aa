import geopandas as gpd
import pandas as pd
import datetime
import os


def get_gee_files(shp_dir):
    """
    Get the file names from the GEE outputs.
    """
    dates = []
    for d in os.listdir(shp_dir):
        sp = d.split('-')
        if d.startswith('BGD') and d.endswith('shp'):
            dates.append((sp[1] + '-' + sp[2] + '-' + sp[3] + '-' + sp[4] + '-' + sp[5]).split('.')[0])
    return dates


def clean_df(df, adm):
    """
    Gets rid of redundant columns, converts to date time format
    df: dataframe output from FE_flood_extent.py
    group: ADM4, ADM3, ADM2, ADM1
    """
    name = adm + '_EN'
    pcode = adm + '_PCODE'
    copy = df
    copy['date'] = pd.to_datetime(copy['date'], format="%Y-%m-%d").dt.strftime('%Y-%m-%d')
    output = copy[[name, pcode, 'flood_fraction', 'date']]
    return output


def calc_extent(adm, shp_dir, data_dir):
    """
    Calculate the extent of flooding for ADM4 regions using the shapefiles output from GEE script.
    dirname = name of folder with the shapefiles output from
    """
    adm_grp = adm + '_PCODE'  # Need to do by pcode because admin names are not unique
    # Read in the shapefile for Bangladesh
    adm_shp = gpd.read_file(os.path.join(shp_dir, 'bdg_shp/bgd_admbnda_adm4_bbs_20180410.shp'))
    # Select unions of interest
    adm_shp = adm_shp[adm_shp['ADM2_EN'].isin(['Bogra', 'Gaibandha', 'Jamalpur', 'Kurigram', 'Sirajganj'])]
    # Set the crs
    adm_shp = adm_shp.to_crs('ESRI:54009')
    # Dissolve the shp if necessary
    if adm_grp != 'ADM4_EN':
        adm_shp = adm_shp.dissolve(by=adm_grp).reset_index()
    adm_shp.loc[:, 'adm_area'] = adm_shp['geometry'].area
    # Get all of the dates from the shapefiles in the directory
    dates = get_gee_files(shp_dir)
    # Create the output dataframe
    output_df = pd.DataFrame()
    # Loop through all shapefiles and calculate the flood extent
    for date in dates:
        print(date)
        fname = os.path.join(shp_dir + f'/BGD_Floods-{date}.shp')
        flood_shp = gpd.read_file(fname)
        flood_shp = flood_shp.to_crs('ESRI:54009')
        intersection = gpd.overlay(adm_shp, flood_shp, how='intersection')
        intersection = intersection.dissolve(by=adm_grp)
        flood_extent = intersection['geometry'].area
        flood_extent = flood_extent.rename('flooded_area')
        output_df_part = pd.merge(adm_shp, flood_extent.to_frame(), left_on=adm_grp, right_index=True)
        output_df_part.loc[:, 'date'] = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
        output_df = output_df.append(output_df_part)
    # Calculate the flooded fraction
    output_df.loc[:, 'flood_fraction'] = output_df['flooded_area'] / output_df['adm_area']
    # Clean the dataframe
    output_df = clean_df(output_df, adm)
    output_df.to_csv(os.path.join(data_dir, f'{adm}_flood_extent_sentinel.csv'), index=False)
    #output_df.to_excel(os.path.join(DATA_DIR, OUTPUT_DIR, f'{adm}_flood_extent_sentinel.xlsx'))
    return output_df
