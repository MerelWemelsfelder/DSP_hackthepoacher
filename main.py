import pandas as pd
import numpy as np
import pickle
import re
import random
import string

from locating_phones import *
from to_usable_format import *

# SETTINGS
TS_START = 0    
TS_STOP = 23801
STEPS = 50

def main():
    df = pd.read_pickle('pickles/df_init.pickle')
    df = set_phone_columns(df)
    timestamps = list(df['timestamp'].unique())
    
    for i in range(TS_START, TS_STOP, STEPS):
        print("timestamp index: "+str(i))
        print("part A")
        df = iterate(df, timestamps, i, STEPS, TS_STOP, 'A')
        print("part B")
        df = iterate(df, timestamps, i, STEPS, TS_STOP, 'B')
        print("part C")
        df = iterate(df, timestamps, i, STEPS, TS_STOP, 'C')

        export_dataframe(df, timestamps, i, i+STEPS)

    df = merge_pickles(['pickles/df_phones.pickle', 'pickles/part2/C/df_part2C_6543T.pickle', 'pickles/part2/C/df_part2C_8835T.pickle'])
    df = reshape_df(df)

    pickle.dump(df, open("pickles/phones_located.pickle", "wb"))

if __name__ == "__main__":
    main()
