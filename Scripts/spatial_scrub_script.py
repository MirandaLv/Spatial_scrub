#Date: 10/9/2014
#Author: MirandaLv
#Note: Using fiona to do spatial scrub


"""

***The input tsv file must have a filed called "country_code" that has TWO Character ABBREVIATION***
***The input shape file mast have a filed called "ISO_A2" that has TWO Character ABBREVIATION***
Inputs: 
	argument: tsv file, lat, lon, shapefile > output file name
Outputs:
	geojson file includes points that are outside administration boundary

In1: /home/mirandalv/Documents/QA-tool/qa_python/scrub-input/tsv-test.tsv
In2: latitude's head name in csv
In3: longitude's head name in csv
In4: /home/mirandalv/Documents/QA-tool/qa_python/scrub-input/country-codes-id-fixed.shp
"""


import csv, sys, getopt, os
from shapely.geometry import Point, shape
import timeit, locale
import fiona, warnings


opts, args= getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="]) #Need to polish the inputs later
inp1_csv=args[0]
lat=args[1]
lon=args[2]
inp4_shp=args[3]

#get all layers' geometry of input polygon, output as a dictionary
def getgeomerty(shp):
	with fiona.open(shp, 'r') as infile:
		dic={}
		for i in range(0,len(infile)-1):
			geometry=infile[i]["geometry"]
			country=infile[i]["properties"]["ISO_A2"] #"SOV_A3" could be an input argument
			dic[country]=geometry
		return dic


geom=getgeomerty(inp4_shp)


# Read in raw data from csv
rawData = csv.DictReader(open(inp1_csv, 'rb'), delimiter='\t')

	
# the template. where data from the csv will be formatted to geojson
template = \
    ''' \
	{ 
		"type" : "Feature",
        "properties" : {
			"project_id": %s, 
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



# loop through the csv by row skipping the first header
iter = 0

for row in rawData:
    iter += 1
    if iter >= 1:
		adm_name=row["country_code"]
		if row[lon]=="" or row[lat]=="":
			warningstring='WARN: ' + row["project_id"] + " does not have latitude/longitude"
			warnings.warn(warningstring)
		if row[lon]!="" and row[lat]!="": 
			#print row["project_id"], iter+1
			pointX = locale.atof(row[lon]) #make sure coordinates are not string
			pointY = locale.atof(row[lat])
			thePoint=Point(pointX, pointY)
			#name = row["title"]
			if not shape(geom[adm_name]).contains(thePoint)==True:
				output += template % (row["project_id"], iter+1, pointX, pointY)


output=output[:-6]

    
# the tail of the geojson file
output+=\
    ''' \
	]
}
    '''

print output


