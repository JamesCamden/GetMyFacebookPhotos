import sys
from User import User
from ArgumentsException import ArgumentsException
from Facebook import Facebook

class FBPhotoRetriever:

	user = None

	def __init__(self, args):
		self.parseArgs(args)
	
	def parseArgs(self, args):
		if len(args) != 3:
			raise ArgumentsException()
		self.user = User(args[1], args[2])

	def retrievePhotos(self):
		fb = Facebook(self.user)
		fb.login()
		firstPhotoId = fb.getFirstPhotoId()
		photoSetId = fb.getPhotoSetId()
		fb.downloadPhotos(firstPhotoId, photoSetId)

def main(args):
	fbpr = FBPhotoRetriever(args)
	fbpr.retrievePhotos()

if __name__ == '__main__':
	main(sys.argv)
