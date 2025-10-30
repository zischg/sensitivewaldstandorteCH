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
import matplotlib.pyplot as plt

#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi"
#projectspace="C:/DATA"
climatescenarios=['rcp45','rcp85']
#climatescenario="rcp85"
#climatescenario="rcp45"
#climatescenario="rcp26"

#import data from database
#Baumartenempfehlungen

for climatescenario in climatescenarios:
    sql = 'SELECT * FROM public."'+climatescenario+'_sensitivestandorte"'
    ba = gpd.read_postgis(sql, con=engine, geom_col='geom')
    len(ba)
    ba = ba[ba['inanalysis'] == 1]
    len(ba)
    ba.columns
    hs_list = ba['tahs'].unique().tolist()
    hs_list.sort()
    print(hs_list)
    tot_area = ba.geometry.area.sum()
    # Area statistics CH
    areastatistics_ch = ba.groupby(['tahs','hszukcor']).agg({'area_m2': 'sum'})
    areastatistics_ch['area_tot_pct'] = areastatistics_ch['area_m2'] / tot_area * 100
    # areastatistics_ch['area_tot_ant']=areastatistics_ch['area_m2']/tot_area
    areastatistics_ch.to_excel(projectspace + '/areastatistics_'+climatescenario+'_Hoehenstufenveränderungen_CH.xlsx')
    areastatistics_sensi = ba.groupby(['sensisto','tahs', 'hszukcor']).agg({'area_m2': 'sum'})
    areastatistics_sensi['area_tot_pct'] = areastatistics_sensi['area_m2'] / tot_area * 100
    # areastatistics_ch['area_tot_ant']=areastatistics_ch['area_m2']/tot_area
    areastatistics_sensi.to_excel(projectspace + '/areastatistics_' + climatescenario + '_Hoehenstufenveränderungen_CH_sensisto.xlsx')
    del ba

print('all done')






