from pytube import YouTube
from bs4 import BeautifulSoup
from pydub import AudioSegment
from pydub.silence import split_on_silence 
import speech_recognition as sr 
import os
import subprocess
from paddlenlp import Taskflow
from googletrans import Translator

summarizer = Taskflow("text_summarization") # load summarization tool
r = sr.Recognizer() # speech recognition tool
translator = Translator() # translate simplified to traditional

url_pre = "https://www.youtube.com/watch?v="
url_post = "Mvk2TNWAV8A"
url = url_pre + url_post

yt = YouTube(url)

file = url_post
filetxt = file + '.txt'
filemp3 = file + '.mp3'
filewav = file + '.wav'

print('download...')
yt.streams.filter().get_audio_only().download(filename=filemp3) # downloading video, mp3

if 'zh-TW' in yt.captions: # exist captions
  print("Captions")
  caption = yt.captions.get_by_language_code('zh-TW') #zh-TW
  xml = caption.xml_captions
  rec = ""
  for s in xml.split('\n')[2:-3]:
    tmp = s[s.find('>')+1:-4]
    # tmp = translator.translate(s[s.find('>')+1:-4], dest='zh-cn', src='zh-tw').text
    rec = rec + tmp
  rec = translator.translate(yt.title + '\n' + rec, dest='zh-cn', src='zh-tw').text
else:
  print("No captions")
  file_write = open(filetxt, "w+")
  # converting .mp3 to .wav for sr
  command = "ffmpeg -i "+filemp3+" -acodec pcm_s16le -ac 1 -ar 16000 " + filewav
  subprocess.call(command, shell=True)

  WAV = sr.AudioFile(filewav)
  with WAV as source:
    r.adjust_for_ambient_noise(source)
    audio = r.record(source)
  print("recoginizing")
  rec = r.recognize_google(audio, language = 'zh-tw')
  rec = translator.translate(yt.title, dest='zh-cn', src='zh-tw').text + '\n' + rec 
  # print("Text: ")
  # for i in range(0,len(rec),20):
  #   print(rec[i:i+20])
  file_write.write(rec) 

translation = translator.translate(summarizer(rec)[0], dest='zh-tw', src='zh-cn')
print("Summarization: ",translation.text)
