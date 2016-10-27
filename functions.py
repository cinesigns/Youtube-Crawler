#!/usr/bin/python


import pymongo
import urllib
from bs4 import BeautifulSoup

def searchString(string):
    """ Extract the # of likes or dislikes within the string given from getVideoData """
    soup = BeautifulSoup(string, "html.parser")
    spans = soup.find_all("span")
    for span in spans:
        if span.get('class')[0] == 'yt-uix-button-content':
            return int(str(span).replace('<span class="yt-uix-button-content">','').replace('</span>',''))
    return None

def getVideoData(source):
    """ Do a full video run on one video, return data and queue """
    r = urllib.urlopen(source).read()
    soup = BeautifulSoup(r, "html.parser")

    metas = soup.find_all('meta')
    data = dict()
    videos = list()


    #First, hunt each meta tag
    for meta in metas:    
        result = None

        if meta.get('property') is not None:
            #Omit because redundant
            if meta.get('property') != "og:video:tag": 
                data[meta.get('property')] = meta.get('content')

        elif meta.get('name') is not None:
                data[meta.get('name')] = meta.get('content')

        elif meta.get('itemprop') is not None:
                data[meta.get('itemprop')] = meta.get('content')

        #Get number of views    
        divs = soup.find_all('div')
        for div in divs:
            lis = div.get('class')
            try:
                if lis[0] == "watch-view-count":
                    mod = int(div.contents[0].replace(' views','').replace(',',''))
                    data[lis[0]] = mod
            except:
                ()


        #Get # of likes and dislikes
        buttons = soup.find_all('button')
        found_dislike = False
        found_like = False

        for button in buttons:
    
            try:
                if (button.get('aria-label')[:26] == 'like this video along with') and (found_like is False):
                    found_like = True
                    number = searchString(str(button))
                    if number is not None:
                        data["likes"] = number
                        #data.append(result)
                        ()
            except:
                ()
    
    
            try:
                if (button.get('aria-label')[:29] == "dislike this video along with") and (found_dislike is False):
                    found_dislike = True
                    number = searchString(str(button))
            
                    if number is not None:
                        data["dislikes"] = number
                        #data.append(result)
                        ()
                    
            except:
                ()


        #Get name of artist
        imgs = soup.find_all('img')
        for img in imgs:
            try:
                if img.get('onload'):
                    name = img.get('alt')
                    data["artist"] = name
                    #data.append(result)
            except:
                ()
            
            
        #Get urls of related videos
        links = soup.find_all('a')
        for a in links:
            try:
                if a.get('href')[:9] == "/watch?v=":
                    if "http://www.youtube.com"+a.get('href') not in videos:
                        videos.append("http://www.youtube.com"+a.get('href'))
            except:
                ()

    return data, videos
    
    
####### MONGO FUNCTIONS #######
    
def getDB():
    """ Return the database for use """
    client = pymongo.MongoClient('localhost:27017')
    db = client.CineSignsYoutube
    return db
    
def addData(db, data, videos):
    """ Add video data and append URLs to the queue """
    db.data.insert(data)
    for video in videos:
        
        #Make sure no redundancies before inserting into queue
        vidmod = video.replace('http://','https://')
        if (db.queue.find({"video":vidmod}).count() == 0) and (db.data.find({"og:url":vidmod}).count() == 0):
            db.queue.insert({"video": vidmod})

def getVideo(db):
    """ Get a video """
    return db.queue.find_one()
    
def removeCompletedVideoFromQueue(db, data):
    """ Remove the completed video from the queue """
    video = data["og:url"]
    #Make sure URLs match, always default to https
    video = video.replace('http://','https://')
    return db.queue.delete_many({"video":video}).deleted_count
    
    
def dataIsGood(data):
    """ Verify we got data.  20 keys is an arbitrary number. Currently 60 are collected """
    if len(data) > 20:
        return True
    else:
        return False
        
def getNextURL(db):
    """ Get the next URL from the queue """
    return db.queue.find_one()["video"]