# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 14:20:12 2018


"""

# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 00:21:32 2017

"""


# -*- coding: utf-8 -*-

import telebot
from telebot import types
import pictures_config as config
import dbworker
import boto
import boto.s3.connection
from boto.s3.key import Key
import numpy as np
#import cv2
import os
import pandas as pd
import pymysql
#from IPython.display import display, Image
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg


import requests
import boto3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from logging import Logger






bot = telebot.TeleBot(config.token)
path=os.getcwd()

# Начало диалога

@bot.message_handler(commands=["start"], content_types=['text'])
def cmd_start(message):
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_ENTER_NAME.value:
        bot.send_message(message.chat.id, "Кажется, кто-то обещал отправить своё имя, но так и не сделал этого :( Жду...")
    elif state == config.States.S_SEND_PIC.value:
        bot.send_message(message.chat.id, "Кажется, кто-то хотел загрузить картинку, но так и не сделал этого :( Жду...")
    else:  # Под "остальным" понимаем состояние "0" - начало диалога
        bot.send_message(message.chat.id, "Привет! Как я могу к тебе обращаться?")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)




# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Как тебя зовут?")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_entering_name(message):
    # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    bot.send_message(message.chat.id, "Отличное имя, запомню! Загружай картинку!")
    dbworker.set_state(message.chat.id, config.States.S_SEND_PIC.value)



    
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND_PIC.value, content_types=['photo'])
def user_picture(message):
    # В 67случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    bot.send_message(message.chat.id, "Загрузил! Давай ещё картинки!")
    user_name=message.from_user.first_name+message.from_user.last_name
    print ('user full name =', message.from_user.first_name,message.from_user.last_name)
    user_id=message.from_user.id
   
    #print ('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    
    print ('fileID =', fileID)
    file = bot.get_file(fileID)
    print ('file.file_path =', file.file_path)
    telegram_api=
    long_url=os.path.join(telegram_api, file.file_path.rsplit('/',1)[-1])
    print(long_url)
    #image = urllib.URLopener()
    #image.retrieve(long_url,"00000001.jpg")
#DOWLOADING THE FILE INTO CURRENT DIRECTORY
    with open(file.file_path.rsplit('/', 1)[-1], 'wb') as handle:
        response = requests.get(long_url, stream=True)





        if not response.ok:
            print (response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)
#OR DOWNLOADING FILE DIRECTLY TO S3 WITHOUT SAVING ON DISK

    # Uses the creds in ~/.aws/credentials
    s3 = boto3.resource('s3',
                        aws_access_key_id=,
                        aws_secret_access_key=)
    bucket_name_to_upload_image_to = 'ec2-18-220-150-231.us-east-2.compute.amazonaws.com'
    s3_image_filename = file.file_path.rsplit('/',1)[-1]

    # Do this as a quick and easy check to make sure your S3 access is OK
    for bucket in s3.buckets.all():
        if bucket.name == bucket_name_to_upload_image_to:
            print('Good to go. Found the bucket to upload the image into.')
            good_to_go = True

    if not good_to_go:
        print('Not seeing your s3 bucket, might want to double check permissions in IAM')

    # Given an Internet-accessible URL, download the image and upload it to S3,
    # without needing to persist the image to disk locally
    req_for_image = requests.get(long_url, stream=True)
    file_object_from_req = req_for_image.raw
    req_data = file_object_from_req.read()

    # Do the actual upload to s3
    s3.Bucket(bucket_name_to_upload_image_to).put_object(Key=s3_image_filename, Body=req_data)


#WRITING INFO INTO SQL TABLE
    host = "fintechbot.cbdlyzrg87lq.us-east-2.rds.amazonaws.com"
    port = 3306
    dbname = "fintechbot"
    user = "fintechbot"
    password = "fintechbot"
    conn = pymysql.connect(host, user=user, port=port,
                           passwd=password, db=dbname, autocommit=True)
    cur=conn.cursor()
    #cur.execute('drop table pictures_bot_info;')
    cur.execute('create table pictures_bot_info '
                '(filename VARCHAR(100), '
                'username VARCHAR(100));')
    add_data = ("INSERT INTO {table} "
                "(filename, username) "
                "VALUES (%s, %s)")
    atable = 'pictures_bot_info'
    data_word = (file.file_path.rsplit('/',1)[-1], user_name)
    cur.execute(add_data.format(table=atable), data_word)


    print(pd.read_sql('select * from pictures_bot_info;', con=conn))


    dbworker.set_state(message.chat.id, config.States.S_SEND_PIC.value)

if __name__ == '__main__':
    try:

        bot.polling(none_stop=True)

        # ConnectionError and ReadTimeout because of possible timout of the requests library

        # TypeError for moviepy errors

        # maybe there are others, therefore Exception

    except Exception as e:

        print(e)

        time.sleep(30)