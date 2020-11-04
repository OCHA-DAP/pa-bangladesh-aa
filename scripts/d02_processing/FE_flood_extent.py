import geopandas as gpd
import pandas as pd
import datetime
import os

DATA_DIR = 'data/processed'
SHP_DIR = 'Shapefiles'

def calc_extent(ADM_GRP):
    """
    Calculate the extent of flooding for ADM4 regions using the shapefiles output from GEE script.
    dirname = name of folder with the shapefiles output from
    """

    # Read in the shapefile for Bangladesh
    adm_shp = gpd.read_file(os.path.join(DATA_DIR, SHP_DIR, 'bdg_shp/bgd_admbnda_adm4_bbs_20180410.shp'))
    # Select unions of interest
    adm_shp = adm_shp[adm_shp['ADM2_EN'].isin(['Bogra', 'Gaibandha', 'Jamalpur', 'Kurigram', 'Sirajganj'])]
    # Set the crs
    adm_shp = adm_shp.to_crs('ESRI:54009')
    # Dissolve the shp if necessary
    if ADM_GRP != 'ADM4_EN':
        adm_shp = adm_shp.dissolve(by=ADM_GRP).reset_index()
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
        intersection = intersection.dissolve(by=ADM_GRP)
        flood_extent = intersection['geometry'].area
        flood_extent = flood_extent.rename('flooded_area')
        output_df_part = pd.merge(adm_shp, flood_extent.to_frame(), left_on=ADM_GRP, right_index=True)
        output_df_part.loc[:, 'date'] = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
        output_df = output_df.append(output_df_part)
    output_df.loc[:, 'flood_fraction'] = output_df['flooded_area'] / output_df['adm_area']
    output_df.to_excel(os.path.join(DATA_DIR, f'Sentinel-1-BGD-Flooding-{ADM_GRP}-TOTAL.xlsx'))
    return output_df


# Run the function to generate the flood extent data at different admin levels
#admin_areas = ['ADM4_PCODE', 'ADM2_PCODE']
#for area in admin_areas:
#    calc_extent(area)

# calc_extent('ADM4_PCODE')