import os
import telebot
import requests
import speech_recognition as sr
import subprocess
import datetime
from keras.models import model_from_json

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D
from tensorflow.python.keras.layers import Activation, Dropout, Flatten, Dense
import tensorflow as tf
import numpy as np
#from py import generate_spectogram
token = '1840603958:AAHYjyuGKnfIFlEmclpx-9agQywzI3Cpj-I'

bot = telebot.TeleBot("1840603958:AAHYjyuGKnfIFlEmclpx-9agQywzI3Cpj-I", parse_mode=None)

logfile = str(datetime.date.today()) + '.log' # формируем имя лог-файла


def audio_to_text(dest_name: str):
    # Функция для перевода аудио, в формате ".vaw" в текст
    r = sr.Recognizer() # такое вообще надо комментить?
    # тут мы читаем наш .vaw файл
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU") # используя возможности библиотеки распознаем текст, так же тут можно изменять язык распознавания
    return result


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
    # Основная функция, принимает голосовуху от пользователя
    try:
        print("Started recognition...")
        # Ниже пытаемся вычленить имя файла, да и вообще берем данные с мессаги
        file_info = bot.get_file(message.voice.file_id)

        path = file_info.file_path # Вот тут-то и полный путь до файла (например: voice/file_2.oga)
        print(path)
        fname = os.path.basename(path) # Преобразуем путь в имя файла (например: file_2.oga)
        print(fname)
        # -*- coding: utf-8 -*-
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))# Получаем и сохраняем присланную голосвуху (Ага, админ может в любой момент отключить удаление айдио файлов и слушать все, что ты там говоришь. А представь, что такую бяку подселят в огромный чат и она будет просто логировать все сообщения [анонимность в телеграмме, ахахаха])
        print()
        with open(fname+'.oga', 'wb') as f:
            f.write(doc.content) # вот именно тут и сохраняется сама аудио-мессага
        procces = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])# здесь используется страшное ПО ffmpeg, для конвертации .oga в .vaw
        result = audio_to_text(fname+'.wav') # Вызов функции для перевода аудио в текст
        bot.send_message(message.from_user.id, format(result)) # Отправляем пользователю, приславшему файл, его текст
    except sr.UnknownValueError as e:
        # Ошибка возникает, если сообщение не удалось разобрать. В таком случае отсылается ответ пользователю и заносим запись в лог ошибок
        bot.send_message(message.from_user.id,  "Прошу прощения, но я не разобрал сообщение, или оно пустое...")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) + ':Message is empty.\n')
    except Exception as e:
        # В случае возникновения любой другой ошибки, отправляется соответствующее сообщение пользователю и заносится запись в лог ошибок
        bot.send_message(message.from_user.id,  "Что-то пошло через не так, но наши смелые инженеры уже трудятся над решением... \nДа ладно, никто эту ошибку исправлять не будет, она просто потеряется в логах.")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) +':' + str(e) + '\n')
    finally:
        # В любом случае удаляем временные файлы с аудио сообщением
        os.remove(fname+'.wav')
        os.remove(fname+'.oga')



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send your voice message")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("model.h5")
    print("Loaded model from disk")
    # load json and create model
    loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    score = loaded_model.predict("venv/test/male/male (60).flac.png")
    print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))



bot.polling(none_stop=True, interval=0)