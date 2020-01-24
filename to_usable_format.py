import pandas as pd
import numpy as np
import pickle
import re
import random
import string

def merge_pickles(filenames):
	df = pd.read_pickle(filenames[0])
	ts = set()
	for f in filenames[1:]:
		df0 = pd.read_pickle(f)

		tsx = set(df['timestamp'].unique())
		tsy = set(df0['timestamp'].unique())

		ts = ts.union(tsx & tsy)
		df = df.append(df0)

	df['len_id'] = df['phone_id'].map(lambda x: len(x))

	df = df.reset_index().drop(columns=['index'])
	dropls = list()
	for t in ts:
	    dropls += list(df[df['len_id']==5][df['timestamp']==t].index)
	df = df.drop(dropls)

	return df

def reshape_df(df):
	df['len_id'] = df['phone_id'].map(lambda x: len(x))

	df['date'] = df['timestamp'].map(lambda x: str(x.year)+'/'+str(x.month)+'/'+str(x.day))
	df['minute'] = df['timestamp'].map(lambda x: x.minute).map("{:02}".format)
	df['hour'] = df['timestamp'].map(lambda x: x.hour).map("{:02}".format)
	df['time'] = df['hour'].map(str) + ":" + df['minute'].map(str)

	df = df.drop_duplicates('phone_id')
	df5 = df[df['len_id']==5]
	df10 = df[df['len_id']==10]

	df5[['phone_cor_y','phone_cor_x']] = pd.DataFrame(df5['phone_cor_rssi'].values.tolist(), index=df5.index)
	df = df5.append(df10, sort=False)
	df = df[['timestamp', 'date', 'time', 'phone_id', 'phone_cor_y', 'phone_cor_x']]
	df = df.reset_index().drop(columns=['index'])

	df = to_lonlat(df)

	return df

def to_lonlat(df):
	# y = latitude, x = longitude
	x_cors = [26.013530731201172, 26.06018829345703, 26.106700897216797, 26.153261184692383, 26.2000675201416, 26.246292114257812]
	y_cors = [-14.73619556427002, -14.779047012329102, -14.826595306396484, -14.873619079589844, -14.916463851928711, -14.962969779968262, -15.007390022277832]

	df['phone_lat'] = find_lonlat_values(df, y_cors, 'y')
	df['phone_lon'] = find_lonlat_values(df, x_cors, 'x')

	df = df[['timestamp', 'date', 'time', 'phone_id', 'phone_lat', 'phone_lon']]

	return df

def find_lonlat_values(df, cors, axis):
	xy_min = cors[0]
	xy_max = cors[-1]

	diff = list()
	for i in range(0,len(cors)-1):
	    diff.append(cors[i+1]-cors[i])
	    
	diff_mean = np.mean(diff)

	df['temp'] = df['phone_cor_'+axis]/255
	df['temp'] = df['temp'].map(lambda x: int(np.floor(x)))

	lst = list()
	for i in range(0,len(df)):
	    lonlat = xy_min
	    base = df['temp'][i]
	    lonlat += sum(diff[:base])
	    if base < len(diff):
	        lonlat += ((df['phone_cor_'+axis][i]%255)/255) * diff[base]
	    else:
	        lonlat += ((df['phone_cor_'+axis][i]%255)/255) * diff_mean
	    lst.append(lonlat)

	return lst