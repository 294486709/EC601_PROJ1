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


def img_detection(Topic):
    print("Start detecting features with google vision analysis")
    files = os.listdir(Topic)
    client = vision.ImageAnnotatorClient()
    f = open(Topic+'/Label_detection.txt','w')
    for file in files:
        file = Topic +'/' + file
        with io.open(file,'rb') as image_file:
            content = image_file.read()
        image = types.Image(content=content)
        response = client.label_detection(image=image)
        labels = response.label_annotations
        f.write(str(file))
        f.write(':')
        for lable in labels:
            f.write(lable.description)
            f.write(",")
        f.write('\n')
    f.close()
    print("Detection complete.")


def image_pre(Topic):
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


def image2video():
    subprocess.run(['ffmpeg','-r','1','-pattern_type','glob','-i',"Temp/*.jpg",'-c:v','mpeg4',Topic + '.mp4'])
    print("MP4 file generated")


def download_image(images,Topic):
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


# Read keys from local file
def readkey():
    f = open('key.txt')
    data = f.readlines()
    keys = []
    for i in data:
        keys.append(i.replace("\n",""))
    return keys


def get_image_url_from_tweet(tweet,images):
    for tweet in tweet:
        pics = tweet.entities.get("media", [])
        if len(pics) > 0:
            for i in range(len(pics)):
                if pics[i]['type'] == "photo":
                    images.add(pics[i]['media_url'])
    return images


def fatch_images(screen_name,num_pic):
    key = readkey()
    consumer_key = key[0]
    consumer_secret = key[1]
    access_key = key[2]
    access_secret = key[3]
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
            except IndexError:
                raise AssertionError("Cannot find enough images for {}.".format(Topic))
            last_tweet_id = tweets[-1].id
            images = get_image_url_from_tweet(tweets,images)
            if len(images) >= num_pic:
                return list(images)[:num_pic]
    else:
        return list(images)[:num_pic]


if __name__ == '__main__':
    Topic = input("Please input the screen_name:")
    num_pic = int(input("Please input the number of image you wish to download:"))
    if int(num_pic) > 999:
        print("Please input smaller number.")
        os._exit(0)
    images = fatch_images(Topic,num_pic)
    print("Image URL fatching complete.")
    download_image(images,Topic)
    image_pre(Topic)
    image2video()
    img_detection(Topic)
