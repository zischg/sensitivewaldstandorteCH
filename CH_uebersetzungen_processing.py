import xlrd
import openpyxl
import pandas as pd
import geopandas as gpd
import numpy as np


# *************************************************************
#environment settings
myworkspace="D:/CCW24sensi"
codespace="C:/DATA/develops/sensitivewaldstandorteCH"

#model parameter file
parameterdf=pd.read_excel(codespace+"/"+"CH_nais_einheiten_unique.xlsx", dtype="str", engine='openpyxl')
parameterdf.columns

#Bereinige JU
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["hoehenstufe1"].isnull()==False)),"NaiS"]=parameterdf["nais1neu"]
#check=parameterdf[((parameterdf["Kanton"]=="JU")&(parameterdf["hoehenstufe1"].isnull()==False))]
parameterdf.loc[((parameterdf["Kanton"]=="JU")),"hoehenstufe1"]=parameterdf["hs1"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["hs1neu"].isnull()==False)),"hoehenstufe1"]=parameterdf["hs1neu"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")),"hsuebergang"]=parameterdf["hsue"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["hsueneu"].isnull()==False)),"hsuebergang"]=parameterdf["hsueneu"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["TreeApp"].isnull()==False)),"NaiS"]=parameterdf["TreeApp"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["Tahs"].isnull()==False)),"hoehenstufe1"]=parameterdf["Tahs"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["naisueneu"].isnull()==False)),"naisue"]=parameterdf["naisueneu"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["TreeApp Uebergang"].isnull()==False)),"naisue"]=parameterdf["TreeApp Uebergang"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["TAUehs"].isnull()==False)),"hsuebergang"]=parameterdf["TAUehs"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["naismosaic neu"].isnull()==False)),"naismosaic"]=parameterdf["naismosaic neu"]
parameterdf.loc[((parameterdf["Kanton"]=="JU")&(parameterdf["hsmo2neu"].isnull()==False)),"hsmo"]=parameterdf["hsmo2neu"]
parameterdf['hsmosaic']=parameterdf['hsmo']
parameterdf=parameterdf[['index', 'Kanton', 'KantonsEInheit', 'KantonsHS', 'Bedingung', 'NaiS','naisue','naismosaic','hoehenstufe1', 'hoehenstufe2', 'hsuebergang', 'hsmosaic','Bemerkungen ']]
parameterdf.to_excel(codespace+"/CH_nais_einheiten_unique2.xlsx")