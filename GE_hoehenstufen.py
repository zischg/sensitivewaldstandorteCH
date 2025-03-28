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
hoehenstufendict={"collin":"co","submontan":"sm","untermontan":"um","obermontan":"om","hochmontan":"hm","subalpin":"sa","obersubalpin":"osa"}
hoehenstufendictabkuerzungen={"co":"collin","sm":"submontan","um":"untermontan","om":"obermontan","hm":"hochmontan","sa":"subalpin","osa":"obersubalpin"}
hsmoddict={2:"collin",3:"collin",4:"submontan",5:"untermontan",6:"obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={2:"co",3:"co",4:"sm",5:"um",6:"om",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["collin","submontan","untermontan","obermontan","hochmontan","subalpin","obersubalpin"]

#read excel files
naiseinheitenunique1=pd.read_excel(codespace+"/GE_FORET_einheiten_unique_bh2_mf_bh.xlsx", sheet_name='Sheet1', dtype="str", engine='openpyxl')
naiseinheitenunique1.columns
naiseinheitenunique1.dtypes
len(naiseinheitenunique1)
naiseinheitenunique1=naiseinheitenunique1[naiseinheitenunique1['nais']!='-']
naiseinheitenunique1=naiseinheitenunique1[naiseinheitenunique1['hs']!='']
naiseinheitenunique1=naiseinheitenunique1[naiseinheitenunique1['hs'].isnull()==False]
naiseinheitenunique1=naiseinheitenunique1[naiseinheitenunique1['hs']!='nan']

naiseinheitenunique2=pd.read_excel(codespace+"/GE_VEGETATION_einheiten_unique_bh2025_mf_bh.xlsx", sheet_name='Sheet1', dtype="str", engine='openpyxl')
naiseinheitenunique2.columns
naiseinheitenunique2.dtypes
len(naiseinheitenunique2)
naiseinheitenunique2.loc[naiseinheitenunique2['nais'].isnull()==True, 'nais']=''
naiseinheitenunique2.loc[naiseinheitenunique2['hs'].isnull()==True, 'hs']=''
naiseinheitenunique2.loc[naiseinheitenunique2['VEGETATION'].isnull()==True, 'VEGETATION']=''
naiseinheitenunique2.loc[naiseinheitenunique2['NO_TYPOLOG'].isnull()==True, 'NO_TYPOLOG']=''
naiseinheitenunique2=naiseinheitenunique2[naiseinheitenunique2['nais']!='']
naiseinheitenunique2=naiseinheitenunique2[naiseinheitenunique2['hs']!='']
naiseinheitenunique2=naiseinheitenunique2[naiseinheitenunique2['hs'].isnull()==False]
naiseinheitenunique2=naiseinheitenunique2[naiseinheitenunique2['hs']!='nan']



#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=myworkspace+"/GE/ge_dem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=myworkspace+"/GE/ge_slopeprz.tif"
radiationraster=myworkspace+"/GE/ge_globradyyw.tif"
hoehenstufenraster=myworkspace+("/GE/ge_hs1975.tif")


#read shapefile
stok_gdf=gpd.read_file(myworkspace+"/GE/GE_forest_merge.gpkg")
stok_gdf.dtypes
len(stok_gdf)
stok_gdf.crs
stok_gdf.columns
stok_gdf['joinid']=stok_gdf.index

#Tannenareale
stok_gdf['taheute']=1



#attribute shapefile
#mean slope in percent
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
stok_gdf["hs1975"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstaths=zonal_stats(stok_gdf, hoehenstufenraster,stats="majority")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"hs1975"]=zonstaths[i]["majority"]
    i+=1
stok_gdf.columns
stok_gdf.dtypes
#stok_gdf=stok_gdf.astype({'hs1975': 'int'})#.dtypes
#stok_gdf.to_file(myworkspace+"/AR/stok_gdf_attributed.gpkg")
#del zonstaths
winsound.Beep(frequency, duration)

stok_gdf.to_file(myworkspace+"/GE/stok_gdf_attributed_temp.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/GE/stok_gdf_attributed_temp.gpkg")
winsound.Beep(frequency, duration)


#uebersetzung von Kantonseinheit in NAIS
stok_gdf.columns
stok_gdf['nais']=''
stok_gdf['nais1']=''
stok_gdf['nais2']=''
stok_gdf['mo']=0
stok_gdf['ue']=0
stok_gdf['hs']=''
stok_gdf['tahs']=''
stok_gdf['tahsue']=''
#transform null values
stok_gdf.loc[stok_gdf['TYPE'].isnull()==True,'TYPE']=''
stok_gdf.loc[stok_gdf['VEGETATION'].isnull()==True,'VEGETATION']=''
naiseinheitenunique1.loc[naiseinheitenunique1['TYPE'].isnull()==True,'TYPE']=''
naiseinheitenunique2.loc[naiseinheitenunique2['VEGETATION'].isnull()==True,'VEGETATION']=''
naiseinheitenunique2.loc[naiseinheitenunique2['nais'].isnull()==True,'nais']=''
naiseinheitenunique2.loc[naiseinheitenunique2['hs'].isnull()==True,'hs']=''

print('iterate for attributing nais and tahs')
for index, row in naiseinheitenunique1.iterrows():
    kantonseinheit=row['TYPE']
    nais=row["nais"]
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
    #Hoehenstufenzuweisung
    stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "nais"] = nais
    stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "hs"] = row['hs']
    #Uebersetzung NaiS
    if '(' in row['nais']:
        stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "nais1"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "nais2"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[1]
        stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "ue"] = 1
    elif '/' in row['nais']:
        stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "nais1"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "nais2"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[1]
        stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "mo"] = 1
        stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "ue"] = 1
    else:
        stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "nais1"] = nais.replace('/', ' ').replace('(', ' ').replace(')', '').replace('  ', ' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["TYPE"] == kantonseinheit)), "nais2"] = ''

len(naiseinheitenunique2)
naiseinheitenunique2=naiseinheitenunique2[naiseinheitenunique2['nais']!='']
naiseinheitenunique2=naiseinheitenunique2[naiseinheitenunique2['hs']!='']
for index, row in naiseinheitenunique2.iterrows():
    kantonseinheit=row['VEGETATION']
    code_nais=row["NO_TYPOLOG"]
    nais=row["nais"]
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
    #Hoehenstufenzuweisung
    stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "nais"] = nais
    stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "hs"] = row['hs']
    #Uebersetzung NaiS
    if '(' in row['nais']:
        stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "nais1"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "nais2"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[1]
        stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "ue"] = 1
    elif '/' in row['nais']:
        stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "nais1"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[0]
        stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "nais2"] = nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()[1]
        stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "mo"] = 1
        stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "ue"] = 1
    else:
        if nais!='':
            stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "nais1"] = nais.replace('/', ' ').replace('(', ' ').replace(')', '').replace('  ', ' ').strip().split()[0]
            stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "nais2"] = ''
        else:
            stok_gdf.loc[((stok_gdf["VEGETATION"] == kantonseinheit) & (stok_gdf["NO_TYPOLOG"] == code_nais)), "nais1"] = ''


#Hohenstufenzuweisung
for index, row in stok_gdf.iterrows():
    if 'co' in row['hs'] and row['hs1975']==2:
        stok_gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen['co']
    else:
        stok_gdf.loc[index, "tahs"] = hoehenstufendictabkuerzungen['sm']

stok_gdf.loc[(stok_gdf["ue"] == 1) , "tahsue"] = stok_gdf["tahs"]
stok_gdf.loc[(stok_gdf["mo"] == 1) , "tahsue"] = stok_gdf["tahs"]
stok_gdf['tahsue'].unique().tolist()
print("write output")
stok_gdf.columns
#stok_gdf['BedingungHangneigung'].unique().tolist()
#stok_gdf['BedingungRegion'].unique().tolist()
stok_gdf.to_file(myworkspace+"/GE/stok_gdf_attributed.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/GE/stok_gdf_attributed.gpkg")
print("done")




#Export for tree-app
print('Export for Tree-App')
stok_gdf.columns
#stok_gdf.loc[((stok_gdf['ue']==1)&(stok_gdf['tahsue']=='')&(stok_gdf['tahs']!='')),'tahsue']=stok_gdf['tahs']
treeapp=stok_gdf[['code_neuch', 'associatio', 'nais', 'nais1', 'nais2', 'mo', 'ue','tahs', 'tahsue','geometry']]
treeapp.to_file(myworkspace+"/GE/GE_treeapp.gpkg", layer='GE_treeapp', driver="GPKG")
treeapp.columns
print("done")

#test = stok_gdf[stok_gdf['nais']=='18M(48)']
#test = stok_gdf[stok_gdf['nais']=='12a(18)']
#test = stok_gdf[stok_gdf['nais']=='46(8*)']
#test = stok_gdf[stok_gdf['nais']=='7a(10a)']
#test = stok_gdf[stok_gdf['nais']=='18v(18*)']
#test = stok_gdf[stok_gdf['nais']=='53Ta(18v)']
#test = stok_gdf[stok_gdf['nais1']=='']
#test = stok_gdf[((stok_gdf['nais2']=='')&(stok_gdf['ue']==1))]

#test2 = naiseinheitenunique[naiseinheitenunique['NaiS']=='60*(53)']
#test=stok_gdf[((stok_gdf['ue']==1)&(stok_gdf['tahsue']=='')&(stok_gdf['tahs']!=''))]



