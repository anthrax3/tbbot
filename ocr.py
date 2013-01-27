# TBBot v1.0 Roee Shenberg and Ron Reiter

import Image
import urllib2
import tb_image
import match_letter
import os
import re
import sys

# Translate the color white (255) to a blank pixel (0) 
# and the color black (0) to a letter pixel (1)
def xlate_col(col):
	if col == 255:
		return 0
	return 1

LETTER_SIZE = (25,30)
MIN_WIDTH = 6

SIGNUP_REGEX = r'<input type="hidden" name="signup" value="(\d+)" />'
IMAGE_LINK = 'http://www.torrentbytes.net/image.php'
SIGNUP_LINK = 'http://www.torrentbytes.net/signup.php'
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; MathPlayer 2.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)'
PHP_SESSION_COOKIE = 'PHPSESSID=94512167fd904e98c584134eadf86bfa; checksum=d3ba4cfe269866e82d60403d634f40de'

USER_LIMIT_REACHED = 'The current user account limit'
ENTER_CONFIRMATION = 'Please enter the confirmation code to continue sign up process'

colcut = []
letter_num = 0
confirmation_code = ''

# Build the "IE" opener
#opener = urllib2.build_opener()
opener = urllib2.build_opener(urllib2.ProxyHandler({'http': 'http://127.0.0.1:8118/'}))
opener.addheaders = [
	('Accept', '*/*'),
	('Connection', 'Keep-Alive'),
	('Accept-Language', 'en'),
	('User-Agent', USER_AGENT),
	('Cookie', PHP_SESSION_COOKIE),
	('Referer', SIGNUP_LINK),
]

# Read the signup temporary variable
print "Opening signup page..."
html = opener.open(SIGNUP_LINK).read()

# Check to see if we got the hidden variable
signup_value = re.findall(SIGNUP_REGEX, html)
if not signup_value:
	print "There was an error getting the signup value!"
	sys.exit(1)

signup = signup_value[0]

# Download the verification image
print "Downloading picture..."
data = opener.open(IMAGE_LINK).read()

# Write it to a temporary image
open("temp.png","wb").write(data)
#os.startfile("temp.png")

# Remove shadow and turn to monochrome
print "Fixing image..."
tb_image.tb_fix_image("temp.png","temp.bmp")
code = Image.open("temp.bmp")

# Scan the columns
first = True
for x in xrange(code.size[0]-1):
	# Get the current column and the next one
	col1 = [xlate_col(code.getpixel((x,y))) for y in xrange(code.size[1])]
	col2 = [xlate_col(code.getpixel((x+1,y))) for y in xrange(code.size[1])]

	# Skip a white column
	if 1 not in col1:
		continue

	# If this is our first column with a letter, add it to the column cut list
	if first:
		first = False
		colcut.append(x-1)

	# Check if the next column connects to the current one
	conn = False

	for y in xrange(1,code.size[1]-1):
			if col1[y] and (col2[y-1] or col2[y] or col2[y+1]):
					conn = True

	# If the columns are not connected, then we've reached a new letter
	if conn == False:
			# If we haven't reached the minimum width, ignore the disconnection
			# between the two parts of the letter and continue
			if x - colcut[-1] < MIN_WIDTH:
				continue

			#print "Checking letter %d at location %d" % (letter_num, x)

			colcut.append(x+1)

			# Create the letter map
			letter_array = []
			for lx in xrange(colcut[-2], colcut[-1]):
				for ly in xrange(LETTER_SIZE[1]):
					pixel = 1 - xlate_col(code.getpixel((lx,ly)))
					letter_array.append(str(pixel))

			letter_map = "".join(letter_array)

			# Find the best matching letter for our current letter map
			confirmation_code += match_letter.find_best_letter(letter_map)[0]
			letter_num += 1

print "Confirmation code: %s" % confirmation_code

# Make sure we got 8 letters total
if letter_num != 8:
	print "Wrong number of letters detected!"
	print "Number of letters: %d" % letter_num
	sys.exit(1)

# Create the query string
query_string = "confirmation_code_enter=%s&signup=%s&btnsignup=Sign+Up!" % (confirmation_code, signup)

# Resend the signup page with a POST of the confirmation code
next_html = opener.open(SIGNUP_LINK, query_string).read()

# Check to see if we can register now
if USER_LIMIT_REACHED in next_html:
	print "Registration limit reached. Try again."
# Uh oh, something went wrong...
elif ENTER_CONFIRMATION in next_html:
	print "There was an error, reached confirmation code screen!"
# We can probably register now... so we wait.
else:
	print "Register now!!!"
	raw_input("Press Enter to continue...")
