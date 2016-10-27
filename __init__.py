#!/usr/bin/python


import functions
import time

import sys


#Ensure user inputs a number for loops
try:
	count = int( sys.argv[1])
except:
	print "Usage: python __init__.py [#loops]"
	sys.exit()


def videoCycle(db):
    """ Start a new video cycle -- get one video and process it, then adjust queue """
    #Get next URL from the Queue
    url = functions.getNextURL(db)
    
    #Analyze the video
    data, videos = functions.getVideoData(url)

    #Check if data was received (in case internet went down, etc)
    if functions.dataIsGood(data) is True:

        #Add the data to the DB for data and queue
        functions.addData(db, data, videos)
        
        #Remove the completed video from the queue
        print functions.removeCompletedVideoFromQueue(db, data)


if __name__ == "__main__":
    #Get Database
    db = functions.getDB()

    #Start loop cycle, calling a new vid each time.  Use sleep to pace requests
    for looping in xrange(0,count):
        videoCycle(db)
        time.sleep(2)
    
