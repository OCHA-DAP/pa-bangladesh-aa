import cdsapi
import zipfile
import os
from pathlib import Path
import json
import pandas as pd
from netCDF4 import Dataset
import numpy as np
from datetime import date, timedelta
import shutil


Bahadurabat_GLOFAS_LON_LAT=[89.65,25.15]
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
GLOFAS_DS_FILENAME='CEMS_ECMWF_dis24_{}_glofas_v2.1.nc'
GLOFAS_DS_FOLDER='GLOFAS_data'

def unzip(zip_file_path, save_path):
    print(f'Unzipping {zip_file_path}')
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(save_path)

def get_GLOFAS_zip(c_api,year,folder):
    
    Path(folder).mkdir(parents=True, exist_ok=True)

    c_api.retrieve(
    'cems-glofas-historical',
    {
        'format': 'zip',
        'dataset': 'Consolidated reanalysis',
        'variable': 'River discharge',
        'version': '2.1',
        'year': '{}'.format(year),
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
    },
    '{}/download_{}.zip'.format(folder,year))

def extract_dis24_val(date,folder):
    try:
        glofas_ds_name='{}/{}'.format(folder,GLOFAS_DS_FILENAME.format(date.strftime("%Y%m%d")))
        glofas = Dataset(glofas_ds_name,'r')

        lats = glofas.variables['lat'][:] 
        lons = glofas.variables['lon'][:]
        
        # latitude lower and upper index
        lonbound = np.argmin(np.abs( lons - Bahadurabat_GLOFAS_LON_LAT[0]))
        latbound = np.argmin(np.abs( lats - Bahadurabat_GLOFAS_LON_LAT[1]))

        # variables are lon,lat,time,dis24
        discharge = glofas.variables['dis24'][:,latbound,lonbound]
        return discharge
    except Exception:
        # print(f'discharge data not available for {date}')
        return None

def get_glofas_df(year,folder):
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    delta = timedelta(days=1)
    glofas_df=pd.DataFrame(columns=['dis24'])
    while start_date <= end_date:
        # print(start_date.strftime("%Y-%m-%d"))
        glofas_discharge=extract_dis24_val(start_date,folder)
        if glofas_discharge is not None:
            glofas_df.at[start_date,'dis24']=glofas_discharge
        start_date += delta
    glofas_df.index=pd.to_datetime(glofas_df.index)
    glofas_df = glofas_df.resample('D').mean().interpolate(method='linear')
    return glofas_df

c = cdsapi.Client()
year=2019

for year in range(1979,2021):
    print(year)
    folder='{}/{}/{}'.format(DIR_PATH,GLOFAS_DS_FOLDER,year)
    get_GLOFAS_zip(c,year,folder)
    unzip('{}/download_{}.zip'.format(folder,year),folder)
    glofas_df=get_glofas_df(year,folder)
    glofas_df.to_csv('{}/{}/{}.csv'.format(DIR_PATH,GLOFAS_DS_FOLDER,year))
    shutil.rmtree(folder)