import numpy as np
import pandas as pd
import joblib
import fiona
import geopandas as gpd
import os
import shapely
from osgeo import ogr
import xlrd
import openpyxl
import psycopg2
import warnings
from osgeo import osr, gdal
from sqlalchemy import create_engine
mypassword=input("Enter database password: ").replace("'","")
db_connection_url = "postgresql://azischg:"+mypassword+"@mobidb02.giub.unibe.ch:5432/ccwdb";
engine = create_engine(db_connection_url)
#con=engine.connect()
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95
gtiff_driver=gdal.GetDriverByName("GTiff")
import winsound
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi"
#projectspace="C:/DATA"
climatescenarios=['rcp45','rcp85']
#climatescenario="rcp85"
#climatescenario="rcp45"
#climatescenario="rcp26"

#import data from database







combi_unique=combi_unique[combi_unique['tahs_1'].isin(['obersubalpin','subalpin','hochmontan','obermontan','untermontan','submontan','collin'])]
combi_unique=combi_unique.sort_values(by=['nais_1'])
combi_unique.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique.xlsx")

areastatistics=combi.groupby(['nais_1', 'tahs_1', 'tahsue_1', 'nais1_rcp45', 'nais2_rcp45','hs_rcp45', 'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85']).agg({'area': 'sum'})
areastatistics.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_area.xlsx")

#Einzeln
rcp45.columns
rcp45['area']=rcp45.geometry.area
rcp45=rcp45[rcp45['area']>=100]
rcp45unique=rcp45[['nais', 'nais1', 'nais2','tahs', 'tahsue', 'nais1_rcp45', 'nais2_rcp45', 'hs_rcp45', 'mo', 'ue','taheute', 'storeg',]]
rcp45unique=rcp45unique.drop_duplicates()
rcp45unique.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_RCP45.xlsx")
areastatistics_rcp45=rcp45.groupby(['nais', 'nais1', 'nais2','tahs', 'tahsue', 'nais1_rcp45', 'nais2_rcp45', 'hs_rcp45', 'mo', 'ue','taheute', 'storeg']).agg({'area': 'sum'})
areastatistics_rcp45.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_area_RCP45.xlsx")

rcp85.columns
rcp85['area']=rcp85.geometry.area
rcp85=rcp85[rcp85['area']>=100]
rcp85unique=rcp85[['nais', 'nais1', 'nais2','tahs', 'tahsue', 'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85', 'mo', 'ue','taheute', 'storeg',]]
rcp85unique=rcp85unique.drop_duplicates()
rcp85unique.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_RCP85.xlsx")
areastatistics_rcp85=rcp85.groupby(['nais', 'nais1', 'nais2','tahs', 'tahsue', 'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85', 'mo', 'ue','taheute', 'storeg']).agg({'area': 'sum'})
areastatistics_rcp85.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_area_RCP85.xlsx")
print('all done')



for climatescenario in climatescenarios:
    print(climatescenario)

