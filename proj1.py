#Copyright Yixue_Zhang jedzhang@bu.edu
import tweepy
import shutil
import requests
import os
from tqdm import tqdm
from PIL import Image
import subprocess
from google.cloud import vision
from google.cloud.vision import types
import io
import getpass
import datetime
import platform
import mysql.connector
import json
from pymongo import MongoClient
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=""
# INFO for MYSQL
mysqlhost = ''
mysqluser = ''
mysqlpassword = ''
mysqldatabase = ''
# INFO for mango DB
MONGODB_URI = ""


def img_detection(Topic):
	"""use google vision api to detecte image"""
	print("Start detecting features with google vision analysis")
	files = os.listdir(Topic)
	client = vision.ImageAnnotatorClient()
	f = open(Topic+'/Label_detection.txt','w')
	img_dis = ""
	for file in files:
		file = Topic +'/' + file
		with io.open(file,'rb') as image_file:
			content = image_file.read()
		image = types.Image(content=content)
		response = client.label_detection(image=image)
		labels = response.label_annotations
		f.write(str(file))
		img_dis += str(file)
		img_dis += ': '
		f.write(': ')
		for lable in labels:
			f.write(lable.description)
			f.write(",")
			img_dis += lable.description
			img_dis += ', '
		f.write('\n')
		img_dis = img_dis[:-2]
		img_dis += '|'
	f.close()
	print("Detection complete.")
	return img_dis


def image_pre(Topic):
	"""pre process images"""
	try:
		shutil.rmtree("Temp")
	except FileNotFoundError:
		pass
	finally:
		os.mkdir("Temp")
	files = os.listdir(Topic)
	print("Start image pre-process.")
	for i in tqdm(range(len(files))):
		img = Image.open(Topic + '/' + files[i])
		img = img.resize((1280,720))
		img.save("Temp/" + files[i][:-4] + '.jpg')


def image2video(Topic):
	"""generate video"""
	subprocess.run(['ffmpeg','-r','1','-pattern_type','glob','-i',"Temp/*.jpg",'-c:v','mpeg4',Topic + '.mp4'])
	print("MP4 file generated")


def download_image(images,Topic):
	"""download images from url"""
	try:
		shutil.rmtree(Topic)
	except FileNotFoundError:
		pass
	finally:
		os.mkdir(Topic)
	print("Start downloading images.")
	for i in tqdm(range(len(images))):
		img = requests.get(images[i]).content
		cc = "{:0>3d}".format(i)
		open(Topic + '/' + cc + images[i][-4:], 'wb').write(img)
	print("Download complete")


def get_image_url_from_tweet(tweet,images):
	"""get image url from each tweet"""
	for tweet in tweet:
		pics = tweet.entities.get("media", [])
		if len(pics) > 0:
			for i in range(len(pics)):
				if pics[i]['type'] == "photo":
					images.add(pics[i]['media_url'])
	return images


def fatch_images(screen_name,num_pic):
	"""fatch image from twitter"""
	# Auth
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)
	# init image url set
	images = set()
	# fatch tweets
	data = api.user_timeline(screen_name=screen_name,count=200,include_rts=False,exclude_replies=True)
	images = get_image_url_from_tweet(data,images)
	last_tweet_id = data[-1].id
	if len(images) < num_pic:
		while True:
			try:
				tweets = api.user_timeline(screen_name=screen_name,count=200,include_rts=False,exclude_replies=True,max_id=last_tweet_id-1)
				last_tweet_id = tweets[-1].id
			except IndexError:
				raise AssertionError("Cannot find enough images for {}.".format(screen_name))
			images = get_image_url_from_tweet(tweets,images)
			if len(images) >= num_pic:
				return list(images)[:num_pic]
	else:
		return list(images)[:num_pic]


def fatch_basic_info():
	"""get basic information about the user"""
	info = []
	username = getpass.getuser()
	info.append(username)
	time = datetime.datetime.now()
	info.append(time)
	system = platform.platform()
	info.append(system)
	return info


def mysqlupdate(info):
	"""update the remote mysql database"""
	for i in range(len(info)):
		info[i] = str(info[i])
	try:
		db = mysql.connector.connect(
			host = mysqlhost,
			user = mysqluser,
			password = mysqlpassword,
			database = mysqldatabase		)
		print('mysql login success')
	except:
		print("Error when login to MYSQL")
		exit(1)
	try:
		cursor = db.cursor()
		sqlformula = 'INSERT INTO project1_log (username, time, os, Topic, Numberofpic, images, diecption) VALUES (%s,%s,%s,%s,%s,%s,%s)'
		cursor.execute(sqlformula,tuple(info))
		db.commit()
		print('MYSQL update complete')
	except:
		print('Error when writing MYSQL')
		exit(1)


def pushRECORD(record,user_records):
	"""push record (MongoDB)"""
	user_records.insert_one(record)


def mongodb(info):
	"""update the remote mongodb database"""
	for i in range(len(info)):
		info[i] = str(info[i])
	try:
		client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
		db = client.get_database("project1_log")
		record = {'username':info[0],
				  'time':info[1],
				  'os':info[2],
				  'topic':info[3],
				  'numberofpic':info[4],
				  'images':info[5],
				  'description':info[6]
				  }
		pushRECORD(record,user_records = db.project1_log)
		print('Mongo DB update complete!')
	except:
		print('Mongo DB update Failed!')



def main():
	"""main function"""
	info = fatch_basic_info()
	Topic = input("Please input the screen_name:")
	info.append(Topic)
	num_pic = int(input("Please input the number of image you wish to download:"))
	info.append(num_pic)
	if int(num_pic) > 99:
		print("Please input smaller number.")
		os.exit(0)
	images = fatch_images(Topic,num_pic)
	info.append(images)
	print("Image URL fatching complete.")
	download_image(images,Topic)
	image_pre(Topic)
	image2video(Topic)
	info.append(img_detection(Topic))
	mysqlupdate(info)
	mongodb(info)


if __name__ == '__main__':
	main()
