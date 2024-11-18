import numpy as np
import pandas as pd
import joblib
import fiona
import geopandas as gpd
import os
#import shapefile
import shapely
#import pyshp
from osgeo import ogr
#import psycopg2
#import sqlalchemy
#import geoalchemy2
#from sqlalchemy import create_engine
import xlrd
import openpyxl


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
combi.to_file(projectspace+"/GL"+"/GL_baumartenempfehlungen_combi.gpkg", layer="GL_GL_baumartenempfehlungen_combi", driver="GPKG")

