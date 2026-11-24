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
from rasterstats import zonal_stats
import joblib
from osgeo import osr, gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95
gtiff_driver=gdal.GetDriverByName("GTiff")
import winsound
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)

#functions
def convert_tif_to_array(intifraster):
    inras = gdal.Open(intifraster)
    inband = inras.GetRasterBand(1)
    outarr = inband.ReadAsArray()
    return outarr
def convertarrtotif(arr, outfile, tifdatatype, referenceraster, nodatavalue):
    ds_in=gdal.Open(referenceraster)
    inband=ds_in.GetRasterBand(1)
    gtiff_driver=gdal.GetDriverByName("GTiff")
    ds_out = gtiff_driver.Create(outfile, inband.XSize, inband.YSize, 1, tifdatatype)
    ds_out.SetProjection(ds_in.GetProjection())
    ds_out.SetGeoTransform(ds_in.GetGeoTransform())
    outband=ds_out.GetRasterBand(1)
    outband.WriteArray(arr)
    outband.SetNoDataValue(nodatavalue)
    ds_out.FlushCache()
    del ds_in
    del ds_out
    del inband
    del outband

#input workspaces
myworkspace="D:/CCW24sensi"
codespace="C:/DATA/develops/sensitivewaldstandorteCH"
hoehenstufendict={"hyperinsubrisch":"hyp","collin mit Buche":"cob","collin":"co","submontan":"sm","untermontan":"um","obermontan":"om","unter-/obermontan":"um/om","hochmontan":"hm","subalpin":"sa","obersubalpin":"osa"}
hoehenstufendictabkuerzungen={"hyp":"hyperinsubroisch","co":"collin","cob":"collin mit Buche","sm":"submontan","um":"untermontan","om":"obermontan","um/om":"unter-/obermontan","hm":"hochmontan","sa":"subalpin","osa":"obersubalpin"}
hsmoddict={1:"hyperinsubrisch",2:"collin",3:"collin",4:"submontan",5:"untermontan",6:"obermontan",7:"unter-/obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={1:"hyp",2:"co",3:"cob",4:"sm",5:"um",6:"om",7:"um/om",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["hyperinsubrisch","collin","collin mit Buche","submontan","untermontan","obermontan","unter-/obermontan","hochmontan","subalpin","obersubalpin"]


#read excel files
naiseinheitenunique=pd.read_excel(codespace+"/GR/GR_nais_einheiten_unique_v2_bh_mf.xlsx", sheet_name='Sheet1', dtype="str", engine='openpyxl')
naiseinheitenunique.columns
naiseinheitenunique.dtypes
len(naiseinheitenunique)
naiseinheitenunique.loc[naiseinheitenunique['ASS_GR'].isnull()==True, 'ASS_GR']=''
naiseinheitenunique.loc[naiseinheitenunique['NAISbg'].isnull()==True, 'NAISbg']=''
naiseinheitenunique.loc[naiseinheitenunique['nais'].isnull()==True, 'nais']=''
naiseinheitenunique.loc[naiseinheitenunique['hs'].isnull()==True, 'hs']=''
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['ASS_GR']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['NAISbg']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['nais']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs'].isnull()==False]
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='nan']
naiseinheitenunique['nais1']=''
naiseinheitenunique['nais2']=''
for index, row in naiseinheitenunique.iterrows():
    nais=row['nais']
    if "(" in nais:
        naislist=nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
        naiseinheitenunique.loc[index,'nais1']=naislist[0]
        naiseinheitenunique.loc[index, 'nais2'] = naislist[1]
    elif "/" in nais:
        naislist=nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
        naiseinheitenunique.loc[index,'nais1']=naislist[0]
        naiseinheitenunique.loc[index, 'nais2'] = naislist[1]
    else:
        naiseinheitenunique.loc[index,'nais1']=nais

#create a list of unique Nais-EInheiten SHK2020
naislist_SHK2020=naiseinheitenunique['nais1'].unique().tolist()
len(naislist_SHK2020)
for item in naiseinheitenunique['nais2'].unique().tolist():
    if item not in naislist_SHK2020:
        naislist_SHK2020.append(item)
len(naislist_SHK2020)
naislist_SHK2020.sort()
if '' in naislist_SHK2020:
    naislist_SHK2020.remove('')
print(naislist_SHK2020)
len(naislist_SHK2020)


#read SHK2026
stok_gdf=gpd.read_file('D:/CCWGR24/export/WSHK_GR_20260713_attributed.gpkg', layer='WSHK_GR_20260713_attributed')
naislist_SHK2026=stok_gdf['nais1'].unique().tolist()
len(naislist_SHK2026)
for item in stok_gdf['naisue'].unique().tolist():
    if item not in naislist_SHK2026:
        naislist_SHK2026.append(item)
len(naislist_SHK2026)
naislist_SHK2026.sort()
if '' in naislist_SHK2026:
    naislist_SHK2026.remove('')
len(naislist_SHK2026)
print(naislist_SHK2026)

#Vergleich der Buendner Einheiten
assgrlist2020=naiseinheitenunique['ASS_GR'].unique().tolist()
len(assgrlist2020)
assgrlist2020.sort()
print(assgrlist2020)

assgrlist2026=stok_gdf['GR_Einheit'].unique().tolist()
len(assgrlist2026)
assgrlist2026.sort()
print(assgrlist2026)

difflist=[]
for item in assgrlist2026:
    if item not in assgrlist2020:
        difflist.append(item)
len(difflist)
difflist.sort()
print(difflist)

#NaiS Uebersetzungen der Differenz
stok_gdf.columns
difflistuebersetzungnais=[]
for item in difflist:
    difflistuebersetzungnais.append([item,stok_gdf.loc[stok_gdf['GR_Einheit']==item]['nais'].unique().tolist()[0]])
difflistuebersetzungnais.sort()
len(difflistuebersetzungnais)
