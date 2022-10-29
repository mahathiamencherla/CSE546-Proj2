import boto3
import face_recognition
import pickle
import os
import ffmpeg
import boto3
import csv
import shutil

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
# event={'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-west-2', 'eventTime': '2022-10-28T08:11:20.197Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AIDASJUR6HKG2QTMFIMDF'}, 'requestParameters': {'sourceIPAddress': '98.191.174.30'}, 'responseElements': {'x-amz-request-id': 'BG7F524BNPWVKJCN', 'x-amz-id-2': 'DpyCtmgSiOwCUSNZlmRS2gwvALbM/aZJ5BQBIGhq/KsL4c/kSavhmau7hv57xOxrYn2yGzetHVRc+8kX+Y4rYDcq61T+7UFL'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '6055bd1e-bd36-481d-9c7d-a23875a1eb34', 'bucket': {'name': 'test-lambdatrig', 'ownerIdentity': {'principalId': 'A2O3XJ6IOHI26F'}, 'arn': 'arn:aws:s3:::test-lambdatrig'}, 'object': {'key': 'test_1.mp4', 'size': 3610877, 'eTag': 'd1a9323ab22f0b4ee4876652b00ab425', 'sequencer': '00635B8EA807521EE7'}}}]}

s3_client = boto3.client('s3',
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key= AWS_SECRET_ACCESS_KEY)

dynamodb_client = boto3.client('dynamodb',
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key= AWS_SECRET_ACCESS_KEY,region_name='us-west-2')
				
input_bucket = 'proj2-input-bucket'
output_bucket = 'proj2-output-bucket'
dynamodb_table = 'Proj2-students'
frames_path = '/tmp/'

# Function to read the 'encoding' file
def open_encoding(filename):
	print("In encoding")
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def download_video_s3(video_name):
	print("in download video")
	s3_client.download_file(Bucket=input_bucket, Key=video_name, Filename='/tmp/'+video_name)
	print("after downloading file")
	os.system("ffmpeg -i " + str('/tmp/'+video_name) + " -r 1 " + str(frames_path) + "image-%3d.jpeg")
	print("after frames")

def get_item(name,video_name):
	# response = dynamodb_client.query(TableName=dynamodb_table, 
    # KeyConditionExpression=Key('name').eq(name))
	# print(response)
	response = dynamodb_client.scan(TableName=dynamodb_table,
    IndexName='name-index')
	# result = response
	#print(response)
	value_list=[]
	for item in response['Items']:
		if item['name']['S']==name:
			print(item)
			for i in item.values():
				print(i)
				if 'S' in i:
					value_list.append(i['S'])
	print("Value List:", value_list)
	filename=video_name.split(".")[0]+".csv"
	print("File name:", filename, video_name)
	
	with open(filename, 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		wr.writerow(value_list)
	
	response=s3_client.upload_file(filename, output_bucket, filename)
	print("upload response: ", response)

	# clear frames
	for filename in os.listdir(frames_path):
		file_path = os.path.join(frames_path, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
		except Exception as e:
			print('Failed to delete %s. Reason: %s' % (file_path, e))

    

def face_recognition_handler(event, context):	

	#encodes known faces and names
	data = open_encoding('encoding')
	known_names = data['name']
	known_face_encodings = data['encoding']
	print("in between encoding and download s3")
	#downloading video from s3
	video_name=event['Records'][0]['s3']['object']['key']
	download_video_s3(video_name)
	print("after download video")
	#variable to store result
	name = ""

	# for all images in frames directory
	# find name of faces 
	#once you find 1 face, return name
	for filename in os.listdir(frames_path):
		if filename.endswith(".jpeg"):
			print("in for loop")
			unknown_image = face_recognition.load_image_file(frames_path+filename)
			unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
			results = face_recognition.compare_faces(known_face_encodings, unknown_encoding)
			if True in results:
				first_match_index = results.index(True)
				name = known_names[first_match_index]
				break

	print("Result of face recognition:", name)
	get_item(name,video_name)
    
# face_recognition_handler(event)
# download_video_s3()
