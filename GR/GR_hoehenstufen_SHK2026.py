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
myworkspace="D:/CCWGR24"
codespace="C:/DATA/develops/sensitivewaldstandorteCH"
hoehenstufendict={"hyperinsubrisch":"hyp","collin mit Buche":"cob","collin":"co","submontan":"sm","untermontan":"um","obermontan":"om","unter-/obermontan":"um/om","hochmontan":"hm","subalpin":"sa","obersubalpin":"osa"}
hoehenstufendictabkuerzungen={"hyp":"hyperinsubroisch","co":"collin","cob":"collin mit Buche","sm":"submontan","um":"untermontan","om":"obermontan","um/om":"unter-/obermontan","hm":"hochmontan","sa":"subalpin","osa":"obersubalpin"}
hsmoddict={1:"hyperinsubrisch",2:"collin",3:"collin",4:"submontan",5:"untermontan",6:"obermontan",7:"unter-/obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={1:"hyp",2:"co",3:"cob",4:"sm",5:"um",6:"om",7:"um/om",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["hyperinsubrisch","collin","collin mit Buche","submontan","untermontan","obermontan","unter-/obermontan","hochmontan","subalpin","obersubalpin"]

#read SHK2026
stok_gdf=gpd.read_file(myworkspace+'/export/WSHK_GR_20260713_attributed.gpkg', layer='WSHK_GR_20260713_attributed')
#stok_gdf.rename(columns={'ass_gr':'ASS_GR', 'naisbg':'NAISbg'}, inplace=True)
#stok_gdf.rename(columns={'meanslopep':'meanslopeprc'}, inplace=True)


##read the rasters
#reference tif raster
print("read reference raster")
referenceraster='D:/CCWGR24/GIS/gr_dem10m.tif'
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
NODATA_value=-9999
sloperaster="D:/CCWGR24/GIS/gr_slopeprz.tif"
radiationraster="D:/CCWGR24/GIS/gr_globradyyw.tif"
hoehenstufenraster="D:/CCWGR24/GIS/gr_vegetationshoehenstufen.tif"

#read attribute data
taheute=gpd.read_file(myworkspace+"/sensi/Waldstandortregionen2026_fixed.gpkg", layer='Waldstandortregionen2026_fixed')
storeg=gpd.read_file(myworkspace+"/sensi/Waldstandortregionen2026_fixed.gpkg", layer='Waldstandortregionen2026_fixed')
stok_gdf.dtypes
len(stok_gdf)
stok_gdf.crs
stok_gdf.columns
stok_gdf['joinid']=stok_gdf.index

#Tannenareale
taheute.crs
taheute.columns
#taheute.plot()
taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
taheute.drop(columns=['id', 'Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code','Subcode', 'Code_Bu', 'Code_Fi', 'Flaeche', ], inplace=True)
#overlay spatial join
#stok_gdf=gpd.sjoin(stok_gdf,taheute, how='left', op="intersects")
stok_gdf=gpd.overlay(stok_gdf,taheute, how='intersection')

#Standortregionen
storeg.crs
storeg.columns
#taheute.plot()
storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
storeg.drop(columns=[ 'id', 'Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code','Code_Bu', 'Code_Fi', 'Flaeche'], inplace=True)
stok_gdf=gpd.overlay(stok_gdf,storeg, how='intersection')
winsound.Beep(frequency, duration)

#attribute shapefile
#mean slope in percent
stok_gdf['joinid']=stok_gdf.index
stok_gdf["meanslopeprc"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstatslope=zonal_stats(stok_gdf, sloperaster,stats="mean")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"meanslopeprc"]=zonstatslope[i]["mean"]
    i+=1
stok_gdf["slpprzrec"]=0
stok_gdf.loc[stok_gdf["meanslopeprc"]>=70.0,"slpprzrec"]=4
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=60.0)&(stok_gdf["meanslopeprc"]<70.0)),"slpprzrec"]=3
stok_gdf.loc[((stok_gdf["meanslopeprc"]>=20.0)&(stok_gdf["meanslopeprc"]<60.0)),"slpprzrec"]=2
stok_gdf.loc[stok_gdf["meanslopeprc"]<20.0,"slpprzrec"]=1
stok_gdf.columns
#del zonstatslope
winsound.Beep(frequency, duration)

#radiation
stok_gdf["rad"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstatrad=zonal_stats(stok_gdf, radiationraster,stats="mean")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"rad"]=zonstatrad[i]["mean"]
    i+=1
przquant90=stok_gdf['rad'].quantile(q=0.9, interpolation='linear')
przquant10=stok_gdf['rad'].quantile(q=0.1, interpolation='linear')

stok_gdf["radiation"]=0
#stok_gdf.loc[stok_gdf["rad"]>=147.0,"radiation"]=1 #90% quantile
#stok_gdf.loc[stok_gdf["rad"]<=112.0,"radiation"]=-1 #10% quantile
stok_gdf.loc[stok_gdf["rad"]>=przquant90,"radiation"]=1 #90% quantile
stok_gdf.loc[stok_gdf["rad"]<=przquant10,"radiation"]=-1 #10% quantile
stok_gdf.columns
#del zonstatrad
winsound.Beep(frequency, duration)

#hoehenstufen heute
stok_gdf["tahs"]=0
stok_gdf["tahsue"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstaths=zonal_stats(stok_gdf, hoehenstufenraster,stats="majority")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"tahs"]=zonstaths[i]["majority"]
    i+=1
stok_gdf.columns
stok_gdf.dtypes

print(stok_gdf['tahs'].unique().tolist())
stok_gdf.loc[((stok_gdf["tahs"] == 1)) , "tahs"] = 'hyperinsubrisch'
stok_gdf.loc[((stok_gdf["tahs"] == 2)) , "tahs"] = 'collin'
stok_gdf.loc[((stok_gdf["tahs"] == 3)) , "tahs"] = 'collin mit Buche'
stok_gdf.loc[((stok_gdf["tahs"] == 4)) , "tahs"] = 'submontan'
stok_gdf.loc[((stok_gdf["tahs"] == 5)) , "tahs"] = 'untermontan'
stok_gdf.loc[((stok_gdf["tahs"] == 6)) , "tahs"] = 'obermontan'
stok_gdf.loc[((stok_gdf["tahs"] == 7)) , "tahs"] = 'unter-/obermontan'
stok_gdf.loc[((stok_gdf["tahs"] == 1)&(stok_gdf["taheute"] == 1)) , "tahs"] = 'hochmontan im Tannen-Hauptareal'
stok_gdf.loc[((stok_gdf["tahs"] == 1)&(stok_gdf["taheute"] == 2)) , "tahs"] = 'hochmontan im Tannen-Nebenareal'
stok_gdf.loc[((stok_gdf["tahs"] == 1)&(stok_gdf["taheute"] == 3)) , "tahs"] = 'hochmontan im Tannen-Reliktareal'
stok_gdf.loc[((stok_gdf["tahs"] == 9)) , "tahs"] = 'subalpin'
stok_gdf.loc[((stok_gdf["tahs"] == 10)) , "tahs"] = 'obersubalpin'


#add ue and mo
stok_gdf['ue']=0
stok_gdf['mo']=0
stok_gdf['tahsue']=''
for index, row in stok_gdf.iterrows():
    nais=row['nais']
    if "(" in nais:
        stok_gdf.loc[index, 'ue'] = 1
    elif "/" in nais:
        stok_gdf.loc[index, 'mo'] = 1
#stok_gdf["tahsue"]=stok_gdf["tahs"]
stok_gdf.loc[((stok_gdf["ue"] == 1)&(stok_gdf["tahsue"] == '')) , "tahsue"] = stok_gdf["tahs"]
stok_gdf.loc[((stok_gdf["mo"] == 1)&(stok_gdf["tahsue"] == '')) , "tahsue"] = stok_gdf["tahs"]
winsound.Beep(frequency, duration)

#write data
print("write output")
stok_gdf.columns
stok_gdf=stok_gdf[['joinid','GR_Einheit', 'nais', 'taheute','storeg', 'meanslopeprc', 'slpprzrec', 'rad', 'radiation','nais1', 'nais2', 'ue',  'mo', 'tahs', 'tahsue', 'geometry']]
stok_gdf.to_file(myworkspace+"/sensi/stok_gdf_attributed.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/GR/stok_gdf_attributed.gpkg")
print("done")

#Export for tree-app
print('Export for Tree-App')
stok_gdf.columns
#stok_gdf.loc[((stok_gdf['ue']==1)&(NAISbg['tahsue']=='')&(stok_gdf['tahs']!='')),'tahsue']=stok_gdf['tahs']
treeapp=stok_gdf[['GR_Einheit', 'nais', 'nais1', 'nais2', 'mo', 'ue','tahs', 'tahsue','geometry']]
treeapp.to_file(myworkspace+"/sensi/GR_treeapp.gpkg", layer='GR_treeapp', driver="GPKG")
treeapp.columns
print("done")
winsound.Beep(frequency, duration)
winsound.Beep(frequency, duration)





