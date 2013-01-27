#
# TorrentBytes Registration Bot
#
# Version:
#	1.1.0
# Authors:
#	Roee Shenberg and Ron Reiter. Updated by Yaron Budowski
# History:
#	1.0.0 - Initial Release (R.S. and R.R.)
#	1.1.0 - Can now fill registration form fully automatically (Y.B.)
#


import Image
import urllib2
import tb_image
import os
import re
import sys
from threading import Timer
from time import sleep
from optparse import OptionParser, OptionValueError


#
# Constants
#

SCRIPT_VERSION = '1.1.0'

REGISTRATION_TIMEOUT = 60.0

TAKE_SIGNUP_LINK = 'http://www.torrentbytes.net/takesignup.php'

RULES_LINK = 'http://www.torrentbytes.net/rules.php'
FAQ_LINK = 'http://www.torrentbytes.net/faq.php'

SIGNUP_REGEX = r'<input type="hidden" name="signup" value="(\d+)" />'
CONFIRMATION_CODE_IMAGE_LINK = 'http://www.torrentbytes.net/image.php'
SIGNUP_LINK = 'http://www.torrentbytes.net/signup.php'
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; MathPlayer 2.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)'
PHP_SESSION_COOKIE = 'PHPSESSID=94512167fd904e98c584134eadf86bfa; checksum=d3ba4cfe269866e82d60403d634f40de'

USER_LIMIT_REACHED = 'The current user account limit'
USER_LIMIT_REACHED2 = 'Sorry, user limit reached. Please try again later.'
IP_EXISTS = 'It appears you (or someone else using the same ip'
SAME_IP_REGEX = 'or someone else using the same ip, ([0-9.]+)'
ENTER_CONFIRMATION = 'Please enter the confirmation code to continue sign up process'
REGISTRATION_SUCCESSFUL = 'A confirmation email has been sent to the address you specified'
CONFIRMATION_EMAIL_REGEX = 'A confirmation email has been sent to the address you specified \((.+)\)\. You need to'

MSG_INFO = 1
MSG_ERROR = 2
MSG_CRITICAL = 3


#
# Functions
#

g_reached_timeout = False

def reached_timeout():
	global g_reached_timeout
	g_reached_timeout = True

def print_message(message_type, message_text):
	if (message_type == MSG_INFO):
		c = '+'
	elif (message_type == MSG_ERROR):
		c = '-'
	elif (message_type == MSG_CRITICAL):
		c = '!'

	print '[%s] %s' % (c, message_text)

	if (message_type == MSG_CRITICAL):
		sys.exit(1)


def check_password(option, opt_str, value, parser):
	if (len(value) < 10):
		raise OptionValueError('Password must be at least 10 characters long!')
	if ((not re.search('[A-Z]', value)) or (not re.search('[a-z]', value))):
		raise OptionValueError('Password must contain both lower and upper case letters!')
	setattr(parser.values, option.dest, value)

def check_email(option, opt_str, value, parser):
	if ('@' not in value):
		raise OptionValueError('Invalid email address!')
	setattr(parser.values, option.dest, value)


def register_to_torrent_bytes(opener, username, password, email):
	global g_reached_timeout

	# Read the signup temporary variable
	print_message(MSG_INFO, "Opening signup page...")
	html = opener.open(SIGNUP_LINK).read()

	# Check to see if we got the hidden variable
	signup_value = re.findall(SIGNUP_REGEX, html)
	if (not signup_value):
		print_message(MSG_CRITICAL, "There was an error getting the signup value!")

	signup = signup_value[0]

	# Download the verification image
	print_message(MSG_INFO, "Downloading confirmation code picture...")
	data = opener.open(CONFIRMATION_CODE_IMAGE_LINK).read()

	# Write it to a temporary image
	open("temp.png","wb").write(data)

	# Remove shadow and turn to monochrome
	print_message(MSG_INFO, "Fixing image...")
	tb_image.tb_fix_image("temp.png","temp.bmp")
	code = Image.open("temp.bmp")

	confirmation_code = tb_image.find_confirmation_code(code)

	print_message(MSG_INFO, "Confirmation code: %s" % confirmation_code)

	# Make sure we got 8 letters total
	if (len(confirmation_code) != 8):
		print_message(MSG_ERROR, "Wrong number of letters detected (%d instead of 8)!" % (len(confirmation_code)))
		return False

	# Create the query string
	query_string = "confirmation_code_enter=%s&signup=%s&btnsignup=Sign+Up!" % (confirmation_code, signup)

	# Resend the signup page with a POST of the confirmation code
	next_html = opener.open(SIGNUP_LINK, query_string).read()

	# Check to see if we can register now
	if (USER_LIMIT_REACHED in next_html):
		print_message(MSG_ERROR, "Registration limit reached.")
		return False
	elif (ENTER_CONFIRMATION in next_html):
		# Uh oh, something went wrong...
		print_message(MSG_ERROR, "There was an error, reached confirmation code screen!")
		return False
	else:
		# We can probably register now... so we wait.
		print_message(MSG_INFO, "Reached registration form. Entering user details...")

		# Start the registration timer.
		g_reached_timeout = False
		timer = Timer(REGISTRATION_TIMEOUT, reached_timeout)
		timer.start()

		# Download the verification image
		print_message(MSG_INFO, "Downloading second confirmation code picture...")
		data = opener.open(CONFIRMATION_CODE_IMAGE_LINK).read()

		# Write it to a temporary image
		open("temp.png","wb").write(data)

		# Remove shadow and turn to monochrome
		print_message(MSG_INFO, "Fixing image...")
		tb_image.tb_fix_image("temp.png","temp.bmp")
		code = Image.open("temp.bmp")

		confirmation_code = tb_image.find_confirmation_code(code)

		print_message(MSG_INFO, "Confirmation code: %s" % confirmation_code)

		# Make sure we got 8 letters total
		if (len(confirmation_code) != 8):
			print_message(MSG_ERROR, "Wrong number of letters detected (%d instead of 8)!" % (len(confirmation_code)))
			return False

		print_message(MSG_INFO, "Reading rules page...")

		# Read the rules page.
		rules_html = opener.open(RULES_LINK).read()

		# Read the FAQ page.
		print_message(MSG_INFO, "Reading FAQ page...")
		faq_html = opener.open(FAQ_LINK).read()

		print_message(MSG_INFO, "Waiting for %d seconds to pass..." % (REGISTRATION_TIMEOUT))

		while (not g_reached_timeout):
			sleep(1)

		# Create the query string
		query_string = "confirmation_code=%s&signup=%s&btnsignup=Sign+Up!&wantusername=%s&wantpassword=%s&passagain=%s&email=%s&rulesverify=yes&faqverify=yes&ageverify=yes" % (confirmation_code, signup, username, password, password, email)

		print_message(MSG_INFO, "Posting registration info...")

		# Send the registration info page with a POST of the confirmation code and user details
		sign_up_html = opener.open(TAKE_SIGNUP_LINK, query_string).read()

		if (USER_LIMIT_REACHED in sign_up_html) or (USER_LIMIT_REACHED2 in sign_up_html):
			print_message(MSG_ERROR, "Registration limit reached.")
			return False

		elif (IP_EXISTS in sign_up_html):
			ip = re.findall(SAME_IP_REGEX, sign_up_html)
			if (ip):
				print_message(MSG_ERROR, "Seems like someone with the same IP address (%s) is already registered at Torrentbytes." % ip[0])
			else:
				print_message(MSG_ERROR, "Seems like someone with the same IP address is already registered at Torrentbytes.")

			print_message(MSG_ERROR, "Replace IP and press Enter to continue...")
			raw_input()
			return False

		elif (REGISTRATION_SUCCESSFUL in sign_up_html):
			email = re.findall(CONFIRMATION_EMAIL_REGEX, sign_up_html)
			if (email):
				print_message(MSG_INFO, "Registration successful! Confirmation email sent to: %s" % email[0])
			else:
				print_message(MSG_INFO, "Registration successful!")

			print_message(MSG_INFO, "Press Enter to continue...")
			raw_input()
			return True
		else:
			print_message(MSG_ERROR, "Unknown response:")
			print sign_up_html
			print_message(MSG_ERROR, "Press Enter to continue...")
			raw_input()
			return False

#
# Main Code
#


parser = OptionParser(usage = '%prog <options>', description = 'TorrentBytes Registration Bot %s. Written by Roee Shenberg and Ron Reiter; updated by Yaron Budowski' % (SCRIPT_VERSION), version = 'TorrentBytes Registration Bot %s' % SCRIPT_VERSION)
parser.add_option('-u', '--user', action = 'store', type = 'string', dest = 'username', metavar = 'USERNAME', help = 'register with USERNAME')
parser.add_option('-p', '--password', action = 'callback', type = 'string', callback = check_password, dest = 'password', metavar = 'PASSWORD', help = 'register with PASSWORD (at least 10 characters long, both lower and upper case letters)')
parser.add_option('-e', '--email', action = 'callback', type = 'string', callback = check_email, dest = 'email', metavar = 'EMAIL', help = 'register with EMAIL')
parser.add_option('-r', '--proxy', action = 'store', type = 'string', dest = 'proxy_url', metavar = 'PROXY_URL', help = 'register to TB via PROXY_URL. i.e.: http://127.0.0.1:8118')
parser.add_option('-t', '--try-count', action = 'store', type = 'int', dest = 'max_try_count', default = '1', metavar = 'TRY_COUNT', help = 'try to register to TB at most TRY_COUNT times (0 = infinite)')

(options, args) = parser.parse_args()

if ((not options.username) and (not options.password) and (not options.email)):
	parser.print_usage()
	sys.exit()

if (not options.username):
	print_message(MSG_CRITICAL, "Username required!")
elif (not options.password):
	print_message(MSG_CRITICAL, "Password required!")
elif (not options.email):
	print_message(MSG_CRITICAL, "Email required!")
elif (options.max_try_count < 0):
	print_message(MSG_CRITICAL, "Try count must be at least zero!")


# Build the "IE" opener

if (options.proxy_url):
	opener = urllib2.build_opener(urllib2.ProxyHandler({'http': options.proxy_url}))
else:
	opener = urllib2.build_opener()

opener.addheaders = [
	('Accept', '*/*'),
	('Connection', 'Keep-Alive'),
	('Accept-Language', 'en'),
	('User-Agent', USER_AGENT),
	('Cookie', PHP_SESSION_COOKIE),
	('Referer', SIGNUP_LINK),
]

registration_try_count = 0
registration_successful = False

while (((registration_try_count < options.max_try_count) or (options.max_try_count == 0)) and (registration_successful == False)):
	print_message(MSG_INFO, 'Registration try #%d' % (registration_try_count + 1))
	registration_successful = register_to_torrent_bytes(opener, options.username, options.password, options.email)

	if (not registration_successful):
		registration_try_count += 1
		print '-----------------------'


