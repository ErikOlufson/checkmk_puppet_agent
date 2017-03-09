#!/usr/bin/python

#Script which runs as plugin in checkmk.
#Written by Steven Wend
#steven.wend [a~t] t-online.de

#This script is tested with Python 2.7

import apt
import sys
import re
import os
import subprocess
import datetime
import time
import syslog


puppetStatePath = None
puppetBinPath = None

neededTime = "0"
stateYamlSize = "0"

def sendSuccessMessage(message):
	sendMessage("0 Puppet_Agent sec=" + neededTime +"|kb=" + stateYamlSize + " " + message)

def sendCritMessage(message):
	sendMessage("2 Puppet_Agent sec=" + neededTime +"|kb=" + stateYamlSize + " " + message)

def sendWarnMessage(message):
	sendMessage("1 Puppet_Agent sec=" + neededTime +"|kb=" + stateYamlSize + " " + message)

def sendMessage(message):
	print "%s" % message
	sys.exit()


def sendToSyslog(message):
	syslog.syslog(syslog.LOG_ERR, message)


def runAllTests():
	global neededTime
	global stateYamlSize

	#If anything does not work probably we need to know.
	try:
		setPuppetPathsAndCheckInstallation()
		neededTime = getNeededTimeForLastRun()
		stateYamlSize = str(getStateYamlSize())

		checkPuppetAgentIsRunning()
		checkTimingLastRun()
		checkForErrorsInLastRun()
		checkForBigStateYaml()
	except Exception, arg:
		sendToSyslog("[{err}]".format(err=str(arg)))
		sendCritMessage("An exception has been thrown.")

	#No one has terminated so everything should be fine.
	sendSuccessMessage("Puppet Agent is working.")


def setPuppetPathsAndCheckInstallation():
	global puppetStatePath
	global puppetBinPath

	pkg_puppet_agent = None
	pkg_puppet = None

	cache = apt.cache.Cache()

	try:
		pkg_puppet_agent = cache["puppet-agent"]
	except Exception, arg:
		sendToSyslog("[{err}]".format(err=str(arg)))

	try:
		pkg_puppet = cache["puppet"]
	except Exception, arg:
		sendToSyslog("[{err}]".format(err=str(arg)))

	if pkg_puppet_agent is not None and pkg_puppet_agent.installed is not None:
		#print "%s is installed" % pkg_puppet_agent
		puppetStatePath = "/opt/puppetlabs/puppet/cache/state/"
		puppetBinPath = "/opt/puppetlabs/bin/"
	elif pkg_puppet is not None and pkg_puppet.installed is not None:
		#print "%s is installed" % pkg_puppet_agent
		puppetStatePath = "/var/lib/puppet/state/"
		puppetBinPath = "/usr/bin/"
	else:
		#print "Nothing is installed"
		sendCritMessage("Puppet Agent is not installed.")


def checkPuppetAgentIsRunning():
	ps = subprocess.Popen("ps -eaf | grep puppet | grep -v mcollectived", shell=True, stdout=subprocess.PIPE)
	output = ps.stdout.read()
	ps.stdout.close()
	ps.wait()

	if re.search("puppet agent", output) is None:
		#print "Puppet Agent is not running."
		sendCritMessage("Puppet Agent is not running.")


def checkTimingLastRun():

	file = open(puppetStatePath+"/last_run_summary.yaml", "r")

	#get timestamp of last run.
	lastRunTimestamp = None
	for line in file:
		if re.search("last_run", line):
			line = line.replace("\n", "").replace("\r", "").replace(" ","").split(":",1)
			lastRunTimestamp = line[1]


	#Get current timestamp.
	currentTimestamp = time.mktime(datetime.datetime.now().timetuple())

	#Calculate duration between last run and current timestamp.
	duration = int(currentTimestamp) - int(lastRunTimestamp)
	
	if duration > 3600 and duration < 86400:
		sendWarnMessage("Puppet Agent was not running since 1h.")
	elif duration > 86400:
		sendCritMessage("Puppet Agent was not running since 24h.")


def checkForErrorsInLastRun():
	file = open(puppetStatePath+"/last_run_summary.yaml", "r")

	#get timestamp of last run.
	errorCounter = None
	for line in file:
		if re.search("failure:", line):
			line = line.replace("\n", "").replace("\r", "").replace(" ","").split(":",1)
			errorCounter = line[1]

	if int(errorCounter) > 0:
		sendCritMessage("Puppet Agent ran with errors.")


def getStateYamlSize():
	stateYamlSize = os.path.getsize(puppetStatePath+"/state.yaml")
	return ( stateYamlSize / 1024 )


def checkForBigStateYaml():
	stateYamlSizeInKb = getStateYamlSize()
	if stateYamlSizeInKb > 5120 and stateYamlSizeInKb < 10240:
		sendWarnMessage("Puppet Agent state.yaml is big (" + str(stateYamlSizeInKb) + "kb).")
	elif getStateYamlSize() > 10240:
		sendCritMessage("Puppet Agent state.yaml is too big (" + str(stateYamlSizeInKb) + "kb).")


def getNeededTimeForLastRun():
	file = open(puppetStatePath+"/last_run_summary.yaml", "r")	
	for line in file:
		if re.search("total:\ [0-9]*\.[0-9]+", line):
			time = line.replace("\n", "").replace("\r", "").replace(" ","").split(":",1)
			neededTime = time[1].split(".",1)

	return neededTime[0]


runAllTests()
