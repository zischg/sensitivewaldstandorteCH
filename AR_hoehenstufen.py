import numpy as np
import pandas as pd
import joblib
import fiona
import geopandas as gpd
import os
import shapely
from osgeo import ogr
import sqlalchemy
from sqlalchemy import create_engine
import xlrd
import openpyxl
from rasterstats import zonal_stats
import joblib
from osgeo import osr, gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95
gtiff_driver=gdal.GetDriverByName("GTiff")


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
hsmoddict={3:"collin",4:"submontan",5:"untermontan",6:"obermontan",8:"hochmontan",9:"subalpin",10:"obersubalpin"}
hsmoddictkurz={3:"co",4:"sm",5:"um",6:"om",8:"hm",9:"sa",10:"osa"}
hoehenstufenlist=["collin","submontan","untermontan","obermontan","hochmontan","subalpin","obersubalpin"]

#read excel files
naiseinheitenunique=pd.read_excel(codespace+"/AR_nais_einheiten_unique_mf.xlsx", dtype="str", engine='openpyxl')

#read the rasters
#reference tif raster
print("read reference raster")
referenceraster=myworkspace+"/AR/dem10m.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
#indatatypeint=gdal.Open(myworkspace+"/regionen.tif").GetRasterBand(1).DataType
#dhmarr=convert_tif_to_array("D:/CCW20/GIS/dhm25.tif")
NODATA_value=-9999

sloperaster=myworkspace+"/AR/slope10mprz.tif"
radiationraster=myworkspace+"/AR/globradyw.tif"
hoehenstufenraster=myworkspace+"/AR/hs1975.tif"
#hsheute=gpd.read_file(myworkspace+"/Ar/vegetationshoehenstufen19611990clipSGAIAR.shp")

#read shapefile
stok_gdf=gpd.read_file(myworkspace+"/AR/forest_types_ar.gpkg")
taheute=gpd.read_file(myworkspace+"/Tannenareale.shp")
storeg=gpd.read_file(myworkspace+"/Waldstandortsregionen.shp")
#stok_gdf=gpd.read_file(projectspace+"/GIS/stok_gdf_attributed.shp")
len(stok_gdf)
stok_gdf.crs
#stok_gdf.plot()
stok_gdf.columns
#change column names (sg___ are the St Gallen units)
#stok_gdf.rename(columns={"DTWGEINHEI": "kanteinh", "naisueberg": "sgue", "naismosaic":"sgmosaic"}, inplace=True)
#stok_gdf["nais1"]=""
#stok_gdf["naisue"]=""
#stok_gdf["naismosaic"]=""
#stok_gdf["joinid"]=0
#stok_gdf["joinid"]=stok_gdf.index


#Tannenareale
taheute.crs
taheute.columns
#taheute.plot()
taheute.rename(columns={"Code_Ta": "taheute"}, inplace=True)
taheute.drop(columns=['Areal_de', 'Areal_fr', 'Areal_it', 'Areal_en','Shape_Leng','Shape_Area'], inplace=True)
#overlay spatial join
stok_gdf=gpd.sjoin(stok_gdf,taheute, how='left', op="intersects")
len(stok_gdf)
#stok_gdfta=gpd.sjoin_nearest(stok_gdf, taheute, how='left', max_distance=500, distance_col=None)#lsuffix='left', rsuffix='right'
#stok_gdfta=gpd.sjoin(stok_gdf,taheute, how='left', op="intersects")
#len(stok_gdfta)
#stok_gdf=stok_gdfta[["joinid","taheute"]].groupby(by=["joinid"]).min()
#stok_gdftagrouped=stok_gdfta[["joinid","taheute"]].groupby(by=["joinid"]).min()
#stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
#len(stok_gdftagrouped)
#stok_gdftagrouped.columns
#stok_gdf.columns
#stok_gdf=stok_gdf.merge(stok_gdftagrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
#len(stok_gdf)
#np.max(stok_gdftagrouped["taheute"])
#stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")
#del taheute
#del stok_gdftagrouped
#del stok_gdfta
stok_gdf.columns
stok_gdf=stok_gdf[['DTWGEINHEI','taheute','geometry']]
stok_gdf['joinid']=stok_gdf.index

#Standortregionen
storeg.crs
storeg.columns
#taheute.plot()
storeg.rename(columns={"Subcode": "storeg"}, inplace=True)
storeg.drop(columns=['Region_de', 'Region_fr', 'Region_it', 'Region_en', 'Code', 'Code_Bu', 'Code_Fi', 'Shape_Leng', 'Shape_Area'], inplace=True)
#overlay spatial join
stok_gdfstoreg=gpd.sjoin(stok_gdf,storeg, how='left', op="intersects")
len(stok_gdfstoreg)
stok_gdfstoreggrouped=stok_gdfstoreg[["joinid","storeg"]].groupby(by=["joinid"]).min()
##stok_gdftagrouped["joinid"]=stok_gdftagrouped.index
len(stok_gdfstoreggrouped)
stok_gdfstoreggrouped.columns
#stok_gdf.columns
stok_gdf=stok_gdf.merge(stok_gdfstoreggrouped, on='joinid', how='left')#left_on='joinid', right_on='joinid',
#len(stok_gdf)
#stok_gdf.to_file(projectspace+"/GIS/stok_gdf_attributed.shp")
del storeg
del stok_gdfstoreggrouped
del stok_gdfstoreg


#attribute shapefile
#mean slope in percent
stok_gdf["meanslopeprc"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="mean")
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
del zonstatslope

#radiation
stok_gdf["rad"]=0
#zonstatslope=zonal_stats(stok_gdf, referenceraster,stats="count min mean max median")
zonstatrad=zonal_stats(stok_gdf, radiationraster,stats="mean")
i=0
while i < len(stok_gdf):
    stok_gdf.loc[i,"rad"]=zonstatrad[i]["mean"]
    i+=1
stok_gdf["radiation"]=0
stok_gdf.loc[stok_gdf["rad"]>=147.0,"radiation"]=1 #10% quantile
stok_gdf.loc[stok_gdf["rad"]<=112.0,"radiation"]=-1 #90% quantile
stok_gdf.columns
del zonstatrad

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
stok_gdf.to_file(myworkspace+"/AR/stok_gdf_attributed.gpkg")
del zonstaths

#uebersetzung von Kantonseinheit in NAIS

naiseinheitenunique=naiseinheitenunique[naiseinheitenunique['NaiS'].isnull() == False]
len(naiseinheitenunique)
stok_gdf['nais']=''
stok_gdf['nais1']=''
stok_gdf['nais2']=''
stok_gdf['mo']=0
stok_gdf['ue']=0
#stok_gdf['hsmod']=0
stok_gdf['hs']=''
stok_gdf['tahs']=''
stok_gdf['tahsue']=''
for index, row in naiseinheitenunique.iterrows():
    kantonseinheit=row["DTWGEINHEI"]
    nais=row["NaiS"]
    hslist=row['hs'].replace('/',' ').replace('(',' ').replace(')','').strip().split()
    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "nais"] = nais
    stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "hs"] =row['hs']
    if '(' in row['hs']:
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "nais1"] = row['NaiS'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[0]
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "nais2"] = row['NaiS'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[1]
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "ue"] = 1
    if '/' in row['hs']:
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "nais1"] = row['NaiS'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[0]
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "nais2"] = row['NaiS'].replace('/',' ').replace('(',' ').replace(')','').strip().split()[1]
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "mo"] = 1
    if len(hslist)==1:
        stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "tahs"] = hoehenstufendictabkuerzungen[hslist[0]]
    else:
        if "(" in row['hs']:
            stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "tahs"] = hslist[0]
            stok_gdf.loc[stok_gdf["DTWGEINHEI"] == kantonseinheit, "tahsue"] = hslist[1]
        else:
            for index2, row2 in stok_gdf[stok_gdf["DTWGEINHEI"]==kantonseinheit].iterrows():
                if row2['hs1975']>0:
                    hsmod=hsmoddictkurz[int(row2['hs1975'])]
                else:
                    hsmod = 'nan'
                if hsmod in row2['hs'].strip().split():
                    stok_gdf.loc[index2,'tahs']=hoehenstufendictabkuerzungen[hsmod]
                else:
                    test=hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[0]]
                    if len(row2['hs'].replace('(',' ').replace(')','').strip().split()) >1 and test == 'collin':
                        stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[-1]]
                    else:
                        stok_gdf.loc[index2, 'tahs'] = hoehenstufendictabkuerzungen[row2['hs'].replace('(',' ').replace(')','').strip().split()[0]]
stok_gdf.columns
stok_gdf=stok_gdf[['joinid', 'DTWGEINHEI', 'taheute', 'storeg', 'meanslopeprc','slpprzrec', 'rad', 'radiation', 'hs1975', 'nais', 'nais1', 'nais2','mo', 'ue', 'hs', 'tahs', 'tahsue','geometry']]
stok_gdf.to_file(myworkspace+"/AR/stok_gdf_attributed.gpkg")
#stok_gdf=gpd.read_file(myworkspace+"/AR/stok_gdf_attributed.gpkg")













#check empty values
stok_gdf["hs1"].unique().tolist()
checknohs=stok_gdf[stok_gdf["hs1"]==""][["DTWGEINHEI","sg1","nais1", "hs1","hsmod"]]
checknohs=stok_gdf[stok_gdf["hs1"]==""][["nais1","hsmod"]]
len(checknohs)
checknohsunique=checknohs.groupby(by=["nais1","hsmod"])
len(checknohsunique)
checknohs["nais1"].unique().tolist()
checknohsunique["nais1"].unique().tolist()

#hoehenstufe heute definitif
stok_gdf["hsheudef"]=""
stok_gdf.loc[stok_gdf["hs1"] == "co","hsheudef"]="collin"
stok_gdf.loc[stok_gdf["hs1"] == "sm","hsheudef"]="submontan"
stok_gdf.loc[stok_gdf["hs1"] == "um","hsheudef"]="untermontan"
stok_gdf.loc[stok_gdf["hs1"] == "om","hsheudef"]="obermontan"
stok_gdf.loc[stok_gdf["hs1"] == "hm","hsheudef"]="hochmontan"
stok_gdf.loc[stok_gdf["hs1"] == "sa","hsheudef"]="subalpin"
stok_gdf.loc[stok_gdf["hs1"] == "osa","hsheudef"]="obersubalpin"



##Lage
##kuppen
#kuppen=gpd.read_file(projectspace+"/GIS/sgkuppen.shp")
#kuppen.crs
#kuppen.columns
#stok_gdf["lage"]=0
#stok_gdflage=gpd.sjoin(stok_gdf,kuppen, how='left', op="within")
#len(stok_gdflage)
#stok_gdflage.loc[stok_gdflage["gridcode"]!=4,["gridcode"]]=0
#stok_gdf.loc[stok_gdflage["gridcode"]==4,["lage"]]=4
##ebene
#stok_gdf.loc[stok_gdf["meanslopeprc"]<10.0,"lage"]=1
##mulden
#mulden=gpd.read_file(projectspace+"/GIS/sgmuldenLV95.shp")
#mulden.crs
##mulden.set_crs(2056, inplace=True)
#mulden.columns
#mulden.plot()
#stok_gdflage=gpd.sjoin(stok_gdf,mulden, how='left', op="within")
#len(stok_gdflage)
#np.max(stok_gdflage["gridcode"])
#stok_gdf.loc[stok_gdflage["gridcode"]==2,["lage"]]=2
##hang
#stok_gdf.loc[stok_gdf["lage"]==0,"lage"]=3
#np.min(stok_gdf["lage"])
#del stok_gdflage



#export for monika to refine
stok_gdf.columns
stok_gdf.to_postgis(name="sg_stok_gdf", con=engine)
sqlstatement='SELECT "DTWGEINHEI",mosaic,uebergang,sg1,sgue,sgmosaic,nais1,naisue,naismosaic, hs1,hsue, hsmo FROM public.sg_stok_gdf GROUP BY "DTWGEINHEI",mosaic,uebergang,sg1,sgue,sgmosaic,nais1,naisue,naismosaic, hs1,hsue, hsmo;'
checkallunique=pd.read_sql_query(sqlstatement,con=engine)
len(checkallunique)
checkallunique.to_excel(projectspace+"/export/checkallunique.xlsx")
checkallunique_reduced=checkallunique[((checkallunique["uebergang"]==1) | (checkallunique["mosaic"]==1))]
checkallunique_reduced["tocheck"]=0
checkallunique_reduced.loc[((checkallunique_reduced["uebergang"]==1) & (checkallunique_reduced["hs1"]!=checkallunique_reduced["hsue"])),"tocheck"]=1
checkallunique_reduced.loc[((checkallunique_reduced["mosaic"]==1) & (checkallunique_reduced["hs1"]!=checkallunique_reduced["hsmo"])),"tocheck"]=1
checkallunique_reduced=checkallunique_reduced[checkallunique_reduced["tocheck"]==1]
len(checkallunique_reduced)
checkallunique_reduced.to_excel(projectspace+"/export/checkallunique_reduced.xlsx")