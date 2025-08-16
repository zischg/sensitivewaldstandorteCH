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
LFI_baumartenanteil=pd.read_excel(codeworkspace+"/"+"LFI5_Stammzahl_NaiS-Vegetationshöhenstufen_(6_Klassen)_Hauptbaumart_export.xlsx",  engine='openpyxl', sheet_name='export')
LFI_baumartenanteil['BL']=LFI_baumartenanteil['BLBS']
LFI_baumartenanteil['BS']=LFI_baumartenanteil['BLBS']
kantone=gpd.read_file(projectspace+"/kantone.gpkg")
kantone=kantone[['kanton','geometry']]
Tannenareal=gpd.read_file(projectspace+"/Waldstandortregionen_2025.shp")
Tannenareal=Tannenareal[['Code_Ta','geometry']]
hs=gpd.read_file(projectspace+"/vegetationshoehenstufen_1975.gpkg", layer='vegetationshoehenstufen_1975')
hs.columns









