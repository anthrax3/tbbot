import Image
import sys
import match_letter

LETTER_SIZE = (25,30)
MIN_WIDTH = 6

# Translate the color white (255) to a blank pixel (0) 
# and the color black (0) to a letter pixel (1)
def xlate_col(col):
	if col == 255:
		return 0
	return 1

def find_confirmation_code(code):
	confirmation_code = ''
	letter_num = 0
	colcut = []

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
	return confirmation_code

def enter_confirmation_code(code):
	confirmation_code = []
	letter_num = 0
	colcut = []

	# Scan the columns
	first = True
	for x in xrange(code.size[0]-1):
		# Get the current column and the next one
		col1 = [1-code.getpixel((x,y)) for y in xrange(code.size[1])]
		col2 = [1-code.getpixel((x+1,y)) for y in xrange(code.size[1])]

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

	# Finished finding letters
	# Create the letter maps
	if (len(colcut) != 9):
		print 'Error! %d letters found (8 expected!)' % (len(colcut)-1)
		return []

	for i in xrange(len(colcut)-1):
		letter_array = []
		for ly in xrange(LETTER_SIZE[1]):
			for lx in xrange(colcut[i], colcut[i+1]):
				letter_array.append(1-code.getpixel((lx,ly)))
		
		temp_img = Image.new('1',(colcut[i+1] - colcut[i],LETTER_SIZE[1]))
		temp_img.putdata(letter_array)
		temp_img.show()
		letter = raw_input("Enter letter: ")
	
	# Find the best matching letter for our current letter map
	confirmation_code += [(letter,temp_img)]
	return confirmation_code




def is_blue_col(idx):
    global lut
    r,g,b = lut[idx]
    # If the color isn't a shade of blue according to this stupid test
    if r>=g or g>=b-10 or r>=b-10:
        # change to white
        return 1
    return 0
def tb_fix_image(src):
    global lut
    im = src
    lut = im.resize((256, 1))
    lut.putdata(range(256))
    lut = lut.convert("RGB").getdata()
    return im.point(is_blue_col,'1')
    

def tb_fix_image_file(src_name,dst_name):
    global lut
    im = Image.open(src_name)
    lut = im.resize((256, 1))
    lut.putdata(range(256))
    lut = lut.convert("RGB").getdata()
    im2 = im.point(is_blue_col,'1')
    im2.save(dst_name,'BMP')

if __name__ == '__main__':
    print 'fix tb image for OCR'
    if (len(sys.argv) != 3):
        print 'usage: %s <src image> <output image>'
        sys.exit(1)
    tb_fix_image_file(sys.argv[1],sys.argv[2])
    print 'Done!'

