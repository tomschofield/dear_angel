import twitter
#PYTHON SCRIPTsends val to arduino from environment var
#draws on example from http://www.daniweb.com/web-development/php/threads/311156/pass-data-from-php-to-python-and-run-python-script all credits for this to authros
import socket, sys
import time, datetime
import serial
import Image, ImageDraw, ImageFont
import os
import textwrap

import string

#for email
from email.mime.text import MIMEText
from datetime import date
import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "MY ADDRESS"
SMTP_PASSWORD = "MY PASSWORD"

#these are just for reporting success to email
EMAIL_TO = ["TARGET EMAIL ADDRESS"]
EMAIL_FROM = "FROM EMAIL ADDRESS"
EMAIL_SUBJECT = "new tweet : "

DATE_FORMAT = "%d/%m/%Y"
EMAIL_SPACE = ", "

use_arduino = True
use_printer = True

api = twitter.Api()
api = twitter.Api(consumer_key='xx',
                      consumer_secret='xx',
                      access_token_key='xx',
                      access_token_secret='xx')

if use_arduino:
  #update to your serial port address
  ser = serial.Serial('/dev/tty.usbmodemfd131', 9600)
else:
  pass

def send_email(DATA):
    msg = MIMEText(DATA)
    msg['Subject'] = EMAIL_SUBJECT + " %s" % (date.today().strftime(DATE_FORMAT))
    msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
    msg['From'] = EMAIL_FROM
    mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    mail.starttls()
    mail.login(SMTP_USERNAME, SMTP_PASSWORD)
    mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    mail.quit()

#print api.VerifyCredentials()
def write_to_arduino(message):
  print "writing to arduino "
  ser.write(message)
  pass
  
def print_tweet(tweet_text):
  #mostly based in pyimage I think
  im = Image.open("tweet_print_template.png")

  draw = ImageDraw.Draw(im)
  fontsize=36
  #make sure you include the font in the same folder
  font = ImageFont.truetype("MONACO.TTF", fontsize)

  margin = 270
  offset = 30
  for line in textwrap.wrap(tweet_text, width=35):
      draw.text((margin, offset), line, font=font, fill="#aa0000")
      offset += font.getsize(line)[1]

  del draw 
  # write to stdout
  im.save("output.png")

  time.sleep(2)
  #send to label printer
  os.system("lp -d Brother_QL_570 output.png")
  pass

#this check if there's an existing tweet so we don't duplicate
def is_tweet_new(tweet):
  _tweet_is_new = True
  filePath = "dear_angel_twitter_log.txt"
  f = open(filePath, 'r')
  for line in f:
    try:
      exploded = line.split(',')
      if len(exploded)>0:
        for pair in exploded:
          exploded_pair = pair.split(':')
          #print exploded_pair[0].strip()        
          if stripPunctuation(exploded_pair[0])== 'id':
            #print 'found pair'
            this_id = exploded_pair[1].strip()
            #print this_id ," ",str(tweet.id)
            if this_id == str(tweet.id):
              _tweet_is_new = False
    except Exception, e:
      print "can't read tweet line", line, e 
        
  return _tweet_is_new

def logTweet(tweet):

  filePath = "dear_angel_twitter_log.txt"
  f = open(filePath, 'a')
  
  lineToWrite = ""
  
  for property, value in vars(tweet).iteritems():
    try:
      #print "property", type(property), repr(property)
      #print "value", type(value), repr(value)
      
      if isinstance(property, str):
        lineToWrite+=str(property)
      elif isinstance(property, unicode):
        lineToWrite+=unicode(property)
      else:
        lineToWrite+=str(property)
      
      lineToWrite+=':'

      if isinstance(value, str):
        lineToWrite+=str(value)
      elif isinstance(value, unicode):
        lineToWrite+=unicode(value)
      else:
        lineToWrite+=str(value)

      lineToWrite+=','
    except Exception, e:
      print "can't read tweet line", e 
    

  lineToWrite[:-1]
  f.write(lineToWrite.encode('utf-8') )
  f.write('\n')
  f.close()
  pass



def stripPunctuation(s):
  out = s.translate(string.maketrans("",""), string.punctuation)
  return out



def getStatuses(_username):
  statuses = api.GetUser_timeline(_username)
  counter = 0
  for s in statuses:
    try: 
      print s.text, str(counter), "\n"
      counter+=1
    except:
      print "bad response"
  pass


username = 'NA_Indicator'

def checkDMS():
  dms = api.GetDirectMessages()

  for s in reversed(dms):
    
    #text = str(s.text)
    if is_tweet_new(s):
      logTweet(s)
      try:
        send_email(s.text)
      except:
        print 'email sending failed'
      if use_printer:
        print_tweet(s.text)
      time.sleep(5)
      if use_arduino:
        write_to_arduino(('3'))
  pass

def checkMentions():
  mentions = api.GetMentions()

  for s in reversed(mentions):
    
    #text = str(s.text)
    if is_tweet_new(s):
      print "found new tweet"
      logTweet(s)
      try:
        send_email(s.text)
      except:
        print 'email sending failed'
      
      if use_printer:
        print_tweet(s.text)
      time.sleep(5)
      if use_arduino:
          write_to_arduino(('3'))
  pass


timeCount=10
while timeCount>0:
  ts = time.time()  
  st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
  print "checking new tweets at", st
  try:
    checkDMS()
  except Exception, e:
      print "can't get DM tweet", e

  try:
    checkMentions()
  except Exception, e:
      print "can't get @ tweet", e 
  #
  time.sleep(22)

  #final_time = 
  #if  result__time!= "no__time_found" and is_timeNew(result__time):
    #print "sending this _time ",result__time
    #sendToArduino(result__time)

#getStatuses(username)
