# Date: 10/2/2014
# Author: Miranda Lv
# QA-tools: Spatial Scrum

"""
Inputs: 
	argument: csv file, lat, lon > output file name
	1. csv/tsv
			/home/mirandalv/Documents/QA-tool/qa_python/qa_project.csv
			latitude in csv (3) y
			longtude in csv (4) x
	2. shapefile of administration boundary
			/home/mirandalv/Documents/QA-tool/qa_python/ad_boundary/NPL_adm0.shp
Outputs:
	geojson file includes points that are outside administration boundary
Test files:
	inp1_csv="/home/mirandalv/Documents/QA-tool/qa_python/qa_project.csv"
	inp4_shp="/home/mirandalv/Documents/QA-tool/qa_python/ad_boundary/NPL_adm0.shp"
	outgeojson="/home/mirandalv/Documents/QA-tool/qa_python/qa_project2.geojson"

In1: /home/mirandalv/Documents/QA-tool/qa_python/scrub-input/tsv-test.tsv
In2: 5
In3: 6
In4: /home/mirandalv/Documents/QA-tool/qa_python/scrub-input/country-codes-id-fixed.shp
In5: /home/mirandalv/Documents/QA-tool/qa_python/scrub-input/test.geojson
"""


import os, csv, sys, getopt
from shapely.geometry import Point
from shapely.wkb import loads
from osgeo import ogr
import shapefile
import locale, timeit, warnings


opts, args= getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="]) #Need to polish the inputs later
inp1_csv=args[0]
lat=args[1]
lon=args[2]
incountry_code=args[3]
inp4_shp=args[4]


"""
inp1_csv="/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/locations.tsv"#"/home/mirandalv/Documents/QA-tool/qa_python/qa_project.csv" #/home/mirandalv/Documents/QA-tool/qa_python/scrub-input/tsv-test.tsv"
lat=4
lon=5
inp4_shp= "/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/TL.shp"#"/home/mirandalv/Documents/QA-tool/qa_python/ad_boundary/NPL_adm0.shp"
outgeojson="/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/TLtest.geojson"
"""

#get geometry of input polygon

def getgeometry(shp):
	openShape=ogr.Open(str(shp))
	basename=os.path.basename(shp)
	shpname=os.path.splitext(basename)[0]
	layers=openShape.GetLayerByName(shpname)
	for element in layers:
		geom=loads(element.GetGeometryRef().ExportToWkb())
		return geom

geom=getgeometry(inp4_shp)


# Read in raw data from csv
rawData = csv.DictReader(open(inp1_csv, 'rb'), delimiter='\t') #csv.reader(open(inp1_csv, 'rb'), delimiter='\t')


# the template. where data from the csv will be formatted to geojson
template = \
    ''' \
	{ 
		"type" : "Feature",
        "properties" : {
			"project_id": "%s",
			"geoname_id": "%s",
			"linenumber" : "%s"
			},
        "geometry" : {
             "type" : "Point",
             "coordinates" : [%f,%f]
             }
	},
    '''

# the head of the geojson file
output = \
    ''' \
{ 
	"type" : "FeatureCollection",
	"features" : [
    '''

outcsv="/home/mirandalv/Documents/QA-tool/qa_python/Timor-Leste/TL.csv"
with open(outcsv, "wb") as outcsv:
	newriter=csv.writer(outcsv, delimiter=",")
# loop through the csv by row skipping the first header
	iter = 0
	for row in rawData:
		iter += 1
		if iter >= 1: #ProjectID
			"""if row["geoname_adm_code"].rsplit("|")[0]!=incountry_code:
				warningstring1='WARN: ' + row["project_id"] + " " + row["geoname_id"] + " is not " + incountry_code +" project"
				warnings.warn(warningstring1)"""
			if row[lon]=="" or row[lat]=="":
				warningstring2='WARN: ' + row["project_id"] + " " + row["geoname_id"] + " does not have latitude/longitude"
				warnings.warn(warningstring2)
			elif row[lon]!="" and row[lat]!="":
				if row["geoname_adm_code"].rsplit("|")[0]!=incountry_code:
					pointX = locale.atof(row[lon]) #make sure coordinates are not string
					pointY = locale.atof(row[lat])
					thePoint=Point(pointX, pointY)
					if not thePoint.within(geom)==True:
						output += template % (row["project_id"], row["geoname_id"], iter+1, pointX, pointY)
						newriter.writerow([row["project_id"], row["geoname_id"], iter+1, pointX, pointY])

output=output[:-6]
     
# the tail of the geojson file
output += \
    ''' \
    ]
}
    '''
print output


