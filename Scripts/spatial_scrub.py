#Date: 10/28/2014
#Author: MirandaLv
"""
Note: spatial scrub for ADM 0, ADM1, ADM2
The inputs for this code should be either 5 or 9
For ADM0 country:
	1. tsv file has coordinates for each project
	2. latitude column name (case sensitive)
	3. longitude column name (case sensitive)
	4. ADM0 country shapefile
	5. output tsv
For ADM 1 & 2 level:
	1. tsv file
	2. latitude column name (case sensitive)
	3. longitude column name (case sensitive)
	4. coloum head of location_type_code
	5. project type code, if it is ADM 1, then this input argument is 1
	6. column head of geoname_adm_code, ususally the format of this column is NP|..|.. or SN|..|.. 
	7. input ADM 1 or ADM 2 shapefile
	8. ISO 2 in shapefile attribute table, usually it's two letter abbriviation of that state name
	9. output tsv
"""
import csv, sys, getopt, os
from shapely.geometry import Point, shape
import locale
import warnings, fiona
import pandas as pd
from pandas import DataFrame as df
from shapely.wkb import loads
from osgeo import ogr

#-------------------------------------input arguements from terminal---------------------------#

opts, args= getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="]) #Need to polish the inputs late

#----------------------------------------test arguements----------------------------------------#
"""
inp1_csv="/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/locations.tsv"
lat="latitude"
lon="longitude"
location_type_code="location_type_code"
type_code=1
geoname_adm_code="geoname_adm_code" #NL|AL|....
inp4_shp="/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/TL_ADM1.shp"
ADM_shp="ADM1_NM_AB"
"""
#-------------------------------------Get geomerty of shapefile---------------------------------#
#----ADM1&ADM2----#
#get all layers' geometry of input polygon, output as a dictionary
def getgeometry_all(shp):
	with fiona.open(shp, 'r') as infile:
		dic={}
		for i in range(0,len(infile)):
			geometry=infile[i]["geometry"]
			country=infile[i]["properties"][ADM_shp] #"SOV_A3" could be an input argument
			dic[country]=geometry
		return dic
#-------ADM0-------#
def getgeometry_sg(shp):
	openShape=ogr.Open(str(shp))
	basename=os.path.basename(shp)
	shpname=os.path.splitext(basename)[0]
	layers=openShape.GetLayerByName(shpname)
	for element in layers:
		geom=loads(element.GetGeometryRef().ExportToWkb())
		return geom

#-----------------------------------read and write a dataframe------------------------------------------#
# Read in raw data from csv
# Check each row's latitude&longitude
# Output a tsv file

#---------9 input arguments------ADM1, ADM2--------#
def ss_9arg(infcsv, latitude, longitude, in_loc_type_code, in_type_code, in_geoname_admcode, shp_geom, csvoutput):
	rawData = csv.DictReader(open(infcsv, 'rb'), delimiter='\t')
	head=rawData.fieldnames
	indictlist=[]
	rownum=1
	for utf8_row in rawData:
		row=dict([(key, unicode(value, 'utf-8')) for key, value in utf8_row.iteritems()])
		rownum+=1
		if row[longitude]=="" or row[latitude]=="":
			warningstring='WARN: ROW ' + str(rownum) + " in the input tsv file does not have latitude/longitude"
			warnings.warn(warningstring)
		if row[in_loc_type_code].lower()=="adm" + str(in_type_code):
			adm_code=row[in_geoname_admcode].rsplit("|")[in_type_code]
			if row[longitude]!="" and row[latitude]!="": 
				pointX = locale.atof(row[longitude])  #make sure coordinates are not string
				pointY = locale.atof(row[latitude])
				thePoint=Point(pointX, pointY)
				if not shape(shp_geom[adm_code]).contains(thePoint)==True:
					indictlist.append(row)
	outdf=df(indictlist, columns=head)
	outdf.to_csv(csvoutput, index_label='ROW_NUM', sep='\t', quotechar='\"', encoding='utf-8')

#---------5 input arguments---------ADM0----------#
def ss_5arg(infcsv, latitude, longitude, shp_geom, csvoutput):
	rawData = csv.DictReader(open(infcsv, 'rb'), delimiter='\t')
	head=rawData.fieldnames
	indictlist=[]
	rownum=1
	for utf8_row in rawData:
		row=dict([(key, unicode(value, 'utf-8')) for key, value in utf8_row.iteritems()])
		rownum+=1
		if row[longitude]=="" or row[latitude]=="":
			warningstring='WARN: ROW ' + str(rownum) + " in the input tsv file does not have latitude/longitude"
			warnings.warn(warningstring)
		elif row[longitude]!="" and row[latitude]!="":
			pointX = locale.atof(row[longitude]) #make sure coordinates are not string
			pointY = locale.atof(row[latitude])
			thePoint=Point(pointX, pointY)
			if not thePoint.within(shp_geom)==True:
				row['ROW_NUM']=rownum
				indictlist.append(row)
	outdf=df(indictlist, columns=head)
	outdf.to_csv(csvoutput, sep='\t', quotechar='\"', encoding='utf-8', index_label='ROW_NUM') 


#-------------------------------------test for 5 input arguments--------------------------------------#
"""
inp1_csv="/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/locations.tsv"#args[0]
lat="latitude"#args[1]
lon="longitude"#args[2]
inp4_shp="/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/TL.shp"#args[3]
output="/home/mirandalv/Desktop/test0.tsv"#args[4]
geom=getgeometry_sg(inp4_shp)
ss_5arg(inp1_csv, lat, lon, geom, output)

"""
#-------------------------Call functions based on input arguments----------------------------------#
if len(args)==9:
	inp1_csv=args[0]
	lat=args[1]
	lon=args[2]
	location_type_code=args[3] #ADM1, ADM2, PPL
	type_code=int(args[4]) #1
	geoname_adm_code=args[5] #NL|AL|....
	inp4_shp=args[6]
	ADM_shp=args[7]
	output=args[8]
	geom=getgeometry_all(inp4_shp)
	ss_9arg(inp1_csv, lat, lon, location_type_code, type_code, geoname_adm_code, geom, output)
elif len(args)==5:
	inp1_csv=args[0]
	lat=args[1]
	lon=args[2]
	inp4_shp=args[3]
	output=args[4]
	geom=getgeometry_sg(inp4_shp)
	ss_5arg(inp1_csv, lat, lon, geom, output)
