tbbot
=====

Registration bot for the late torrentbytes written in February 2007. Solved their captcha to give a significant edge on the rest of the internet when hammering their registration page.

Was written by a few friends and myself as a quick hack.

The captcha had a few severe issues:
* letters aren't warped at all (constant size, etc.)
* colors are constant, making it easy to separate foreground from background
* letters are separated by at least one blank column

Captcha-solving works as follows:

1. convert the image to binary, where only blue-enough colors are black, and the rest is white (this step removes the shadows)

2. split the bitmap into letter bitmaps by looking for blank columns separating them

3. for each letter, cross-correlate its bitmap as a 1d vector with a small amount of pre-solved bitmaps. Correlation is done by using an FFT->multiplication->iFFT to perform a convolution, and the convolution with the highest maximum value is considered the match.

File details:

* c*.bmp - sample captchas, and after some processing.
* letters.dat - file with solved letters
* match_letters.py - code to cross-correlate a bitmap with the database entries to find the best match.
* ocr.py - old version of the actual bot, includes letter separation
* tb_image.py - get the text from the captcha. Does image -> b/w bitmap conversion, letter separation, calls match_letters for solving each letter
* tbbot.py - newer version of the bot in response to changes in their HTML.s

