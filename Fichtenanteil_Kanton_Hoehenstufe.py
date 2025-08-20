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

kantonelist=['AG', 'AI', 'AR', 'BE', 'BL', 'BS', 'FR', 'GE', 'GL', 'GR', 'JU', 'LU', 'NE', 'NW', 'OW', 'SG', 'SH', 'SO', 'SZ', 'TG', 'UR', 'VD', 'VS', 'ZG', 'ZH'] #'TI',

#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi"
LFI_baumartenanteil=pd.read_excel(codeworkspace+"/"+"LFI5_Stammzahl_NaiS-Vegetationshöhenstufen_(6_Klassen)_Hauptbaumart_export.xlsx",  engine='openpyxl', sheet_name='export')
LFI_baumartenanteil['BL']=LFI_baumartenanteil['BLBS']
LFI_baumartenanteil['BS']=LFI_baumartenanteil['BLBS']
kantone=gpd.read_file(projectspace+"/kantone.gpkg")
kantone=kantone[['kanton','geometry']]
Tannenareal=gpd.read_file(projectspace+"/Waldstandortregionen_2025.shp")
Tannenareal=Tannenareal[['Subcode','Code_Ta','geometry']]
Tannenareal.rename(columns={'Subcode':'storeg'}, inplace=True)
hs=gpd.read_file(projectspace+"/vegetationshoehenstufen_1975.gpkg", layer='vegetationshoehenstufen_1975')
len(hs)
hs.columns
hs=hs[['HS_de','Code','Subcode','geometry']]
#intersect
#baumartenanteil=kantone.overlay(Tannenareal, how='intersection')
#baumartenanteil=baumartenanteil.overlay(hs, how='intersection')
baumartenanteil=gpd.read_file(projectspace+"/kanton_intsct_hs_storeg.gpkg")
#baumartenanteil.to_file(projectspace+"/kanton_intsct_hs_storeg.gpkg", driver='GPKG')
#join
baumartenanteil['FIanteil']=0
baumartenanteil['TAanteil']=0
baumartenanteil['LAEanteil']=0
LFI_baumartenanteil['HS'].unique().tolist()
for kanton in kantonelist:
    print(kanton)
    #osa
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Fichte'))][kanton].values)>0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'obersubalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Tanne'))][kanton].values)>0:
        tannenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Lärche'))][kanton].values)>0:
        laerchenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'LAEanteil'] = laerchenanteil
    # sa
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'LAEanteil'] = laerchenanteil
    # hm
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'LAEanteil'] = laerchenanteil
    # om
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'LAEanteil'] = laerchenanteil
    # um
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'LAEanteil'] = laerchenanteil
    # sm
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'LAEanteil'] = laerchenanteil
    # co
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'LAEanteil'] = laerchenanteil
    # cob
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'LAEanteil'] = laerchenanteil
    # hyp
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'LAEanteil'] = laerchenanteil
    # um/om
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'FIanteil'] = fichtenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'TAanteil'] = tannenanteil
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'LAEanteil'] = laerchenanteil

baumartenanteil.to_file(projectspace + "/baumartenanteil.gpkg", driver='GPKG')

