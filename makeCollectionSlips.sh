#!/bin/bash

# this dir..
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# temp dir to make the intermediate xml from the pdf
TMP=$(dirname $(mktemp tmp.XXXXXXXXXX -ut))

XMLFILE=$TMP/dump.xml
CVSCRIPT=$DIR/fromXml.py

echo Converting pdf to xml
pdftohtml -enc ISO-8859-6 -i -s -wbt 20 -xml $1 $XMLFILE

echo running $CVSCRIPT $XMLFILE
python $CVSCRIPT $XMLFILE  > "${DIR}/${1%.pdf}.html"