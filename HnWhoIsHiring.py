#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json #
import csv  # save to csv format
import re   # regex
from bs4 import BeautifulSoup # html encoding
import urlmarker # find url from text

# URL: https://news.ycombinator.com/item?id=11611867
# API: https://github.com/HackerNews/API
listingUrl = 'https://hacker-news.firebaseio.com/v0/item/11814828.json'
baseCommentUrl = 'https://hacker-news.firebaseio.com/v0/item/'

response = requests.get(listingUrl)
jsonData = json.loads(response.text)
commentIds = jsonData['kids']  # all the main comments from the Who's Hiring post

myfile = open('hn_who_is_hiring.csv','wb')
out = csv.writer(myfile, delimiter=',',quoting=csv.QUOTE_ALL, lineterminator='\n')
out.writerow(["commentId", "url", "companyName", "jobTitle", "fullPartTime", "textBlock"])

commentIter = iter(commentIds)
for commentId in commentIter: 
	#print "commentId=" + str(commentId)
	commentResponse = requests.get(baseCommentUrl +  str(commentId) + ".json")
	jsonComment = json.loads(commentResponse.text)

	if('text' in jsonComment):
		validJsonComment = (BeautifulSoup(jsonComment['text'], 'lxml'))
		encodedComment = validJsonComment.encode('utf-8')

		titleLine = encodedComment.split('</p>')
		textBlock = ""
		if(1 < len(titleLine)):
			textBlock = titleLine[1]

		url = ""
		urls = re.findall(urlmarker.WEB_URL_REGEX, str(titleLine[0])) # need to convert the return value to string
		if(len(urls) > 0): 
			url = urls[0]
		#print "URL=" + url

		fullPartTime = ""
		isFullTime = re.search('.*full.(\s|\-)?time.*', str(titleLine[0]), re.IGNORECASE)
		isPartTime = re.search('.*part.(\s|\-)?time.*', str(titleLine[0]), re.IGNORECASE)
		if (isFullTime): 
			fullPartTime = "FULL TIME"
		if (isPartTime): 
			if (isFullTime): 
				fullPartTime += " / "
			fullPartTime += "PART TIME"
		#print fullPartTime

		salary = ""
		hasSalary = re.search('([£\$\€])(\s)?(\d+(?:\.\d{2})?[^|]*)', str(titleLine[0]), re.IGNORECASE)
		if (hasSalary):
			salary = hasSalary.group()
		#print "SALARY=" + salary

		jobTitle = ""
		fields = titleLine[0].split('|')
		for field in fields: 
			isJobTitle = re.search('.*(engineer).*', str(field), re.IGNORECASE)
			if(isJobTitle):
				jobTitle = re.sub("<.*?>", "", isJobTitle.group())


		#remove all html tags, company name shouldn't be longer than 100 characters
		companyName = ""
		if (len(re.sub("<.*?>", "", fields[0])) < 50): 
			companyName = re.sub("<.*?>", "", fields[0])
		else: 
			if(1 < len(titleLine)):
				textBlock = titleLine[0] + titleLine[1]

		#print "COMPANY=" + companyName
		#print "JOB TITLE=" + jobTitle
		#print "*****************************************"
			
		out.writerow([commentId, url, companyName, jobTitle, fullPartTime, textBlock])

myfile.close()


'''
TODO://
- Google Sheet intgration.
- Add 'Who Is Hiring' as input param instead of hardcoded ID.
- Convert script to Exe (dependencies).
- Name output file based on Who's hiring month.
'''