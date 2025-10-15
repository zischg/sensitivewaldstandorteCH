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
varname='var1'
#varname='var2'

#thresholds for claissifying climate-sensitive stocks (klimasensitive Bestaende)
threshold_nicht_empfohlen_min=0
threshold_nicht_empfohlen_max=95
threshold_nicht_bedingt_min=0
threshold_nicht_bedingt_max=20
threshold_nicht_gef_min=0
threshold_nicht_gef_max=10
threshold_schwach_empfohlen_min=95
threshold_schwach_empfohlen_max=100
threshold_schwach_bedingt_min=20
threshold_schwach_bedingt_max=70
threshold_schwach_gef_min=10
threshold_schwach_gef_max=20
threshold_mittel_bedingt_min=70
threshold_mittel_bedingt_max=95
threshold_mittel_gef_min=20
threshold_mittel_gef_max=40
threshold_stark_bedingt_min=95
threshold_stark_bedingt_max=100
threshold_stark_gef_min=40

##var2
#varname='var2'
#threshold_schwach_gef_max=30
#threshold_mittel_gef_min=30
#threshold_mittel_gef_max=50
#threshold_stark_gef_min=50

#Arven, Laerchen und Foehren
arvenundlaerchen=['59','59A','59C','59E','59J','59L','59S','59V','59H','59R','72,' '59*','59G','59AG','59EG','59VG','72G','57CLä','57VLä','58Lä', '59Lä', '59ELä', '59LLä', '59VLä','59LLä']
foehren=['61','62','65','66','67','68','69','70','71','65*','66PM','67*','67G','68*','69G','70G','71G','72G']

#******************************************************************************************************
#Sensitive Bestaende
#******************************************************************************************************
treetypes=["FI"]#, "TA", "LA", "WFO", "BU","TEI", "BAH", "ES"]
treetypesplusgeometry=treetypes.copy()
treetypesplusgeometry.append('geometry')
#sb= sensitiver Bestand
treetypes_sb=[]
for item in treetypes:
    treetypes_sb.append("sb"+item)

#bk_gdf.crs
#len(bk_gdf)
#bk_gdf.columns
#bk_gdf["bkid"]=bk_gdf.index
##bk_gdf.to_file(projectspace+"/FR/"+"FR_bk_ausNadelholzanteil.gpkg")
##bk_gdf=bk_gdf[['bkid','mischung', 'entwicklun','schlussgra','nhd_anteil', 'hdom', 'hmax', 'gru_strukt','dg_os','dg_ms', 'dg_us','geometry']]#,"TACODE","BUCODE"
#bk_gdf.dtypes

##Intersect with Fichtenanteil
##bk_gdf_fi=bk_gdf.overlay(fi, how='intersection', make_valid=True, keep_geom_type=True)
#bk_gdf_fi=gpd.read_file(projectspace+"/FR/"+"FR_bk_Fichtenanteil.gpkg", layer='FR_bk_Fichtenanteil')
##Fichtenanteil
#bk_gdf_fi["FI"]=bk_gdf_fi['FIanteil']#bk_gdf_fi['NH']/100.0*bk_gdf_fi['FIanteil']/100.0*100.0
#bk_gdf_fi.columns

len(bk_gdf_fi)
for climatescenario in climatescenarios:
    print(climatescenario)
    #rcp_baumartenempfehlungen_gdf_in=joblib.load(projectspace+"/FR/FR_"+climatescenario+"_baumartenempfehlungen.sav")
    #len(rcp_baumartenempfehlungen_gdf_in)
    #rcp_baumartenempfehlungen_gdf_in.columns
    #rcp_baumartenempfehlungen_gdf_in=rcp_baumartenempfehlungen_gdf_in[treetypesplusgeometry]#"TA_1", #,"BU","TA",,"WFO","BAH"
    #rcp_baumartenempfehlungen_gdf_in.columns
    ##intersect Baumartenempfehlungen layer with Bestandeskarte layer
    print('intersect')
    #rcp_bk_gdf_in=gpd.overlay(rcp_baumartenempfehlungen_gdf_in, bk_gdf_fi, how='intersection', make_valid=True, keep_geom_type=True)
    rcp_bk_gdf_in=gpd.read_file(projectspace+"/"+climatescenario+"_tbk_bestandeskarte_baumartenanteil_baumartenempfehlungen.gpkg", layer=climatescenario+'_tbk_bestandeskarte_baumartenanteil_baumartenempfehlungen')

    #sql='SELECT * FROM "'+climatescenario+'_TBk_Bestandeskarte_Baumartenanteil_Baumartenempfehlungen"'
    #rcp_bk_gdf_in=gpd.read_postgis(sql, con=engine, geom_col='geom')
    #rcp_bk_gdf_in["area_m2"] = rcp_bk_gdf_in['geometry'].area
    mainlayercolumnslist=rcp_bk_gdf_in.columns.tolist()
    if 'index' in mainlayercolumnslist:
        rcp_bk_gdf_in.drop('index', axis=1, inplace=True)
    #rcp_bk_gdf_in.to_file(projectspace+"/FR/"+"FR_"+climatescenario+"_baumartenempfehlungen_intsct_bk.gpkg")
    mainlayercolumnslist=rcp_bk_gdf_in.columns.tolist()
    len(rcp_bk_gdf_in)
    #add columns to main layer
    #senstitive Bestaende pro Baumart:
    #-999 keine Angabe, 0 nicht klimasensitiv, 1 schwach klimasensitiv, 2 mittel klimasensitiv, 3 stark klimasensitiv, 4 bedingt klimasensitiv
    #Baumartenempfehlung:
    #-999 keine Angabe, 1 empfohlen, 2 bedingt empfohlen, 3 gefaehrdet, 4 in Zukunft empfohlen, 5 in Zukunft bedingt empfohlen

    #calculate Fichtenanteil
    rcp_bk_gdf_in['FIantTBk']=rcp_bk_gdf_in['FIantNHant']*rcp_bk_gdf_in['NH']
    # Bei Arven und Laerchen wird der Fichtenanteil auf Null gesetzt
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in['nais1'].isin(arvenundlaerchen), 'FIantTBk'] = 0
    # Bei Foehren und Laerchen wird der Fichtenanteil auf Null gesetzt
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in['nais1'].isin(foehren), 'FIantTBk'] = 0
    print("sensitive bestaende FI")
    rcp_bk_gdf_in["sbFI"] = -999
    #nicht klimasensitiv - empfohlen
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] >= threshold_nicht_empfohlen_min) & (rcp_bk_gdf_in['FIantTBk'] <= threshold_nicht_empfohlen_max) & (rcp_bk_gdf_in['FI'].isin([1, 4])))].index, "sbFI"] = 0
    #nicht klimasensitiv - bedingt empfohlen
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] >= threshold_nicht_bedingt_min) & (rcp_bk_gdf_in['FIantTBk'] <= threshold_nicht_bedingt_max) & (rcp_bk_gdf_in['FI'].isin([2, 5])))].index, "sbFI"] = 0
    #nicht klimasensitiv - gefaehrdet
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] >= threshold_nicht_gef_min) & (rcp_bk_gdf_in['FIantTBk'] <= threshold_nicht_gef_max) & (rcp_bk_gdf_in['FI'].isin([3])))].index, "sbFI"] = 0
    #schwach klimasensitiv - empfohlen
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] >threshold_schwach_empfohlen_min)&(rcp_bk_gdf_in['FI'].isin([1,4])))].index, "sbFI"]=1
    #schwach klimasensitiv - bedingt empfohlen
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] > threshold_schwach_bedingt_min) & (rcp_bk_gdf_in['FIantTBk'] <= threshold_schwach_bedingt_max) & (rcp_bk_gdf_in['FI'].isin([2, 5])))].index, "sbFI"] = 1
    #schwach klimasensitiv - gefaehrdet
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] > threshold_schwach_gef_min) & (rcp_bk_gdf_in['FIantTBk'] <= threshold_schwach_gef_max) & (rcp_bk_gdf_in['FI'].isin([3])))].index, "sbFI"] = 1
    #mittel klimasensitiv - bedingt empfohlen
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] > threshold_mittel_bedingt_min) & (rcp_bk_gdf_in['FIantTBk'] <= threshold_mittel_bedingt_max) & (rcp_bk_gdf_in['FI'].isin([2, 5])))].index, "sbFI"] = 2
    #mittel klimasensitiv - gefaehrdet
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] > threshold_mittel_gef_min) & (rcp_bk_gdf_in['FIantTBk'] <= threshold_mittel_gef_max) & (rcp_bk_gdf_in['FI'].isin([3])))].index, "sbFI"] = 2
    #stark klimasensitiv - bedingt empfohlen
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] > threshold_stark_bedingt_min) & (rcp_bk_gdf_in['FI'].isin([2, 5])))].index, "sbFI"] = 3
    # stark klimasensitiv - gefaehrdet
    rcp_bk_gdf_in.loc[rcp_bk_gdf_in[((rcp_bk_gdf_in['FIantTBk'] > threshold_stark_gef_min) & (rcp_bk_gdf_in['FI'].isin([3])))].index, "sbFI"] = 3

    #calculate maximum sensitivity over all treetypes
    rcp_bk_gdf_in["maxsens"]=rcp_bk_gdf_in["sbFI"]

    #write the output
    print('write output '+climatescenario)
    rcp_bk_gdf_in.to_file(projectspace+"/"+climatescenario+"_sensitivebestaende_FI_TBk_"+varname+".gpkg")

print('all done')

print('analysis ...')
#Auswertungen
sensi45var1=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp45"+"_sensitivebestaende_FI_"+"var1"+".gpkg")
sensi45var1=sensi45var1[sensi45var1["maxsens"]>=0]
sensi45var2=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp45"+"_sensitivebestaende_FI_"+"var2"+".gpkg")
sensi45var2=sensi45var2[sensi45var2["maxsens"]>=0]
sensi85var1=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp85"+"_sensitivebestaende_FI_"+"var1"+".gpkg")
sensi85var1=sensi85var1[sensi85var1["maxsens"]>=0]
sensi85var2=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp85"+"_sensitivebestaende_FI_"+"var2"+".gpkg")
sensi85var2=sensi85var2[sensi85var2["maxsens"]>=0]

outfile = open(projectspace + "/FR/" + "FR_"+"sensitiveBestaende_FI_stat.txt", "w")
outfile.write("var;totarea;prz_nichtsensitiv;prz_schwachsensitiv;prz_mittelsensitiv;prz_starksensitiv;prz_bedingtsensitiv\n")
shapes=[sensi45var1,sensi45var2,sensi85var1,sensi85var2]
varnames=['sensi45var1','sensi45var2','sensi85var1','sensi85var2']
i=0
for shape in shapes:
    areatot=np.sum(shape.area)
    area0=round(np.sum(shape[shape["maxsens"]==0].area)/areatot*100.0,2)
    area1 = round(np.sum(shape[shape["maxsens"] == 1].area) / areatot * 100.0, 2)
    area2 = round(np.sum(shape[shape["maxsens"] == 2].area) / areatot * 100.0, 2)
    area3 = round(np.sum(shape[shape["maxsens"] == 3].area) / areatot * 100.0, 2)
    area4 = round(np.sum(shape[shape["maxsens"] == 4].area) / areatot * 100.0, 2)
    outfile.write(varnames[i] + ";" + str(areatot) + ";" + str(area0) + ";" + str(area1)+ ";" + str(area2)+ ";" + str(area3)+ ";" + str(area4) + "\n")
    i+=1
outfile.close()
print('analysis done')



print('analysis original BK nur FI ...')
#Auswertungen
sensi45var1=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp45"+"_sensitivebestaende_"+"var1"+".gpkg")
sensi45var1=sensi45var1[sensi45var1["maxsens"]>=0]
sensi45var2=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp45"+"_sensitivebestaende_"+"var2"+".gpkg")
sensi45var2=sensi45var2[sensi45var2["maxsens"]>=0]
sensi85var1=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp85"+"_sensitivebestaende_"+"var1"+".gpkg")
sensi85var1=sensi85var1[sensi85var1["maxsens"]>=0]
sensi85var2=gpd.read_file(projectspace+"/FR/"+"FR_"+"rcp85"+"_sensitivebestaende_"+"var2"+".gpkg")
sensi85var2=sensi85var2[sensi85var2["maxsens"]>=0]

outfile = open(projectspace + "/FR/" + "FR_"+"sensitiveBestaende_FIausBK_stat.txt", "w")
outfile.write("var;totarea;prz_nichtsensitiv;prz_schwachsensitiv;prz_mittelsensitiv;prz_starksensitiv;prz_bedingtsensitiv\n")
shapes=[sensi45var1,sensi45var2,sensi85var1,sensi85var2]
varnames=['sensi45var1','sensi45var2','sensi85var1','sensi85var2']
i=0
for shape in shapes:
    areatot=np.sum(shape.area)
    area0=round(np.sum(shape[shape["sbFI"]==0].area)/areatot*100.0,2)
    area1 = round(np.sum(shape[shape["sbFI"] == 1].area) / areatot * 100.0, 2)
    area2 = round(np.sum(shape[shape["sbFI"] == 2].area) / areatot * 100.0, 2)
    area3 = round(np.sum(shape[shape["sbFI"] == 3].area) / areatot * 100.0, 2)
    area4 = round(np.sum(shape[shape["sbFI"] == 4].area) / areatot * 100.0, 2)
    outfile.write(varnames[i] + ";" + str(areatot) + ";" + str(area0) + ";" + str(area1)+ ";" + str(area2)+ ";" + str(area3)+ ";" + str(area4) + "\n")
    i+=1
outfile.close()
print('analysis done')

shape.columns