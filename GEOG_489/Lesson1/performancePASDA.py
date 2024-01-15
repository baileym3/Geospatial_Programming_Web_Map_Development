# Setup _very_ simple timing.
import time
process_start_time = time.time()

import arcpy
from arcpy.sa import *

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'C:\PSU\GEOG489\Lesson1\Lesson1Data\PASDA\unzipped'

## If our rasters aren't in our filter list then drop them from our list.
def filter_list(fileList,filterList):
    return[i for i in fileList if any(j in i for j in filterList)]

# Ordinarily we would want all of the rasters I'm filtering by a small set for testing & efficiency
# I did this by manually looking up the tile index for the LiDAR and determining an area of interest
# tiles ending in 227, 228, 230, 231, 232, 233, 235, 236

wildCardList = set(['227','228','230','231','232','233','235','236'])
# Get a list of rasters in my folder
rasters = arcpy.ListRasters("*")
new_rasters = filter_list(rasters,wildCardList)

# for all of our rasters
for raster in new_rasters:
    raster_start_time = time.time()
    # Now that we have our list of rasters
    ## Note also for performance we're not saving any of the intermediate rasters - they will exist only in memory
    ## Fill the DEM to remove any sinks
    try:
        FilledRaster = Fill(raster)
        ## Calculate the Flow Direction (how water runs across the surface)
        FlowDirRaster = FlowDirection(FilledRaster)
        ## Calculate the Flow Accumulation (where the water accumulates in the surface)
        FlowAccRaster = FlowAccumulation(FlowDirRaster)
        ## Convert the Flow Accumulation to a Stream Network
        ## We're setting an arbitray threshold of 100 cells flowing into another cell to set it as part of our stream
        ## http://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/identifying-stream-networks.htm
        Streams = Con(FlowAccRaster,1,"","Value > 100")
        ## Convert the Raster Stream network to a feature class
        output_Polyline = raster.replace(".img",".shp")
        arcpy.CheckOutExtension("Spatial")
        arcpy.sa.StreamToFeature(Streams,FlowDirRaster,output_Polyline)
        arcpy.CheckInExtension("Spatial")
    except:
        print ("Errors occured")
        print (arcpy.GetMessages())
        arcpy.AddMessage ("Errors occurred")
        arcpy.AddMessage(arcpy.GetMessages())

# Output how long the whole process took.
arcpy.AddMessage("--- %s seconds ---" % (time.time() - process_start_time))
print ("--- %s seconds ---" % (time.time() - process_start_time))