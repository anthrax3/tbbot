import numpy

# list of tuples in form of ('a',[-/+1,-/+1,-/+1,...])
letter_glyphs = []

def match_letter(let1, let2):
	"""assumes let1 and let2 are sequences of -1 and 1, signifying black and white
	Doesn't matter which is which as long as they're consistent"""
	return max(map(abs,numpy.correlate(let1,let2,mode="full")))

def find_best_letter(let):
	"Find the glyph that best matches the input"

	let += "0" * (30 * 25 - len(let))
	letter_row = [[-1,1][pix == '1'] for pix in let]

	matches = [(char,match_letter(letter_row,data)) for char,data in letter_glyphs]
	# fugly
	matches.sort(cmp = lambda x,y: cmp(x[1],y[1]))
	return matches[-1]


#temp
def load_letter(fname):
	im = Image.open(fname)
	return [[-1,1][pix] for pix in im.getdata()]

def load_letter_file(fname):
	glyph_list = []
	for line in open(fname):
		letter, letter_map = line.strip().split("=")
		letter_map += "0" * (30 * 25 - len(letter_map))
		letter_row = [[-1,1][pix == '1'] for pix in letter_map]
		glyph_list.append((letter, letter_row))
	return glyph_list

letter_glyphs = load_letter_file("letters.dat")

def main():
	global letter_glyphs
	b = letter_glyphs.pop()
	print find_best_letter(b[1])

if __name__ == '__main__':
	main()

