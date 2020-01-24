# DSP_hackthepoacher

As a very first step, init.py should be executed to transform the mock data csv to the workable format of a pandas dataframe.

Then, main.py may be executed. The working code for this process can be found in locating_phones.py and to_usable_format.py. The former analyses the phone detections at all timestamps to find out which detections stem from the same phone. To all found phones, a unique ID and an estimated location is assigned. In case the former code is executed in multiple iterations, as it was in our case, multiple files exist with resulting data. The code in to_usable_format.py merges those files and creates a clean final dataframe.

The file poacher_risks.py is executed using the dataframe that resulted from running main.py as input. This code assigns a risk value to phones, indicating the estimated chance that that phone belongs to a poacher.

The file track_phones.py makes an attempt to find out which phones, detected at different timestamps, are in reality the same phone. Phones that are expected to be the same are assigned a same unique ID to indicate this.

The file to_json.py exports the last 30 days of all data in the resulting dataframe to an AWS s3 bucket. From this bucket, it can be loaded into the built application.

Finally, the phones_to_map.ipynb file stands a little apart from the rest of the code. This notebook was used to visualise the locations of all detections, phones, tourist lodges etc. This may be used to get more insight in the data.