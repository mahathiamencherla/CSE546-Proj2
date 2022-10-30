from boto3 import client as boto3_client
import os

input_bucket = "proj2-input-bucket"
output_bucket = "proj2-output-bucket"
test_cases = "test_cases/"

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

s3_client = boto3_client('s3',
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key= AWS_SECRET_ACCESS_KEY)


def clear_input_bucket():
	global input_bucket
	# s3 = s3_client('s3')
	list_obj = s3_client.list_objects_v2(Bucket=input_bucket)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3_client.delete_object(Bucket=input_bucket, Key=key)
	except:
		print("Nothing to clear in input bucket")
	
def clear_output_bucket():
	global output_bucket
	# s3 = boto3_client('s3')
	list_obj = s3_client.list_objects_v2(Bucket=output_bucket)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3_client.delete_object(Bucket=output_bucket, Key=key)
	except:
		print("Nothing to clear in output bucket")

def upload_to_input_bucket_s3(path, name):
	global input_bucket
	# s3 = boto3_client('s3')
	s3_client.upload_file(path + name, input_bucket, name)

	
	
def upload_files(test_case):	
	global input_bucket
	global output_bucket
	global test_cases
	
	
	# Directory of test case
	test_dir = test_cases + test_case + "/"
	
	# Iterate over each video
	# Upload to S3 input bucket
	for filename in os.listdir(test_dir):
		if filename.endswith(".mp4") or filename.endswith(".MP4"):
			print("Uploading to input bucket..  name: " + str(filename)) 
			upload_to_input_bucket_s3(test_dir, filename)
			
	
def workload_generator():
	
	print("Running Test Case 1")
	upload_files("test_case_1")

	print("Running Test Case 2")
	upload_files("test_case_2")
	

# clear_input_bucket()
clear_output_bucket()	
workload_generator()	

	

