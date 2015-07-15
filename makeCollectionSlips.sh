#!/bin/bash
XMLFILE=/tmp/dump.xml
CVSCRIPT=/home/tdownes/workspace/foodAssembly/fromXml.py
echo Converting pdf to xml
pdftohtml -enc ISO-8859-6 -i -s -wbt 20 -xml $1 $XMLFILE

echo running $CVSCRIPT $XMLFILE
python $CVSCRIPT $XMLFILE  > "${1%.pdf}.html"