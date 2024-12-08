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

baumartenempfehlungenrcp45=gpd.read_file(projectspace+"/GL"+"/GL_rcp45_baumartenempfehlungen.gpkg", layer="GL_rcp45_baumartenempfehlungen", driver="GPKG")
baumartenbedeutungenrcp45=gpd.read_file(projectspace+"/GL"+"/GL_rcp45_baumartenbedeutungen.gpkg", layer="GL_rcp45_baumartenbedeutungen", driver="GPKG")
baumartenbedeutungenrcp85=gpd.read_file(projectspace+"/GL"+"/GL_rcp85_baumartenbedeutungen.gpkg", layer="GL_rcp85_baumartenbedeutungen", driver="GPKG")
combi=gpd.overlay(baumartenbedeutungenrcp45, baumartenbedeutungenrcp85, how='intersection', make_valid=True, keep_geom_type=True)

for item in combi.columns.tolist():
    if "FI" in item:
        print(item)
treetypeslist=baumartenempfehlungenrcp45.columns.tolist()[26:-1]
#****************************************************************************
# #combi
for col in treetypeslist:
    print(col)
    #empfohlene Baumarten. in Zukunft entweder in beiden Klimazukünften dominante oder wichtige beigemischte Naturwaldbaumarten (fett) oder dies trifft entweder bei «mässigem» oder «starkem» Klimawandel zu, während sie in der anderen Klimazukunft nur weitere Baumart sind (Normalschrift)
    combi[col]=0
    combi[col+"Fall"] = 0
    for index, row in combi.iterrows():
        #Empfohlen 1
        if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['a', 'b'] and row[col + 'zuk1_2'] in ['a', 'b']:
            combi.loc[index, col]=1
            combi.loc[index, col+"Fall"] = 1
        if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] in ['a', 'b']:
            combi.loc[index, col]=1
            combi.loc[index, col+"Fall"] = 2
        if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['a','b'] and row[col + 'zuk1_2'] in ['c']:
            combi.loc[index, col]=1
            combi.loc[index, col+"Fall"] = 3
        #bedingt empfohlen 2
        if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2']  in ['c']:
            combi.loc[index, col]=2
            combi.loc[index, col+"Fall"] = 7
        if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2']not in ['a', 'b','c']:
            combi.loc[index, col]=2
            combi.loc[index, col+"Fall"] = 8
        if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b','c'] and row[col + 'zuk1_1'] not in ['a','b','c'] and row[col + 'zuk1_2'] in ['a','b']:
            combi.loc[index, col]=2
            combi.loc[index, col+"Fall"] = 9
        #gefaehrdet 3
        if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] not in ['a', 'b','c']:
            combi.loc[index, col]=3
            combi.loc[index, col+"Fall"] = 15
        if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b','c'] and row[col + 'zuk1_1'] not in ['a', 'b','c'] and row[col + 'zuk1_2'] in ['c']:
            combi.loc[index, col]=3
            combi.loc[index, col+"Fall"] = 16
        if row['ue_1'] == 0 and row[col + 'heu1_1'] in ['a', 'b','c'] and row[col + 'zuk1_1'] not in ['a','b','c'] and row[col + 'zuk1_2'] not in ['a','b','c'] :
            combi.loc[index, col]=3
            combi.loc[index, col+"Fall"] = 17
        #in Zukunft empfohlen 4
        if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['a','b'] and row[col + 'zuk1_2'] in ['a', 'b']:
            combi.loc[index, col]=4
            combi.loc[index, col+"Fall"] = 4
        if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['a','b'] and row[col + 'zuk1_2'] in ['c']:
            combi.loc[index, col]=4
            combi.loc[index, col+"Fall"] = 5
        if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] in ['a', 'b']:
            combi.loc[index, col]=4
            combi.loc[index, col+"Fall"] = 6
        #in Zukunft bedingt empfohlen 5
        if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] in ['c']:
            combi.loc[index, col]=5
            combi.loc[index, col+"Fall"] = 10
        if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['a', 'b'] and row[col + 'zuk1_2'] not in ['a', 'b','c'] :
            combi.loc[index, col]=5
            combi.loc[index, col+"Fall"] = 11
        if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b','c'] and row[col + 'zuk1_1'] not in ['a', 'b','c'] and row[col + 'zuk1_2'] in ['a', 'b'] :
            combi.loc[index, col]=5
            combi.loc[index, col+"Fall"] = 12
        if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b','c'] and row[col + 'zuk1_1'] in ['c'] and row[col + 'zuk1_2'] not in ['a', 'b','c']:
            combi.loc[index, col]=5
            combi.loc[index, col+"Fall"] = 13
        if row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a', 'b', 'c'] and row[col + 'zuk1_1'] not in ['a', 'b', 'c'] and row[ col + 'zuk1_2'] in ['c']:
            combi.loc[index, col] = 5
            combi.loc[index, col + "Fall"] = 14
        #Achtung 6
        if col == "GO" and row['ue_1'] == 0 and row[col + 'heu1_1'] in ['c'] and row[col + 'zuk1_1'] in ['c'] and row[ col + 'zuk1_2'] not in ['a','b','c']:
            combi.loc[index, col] = 6
            combi.loc[index, col + "Fall"] = 18
        if col == "GO" and row['ue_1'] == 0 and row[col + 'heu1_1'] in ['c'] and row[col + 'zuk1_1'] not in ['a','b','c'] and row[ col + 'zuk1_2']  in ['c']:
            combi.loc[index, col] = 6
            combi.loc[index, col + "Fall"] = 19
        if col == "GO" and row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a','b','c'] and row[col + 'zuk1_1'] in ['c'] and row[ col + 'zuk1_2'] not in ['a','b','c']:
            combi.loc[index, col] = 6
            combi.loc[index, col + "Fall"] = 20
        if col == "GO" and row['ue_1'] == 0 and row[col + 'heu1_1'] not in ['a','b','c'] and row[col + 'zuk1_1'] not in ['a','b','c'] and row[ col + 'zuk1_2'] in ['c']:
            combi.loc[index, col] = 6
            combi.loc[index, col + "Fall"] = 21
        #****************
        #Uebergang
            # Empfohlen 1
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['a', 'b'] and \
                    row[col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 1
                combi.loc[index, col + "Fall"] = 1
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['c'] and row[
                col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 1
                combi.loc[index, col + "Fall"] = 2
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['a', 'b'] and \
                    row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 1
                combi.loc[index, col + "Fall"] = 3
            # bedingt empfohlen 2
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['c'] and row[
                col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 2
                combi.loc[index, col + "Fall"] = 7
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['c'] and row[
                col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 2
                combi.loc[index, col + "Fall"] = 8
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and row[col + 'zukUE_1'] not in ['a', 'b','c'] and row[
                col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 2
                combi.loc[index, col + "Fall"] = 9
            # gefaehrdet 3
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['c'] and row[
                col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 3
                combi.loc[index, col + "Fall"] = 15
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and row[col + 'zukUE_1'] not in ['a', 'b','c'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 3
                combi.loc[index, col + "Fall"] = 16
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['a', 'b', 'c'] and row[col + 'zukUE_1'] not in ['a', 'b','c'] and row[
                col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 3
                combi.loc[index, col + "Fall"] = 17
            # in Zukunft empfohlen 4
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['a', 'b'] and \
                    row[col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 4
                combi.loc[index, col + "Fall"] = 4
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['a', 'b'] and \
                    row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 4
                combi.loc[index, col + "Fall"] = 5
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['c'] and row[
                col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 4
                combi.loc[index, col + "Fall"] = 6
            # in Zukunft bedingt empfohlen 5
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['c'] and row[
                col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 10
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['a', 'b'] and \
                    row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 11
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_1'] not in ['a', 'b',
                                                                                                               'c'] and \
                    row[col + 'zukUE_2'] in ['a', 'b']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 12
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_1'] in ['c'] and row[
                col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 13
            if row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_1'] not in ['a', 'b',
                                                                                                               'c'] and \
                    row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 5
                combi.loc[index, col + "Fall"] = 14
            # Achtung 6
            if col == "GO" and row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['c'] and row[col + 'zukUE_1'] in ['c'] and \
                    row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 6
                combi.loc[index, col + "Fall"] = 18
            if col == "GO" and row['ue_1'] ==1 and row[col + 'heuUE_1'] in ['c'] and row[col + 'zukUE_1'] not in ['a',
                                                                                                                 'b',
                                                                                                                 'c'] and \
                    row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 6
                combi.loc[index, col + "Fall"] = 19
            if col == "GO" and row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[
                col + 'zukUE_1'] in ['c'] and row[col + 'zukUE_2'] not in ['a', 'b', 'c']:
                combi.loc[index, col] = 6
                combi.loc[index, col + "Fall"] = 20
            if col == "GO" and row['ue_1'] ==1 and row[col + 'heuUE_1'] not in ['a', 'b', 'c'] and row[
                col + 'zukUE_1'] not in ['a', 'b', 'c'] and row[col + 'zukUE_2'] in ['c']:
                combi.loc[index, col] = 6
                combi.loc[index, col + "Fall"] = 21

combi.loc[(combi['hszukcor_2']==combi['hszukcor_1']),'naiszuk1_2']=combi['naiszuk1_1']
combi.loc[(combi['hszukcor_2']==combi['hszukcor_1']),'naiszuk2_2']=combi['naiszuk2_1']

for col in treetypeslist:
    combi.drop(columns=col+ 'heu1_1', axis=1, inplace=True)
    combi.drop(columns=col + 'heu2_1', axis=1, inplace=True)
    combi.drop(columns=col + 'zuk1_1', axis=1, inplace=True)
    combi.drop(columns=col + 'zuk2_1', axis=1, inplace=True)
    combi.drop(columns=col + 'heuUE_1', axis=1, inplace=True)
    combi.drop(columns=col + 'zukUE_1', axis=1, inplace=True)
    combi.drop(columns=col + 'heu1_2', axis=1, inplace=True)
    combi.drop(columns=col + 'heu2_2', axis=1, inplace=True)
    combi.drop(columns=col + 'zuk1_2', axis=1, inplace=True)
    combi.drop(columns=col + 'zuk2_2', axis=1, inplace=True)
    combi.drop(columns=col + 'heuUE_2', axis=1, inplace=True)
    combi.drop(columns=col + 'zukUE_2', axis=1, inplace=True)

combi.columns.tolist()
for column in combi.columns.tolist():
    if '_1' in column:
        combi.rename(columns={column: str(column[0:-2])}, inplace=True)
    if '_2' in column:
        combi.drop(columns=column, axis=1, inplace=True)
combi.columns

combi.to_file(projectspace+"/GL"+"/GL_baumartenempfehlungen_combi.gpkg", layer="GL_baumartenempfehlungen_combi", driver="GPKG")
print('all done')

#unique pathways
combi=gpd.overlay(baumartenbedeutungenrcp45, baumartenbedeutungenrcp85, how='intersection', make_valid=True, keep_geom_type=True)
test45=baumartenbedeutungenrcp45[baumartenbedeutungenrcp45['nais']=='18M(48)']
test85=baumartenbedeutungenrcp85[baumartenbedeutungenrcp85['nais']=='18M(48)']
colist=combi.columns.tolist()
combi=combi[['nais_1','tahs_1','tahsue_1','naiszuk1_1', 'naiszuk2_1','hszukcor_1','naiszuk1_2', 'naiszuk2_2','hszukcor_2','geometry']]
combi.rename(columns={'nais_1':'nais_heute', 'tahs_1':'hs_heute','tahsue_1':'hsue_heute','naiszuk1_1':'nais1_rcp45', 'naiszuk2_1':'nais2_rcp45','hszukcor_1':'hs_rcp45','naiszuk1_2':'nais1_rcp85', 'naiszuk2_2':'nais2_rcp85','hszukcor_2':'hs_rcp85'}, inplace=True)
combi.loc[(combi['hs_rcp85']==combi['hs_rcp45']),'nais1_rcp85']=combi['nais1_rcp45']
combi.loc[(combi['hs_rcp85']==combi['hs_rcp45']),'nais2_rcp85']=combi['nais2_rcp45']
combi['area']=combi.geometry.area
#test = combi[combi['nais_heute']=='18M(48)']
len(combi)
combi.to_file(projectspace+"/GL"+"/GL_Projektionswege_combi.gpkg", layer="GL_Projektionswege_combi", driver="GPKG")
combi=combi[combi['area']>=10000]
combi.columns
combi=combi[['nais_heute', 'hs_heute', 'hsue_heute', 'nais1_rcp45', 'nais2_rcp45','hs_rcp45', 'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85']]
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
