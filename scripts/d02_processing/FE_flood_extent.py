import geopandas as gpd
import pandas as pd
import datetime
import os
import argparse

DATA_DIR = 'data/processed'
SHP_DIR = 'Shapefiles'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('adm_level', help='Admin level to calculate flood fraction')
    args = parser.parse_args()
    return args


def calc_extent(adm_grp):
    """
    Calculate the extent of flooding for ADM4 regions using the shapefiles output from GEE script.
    dirname = name of folder with the shapefiles output from
    """
    adm_grp = adm_grp + '_EN'
    # Read in the shapefile for Bangladesh
    adm_shp = gpd.read_file(os.path.join(DATA_DIR, SHP_DIR, 'bdg_shp/bgd_admbnda_adm4_bbs_20180410.shp'))
    # Select unions of interest
    adm_shp = adm_shp[adm_shp['ADM2_EN'].isin(['Bogra', 'Gaibandha', 'Jamalpur', 'Kurigram', 'Sirajganj'])]
    # Set the crs
    adm_shp = adm_shp.to_crs('ESRI:54009')
    # Dissolve the shp if necessary
    if adm_grp != 'ADM4_EN':
        adm_shp = adm_shp.dissolve(by=adm_grp).reset_index()
    adm_shp.loc[:, 'adm_area'] = adm_shp['geometry'].area
    # Get all of the dates from the shapefiles in the directory
    dates = []
    for d in os.listdir(os.path.join(DATA_DIR, SHP_DIR)):
        sp = d.split('-')
        if d.startswith('BGD') and d.endswith('shp'):
            dates.append((sp[1] + '-' + sp[2] + '-' + sp[3] + '-' + sp[4] + '-' + sp[5]).split('.')[0])
    # Create the output dataframe
    output_df = pd.DataFrame()
    # Loop through all shapefiles and calculate the flood extent
    for date in dates:
        print(date)
        fname = os.path.join(DATA_DIR, SHP_DIR + f'/BGD_Floods-{date}.shp')
        flood_shp = gpd.read_file(fname)
        flood_shp = flood_shp.to_crs('ESRI:54009')
        intersection = gpd.overlay(adm_shp, flood_shp, how='intersection')
        intersection = intersection.dissolve(by=adm_grp)
        flood_extent = intersection['geometry'].area
        flood_extent = flood_extent.rename('flooded_area')
        output_df_part = pd.merge(adm_shp, flood_extent.to_frame(), left_on=adm_grp, right_index=True)
        output_df_part.loc[:, 'date'] = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
        output_df = output_df.append(output_df_part)
    output_df.loc[:, 'flood_fraction'] = output_df['flooded_area'] / output_df['adm_area']
    output_df.to_excel(os.path.join(DATA_DIR, f'Sentinel-1-BGD-Flooding-{adm_grp}-TOTAL.xlsx'))
    return output_df


if __name__ == "__main__":
    arg = parse_args()
    calc_extent(arg.adm_level)
