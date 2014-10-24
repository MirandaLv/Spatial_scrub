#Date: 10/9/2014
#Author: MirandaLv
#Note: Using fiona to do spatial scrub

import csv, sys, getopt, os
from shapely.geometry import Point, shape
import locale
import warnings, fiona
import pandas as pd
from pandas import DataFrame as df

#-------------------------------------input arguements from terminal---------------------------#
"""
opts, args= getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="]) #Need to polish the inputs later
inp1_csv=args[0]
lat=args[1]
lon=args[2]
location_type_code=args[3] #ADM1, ADM2, PPL
type_code=args[4]
geoname_adm_code=args[5] #NL|AL|....
inp4_shp=args[6]
ADM_shp=args[7]
"""
#----------------------------------------test arguements----------------------------------------#

inp1_csv="/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/locations.tsv"
lat="latitude"
lon="longitude"
location_type_code="location_type_code"
type_code=1
geoname_adm_code="geoname_adm_code" #NL|AL|....
inp4_shp="/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/TL_ADM1.shp"
ADM_shp="ADM1_NM_AB"

#-------------------------------------Get geomerty of shapefile---------------------------------#
#get all layers' geometry of input polygon, output as a dictionary
def getgeomerty(shp):
	with fiona.open(shp, 'r') as infile:
		dic={}
		for i in range(0,len(infile)):
			geometry=infile[i]["geometry"]
			country=infile[i]["properties"][ADM_shp] #"SOV_A3" could be an input argument
			dic[country]=geometry
		return dic


geom=getgeomerty(inp4_shp)

#-----------------------------------read and write a dataframe------------------------------------------#
# Read in raw data from csv
rawData = csv.DictReader(open(inp1_csv, 'rb'), delimiter='\t')
head=rawData.fieldnames
indictlist=[]
rownum=1
for utf8_row in rawData:
	row=dict([(key, unicode(value, 'utf-8')) for key, value in utf8_row.iteritems()])
	rownum+=1
	if row[lon]=="" or row[lat]=="":
		warningstring='WARN: ROW ' + str(rownum) + " in the input tsv file does not have latitude/longitude"
		warnings.warn(warningstring)
	if row[location_type_code].lower()=="adm" + str(type_code):
		adm_code=row[geoname_adm_code].rsplit("|")[type_code]
		if row[lon]!="" and row[lat]!="": 
			pointX = locale.atof(row[lon])  #make sure coordinates are not string
			pointY = locale.atof(row[lat])
			thePoint=Point(pointX, pointY)
			if not shape(geom[adm_code]).contains(thePoint)==True:
				indictlist.append(row)

#----------------------------------output dataframe------------------------------------------------#
#outdf=df(columns=head) #create a new blank dataframe
outdf=df(indictlist, columns=head)
print outdf
#outdf.to_csv('/home/mirandalv/Desktop/Honduras_spatial_scrub_output.tsv', index_label='ROW_NUM', sep='\t', quotechar='\"')

