import pandas as pd
import os

DATA_DIR = 'data/processed'


def read_data(fname):
    return pd.read_excel(os.path.join(DATA_DIR, fname))