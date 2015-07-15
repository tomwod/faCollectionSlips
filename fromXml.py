import re
import sys

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]   

def parseLines(f):
    """ generator. parses lines in the provided file.  yields tuples of (leftAlign, text)
    leftAlign is the best indicator of current column (ie each type of data always has same left 
    alignment)
    """
    for l in f.readlines():
        l = l.strip()
        if not l:
            continue
        if any([x in l for x in skip]): 
            continue
        data = [x for x in re.findall(r"\>(.*?)\<",l) if x]
        if not data:
            continue
        if len(data)>1: # there should be one tag per line
            sys.stderr.write("More than one xml tag on this line.  Thats unexpected! (%s)" % l)
            sys.exit(1)
            
        try:
            leftAlign = [x for x in re.findall(r"left=\"(.*?)\"",l) if x][0]
        except Exception:
            sys.stderr.write("Failed to get left alignment from line (%s).  Thats unexpected!" % l)
            sys.exit(1)

        yield leftAlign, data[0]

try:
    xmlfile = sys.argv[1]
except KeyError:
    sys.stderr.write("No output filename specified")
    sys.exit(1)

allinfo = {}
# skip any line containing any these words
skip = ['Page','Do not litter', 'MEMBER','SIGNATURE','QUANTITY', 'PRODUCER','Collection of']




# first bit is to go through the xml (which was generated from
# the original order confirmation pdf)

orderId=None

# list of member data (#-name, name, phone, address)
memberData = []
# dict of order data (key is producer) - values are tuples (count, product)
orderData = {}
productdata=[]
productCount = None
producer=None


leftalign_member = None
leftalign_producer = None
leftalign_product = None
leftalign_productcount = None

for i, x in enumerate(parseLines(open(xmlfile))):
    leftAlign, data = x
    
    # orderNumber - name
    if re.match("[0-9]+ [-]", data):
        # this usually means the end of the previous order - so store it (it's not if this is the
        # first name in the file)
        if orderId:
            if productdata:
                orderData[producer].append((productCount, " ".join(productdata)))
                productdata = []
            allinfo[orderId]['member'] = memberData
            allinfo[orderId]['order'] = orderData

        # remember this left alignment - it will always be the same for member data
        leftalign_member = leftalign_member or leftAlign

        # next order id ("# - name")
        orderId = data

        # reset, ready for this next order to go in
        allinfo.setdefault(orderId,{})
        memberData = []
        orderData = {}
        producernamedata = []

    # ignore everything until we've hit the first member entry
    if not leftalign_member:
        continue

    if leftAlign == leftalign_member:
        memberData.append(data)
        continue
    
    if not leftalign_producer:
        # this is the first producer line (we've never seen one before and the previous line
        # was info about the member)
        leftalign_producer = leftAlign
    
    if leftalign_producer == leftAlign:
        # a producer name may be split over more than one line, so keep adding while in the same
        # column (ie while alignment is the same)
        producernamedata.append(data)
        continue
    
    if not leftalign_productcount:
        # first time we've seen a product count (after the first producer)
        leftalign_productcount = leftAlign

    if leftAlign == leftalign_productcount:
        # this line is a product count column

        # if we have previous product title data then it's time to add the count+product to this
        # order under the current producer
        if productdata:
            # productCount is the PREVIOUS count (not the current line - that's for the next product)
            orderData[producer].append((productCount, " ".join(productdata)))

            # empty the productdata list ready for the next product
            productdata = []
        
        # if there's producer name data then add the producer name to the order data
        if producernamedata:
            producer = " ".join(producernamedata).title()
        
        # next product has this many..
        productCount = data

        # as we're on a new product next, clear some data
        producernamedata = [] 
        orderData.setdefault(producer, [])
        continue

    if not leftalign_product:
        # first product
        leftalign_product = leftAlign

    if leftAlign == leftalign_product:
        # one product may take more than one line so this will keep adding while we're in the
        # same column (same alignment)
        productdata.append(data)

# add the last order to the dict
if orderId:
    allinfo[orderId]['member'] = memberData
    allinfo[orderId]['order'] = orderData



# output everything as html ready to be printed out
print '<body style="font-size:10;"'# font-family:verdana">'
page = ''
pages = []
pageLen = 60
tables = []
for x in sorted(allinfo.keys(),key=natural_sort_key):
    table = '<br>'
    table+= '<table cellpadding=0 width=85% style="border:4px solid black;">'
    table+= "<tr>"

    # ['member'][2] is in MOST cases the full name, but sometimes a long/double barrelled  first 
    #   name might put that out
    nameData = allinfo[x]['member']
    name = allinfo[x]['member'][2]
    
    # for a better attempt at name, the full name is all the memberdata elements between the 
    # order count (ie "6th order") and the phone number.  this convoluted hackery gets the full name
    start = end = 0
    for n, e in enumerate(nameData):
        if "order" in e:
            # from here..
            start = n+1
        if e.replace(" ", "").isdigit():
            # to here (this must be the phone number...)
            name = " ".join(nameData[start:n])
            break
    name = name.title()

    table+= '<td border=0 colspan=3><p style="background: linear-gradient(to right, #AAAAAA, white); font-size:14; font-family:verdana;"><b>%s - %s</bv></p></td><td valign="top" rowspan=10 width=105><img height="115" width="100" src=logo.png></td>' % (x.split("-")[0], name)
    table+= "</tr>\n"
    for p in allinfo[x]['order']:
        table+= "<tr>"
        table+= '<td border=0 colspan=3><p style="background: linear-gradient(to right, #CCCCCC, white); font-size:12; font-family:verdana"><i>%s</i><p></td><td></td>' % p
        table+= "</tr>\n"
        for i in allinfo[x]['order'][p]:
            if i[0]:
                table+= "<tr>"
                table+= '<td></td><td border=0><p style="font-size:10; font-family:verdana">%s x </p></td><td><p style="font-size:11; font-family:verdana">%s</p></td><td></td>' % (i[0],i[1])
                table+= "</tr>\n"
    table+= '<tr><td colspan=3> </td></tr>'
    table+= "</table>"
    tables.append(table)
# put the orders in order of length - i think thats more paper efficient.
tables.sort(key=lambda x:len(x))
tpp=2
minh = 8
for t in tables:
    if len(t.split("\n")) > pageLen:
        p = t
        p+= "<p><!-- pagebreak --></p>" 
        p+= '<p style="page-break-before: always">'
        p.append(p)
        continue
    elif tpp+len(t.split("\n"))+len(page.split("\n")) > pageLen:
        page+= "<p><!-- pagebreak --></p>" 
        page+= '<p style="page-break-before: always">'
        pages.append(page)
        page = ''
        tpp=2
    tpp+=1
    if minh-len(t.split("\n"))>0:
        tpp+= minh-len(t.split("\n"))
    page+=t
page+= "<p><!-- pagebreak --></p>" 
page+= '<p style="page-break-before: always">'
pages.append(page)
    #pprint(allinfo[x])
for page in pages:
    print page
print "</body>"
