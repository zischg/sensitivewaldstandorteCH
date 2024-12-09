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
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi"

rcp45=gpd.read_file(projectspace+"/GL"+"/GL_rcp45_zukuenftigestandorte.gpkg", layer="GL_rcp45_zukuenftigestandorte", driver="GPKG")
rcp85=gpd.read_file(projectspace+"/GL"+"/GL_rcp85_zukuenftigestandorte.gpkg", layer="GL_rcp85_zukuenftigestandorte", driver="GPKG")
rcp45.columns
rcp45=rcp45[['nais','nais1', 'nais2', 'mo', 'ue','taheute', 'storeg', 'tahs', 'tahsue','naiszuk1','naiszuk2', 'hszukcor', 'geometry']]
rcp45=rcp45.rename(columns={'naiszuk1':'nais1_rcp45','naiszuk2':'nais2_rcp45', 'hszukcor':'hs_rcp45'})
rcp85=rcp85[['naiszuk1','naiszuk2', 'hszukcor', 'geometry']]
rcp85=rcp85.rename(columns={'naiszuk1':'nais1_rcp85','naiszuk2':'nais2_rcp85', 'hszukcor':'hs_rcp85'})

#unique pathways
combi=gpd.overlay(rcp45, rcp85, how='intersection', make_valid=True, keep_geom_type=True)
test45=baumartenbedeutungenrcp45[baumartenbedeutungenrcp45['nais']=='18M(48)']
test85=baumartenbedeutungenrcp85[baumartenbedeutungenrcp85['nais']=='18M(48)']
colist=combi.columns.tolist()
#combi=combi[['nais_1','tahs_1','tahsue_1','naiszuk1_1', 'naiszuk2_1','hszukcor_1','naiszuk1_2', 'naiszuk2_2','hszukcor_2','geometry']]
#combi.rename(columns={'nais_1':'nais_heute', 'tahs_1':'hs_heute','tahsue_1':'hsue_heute','naiszuk1_1':'nais1_rcp45', 'naiszuk2_1':'nais2_rcp45','hszukcor_1':'hs_rcp45','naiszuk1_2':'nais1_rcp85', 'naiszuk2_2':'nais2_rcp85','hszukcor_2':'hs_rcp85'}, inplace=True)
combi.loc[(combi['hs_rcp85']==combi['hs_rcp45']),'nais1_rcp85']=combi['nais1_rcp45']
combi.loc[(combi['hs_rcp85']==combi['hs_rcp45']),'nais2_rcp85']=combi['nais2_rcp45']
combi['area']=combi.geometry.area
#test = combi[combi['nais_heute']=='18M(48)']
len(combi)
combi=combi[combi['area']>=0]
combi.to_file(projectspace+"/GL"+"/GL_Projektionswege_combi.gpkg", layer="GL_Projektionswege_combi", driver="GPKG")
combi=combi[combi['area']>=10000]
combi.columns
combi=combi[['nais', 'tahs', 'tahsue', 'nais1_rcp45', 'nais2_rcp45','hs_rcp45', 'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85']]
#test=combi[((combi['hs_rcp85']==combi['hs_rcp45'])&(combi['nais2_rcp45']!=combi['nais2_rcp85']))]
#testunique=test.drop_duplicates()
#len(testunique)
combi.columns
combi_unique=combi.drop_duplicates()
#combi_unique.loc[combi_unique['hs_heute']==10,'hs_heute']='obersubalpin'
#combi_unique.loc[combi_unique['hs_heute']==9,'hs_heute']='subalpin'
#combi_unique.loc[combi_unique['hs_heute']==8,'hs_heute']='hochmontan'
#combi_unique.loc[combi_unique['hs_heute']==6,'hs_heute']='obermontan'
#combi_unique.loc[combi_unique['hs_heute']==5,'hs_heute']='untermontan'
#combi_unique.loc[combi_unique['hs_heute']==4,'hs_heute']='submontah'
#combi_unique.loc[combi_unique['hs_heute']==2,'hs_heute']='collin'
len(combi_unique)
combi_unique=combi_unique[combi_unique['hs_heute'].isin(['obersubalpin','subalpin','hochmontan','obermontan','untermontan','submontan','collin'])]
combi_unique=combi_unique.sort_values(by=['nais_heute'])
combi_unique.to_excel(projectspace+'/GL/'+"/GL_Projektionspfade_unique.xlsx")

