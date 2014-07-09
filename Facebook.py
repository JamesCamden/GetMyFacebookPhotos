import urllib2, urllib, cookielib, re, os, sys, time

class Facebook():

    def __init__(self, user):
	self.user = user
	cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	opener.addheaders = [('Referer', 'http://login.facebook.com/login.php'),
                            ('Content-Type', 'application/x-www-form-urlencoded'),
                            ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7 (.NET CLR 3.5.30729)')]
        self.opener = opener
	
    def login(self):
	url = 'https://login.facebook.com/login.php?login_attempt=1'
	data = "locale=en_US&non_com_login=&email="+self.user.username+"&pass="+self.user.password+"&lsd=20TOl"
	usock = self.opener.open('http://www.facebook.com')
	usock = self.opener.open(url, data)
	body = usock.read()
	if body.find("<div class=\"pam login_error_box uiBoxRed\">") != -1:
	    body = body[body.find("<div class=\"pam login_error_box uiBoxRed\">"):]
	    if body.find("<div class=\"fsl fwb fcb\">") != -1:
		body = body[body.find("<div class=\"fsl fwb fcb\">"):]
		failureCause = body[25:body.find("</div")]
		failureCause = self.changeError2Cause(failureCause)
		raise Exception("Failed to login: " + failureCause)
            else:
                raise Exception ("Failed to login: unable to determine cause")
        print "Successfully logged in!"
	body.find("<li class=\"navItem firstItem tinyman litestandNavItem\">")
	body = body[body.find("<li class=\"navItem firstItem tinyman litestandNavItem\">"):]
	body = body[body.find("profile_pic_header_"):]
	body = body[len("profile_pic_header_"):]
        self.user.profileId = body[:body.find("\"")]
	if self.user.profileId == "":
	    raise Exception("Unable to identify profile id.")
	print "Profile id: " + self.user.profileId

    def getFirstPhotoId(self):
        url = 'https://www.facebook.com/profile.php?id=' + self.user.profileId + '&sk=photos'
	usock = self.opener.open(url)
	body = usock.read()
	body = body[body.find('<i style="background-image: url(https://'):]
	body = body[40:body.find(');"')]
	body = body.split('_')[1]
	return body

    def getPhotoSetId(self):
	'''
	url = 'https://www.facebook.com/profile.php?id=' + self.user.profileId + '&sk=photos'
	usock = self.opener.open(url)
	body = usock.read()
	body = body[body.find('<noscript><meta http-equiv="refresh" content="0; URL=/profile.php?id='):]
	body = body[len('<noscript><meta http-equiv="refresh" content="0; URL=/profile.php?id='):]
	body = body[:9]
	if body == "":
	    raise Exception("Unable to identify set id.")
	print "set id: " + body
	return body
	'''
	return self.user.profileId

    def downloadPhotos(self, firstPhotoId, photoSetId):
	photoId = firstPhotoId
	firstPhoto = True
	photoCount = 0
	print "Downloading photos"
	while (photoId != firstPhotoId) or firstPhoto:
	    firstPhoto = False
	    url = 'https://www.facebook.com/photo.php?fbid=' + photoId + '&set=t.' + photoSetId + '&type=1'
	    usock = self.opener.open(url)
	    body = usock.read()
	    photoUrl = self.getPhotoUrlFromBody(body)
	    try:
	        self.savePhoto(photoUrl)
	    except Exception as e:
 	        print str(e) + " url=" + url
            photoCount = photoCount + 1
	    nextUrl = self.getUrlOfNextPhoto(body)
	    if nextUrl.find('fbid=') != -1:
		tempBody = nextUrl[:nextUrl.find('&amp;set=')]
	        photoId = tempBody.split('fbid=')[1]
	    else:
		try:
		    print ""
		    print "problem finding next Id ",
		    tempBody = nextUrl[:nextUrl.find('"')]
		    if tempBody.find('v=') != -1:
                        photoId = tempBody[tempBody.find('v=') + 2:tempBody.find('v=') + 15]
	            else:
		        photoId = tempBody.split('/')[6]
		    if photoId == "":
			raise Exception("No Id found!!!")
		    print ""
		except Exception as e:
		    raise Exception("problem finding id in url: " + nextUrl + ":" + str(e))
	    if photoCount % 10 == 0:
		print ".",
	print ""
	print str(photoCount) + " photos downloaded"

    def getPhotoUrlFromBody(self, body):
	tempBody = body[body.find('<img class="fbPhotoImage img" id="fbPhotoImage" src="'):]
	return tempBody[53:tempBody.find('" alt')]

    def getUrlOfNextPhoto(self, body):
	tempBody = body[body.find('<a class="photoPageNextNav" onclick="PhotoPermalink.getInstance().pagerClick(&quot;next&quot;);" href="'):]
        tempBody = tempBody[len('<a class="photoPageNextNav" onclick="PhotoPermalink.getInstance().pagerClick(&quot;next&quot;);" href="'):]
	return tempBody[:tempBody.find('">Next</a>')]

    def savePhoto(self, url, attempts=0):
	try:
	    url = url.replace('&amp;', '&')
	    f = urllib.urlopen(url)
	    imageData = f.read()
	    f.close()
	    time.sleep(attempts) #Wait an increasing amount of time in case urlopen continues before completion
	    with open("photos\\photosofme\\" + url.split("_")[1] + ".jpg", "wb") as imgFile:
	        imgFile.write(imageData)
	    time.sleep(attempts) #Wait an increasing amount of time in case writing to file takes longer than expected
    	    self.checkPhotoIsSaved(url, attempts=attempts)
	    if attempts != 0:
		print "Successfully saved photo: " + url
	except Exception as e:
            attempts = attempts + 1
	    if attempts > 20:
		raise Exception("Can't download image: " + url + " " + str(e))
	    else:
                print "Failed to download image: " + url.split("_")[1] + " :" + str(e)
		print "Retrying. " + str(20 - attempts) + " attempts remain..."
  	        self.savePhoto(url, attempts=attempts)

    def checkPhotoIsSaved(self, url, attempts=0):
        try:
            f = open("photos\\photosofme\\" + url.split("_")[1] + ".jpg", 'r')
	    body = f.read()
	    f.close()
	    if body.find('An error occurred while processing your request.') != -1 or body.find('Sorry, something went wrong.') != -1 or body == "" or len(body) <= 3:
		raise Exception("Image contents error")
        except Exception as e:
	    os.remove("photos\\photosofme\\" + url.split("_")[1] + ".jpg")
	    time.sleep(5)
	    raise Exception("Failed to save image to file: " + str(e))

    def changeError2Cause(self, error):
        if error == "Please re-enter your password":
            return "Incorrect password"
	else:
	    return error
