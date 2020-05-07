######
# If you want to use twitter, change useTwitter = True and fill out the info in the initTwitter function
######

import time
import os
import httplib2
import requests
import classes.utility
import json

tools = classes.utility.ScavUtility()
iterator = 1

useTwitter = False
pastebinLimit = 50


def initTwitter():
	import tweepy
	#If you want to use Twitter, fill out the following, and use the --twitter arg when you run it
	consumer_key = ""  # TWITTER
	consumer_secret = ""  # TWITTER
	access_key = ""  # TWITTER
	access_secret = ""  # TWITTER

	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)  # TWITTER
	auth.set_access_token(access_key, access_secret)  # TWITTER
	api = tweepy.API(auth)  # TWITTER

	print("[#] Using API to gather pastes.")

	# loading notification targets
	with open("notification_targets.txt") as f:
		notificationtargets = f.readlines()
	print("[#] Loaded " + str(len(notificationtargets)) + " notification targets.")

while 1:
	# test if ready to archive
	archivepath = "data/raw_pastes"
	archiveit = tools.testifreadytoarchive(archivepath) #classes.utility.ScavUtility()
	if archiveit == 1:
		print("[*] Get all the pastes with credentials...")
		tools.getthejuicythings(archivepath, "pastebincom")
		print("[*] Archiving old Paste.org pastes...")
		tools.archivepastes(archivepath, "pastebincom")

	print(f"Iteration: {str(iterator)}")
	iterator += 1
	http = httplib2.Http()
	try:
		r = requests.post(f"https://scrape.pastebin.com/api_scraping.php?limit={pastebinLimit}")
		#status, response = http.request(f"https://scrape.pastebin.com/api_scraping.php?limit={pastebinLimit}")
		#result =  json.loads(response.decode('utf-8'))
		result = r.json()
		print(f"[#] Pastebin limit set to: {pastebinLimit}\n[#] Gathering Tasty Pastes...")
		time.sleep(20)

		for apiPaste in result: # Iterate over the json file to find Paste URLs
			if  os.path.exists("data/raw_pastes/" + apiPaste["key"]):
				print("[-] " + apiPaste["key"] + " already exists. Skipping...")
				continue
			print("[*] Crawling " + apiPaste["key"])
			binStatus, binResponse = http.request(apiPaste["scrape_url"])
			try:
				foundPasswords = 0

				file_ = open("data/raw_pastes/" + apiPaste["key"], "wb")
				file_.write(binResponse)
				file_.close()

				emailPattern = os.popen("grep -l -E -o \"\\b[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z0-9.-]+\\b\" data/raw_pastes/" + apiPaste["key"]).read()
				emailPattern = emailPattern.split("\n")
				for file in emailPattern:
					if file != "":
						with open("data/raw_pastes/" + apiPaste["key"]) as f:
							pasteContent = f.readlines()
						skip = 0
						if useTwitter:
							for line in pasteContent:
								curLine = line.strip()
								if (":" in curLine or ";" in curLine or "," in curLine) and "://" not in curLine and len(curLine) <=100 and "android:" not in curLine and "#EXTINF" not in curLine:
									tools.checknotificationtargets(notificationtargets, curLine, apiPaste["key"]) #classes.utility.ScavUtility()
								else:
									skip = 1
						if skip == 0:
							foundPasswords = 1

				foundSQLdump = 0
				with open("data/raw_pastes/" + apiPaste["key"]) as f:
					pasteContent = f.readlines()

				completePaste = ""
				for line in pasteContent:
					curLine = line.strip()
					completePaste += curLine

				if ("insert into" in completePaste or "INSERT INTO" in completePaste) and ("users" in completePaste or "USERS" in completePaste) and len(completePaste) >= 500 and ("<?php" not in completePaste) and ("values" in completePaste or "VALUES" in completePaste):
					rex = re.compile("INSERT INTO (\S+) \(")
					rex2 = re.compile("insert into (\S+) \(")
					if len(rex.findall(completePaste)) > 0 or len(rex2.findall(completePaste)) > 0:
						foundSQLdump = 1

				curPasteMySQLi = os.popen("grep -i mysqli_connect\( data/raw_pastes/" + apiPaste["key"]).read()
				curPasteRSA = os.popen("grep -i 'BEGIN RSA PRIVATE KEY' data/raw_pastes/" + apiPaste["key"]).read()
				curPasteWP = os.popen("grep -i 'The name of the database for WordPress' data/raw_pastes/" + apiPaste["key"]).read()
				curPasteAPIKey = os.popen("grep -i 'apiKey: ' data/raw_pastes/" + apiPaste["key"]).read()
				curPasteMailContent = os.popen("grep -i 'Return-Path: ' data/raw_pastes/" + apiPaste["key"]).read()

				# search for onion links
				containsOnion = 0
				containsDocument = 0
				with open("data/raw_pastes/" + apiPaste["key"]) as f:
					onionContent = f.readlines()
				for line in onionContent:
					if ".onion" in line and len(line) <= 150:
						containsOnion = 1
						if ".pdf" in line or ".doc" in line or ".docx" in line or ".xls" in line or ".xlsx" in line:
							containsDocument = 1

				if foundSQLdump == 1:
					foundSQLdump = 0
					print("Found SQL dump. Posting on Twitter...")
					tweetText = "http://pastebin.com/raw/" + apiPaste["key"] + " possibly contains a SQL dump (size: " + str(apiPaste["size"]) + ") "
					if useTwitter: api.update_status()  # TWITTER
					os.system("cp data/raw_pastes/" + apiPaste["key"] + " data/sql_dumps/.")
					tools.statisticsaddpoint()
				elif foundPasswords == 1:
					foundPasswords = 0
					print("Found credentials. Posting on Twitter...")
					if useTwitter: api.update_status()  # TWITTER
					tools.statisticsaddpoint()
				elif curPasteAPIKey != "":
					print("Found API key. Posting on Twitter...")
					if useTwitter: api.update_status()  # TWITTER
					os.system("cp data/raw_pastes/" + apiPaste["key"] + " data/api_leaks/.")
				elif curPasteMailContent != "":
					print("Found email content. Posting on Twitter...")
					if useTwitter: api.update_status()  # TWITTER
					os.system("cp data/raw_pastes/" + apiPaste["key"] + " data/mails_leaks/.")
				elif curPasteRSA != "":
					print("Found RSA key. Posting on Twitter...")
					if useTwitter: api.update_status()  # TWITTER
					tools.statisticsaddpoint()
					os.system("cp data/raw_pastes/" + apiPaste["key"] + " data/rsa_leaks/.")
				elif curPasteWP != "":
					print("Found Wordpress configuration file. Posting on Twitter...")
					if useTwitter: api.update_status()  # TWITTER
					tools.statisticsaddpoint()
					os.system("cp data/raw_pastes/" + apiPaste["key"] + " data/wordpress_leaks/.")
				elif curPasteMySQLi != "":
					print("Found MySQL connect string. Posting on Twitter...")
					if useTwitter: api.update_status()  # TWITTER
					tools.statisticsaddpoint()
					os.system("cp data/raw_pastes/" + apiPaste["key"] + " data/mysql_leaks/.")
				elif containsOnion == 1:
					if containsDocument == 1:
						print("Found .onion link to a document. Posting on Twitter...")
						if useTwitter: api.update_status()  # TWITTER
						tools.statisticsaddpoint()
						os.system("cp data/raw_pastes/" + apiPaste["key"] + " data/onion_docs/.")
					else:
						print("Found .onion link. Posting on Twitter...")
						if useTwitter: api.update_status()  # TWITTER
						tools.statisticsaddpoint()
						os.system("cp data/raw_pastes/" + apiPaste["key"] + " data/onion/.")

				time.sleep(1)
			except Exception as e:
				print(e)
				continue

		print("++++++++++")
		print("")
	except Exception as e:
		print(e)
		continue
