#!/usr/bin/env python

import twitter
import getopt,sys
import time
import random
import re
import os

def getBotname():
	return re.sub(".py$","",sys.argv[0].split("/").pop())

def getDirname():
	return re.sub(getBotname()+".py$","",sys.argv[0])

def getConfigfile():
	return os.environ["HOME"]+"/.pyTwtBotrc"


def showConfigHowto():
	print ""
	print "    password for "+getBotname()+" is needed in "+getConfigfile()
	print "    by adding line \""+getBotname()+"=<password>\" you set this pass"

def getPassword():
	retval=""

	try:
		f = open(getConfigfile(),"r")
		for line in f.readlines():
			if( re.match("^"+getBotname(),line) ):
				retval=line.split("=").pop().rstrip('\n')

		f.close()	
	except IOError:
		showConfigHowto()

	if( retval == "" ):
		showConfigHowto()

	return retval


def prereqcheck():
	twitversion="0.6"
	#twitter.require("twitter >= 0.6")
	if( re.match("^"+twitversion,twitter.__version__) ):
		return True
	else: 
		print "Twitter API is needed in version "+twitversion

	return False

def saveID(id=""):
	try:
		f = open(getDirname()+"Twtcek.id",'w')
		f.write(id +"\n")
		f.close()
		#print "Saving id "+ id+"\n"
	except IOError:
		return 1

	return 0


def readID():
	try:
		f = open(getDirname()+"Twtcek.id",'r')
		id = f.readline()
		id.rstrip('\n')
		f.close()
	except IOError:
		id = ""

	#print "Loaded id "+ id +"\n"
	return id

def getAnswer(text="",direct=False):
	dict = [] 
	defdict = [] 
	directdict = [] 
	try:
		f = open(getDirname()+"Twtcek.db",'r')
		msgList = f.readlines()
		for line in msgList:
			l = line.split(":")
			regs = l[0].split(",")
			for reg in regs:
				regex = ".*"+reg+".*"
				#print "check "+l[1]+" for regex "+regex+" on "+text
				if(re.match(regex,text)):
					dict.append( l[1] )
					#print "added "+l[1]+" for regex "+regex+" on "+text
				elif( re.match("default",reg)):
					defdict.append( l[1] )
					#print "added default "+l[1]+" "+regex+" on "+text
				elif( re.match("direct",reg)):
					directdict.append( l[1] )
					#print "added direct "+l[1]+" "+regex+" on "+text
		f.close()
	except IOError:
		print "No DB found"
		return "Wooot ?"

	if( len(dict) < 1 ):
		dict = defdict

	if( direct ):
		dict = directdict

	ran = random.randint(0,len(dict)-1)
	answer = dict[ran].rstrip('\n')
	#answer =  answer + " (by PyBot)"
	#print "Evaluated answer: "+answer
	return answer

def usage():
	print "Usage is:"
	print "   -d status update random @<follower>"
	print "   -a answer by status_update to last messages"
	print "   -h shows this help"


if( not prereqcheck() ):
	exit(1)


def main():
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "adh", ["answer", "direct","help"])
	except getopt.GetoptError, err:
		# print help information and exit:
		usage()
		sys.exit(2)

	answer = False
	direct = False
	for o, a in opts:
		if o == "-a":
			answer = True
		elif o in ("-h", "--help"):
			usage()
			showConfigHowto()
			sys.exit()
		elif o in ("-d", "--direct"):
			direct = True
		else:
			assert False, "unhandled option"

	
	user = getBotname()
	#passwd = getPassword()
	passwd = "ficken500"
	t = twitter.Api(username=user,password=passwd )
	
	# Direct messages
	if ( direct ):
		followers = t.GetFollowers()
		#print "Followers "+followers.name
		msg = getAnswer(direct=True)
		ran = random.randint(0,len(followers)-1)
		follower = followers[ran]
		print "Sending direct status update "+msg+" to "+follower.screen_name
		t.PostUpdate("@"+follower.screen_name+" "+msg)
	
	elif ( answer ):
		id = readID()
	
		replies = t.GetReplies(since_id=id)
		lastId = id
	
		for message in replies:
			lastId = message.id
			if message.user.name != getBotname():
				txt = "@"+message.user.screen_name+" "+getAnswer(message.text)
				t.PostUpdate(txt)
				print "Status update "+txt+" to "+message.user.name
				friendlist = t.GetFriends(getBotname())
				isFriend = False
				for friend in friendlist:
					if friend.name == message.user.name:
						isFriend = True
				if not isFriend:
						t.CreateFriendship(message.user.id)
						print "Create friendship with "+message.user.name
		
		
		saveID(str(lastId))
	
	else:
		usage()
	
	
if __name__ == "__main__":
	main()
	
