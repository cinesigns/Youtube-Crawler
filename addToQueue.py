#!/usr/bin/python

import sys
import functions

def addToQueue(url):
		db = functions.getDB()
		db.queue.insert({"video ": url})
	


if __name__ == "__main__":

	try:
		print "Adding" + sys.argv[1]
		addToQueue(sys.argv[1])

	except:
		print "Usage: python addToQueue.py [YouTube URL]"


