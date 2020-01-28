import pandas as pd
import numpy as np
import pickle
import re
import random
import string
import json
import boto3 

df = pd.read_pickle('pickles/tracked_phones.pickle')
df['month'] = df['timestamp'].map(lambda x: x.month)
df = df[df['month'] == 8]

timestamps = list(df['timestamp'].unique())
timestamps.sort(reverse=True)

dates = list(df['date'].unique())
numbers = range(0,len(dates))

previous_day = np.datetime64(timestamps[0], 'D')
counter = 1

for i in range(0,len(timestamps)):
	# if counter > 30:
	# 	break
	# else:
	t = timestamps[i]
	minute = np.datetime64(t, 'm')
	day = np.datetime64(t, 'D')

	if day != previous_day:
		print(day)
		diff = previous_day - day
		diff = (diff / np.timedelta64(1, 'D')).astype(int)

		previous_day = day
		counter += diff

	s3 = boto3.resource('s3', aws_access_key_id='AKIAYQRTZVKS5F77TBWK', aws_secret_access_key='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')
	s3object = s3.Object('phone-coordinates', str(counter)+' '+str(minute)[-5:]+'.json')

	json_data = df[df['timestamp']==t].to_json(orient='index')
	s3object.put(
	    Body=(bytes(json.dumps(json_data).encode('UTF-8')))
	)
