import geopandas as gpd
import pandas as pd
import datetime
import matplotlib.pyplot as plt

dates=['20200701_S1ASC',
'20200703_S1DESC',
'20200713_S1ASC',
'20200715_S1DESC',
'20200719_S1ASC',
'20200721_S1DESC',
'20200725_S1ASC',
'20200727_S1DESC'
]
output_fields=['ADM1_EN','ADM2_EN','ADM3_EN','ADM4_EN','union_area']

# unions_shp=flood_shp=gpd.read_file(f'bgd_admbnda_adm4_bbs_20180410/bgd_admbnda_adm4_bbs_20180410.shp')
# unions_shp=unions_shp[unions_shp['ADM2_EN'].isin(['Bogra','Gaibandha','Jamalpur','Kurigram','Sirajganj'])]
# unions_shp=unions_shp.to_crs('ESRI:54009')
# unions_shp.loc[:,'union_area']=unions_shp['geometry'].area

# output_df=pd.DataFrame()

# for date in dates:
#     flood_shp=gpd.read_file(f'Sentinel-1-Data/BGD_Floods_{date}.shp')
#     flood_shp=flood_shp.to_crs('ESRI:54009')
#     intersection=gpd.overlay(unions_shp, flood_shp, how='intersection')
#     intersection=intersection.dissolve(by='ADM4_PCODE')
#     flood_extent= intersection['geometry'].area
#     flood_extent=flood_extent.rename('flooded_area')
#     output_df_part=pd.merge(unions_shp,flood_extent.to_frame(), left_on='ADM4_PCODE', right_index=True)
#     output_df_part.loc[:,'date']=datetime.datetime.strptime(date[:8],'%Y%m%d')
#     output_df=output_df.append(output_df_part)    
#     print(output_df_part)

# output_df.loc[:,'flood_fraction']=output_df['flooded_area']/output_df['union_area']
# output_df.to_excel('Sentinel-1-BGD-Flooding.xlsx')

df=pd.read_excel('Sentinel-1-BGD-Flooding.xlsx')
# df.groupby('ADM2_EN')['flood_fraction'].plot(legend=True)
df=df.groupby(['date','ADM2_EN']).mean().reset_index()
df=df.set_index(['date'])
df.groupby('ADM2_EN')['flood_fraction'].plot(legend=True)
plt.show()
# print(df)