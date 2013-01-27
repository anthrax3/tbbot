

def append_letter(datfile,img,name):
    data = img.getdata()
    width,height = img.size
    columns = [data[i::width] for i in xrange(width)]
    transposed = reduce(lambda x,y: x+y, columns)
    transformed = "".join(map(str,transposed))
    datfile.write(name + '=' + transformed)