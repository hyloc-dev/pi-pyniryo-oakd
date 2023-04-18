import os
import glob

def grab_recent():
	# define the directory path
	dir_path = "image_eval_data/"

	# create a list of jpeg files in the directory
	jpeg_files = glob.glob(os.path.join(dir_path, "*.jpeg"))

	# sort the list of files by modification time, most recent first
	jpeg_files.sort(key=os.path.getmtime, reverse=True)

	# get the filename of the most recent jpeg file
	most_recent_jpeg = os.path.basename(jpeg_files[0])

	most_recent_jpeg_modified = dir_path + most_recent_jpeg

	print(most_recent_jpeg_modified)
	return most_recent_jpeg_modified

