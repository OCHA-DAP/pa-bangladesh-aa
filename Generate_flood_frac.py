from scripts.d02_processing import FE_flood_extent as fe
from scripts.d02_processing import FE_clean_data as cd
from scripts.d03_analysis import FE_fit_function as ff

import pandas as pd
import argparse
from datetime import datetime
import numpy as np

# SHP_DIR =
# OUTPUT_DIR =


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('adm_level', help='Admin level to calculate flood fraction')
    args = parser.parse_args()
    return args


def calc_fit(adm_grp):
    dates = pd.DataFrame([])
    flood_extents = pd.DataFrame([])

    for adm in df1[adm_grp + '_EN'].unique():

        # Fit the data
        df2 = cd.select_df(df1, adm)  # New grouped dataframe
        x, y = ff.get_xy(df2)[0], ff.get_xy(df2)[1]  # Get the x and y
        x_new = np.linspace(x[0], x[-1], 85)  # Generate new x data (at daily intervals)

        # TODO: Some regions don't have observations for every date, not incl when there is 0 flooding
        # Need to break out when there aren't enough original points to fit function
        if len(x) < 10:
            print(adm)
            print(len(x))
            continue

        # New y values using same x data to calc the error
        y_g_old = ff.gauss(x, *ff.gauss_fit(x, y))  # Generate Gaussian fitted y data
        y_p_old = ff.poly_fit(x, x, y, 3)  # Generate polynomial fitted y data - degree 3

        # New y values using daily x data to get better peak estimate
        y_g_new = ff.gauss(x_new, *ff.gauss_fit(x, y))  # Generate Gaussian fitted y data
        y_p_new = ff.poly_fit(x_new, x, y, 3)  # Generate polynomial fitted y data - degree 3

        # Calc the rmse to compare poly vs gauss
        rmse_g = ff.rmse(y_g_old, y)
        rmse_p = ff.rmse(y_p_old, y)

        # Get the peak dates
        date_actual = datetime.strptime(ff.get_peak(x, y), "%Y-%m-%d")
        date_g = datetime.strptime(ff.get_peak(x_new, y_g_new), "%Y-%m-%d")
        date_p = datetime.strptime(ff.get_peak(x_new, y_p_new), "%Y-%m-%d")

        # Calculate the difference between dates
        act_g = (date_actual - date_g).days
        act_p = (date_actual - date_p).days

        # Create dict with the results - flood extent
        flood_extent = pd.DataFrame(
            {'ADM': adm,
             'DATE': x_new,
             'FLOOD_EXTENT_G': y_g_new,
             'FLOOD_EXTENT_P': y_p_new})
        flood_extents = flood_extents.append(flood_extent, ignore_index=True)

        # Create dict with the results - peak dates
        result = {'ADM': adm,
                  'RMSE_G': rmse_g,
                  'RMSE_P': rmse_p,
                  'PEAK_ACT': date_actual,
                  'PEAK_G': date_g,
                  'PEAK_P': date_p,
                  'DIFF_ACT_G': act_g,
                  'DIFF_ACT_P': act_p}
        dates = dates.append(result, ignore_index=True)


if __name__ == "__main__":
    arg = parse_args()
    # Calculate the flood fraction from Sentinel-1 data for the desired admin level
    flood_extent = fe.calc_extent(arg.adm_level)
    # Fit function to the flood fraction estimates from Sentinel-1 and calculate peak flood dates
    df1 = cd.group_df(flood_extent, arg.adm_level)
