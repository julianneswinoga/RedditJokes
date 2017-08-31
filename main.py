#!/usr/bin/python

import praw
import urllib
import sys
import json
import csv
from fuzzywuzzy import fuzz, process

def alreadyPosted(jokesArray, text):
    for joke in jokesArray:
	ratio = fuzz.token_sort_ratio(joke[1], text)
	if ratio > 80:
	    return {"ratio": ratio, "uid": joke[0]}
    return False

def updateJokesList(submissions):
    jokesFile = open('jokes.json', 'rb')
    jokesJSON = json.load(jokesFile)
    jokesFile.close()

    uid = len(jokesJSON["jokes"])
    for i, submission in enumerate(submissions):
        posted = alreadyPosted(jokesJSON["jokes"], submission.selftext)
        if posted != False and submission.url not in jokesJSON["jokes"][posted["uid"]][3]: # Repost
            jokesJSON["jokes"][posted["uid"]][2] += 1
            jokesJSON["jokes"][posted["uid"]][3].append(submission.url)
        elif posted == False: # New submission!
            jokesJSON["jokes"].append([uid, submission.selftext, 0, [submission.url]])
            uid += 1
        percent = float(i) / len(submissions) * 100
        if percent % 10 == 0:
            print '%s%%...' % percent

    print 'Done!'
    jokesFile = open('jokes.json', 'w')
    json.dump(jokesJSON, jokesFile)
    jokesFile.close()

r = praw.Reddit('jokes', user_agent="/r/Jokes repost check")
print 'Made Reddit instance'

subreddit = r.subreddit('jokes')
submissions = list(subreddit.top(time_filter='week', limit=100))
print 'Retrieved submissions: %s' % len(submissions)

updateJokesList(submissions)

jokesFile = open('jokes.json', 'rb')
jokesJSON = json.load(jokesFile)
jokesFile.close()

statsFile = open('stats.csv', 'wb')
CSVWriter = csv.writer(statsFile)
for j in jokesJSON["jokes"]:
    CSVWriter.writerow([j[0], j[1][0:50].encode("utf-8"), j[2]])
statsFile.close()
	

uid = 0
max_reposts = 0
for j in jokesJSON["jokes"]:
    if (j[2] > max_reposts):
	max_reposts = j[2]
	uid = j[0]

print "Stats:"
print "Total number of jokes:", len(jokesJSON["jokes"])
print "Max num of reposts:", max_reposts, "for joke", jokesJSON["jokes"][uid]
