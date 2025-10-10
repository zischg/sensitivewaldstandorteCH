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
naismatrixdf=pd.read_excel(codeworkspace+"/"+"Matrix_Baum_inkl_collin_20210412_mit AbkuerzungenCLEAN.xlsx", dtype="str", engine='openpyxl')
projectionswegedf=pd.read_excel(codeworkspace+"/"+"L_Projektionswege_im_Klimawandel_18022020_export.xlsx", dtype="str", engine='openpyxl')
naismatrixstandortelist=joblib.load(projectspace+"/GR/"+"nais_matrix_standorte_list.sav")
len(naismatrixstandortelist)
projektionswegestandortelist=projectionswegedf['Standortstyp_heute'].unique().tolist()
len(projektionswegestandortelist)
schnittmengelist=list(set(naismatrixstandortelist).intersection(set(projektionswegestandortelist)))
len(schnittmengelist)
joblib.dump(schnittmengelist, codeworkspace+"/schnittmenge_standortstypen_list.sav")
joblib.dump(projektionswegestandortelist, codeworkspace+"/projektionswegestandortelist.sav")
joblib.dump(naismatrixstandortelist, codeworkspace+"/naismatrixstandortelist.sav")

#write output
outfile = open(codeworkspace + "/schnittmengelist.txt", "w")
outfile.write("standortstyp\n")
for item in schnittmengelist:
    outfile.write(str(item).replace("'","")+ "\n")
outfile.close()

#write output
outfile = open(codeworkspace + "/projektionswegestandortelist.txt", "w")
outfile.write("standortstyp\n")
for item in projektionswegestandortelist:
    outfile.write(str(item).replace("'","")+ "\n")
outfile.close()

#write output
outfile = open(codeworkspace + "/naismatrixstandortelist.txt", "w")
outfile.write("standortstyp\n")
for item in naismatrixstandortelist:
    outfile.write(str(item).replace("'","")+ "\n")
outfile.close()