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

# *************************************************************
#environment settings
myworkspace="D:/CCW24sensi"
codespace="C:/DATA/develops/sensitivewaldstandorteCH"
hoehenstufendict={"collin":"co","submontan":"sm","untermontan":"um","obermontan":"om","hochmontan":"hm","subalpin":"sa","obersubalpin":"osa"}
hoehenstufenlist=["collin","submontan","untermontan","obermontan","hochmontan","subalpin","obersubalpin"]
hoehenstufenlistshort=["co","sm","um","om","hm","sa","osa"]


#read geodata GR
gr_gdf=gpd.read_file(myworkspace+"/GR/gr_bestguessLV95transform.gpkg", layer='gr_bestguessLV95transform')
len(gr_gdf)
gr_gdf['joinid']=gr_gdf.index
gr_gdf.columns
parameterdf=pd.read_excel(codespace+"/"+"GR_nais_einheiten_unique.xlsx", dtype="str", engine='openpyxl', sheet_name='VarianteGISforexport')
taheute=gpd.read_file(myworkspace+"/Tannenareale.shp")
storeg=gpd.read_file(myworkspace+"/Waldstandortsregionen.shp")
origlen=len(gr_gdf)


#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=myworkspace+"/GR/gr_dem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=myworkspace+"/GR/gr_slopeprz.tif"
radiationraster=myworkspace+"/GR/gr_globradyyw.tif"
hoehenstufenraster=myworkspace+("/GR/gr_vegetationshoehenstufen.tif")
region=myworkspace+("/GR/gr_region.tif")
subregion=myworkspace+("/GR/gr_subregion.tif")

#Tannenareale
taheute.crs
taheute.columns
taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
taheute.drop(columns=['Areal_de', 'Areal_fr', 'Areal_it', 'Areal_en','Shape_Leng','Shape_Area'], inplace=True)
#overlay spatial join
gr_gdf=gpd.sjoin(gr_gdf,taheute, how='left', op="intersects")
len(gr_gdf)==origlen
gr_gdf.columns
#gr_gdf=gr_gdf[['DTWGEINHEI','taheute','geometry']]
winsound.Beep(frequency, duration)

#Standortregionen
storeg.crs
storeg.columns
storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
storeg.drop(columns=[ 'Region_fr', 'Region_it', 'Region_en', 'Code', 'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area'], inplace=True)
#overlay spatial join
gr_gdf.columns
gr_gdf.drop(columns=[ 'index_right'], inplace=True)
gr_gdfstoreg=gr_gdf.sjoin(storeg, how='left', op="intersects")
len(gr_gdfstoreg)
gr_gdfstoreggrouped=gr_gdfstoreg[["joinid","storeg"]].groupby(by=["joinid"]).min()
len(gr_gdfstoreggrouped)
gr_gdfstoreggrouped.columns
gr_gdf=gr_gdf.merge(gr_gdfstoreggrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
len(gr_gdf)==origlen
winsound.Beep(frequency, duration)


#attribute shapefile
#mean slope in percent
gr_gdf["meanslopeprc"]=0
#zonstatslope=zonal_stats(gr_gdf, referenceraster,stats="count min mean max median")
zonstatslope=zonal_stats(gr_gdf, sloperaster,stats="mean")
i=0
while i < len(gr_gdf):
    gr_gdf.loc[i,"meanslopeprc"]=zonstatslope[i]["mean"]
    i+=1
gr_gdf["slpprzrec"]=0
gr_gdf.loc[gr_gdf["meanslopeprc"]>=70.0,"slpprzrec"]=4
gr_gdf.loc[((gr_gdf["meanslopeprc"]>=60.0)&(gr_gdf["meanslopeprc"]<70.0)),"slpprzrec"]=3
gr_gdf.loc[((gr_gdf["meanslopeprc"]>=20.0)&(gr_gdf["meanslopeprc"]<60.0)),"slpprzrec"]=2
gr_gdf.loc[gr_gdf["meanslopeprc"]<20.0,"slpprzrec"]=1
gr_gdf.columns
#del zonstatslope
winsound.Beep(frequency, duration)

#radiation
gr_gdf["rad"]=0
#zonstatslope=zonal_stats(gr_gdf, referenceraster,stats="count min mean max median")
zonstatrad=zonal_stats(gr_gdf, radiationraster,stats="mean")
i=0
while i < len(gr_gdf):
    gr_gdf.loc[i,"rad"]=zonstatrad[i]["mean"]
    i+=1
przquant90=gr_gdf['rad'].quantile(q=0.9, interpolation='linear')
przquant10=gr_gdf['rad'].quantile(q=0.1, interpolation='linear')

gr_gdf["radiation"]=0
#gr_gdf.loc[gr_gdf["rad"]>=147.0,"radiation"]=1 #90% quantile
#gr_gdf.loc[gr_gdf["rad"]<=112.0,"radiation"]=-1 #10% quantile
gr_gdf.loc[gr_gdf["rad"]>=przquant90,"radiation"]=1 #90% quantile
gr_gdf.loc[gr_gdf["rad"]<=przquant10,"radiation"]=-1 #10% quantile
gr_gdf.columns
#del zonstatrad
winsound.Beep(frequency, duration)

#hoehenstufen heute
gr_gdf["hs1975"]=0
#zonstatslope=zonal_stats(gr_gdf, referenceraster,stats="count min mean max median")
zonstaths=zonal_stats(gr_gdf, hoehenstufenraster,stats="majority")
i=0
while i < len(gr_gdf):
    gr_gdf.loc[i,"hs1975"]=zonstaths[i]["majority"]
    i+=1
gr_gdf.columns
gr_gdf.dtypes
#gr_gdf=gr_gdf.astype({'hs1975': 'int'})#.dtypes
#gr_gdf.to_file(myworkspace+"/AR/gr_gdf_attributed.gpkg")
#del zonstaths
winsound.Beep(frequency, duration)

gr_gdf.to_file(myworkspace+"/NE/gr_gdf_attributed_temp.gpkg")
#gr_gdf=gpd.read_file(myworkspace+"/NE/gr_gdf_attributed_temp.gpkg")
winsound.Beep(frequency, duration)






gr_gdf.to_file(myworkspace+"/GR/gr_gdf_temp.gpkg")















gr_unique=gr_gdf[['wg_haupt', 'wg_zusatz', 'wg_name','nais_profi']].drop_duplicates()
len(gr_unique)
gr_unique["nais1"]=''
gr_unique["nais2"]=''
gr_unique["tahs"]=''
gr_unique["tahsue"]=''
#for index, row in gr_unique.iterrows():
#    stotyp=row['NaiS']
#    if stotyp is not None:
#        if "(" in stotyp:
#            stoyplist=stotyp.replace('(', ' ').replace(')', '').strip().split()
#            if len(stoyplist)>1:
#                gr_unique.loc[index,'nais1']=stoyplist[0]
#                gr_unique.loc[index, 'nais2'] = stoyplist[1]
#            else:
#                gr_unique.loc[index, 'nais1'] = stoyplist[0]
#        elif "/" in stotyp:
#            stoyplist = stotyp.replace('/', ' ')
#            if len(stoyplist) > 1:
#                gr_unique.loc[index, 'nais1'] = stoyplist[0]
#                gr_unique.loc[index, 'nais2'] = stoyplist[1]
#            else:
#                gr_unique.loc[index, 'nais1'] = stoyplist[0]
#        else:
#            gr_unique.loc[index, 'nais1']=stotyp
#
#for index, row in gr_unique.iterrows():
#    tahs_list=[]
#    tahs_listshort = []
#    flistshort=[]
#    tahsue_list = []
#    tahsue_listshort = []
#    flistueshort = []
#    nais1=row["nais1"]
#    nais2 = row["nais2"]
#    #print(stotyp)
#    tempsel=parameterdf[(parameterdf["naishaupt"]==nais1)]
#    tahs_list=tempsel["hoehenstufe1"].unique().tolist()
#    tempsel = parameterdf[(parameterdf["naisue"] == nais2)]
#    tahsue_list = tempsel["hoehenstufe1"].unique().tolist()
#    for item in tahs_list:
#        for i in str(item).replace(',','').strip().split():
#            if i not in tahs_listshort and str(item) != 'nan':
#                tahs_listshort.append(item)
#    for item in tahsue_list:
#        for i in str(item).replace(',','').strip().split():
#            if i not in tahsue_listshort and str(item) != 'nan':
#                tahsue_listshort.append(item)
#    flist=list(set(tahs_listshort))
#    flist2 = list(set(tahsue_listshort))
#    #for item in str(flist).strip().split():
#    #    if item not in flistshort:
#    #        flistshort.append(item)
#    gr_unique.loc[((gr_unique["NaiS"] == nais1)), "tahs"] = str(flist).replace("[","").replace("]","").replace("'","").replace("]","").replace('nan','').replace(',','').replace('"','')
#    gr_unique.loc[((gr_unique["NaiS"] == nais2)), "tahsue"] = str(flist2).replace("[", "").replace("]", "").replace("'","").replace("]", "").replace('nan', '').replace(',', '').replace('"', '')

gr_unique.to_excel(codespace+"/GL_nais_einheiten_unique.xlsx")