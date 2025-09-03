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

kantonelist=['AG', 'AI', 'AR', 'BE', 'BL', 'BS', 'FR', 'GE', 'GL', 'GR', 'JU', 'LU', 'NE', 'NW', 'OW', 'SG', 'SH', 'SO', 'SZ', 'TG', 'TI','UR', 'VD', 'VS', 'ZG', 'ZH'] #'TI',????

#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi"
LFI_baumartenanteil=pd.read_excel(codeworkspace+"/"+"LFI5_Stammzahl_NaiS-Vegetationshöhenstufen_(6_Klassen)_Hauptbaumart_export.xlsx",  engine='openpyxl', sheet_name='export')
LFI_baumartenanteil['BL']=LFI_baumartenanteil['BLBS']
LFI_baumartenanteil['BS']=LFI_baumartenanteil['BLBS']
LFI_baumartenanteil.dtypes
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
baumartenanteil['FOEanteil']=0
baumartenanteil['ARVanteil']=0
baumartenanteil['ueNHanteil']=0
baumartenanteil['NHanteil']=0

LFI_baumartenanteil['HS'].unique().tolist()
for kanton in kantonelist:
    print(kanton)
    NHanteil=0
    #osa
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Fichte'))][kanton].values)>0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'obersubalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Tanne'))][kanton].values)>0:
        tannenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Lärche'))][kanton].values)>0:
        laerchenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values)>0:
        foehrenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values)>0:
        arvenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values)>0:
        ueNHanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='obersubalpin')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil=0
    NHanteil=fichtenanteil+tannenanteil+laerchenanteil+foehrenanteil+arvenanteil+ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 10)), 'NHanteil'] = NHanteil
    # sa
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'subalpin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='subalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values)>0:
        foehrenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='subalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='subalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values)>0:
        arvenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='subalpin')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='subalpin')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values)>0:
        ueNHanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='subalpin')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil=0
    NHanteil=fichtenanteil+tannenanteil+laerchenanteil+foehrenanteil+arvenanteil+ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 9)), 'NHanteil'] = NHanteil
    # hm
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hochmontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='hochmontan')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values)>0:
        foehrenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='hochmontan')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='hochmontan')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values)>0:
        arvenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='hochmontan')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='hochmontan')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values)>0:
        ueNHanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='hochmontan')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil=0
    NHanteil=fichtenanteil+tannenanteil+laerchenanteil+foehrenanteil+arvenanteil+ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 8)), 'NHanteil'] = NHanteil
    # om
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values)>0:
        foehrenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values)>0:
        arvenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values)>0:
        ueNHanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil=0
    NHanteil=fichtenanteil+tannenanteil+laerchenanteil+foehrenanteil+arvenanteil+ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 6)), 'NHanteil'] = NHanteil
    # um
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values)>0:
        foehrenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values)>0:
        arvenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values)>0:
        ueNHanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='unter- und obermontan')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil=0
    NHanteil=fichtenanteil+tannenanteil+laerchenanteil+foehrenanteil+arvenanteil+ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 5)), 'NHanteil'] = NHanteil
    # sm
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='submontan')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values)>0:
        foehrenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='submontan')&(LFI_baumartenanteil['Hauptbaumart']=='Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='submontan')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values)>0:
        arvenanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='submontan')&(LFI_baumartenanteil['Hauptbaumart']=='Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='submontan')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values)>0:
        ueNHanteil=LFI_baumartenanteil[((LFI_baumartenanteil['HS']=='submontan')&(LFI_baumartenanteil['Hauptbaumart']=='übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil=0
    NHanteil=fichtenanteil+tannenanteil+laerchenanteil+foehrenanteil+arvenanteil+ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 4)), 'NHanteil'] = NHanteil
    # co
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Föhre'))][kanton].values) > 0:
        foehrenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Arve'))][kanton].values) > 0:
        arvenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'übrige Nadelhölzer'))][kanton].values) > 0:
        ueNHanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil = 0
    NHanteil = fichtenanteil + tannenanteil + laerchenanteil + foehrenanteil + arvenanteil + ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 2)), 'NHanteil'] = NHanteil
    # cob
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Föhre'))][kanton].values) > 0:
        foehrenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Arve'))][kanton].values) > 0:
        arvenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'übrige Nadelhölzer'))][kanton].values) > 0:
        ueNHanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'submontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil = 0
    NHanteil = fichtenanteil + tannenanteil + laerchenanteil + foehrenanteil + arvenanteil + ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 3)), 'NHanteil'] = NHanteil
    # hyp
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil=0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Föhre'))][kanton].values) > 0:
        foehrenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Arve'))][kanton].values) > 0:
        arvenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'übrige Nadelhölzer'))][kanton].values) > 0:
        ueNHanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'hyperinsubrisch und kollin') & (LFI_baumartenanteil['Hauptbaumart'] == 'übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil = 0
    NHanteil = fichtenanteil + tannenanteil + laerchenanteil + foehrenanteil + arvenanteil + ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 1)), 'NHanteil'] = NHanteil
    # um/om
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values) > 0:
        fichtenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Fichte'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'FIanteil'] = fichtenanteil
    else:
        fichtenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values) > 0:
        tannenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Tanne'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'TAanteil'] = tannenanteil
    else:
        tannenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values) > 0:
        laerchenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Lärche'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'LAEanteil'] = laerchenanteil
    else:
        laerchenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Föhre'))][kanton].values) > 0:
        foehrenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Föhre'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'FOEanteil'] = foehrenanteil
    else:
        foehrenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Arve'))][kanton].values) > 0:
        arvenanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'Arve'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'ARVanteil'] = arvenanteil
    else:
        arvenanteil = 0
    if len(LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'übrige Nadelhölzer'))][kanton].values) > 0:
        ueNHanteil = LFI_baumartenanteil[((LFI_baumartenanteil['HS'] == 'unter- und obermontan') & (LFI_baumartenanteil['Hauptbaumart'] == 'übrige Nadelhölzer'))][kanton].values[0]
        baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'ueNHanteil'] = ueNHanteil
    else:
        ueNHanteil = 0
    NHanteil = fichtenanteil + tannenanteil + laerchenanteil + foehrenanteil + arvenanteil + ueNHanteil
    baumartenanteil.loc[((baumartenanteil['kanton'] == kanton) & (baumartenanteil['Code'] == 7)), 'NHanteil'] = NHanteil

baumartenanteil['FIantNHant']=baumartenanteil['FIanteil']/baumartenanteil['NHanteil']
baumartenanteil.to_file(projectspace + "/baumartenanteil.gpkg", driver='GPKG')

baumartenanteilFR=baumartenanteil[baumartenanteil['kanton']=='FR']
baumartenanteilFR=baumartenanteilFR[baumartenanteilFR['Code']>0]
baumartenanteilFR.to_file(projectspace + "/FR/baumartenanteilFR.gpkg", driver='GPKG')