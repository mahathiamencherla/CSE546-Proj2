from boto3 import client as boto3_client
import face_recognition
import pickle
import os
import ffmpeg
import boto3

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

s3_client = boto3.client('s3',
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key= AWS_SECRET_ACCESS_KEY,region_name='us-west-2')

dynamodb_client = boto3.client('dynamodb',
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key= AWS_SECRET_ACCESS_KEY,region_name='us-west-2')
				
input_bucket = 'proj2-input-bucket'
output_bucket = 'proj2-output-bucket'
dynamodb_table = 'Proj2-students'
frames_path = 'frames/'

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def download_video_s3():
	response = s3_client.list_objects(Bucket = input_bucket)
	print(response['Contents'])
	for file in response['Contents']:
		name = file['Key'].rsplit('/', 1)
		print (name, file['Key'])
		s3_client.download_file(Bucket=input_bucket, Key=file['Key'], Filename='download/'+name[0])
		
		os.system("ffmpeg -i " + str('download/'+name[0]) + " -r 1 " + str(frames_path) + "image-%3d.jpeg")

def get_item(name):
	# response = dynamodb_client.query(TableName=dynamodb_table, 
    # KeyConditionExpression=Key('name').eq(name))
	# print(response)
	response = dynamodb_client.scan(TableName=dynamodb_table,
    IndexName='name-index')
	result = response['']
	print(response)

def face_recognition_handler():	

	#encodes known faces and names
	data = open_encoding('encoding')
	known_names = data['name']
	known_face_encodings = data['encoding']
	
	#downloading video from s3
	download_video_s3()

	#variable to store result
	name = ""

	# for all images in frames directory
	# find name of faces 
	#once you find 1 face, return name
	for filename in os.listdir(frames_path):
		if filename.endswith(".jpeg"):
			unknown_image = face_recognition.load_image_file(frames_path+filename)
			unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
			results = face_recognition.compare_faces(known_face_encodings, unknown_encoding)
			if True in results:
				first_match_index = results.index(True)
				name = known_names[first_match_index]
				break

	print("Result:", name)
	get_item(name)
    
face_recognition_handler()
# download_video_s3()