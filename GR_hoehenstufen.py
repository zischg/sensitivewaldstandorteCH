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
hoehenstufendict={"hyperinsubrisch":"hyp","collin":"co","collin mit Buche":"cob","submontan":"sm","untermontan":"um","obermontan":"om","hochmontan":"hm","subalpin":"sa","obersubalpin":"osa"}
hoehenstufendictabkuerzungen={"hyp":"hyperinsubrisch","co":"collin","cob":"collin mit Buche","sm":"submontan","um":"untermontan","om":"obermontan","hm":"hochmontan","sa":"subalpin","osa":"obersubalpin"}
hsmoddict={2:"collin",3:"collin",4:"submontan",5:"untermontan",6:"obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={2:"co",3:"co",4:"sm",5:"um",6:"om",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["collin","submontan","untermontan","obermontan","hochmontan","subalpin","obersubalpin"]

#read excel files
naiseinheitenunique=pd.read_excel(codespace+"/GR_nais_einheiten_unique_v2_bh_mf.xlsx", sheet_name='Sheet1', dtype="str", engine='openpyxl')
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
naiseinheitenunique['nais1']==''
naiseinheitenunique['nais2']==''
for index, row in naiseinheitenunique.iterrows():
    assgr=row['ASS_GR']
    naisbg=row['NAISbg']
    nais=row['nais']
    if "(" in nais:
        naislist=nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR']==assgr)&(naiseinheitenunique['NAISbg']==naisbg)),'nais1']=naislist[0]
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR'] == assgr) & (naiseinheitenunique['NAISbg'] == naisbg)), 'nais2'] = naislist[1]
    elif "/" in nais:
        naislist=nais.replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR']==assgr)&(naiseinheitenunique['NAISbg']==naisbg)),'nais1']=naislist[0]
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR'] == assgr) & (naiseinheitenunique['NAISbg'] == naisbg)), 'nais2'] = naislist[1]
    else:
        naiseinheitenunique.loc[((naiseinheitenunique['ASS_GR']==assgr)&(naiseinheitenunique['NAISbg']==naisbg)),'nais1']=nais

#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=myworkspace+"/GR/GR_dem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
NODATA_value=-9999
sloperaster=myworkspace+"/GR/GR_slopeprz.tif"
radiationraster=myworkspace+"/GR/GR_globradyyw.tif"
hoehenstufenraster=myworkspace+("/GR/GR_vegetationshoehenstufen1975.tif")


#read shapefile
stok_gdf=gpd.read_file(myworkspace+"/GR/STATIONS_20250430_fixed.gpkg", layer='STATIONS_20250430')
taheute=gpd.read_file(myworkspace+"/Tannenareale2025.gpkg")
storeg=gpd.read_file(myworkspace+"/Waldstandortregionen_2024_TI4ab_Final_GR.gpkg", layer='waldstandortregionen_2024_ti4ab_final')
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

stok_gdf.to_file(myworkspace+"/GR/stok_gdf_attributed_temp4.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/GR/stok_gdf_attributed_temp4.gpkg")
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
stok_gdf.loc[stok_gdf['ASS_GR'].isnull()==True,'ASS_GR']=''
stok_gdf.loc[stok_gdf['NAISbg'].isnull()==True,'NAISbg']=''
stok_gdf.loc[stok_gdf['ASS_GR'].isnull()==True,'ASS_GR']=''
stok_gdf.loc[stok_gdf['NAISbg']=='<Null>','NAISbg']=''
stok_gdf.loc[stok_gdf['ASS_GR'].isnull()==True,'ASS_GR']=''
stok_gdf.loc[stok_gdf['NAISbg'].isnull()==True,'NAISbg']=''
naiseinheitenunique.loc[naiseinheitenunique['nais'].isnull()==True,'nais']=''
naiseinheitenunique.loc[naiseinheitenunique['hs'].isnull()==True,'hs']=''
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['nais']!='']
naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['hs']!='']


print('iterate for attributing nais and tahs')
len(naiseinheitenunique)
for index, row in naiseinheitenunique.iterrows():
    kantonseinheit=row['ASS_GR']
    NAISbg=row["NAISbg"]
    nais = row["nais"]
    nais1 = row["nais1"]
    nais2 = row["nais2"]
    hs=row['hs']
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').replace('  ',' ').strip().split()
    #Hoehenstufenzuweisung
    stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "nais"] = nais
    stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "nais1"] = nais1
    stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "nais2"] = nais2
    stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "hs"] = row['hs']
    #Uebersetzung NaiS
    if row['nais2']!='':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "ue"] = 1
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "nais"] = row['nais1']+'('+row['nais2']+')'
    else:
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "nais"] = row['nais1']
    #Uebergang
    if nais2 !='':
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "ue"] = 1
    #Hohenstufenzuweisung
    if len(hslist)==1:
        stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
    else:
        if "(" in row['hs']:
            stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
            stok_gdf.loc[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg)), "tahsue"] = hoehenstufendictabkuerzungen[hslist[1]]
        else:
            for index2, row2 in stok_gdf[((stok_gdf["ASS_GR"] == kantonseinheit) & (stok_gdf["NAISbg"] == NAISbg))].iterrows():
                if row2['hs1975']>0:
                    hsmod=hsmoddictkurz[int(row2['hs1975'])]
                else:
                    hsmod = 'nan'
                if hsmod in row2['hs'].strip().split():
                    stok_gdf.loc[index2,'tahs']=hoehenstufendictabkuerzungen[hsmod]
                else:
                    if len(row2['hs'].replace('(',' ').replace(')','').strip().split()) >0:
                        test=hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[0]]
                        if len(row2['hs'].replace('(',' ').replace(')','').strip().split()) >1 and test == 'collin':
                            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[-1]]
                        else:
                            stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(', ' ').replace(')', '').strip().split()[-1]]
winsound.Beep(frequency, duration)

#check Hohenstufenzuweisung
checknohs=stok_gdf[((stok_gdf["tahs"]==""))]
fehlendeuebersetzungen=checknohs['ASS_GR'].unique().tolist()

stok_gdf.loc[((stok_gdf["ue"] == 1)&(stok_gdf["tahsue"] == '')) , "tahsue"] = stok_gdf["tahs"]
stok_gdf.loc[((stok_gdf["mo"] == 1)&(stok_gdf["tahsue"] == '')) , "tahsue"] = stok_gdf["tahs"]
stok_gdf['tahsue'].unique().tolist()
stok_gdf['tahs'].unique().tolist()
print("write output")
stok_gdf.columns
stok_gdf=stok_gdf[['ASS_GR', 'NAISbg','joinid', 'taheute','storeg', 'meanslopeprc', 'slpprzrec', 'rad', 'radiation','hs1975', 'nais','nais1', 'nais2', 'hs', 'ue',  'mo', 'tahs', 'tahsue', 'geometry']]
stok_gdf.to_file(myworkspace+"/GR/stok_gdf_attributed.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/GR/stok_gdf_attributed.gpkg")
print("done")




#Export for tree-app
print('Export for Tree-App')
stok_gdf.columns
#stok_gdf.loc[((stok_gdf['ue']==1)&(NAISbg['tahsue']=='')&(stok_gdf['tahs']!='')),'tahsue']=stok_gdf['tahs']
treeapp=stok_gdf[['ASS_GR', 'NAISbg''nais', 'nais1', 'nais2', 'mo', 'ue','tahs', 'tahsue','geometry']]
treeapp.to_file(myworkspace+"/GR/GR_treeapp.gpkg", layer='GR_treeapp', driver="GPKG")
treeapp.columns
print("done")
