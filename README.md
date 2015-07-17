# faCollectionSlips
food assembly member collection summary pdf to collection slips converter

# what?
at food assembly collections, customers forget what they have ordered.  this hackery generates printable collection 
receipts from the food assembly generated customer collection summary pdf.

# how?
get this code.
 
## pdftohtml
make sure you have pdftohtml (http://www.foolabs.com/xpdf/download.html) installed.  windows, mac and 
linux binaries available

on ubuntu you can get it like this
```
apt-get install poppler-utils
```

then download the customer collection summary pdf from your food assembly.  if you're here you know how to do that.
```
./makeCollectionSlips.sh thatPdfFile.pdf
```

this will result (hopefully) in an html file with the same name as the pdf.  load this in chrome, check, then print

## something is wrong
of course. this is a complete hack.  all sort of things could make it fail.  any change to the format/layout of the 
food assembly pdfs will break this.

get in touch, i'll probably help if this is useful to you.

## ps
why not print the main collection summary?  the document that this code produces has less personal info on it - 
no address/phone number

it's formatted such that collection receipts do not span page breaks. (unless an order is massive)

the slips are listed in order of size.  that might save paper. woo.

# what's food assembly?
https://thefoodassembly.com/en

i help a bit with the food assembly in Frome, UK. 