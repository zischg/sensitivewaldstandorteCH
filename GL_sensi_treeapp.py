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


#*************************************
#functions
def givenexthigheraltitudinalvegetationbelt(in_belt):
    if in_belt=="obersubalpin":
        out_belt="obersubalpin"
    elif in_belt == "subalpin":
        out_belt = "obersubalpin"
    elif "hochmontan" in in_belt:
        out_belt="subalpin"
    elif in_belt=="obermontan":
        out_belt="hochmontan"
    elif in_belt=="untermontan":
        out_belt="obermontan"
    elif in_belt=="submontan":
        out_belt="untermontan"
    elif in_belt=="unter- & obermontan":
        out_belt="hochmontan"
    elif in_belt=="collin":
        out_belt = "submontan"
    elif in_belt=="collin mit Buche":
        out_belt = "submontan"
    elif in_belt=="hyperinsubrisch":
        out_belt = "collin mit Buche"
    return out_belt
def givenextloweraltitudinalvegetationbelt(in_belt, in_standortregion):
    out_belt=in_belt
    if in_belt=="obersubalpin":
        out_belt="subalpin"
    elif in_belt=="subalpin":
        out_belt="hochmontan"
    elif "hochmontan" in in_belt and in_standortregion not in ["5", "5a", "5b", "4", "Me"]:
        out_belt="obermontan"
    elif "hochmontan" in in_belt and in_standortregion in ["5", "5a", "5b", "4", "Me"]:
        out_belt="unter- & obermontan"
    elif in_belt=="obermontan":
        out_belt="untermontan"
    elif in_belt=="untermontan":
        out_belt="submontan"
    elif in_belt in ["unter- & obermontan", "unter-/obermontan"] and in_standortregion in ["5", "5a", "5b", "Me"]:
        out_belt="collin mit Buche"
    elif in_belt in ["unter- & obermontan", "unter-/obermontan"] and in_standortregion in ["2b","3", "4"]:
        out_belt="collin"
    elif in_belt=="submontan" and in_standortregion not in ["2b","3", "4","5", "5a", "5b", "Me"]:
        out_belt="collin mit Buche"
    elif in_belt=="submontan" and in_standortregion in ["2b","3", "4"]:
        out_belt="collin"
    elif in_belt=="collin mit Buche":
        out_belt="hyperinsubrisch"
    elif in_belt=="collin" and in_standortregion in ["5", "5a", "5b", "Me"]:
        out_belt="hyperinsubrisch"
    elif in_belt=="hyperinsubrisch":
        out_belt="hyperinsubrisch"
    return out_belt
def give_standortregionencombi_from_projektionspfade(in_Standortregion):
    if in_Standortregion in ["1","J","M","2","2a","2b","3"]:# and in_hoehenstufe != "collin":
        out_combi="R, J, M, 1, 2, 3"
    #elif in_Standortregion in ["1","J","M","2","2a","2b","3"]:# and in_hoehenstufe == "collin":
        #out_combi = "R J, M,1, 2 Beginn co "
    elif in_Standortregion == "4":
        out_combi = "R 4"
    elif in_Standortregion in ["5","5a","5b"]:
        out_combi = "R 5"
    elif in_Standortregion == "Me":
        out_combi = "R Mendrisiotto"
    else:
        out_combi=""
    return out_combi
def give_future_foresttype_from_projectionspathways(sto_heute,hs_heute,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion,instandortregionplain,inslope,inlage, inradiation):
    #create a  query from projections pathways
    sto_zukunft = ""
    #if intannenareal_heute ==
    if hs_heute==hs_zukunft:
        sto_zukunft=sto_heute
    else:
        if [instandortregion,sto_heute,hs_heute,hs_zukunft] in pairsofforesttypesandaltitudinalvegetationbelts_inprojektionspfade:
            query_possiblepathways=projectionswegedf[((projectionswegedf["Standortstyp_heute"]==sto_heute) & (projectionswegedf["Standortsregionen"]==instandortregion))]
            if "hochmontan" in hs_zukunft:
                query_possiblepathwayszukunft=query_possiblepathways[query_possiblepathways["Hoehenstufe_Zukunft"].isin([hs_zukunft,"hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne"])]
            else:
                query_possiblepathwayszukunft = query_possiblepathways[query_possiblepathways["Hoehenstufe_Zukunft"] == hs_zukunft]
            if len(query_possiblepathwayszukunft)==0:
                sto_zukunft="nopath"
            elif len(query_possiblepathwayszukunft)==1:
                sto_zukunft=query_possiblepathwayszukunft["Standortstyp_Zukunft"].tolist()[0]
            else:
                #check conditions
                # tannenareal
                # hochmontan
                if "hochmontan" in query_possiblepathwayszukunft["Standortstyp_Zukunft"].unique().tolist():
                    if intannenareal_zukunft == 1:
                        query_possiblepathwayszukunft1 = query_possiblepathwayszukunft[(
                                    (query_possiblepathwayszukunft["Hoehenstufe_Zukunft"] == "hochmontan") & (
                                        query_possiblepathwayszukunft[
                                            "Tannenareal_Zukunft"] == "Hauptareal"))]  # Hauptareal der Tanne"]
                    elif intannenareal_zukunft == 2:
                        query_possiblepathwayszukunft1 = query_possiblepathwayszukunft[(
                                    (query_possiblepathwayszukunft["Hoehenstufe_Zukunft"] == "hochmontan") & (
                                        query_possiblepathwayszukunft[
                                            "Tannenareal_Zukunft"] == "Nebenareal"))]  # Nebenareal der Tanne"]
                    elif intannenareal_zukunft == 3:
                        query_possiblepathwayszukunft1 = query_possiblepathwayszukunft[(
                                    (query_possiblepathwayszukunft["Hoehenstufe_Zukunft"] == "hochmontan") & (
                                        query_possiblepathwayszukunft[
                                            "Tannenareal_Zukunft"] == "Reliktareal"))]  # Reliktareal der Tanne"]
                else:
                    query_possiblepathwayszukunft1=query_possiblepathwayszukunft
                if len(query_possiblepathwayszukunft1) == 0:
                    sto_zukunft = "no path"
                elif len(query_possiblepathwayszukunft1) == 1:
                    sto_zukunft = query_possiblepathwayszukunft1["Standortstyp_Zukunft"].tolist()[0]
                else:
                # Standortregion
                    if len(query_possiblepathwayszukunft1["Standortsregion"].unique().tolist()) > 1:
                        if instandortregionplain == "3":
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(['2b, 3', '3', '1, 2, 3'])]
                        elif instandortregionplain == "2a":
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(
                                    ['M, J, 1, 2a', '1, 2, 3', 'J, M, 1, 2a'])]
                        elif instandortregionplain == "2b":
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(['2b, 3', '2b', '1, 2, 3'])]
                        elif instandortregionplain in ['M', 'J']:
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(
                                    ['M, J, 1, 2a', 'J, M', 'J, M, 1, 2a'])]
                        elif instandortregionplain == '1':
                            query_possiblepathwayszukunft2= query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(
                                    ['M, J, 1, 2a', 'J, M, 1, 2a', '1, 2, 3'])]
                        else:
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft1
                    else:
                        query_possiblepathwayszukunft2=query_possiblepathwayszukunft1
                    if len(query_possiblepathwayszukunft2) == 0:
                        sto_zukunft = "no path"
                    elif len(query_possiblepathwayszukunft2) == 1:
                        sto_zukunft = query_possiblepathwayszukunft2["Standortstyp_Zukunft"].tolist()[0]
                    else:
                        #inslope
                        inslopeconditions =query_possiblepathwayszukunft2["Hangneigung"].unique().tolist()
                        if len(inslopeconditions)>1 and inslope in inslopeconditions:
                            query_possiblepathwayszukunft3 = query_possiblepathwayszukunft2[query_possiblepathwayszukunft2["Hangneigung"] == inslope]
                        else:
                            query_possiblepathwayszukunft3=query_possiblepathwayszukunft2
                        if len(query_possiblepathwayszukunft3) == 0:
                            sto_zukunft = "no path"
                        elif len(query_possiblepathwayszukunft3) == 1:
                            sto_zukunft = query_possiblepathwayszukunft3["Standortstyp_Zukunft"].tolist()[0]
                        else:
                            #inlage
                            if len(query_possiblepathwayszukunft3["Relief"].unique().tolist())>1 and inlage ==2:
                                query_possiblepathwayszukunft4 = query_possiblepathwayszukunft3[query_possiblepathwayszukunft3["Relief"] == 'Hang- und Muldenlage']
                            elif len(query_possiblepathwayszukunft3["Relief"].unique().tolist())>1 and inlage ==3:
                                query_possiblepathwayszukunft4 = query_possiblepathwayszukunft3[query_possiblepathwayszukunft3["Relief"].isin(['Hang- oder Muldenlage','Hang- und Muldenlage'])]
                            elif len(query_possiblepathwayszukunft3["Relief"].unique().tolist())>1 and inlage ==4:
                                query_possiblepathwayszukunft4 = query_possiblepathwayszukunft3[query_possiblepathwayszukunft3["Relief"] == 'Kuppenlage']
                            else:
                                query_possiblepathwayszukunft4=query_possiblepathwayszukunft3
                            if len(query_possiblepathwayszukunft4) == 0:
                                sto_zukunft = "no path"
                            elif len(query_possiblepathwayszukunft4) == 1:
                                sto_zukunft = query_possiblepathwayszukunft4["Standortstyp_Zukunft"].tolist()[0]
                            else:
                                # Weitere (inradiation)
                                if len(query_possiblepathwayszukunft4["Weitere"].unique().tolist()) > 1:
                                    if inradiation == "-1":
                                        query_possiblepathwayszukunft5 = query_possiblepathwayszukunft4[query_possiblepathwayszukunft4["Weitere"].isin(['schattig, kühl','kühl'])]
                                    elif inradiation == "1":
                                        query_possiblepathwayszukunft5 = query_possiblepathwayszukunft4[query_possiblepathwayszukunft4["Standortsregion"].isin(['warm','warm und strahlungsreich'])]
                                    elif inradiation == "0":
                                        query_possiblepathwayszukunft5 = query_possiblepathwayszukunft4[query_possiblepathwayszukunft4["Standortsregion"].isin([nan,"","normal", " "])]
                                    else:
                                        query_possiblepathwayszukunft5 = query_possiblepathwayszukunft4
                                else:
                                    query_possiblepathwayszukunft5=query_possiblepathwayszukunft4
                                if len(query_possiblepathwayszukunft5) == 0:
                                    sto_zukunft = "no path"
                                elif len(query_possiblepathwayszukunft5) >= 1:
                                    sto_zukunft = query_possiblepathwayszukunft5["Standortstyp_Zukunft"].tolist()[0]
    return sto_zukunft
def count_changes_altitudinalvegetationbelts(hs_in, hs_out):
    count=0
    if hs_in==hs_out:
        count=0
    elif "hochmontan" in hs_in and "hochmontan" in hs_out:
        count =0
    elif hs_in == 'obersubalpin' and hs_out!=hs_in:
        if hs_out=="subalpin":
            count=1
        elif hs_out in ["hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
            count=2
        elif hs_out in ["obermontan","unter-/obermontan", "unter- & obermontan"]:
            count=3
        elif hs_out in ["untermontan"]:
            count=4
        elif hs_out in ["submontan"]:
            count=5
        elif hs_out in ["collin", "collin mit Buche"]:
            count=6
        elif hs_out in ["hyperinsubrisch"]:
            count=7
        elif hs_out in ["mediterran"]:
            count=8
    elif hs_in == 'subalpin' and hs_out!=hs_in:
        if hs_out in ["hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
            count=1
        elif hs_out in ["obermontan","unter-/obermontan", "unter- & obermontan"]:
            count=2
        elif hs_out in ["untermontan"]:
            count=3
        elif hs_out in ["submontan"]:
            count=4
        elif hs_out in ["collin", "collin mit Buche"]:
            count=5
        elif hs_out in ["hyperinsubrisch"]:
            count=6
        elif hs_out in ["mediterran"]:
            count=7
    elif  hs_out!=hs_in and hs_in in ["hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        if hs_out in ["obermontan","unter-/obermontan", "unter- & obermontan"]:
            count=1
        elif hs_out in ["untermontan"]:
            count=2
        elif hs_out in ["submontan"]:
            count=3
        elif hs_out in ["collin", "collin mit Buche"]:
            count=4
        elif hs_out in ["hyperinsubrisch"]:
            count=5
        elif hs_out in ["mediterran"]:
            count=6
    elif hs_in == "obermontan" and hs_out!=hs_in:
        if hs_out in ["untermontan"]:
            count=1
        elif hs_out in ["submontan"]:
            count=2
        elif hs_out in ["collin", "collin mit Buche"]:
            count=3
        elif hs_out in ["hyperinsubrisch"]:
            count=4
        elif hs_out in ["mediterran"]:
            count=5
    elif hs_in in ["unter-/obermontan", "unter- & obermontan"] and hs_out!=hs_in:
        if hs_out in ["submontan"]:
            count=1
        elif hs_out in ["collin", "collin mit Buche","hyperinsubrisch"]:
            count=1
        elif hs_out in ["mediterran"]:
            count=2
    elif hs_in== "untermontan" and hs_out!=hs_in:
        if hs_out in ["submontan"]:
            count=1
        elif hs_out in ["collin", "collin mit Buche"]:
            count=2
        elif hs_out in ["hyperinsubrisch"]:
            count=3
        elif hs_out in ["mediterran"]:
            count=4
    elif hs_in == "submontan" and hs_out!=hs_in:
        if hs_out in ["collin", "collin mit Buche"]:
            count=1
        elif hs_out in ["hyperinsubrisch"]:
            count=2
        elif hs_out in ["mediterran"]:
            count=3
    elif hs_in =="collin mit Buche" and hs_out!=hs_in:
        if hs_out in ["hyperinsubrisch"]:
            count=1
        elif hs_out in ["mediterran"]:
            count=2
        elif "collin" in hs_out:
            count=0
    elif hs_in == "collin" and hs_out!=hs_in:
        if hs_out in ["mediterran"]:
            count=1
    else:
        count=0
    return count
def is_hszukunft_higherthan_hsheute(hsheute,hszukunft):
    if hsheute=="subalpin" and hszukunft=="obersubalpin":
        out=True
    elif "hochmontan" in hsheute and hszukunft in ["subalpin","obersubalpin"]:
        out=True
    elif "obermontan" in hsheute and hszukunft in ["subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    elif "unter" in hsheute and hszukunft in ["obermontan","subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    elif "submontan" in hsheute and hszukunft in ["unter-/obermontan","unter- & obermontan","untermontan","obermontan","subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    elif "collin" in hsheute and hszukunft in ["submontan","unter-/obermontan","unter- & obermontan","untermontan","obermontan","subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    elif "hyperinsubrisch" in hsheute and hszukunft in ["collin", "collin mit Buche","submontan","unter-/obermontan","unter- & obermontan","untermontan","obermontan","subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    else:
        out=False
def concatenate_pathways(sto_heute, hs_heute, hs_zukunft, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope, inlage, inradiation):
    if count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 1:
        outnais=give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hs_zukunft, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope, inlage, inradiation)
    elif hs_heute =="obersubalpin" and hs_zukunft=="collin" and instandortregionplain in ["2b","3","4"]:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,
                                                                            intannenareal_heute, intannenareal_zukunft,
                                                                            instandortregion, instandortregionplain,
                                                                            inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1,
                                                                            hsintermediary2, intannenareal_heute,
                                                                            intannenareal_zukunft, instandortregion,
                                                                            instandortregionplain, inslope, inlage,
                                                                            inradiation)
        if naisintermediary2 in hochmontandirektzucollinlist:
            outnais = give_future_foresttype_from_projectionspathways(naisintermediary2, hsintermediary2, hs_zukunft,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregionplain in ["2b","3","4"]:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,
                                                                            intannenareal_heute, intannenareal_zukunft,
                                                                            instandortregion, instandortregionplain,
                                                                            inslope, inlage, inradiation)
        outnais = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hs_zukunft,
                                                                  intannenareal_heute, intannenareal_zukunft,
                                                                  instandortregion, instandortregionplain, inslope,
                                                                  inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 2:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary1,hsintermediary1,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 3:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hsintermediary2,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary2,hsintermediary2,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 4:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hsintermediary2,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary3 = givenextloweraltitudinalvegetationbelt(hsintermediary2, instandortregion)
        naisintermediary3 = give_future_foresttype_from_projectionspathways(naisintermediary2, hsintermediary2,hsintermediary3, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary3,hsintermediary3,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 5:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hsintermediary2,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary3 = givenextloweraltitudinalvegetationbelt(hsintermediary2, instandortregion)
        naisintermediary3 = give_future_foresttype_from_projectionspathways(naisintermediary2, hsintermediary2,hsintermediary3, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        hsintermediary4 = givenextloweraltitudinalvegetationbelt(hsintermediary3, instandortregion)
        naisintermediary4 = give_future_foresttype_from_projectionspathways(naisintermediary3, hsintermediary3,hsintermediary4, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary4,hsintermediary4,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 6:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hsintermediary2,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary3 = givenextloweraltitudinalvegetationbelt(hsintermediary2, instandortregion)
        naisintermediary3 = give_future_foresttype_from_projectionspathways(naisintermediary2, hsintermediary2,hsintermediary3, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        hsintermediary4 = givenextloweraltitudinalvegetationbelt(hsintermediary3, instandortregion)
        naisintermediary4 = give_future_foresttype_from_projectionspathways(naisintermediary3, hsintermediary3,hsintermediary4, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        hsintermediary5 = givenextloweraltitudinalvegetationbelt(hsintermediary4, instandortregion)
        naisintermediary5 = give_future_foresttype_from_projectionspathways(naisintermediary4, hsintermediary4,hsintermediary5, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary5,hsintermediary5,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    else:
        outnais="no path c"
    return outnais
def correct_nopaths_exemptions(instandortregion,instandortregionplain,sto_heute,hs_heute,hs_zukunft, codetannenareal, inslope, inlage, inradiation):
    #correct combinations with no paths
    nais_zukunft_out= "no path"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25as', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '42Q', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '33m', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '4', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="3L/4L"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25a', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="25a med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '32V', 'collin mit Buche', 'collin']:
        nais_zukunft_out="32C"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '42Q', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="42Q med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '42C', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="42C med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '33m', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="33m med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '40P', 'collin mit Buche', 'collin']:
        nais_zukunft_out="40Pt"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25au', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="25au med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25au', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25as', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="25as med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '33V', 'collin mit Buche', 'collin']:
        nais_zukunft_out="3L/4L"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '42C', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '4', 'collin mit Buche', 'collin']:
        nais_zukunft_out="3L/4L"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25a', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '32C', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '3', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="42V med"
    if instandortregion in ["R 5", "R 4", "R Mendrisiotto"] and hs_heute in ["collin","collin mit Buche", "hyperinsubrisch"] and hs_zukunft=="mediterran" and sto_heute in ["3","4","47","19LP","25a","25as""25au","32*","32V","33m","33V","40P","42C","42Q"]:
        nais_zukunft_out = sto_heute+" med"
    if instandortregion in ["R 5", "R 4", "R Mendrisiotto"] and hs_heute in ["collin","collin mit Buche", "hyperinsubrisch"] and hs_zukunft=="mediterran" and sto_heute2 in ["3","4","47","19LP","25a","25as""25au","32*","32V","33m","33V","40P","42C","42Q"]:
        combinations_df.loc[index, "naiszuk2"] = sto_heute2+" med"
    if instandortregion =="R, J, M, 1, 2, 3" and hs_heute =="submontan" and hs_zukunft=="collin" and sto_heute in ["18","19","20","51","52","18*","18M","18v","18w","1h","24*","27h","32*","32V","53*"]:
        nais_zukunft_out = sto_heute+" med"
    if instandortregion =="R, J, M, 1, 2, 3" and hs_heute =="submontan" and hs_zukunft=="collin" and sto_heute2 in ["18","19","20","51","52","18*","18M","18v","18w","1h","24*","27h","32*","32V","53*"]:
        combinations_df.loc[index, "naiszuk2"] = sto_heute2+" med"
    #AV
    if sto_heute=="AV" and hs_zukunft in ["collin mit Buche","hyperinsubrisch"]:
        nais_zukunft_out = "25au"
    if sto_heute=="AV" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "50 collin"
    if sto_heute=="AV" and hs_zukunft =="collin" and instandortregion in ["R 4", "R 5"]:
        nais_zukunft_out = "25au"
    if sto_heute=="AV" and hs_zukunft in ["unter- & obermontan"]:
        nais_zukunft_out = "25au"
    if sto_heute=="AV" and hs_zukunft in ["hochmontan, subalpin"]:
        nais_zukunft_out = "AV"
    if sto_heute=="AV" and hs_heute=="subalpin" and hs_zukunft == "hochmontan":
        nais_zukunft_out = "50"
    if sto_heute=="AV" and hs_heute=="obersubalpin" and hs_zukunft == "hochmontan":
        nais_zukunft_out = "47D"
    #N
    if sto_heute=="19L" and hs_heute == "obermontan" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "3"
    if sto_heute=="10a" and hs_heute == "untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "10a"
    if sto_heute=="10a" and hs_heute == "untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "10a collin"
    if sto_heute=="23" and hs_heute in ["hochmontan", "obermontan"] and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "23 collin"
    if sto_heute=="23" and hs_heute in ["hochmontan", "obermontan"] and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "25* collin"
    if sto_heute=="40*" and hs_heute == "obersubalpin" and hs_zukunft=="hochmontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute=="47" and hs_heute =="obermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "42t"
    if sto_heute=="47" and hs_heute =="obermontan" and hs_zukunft =="collin mit Buche" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "42t"
    if sto_heute=="47" and hs_heute =="obermontan" and hs_zukunft =="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "47"
    if sto_heute=="47" and hs_heute =="obermontan" and hs_zukunft =="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "47"
    if sto_heute=="51" and hs_heute in ["hochmontan", "obermontan"] and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "51 collin"
    if sto_heute=="51" and hs_heute =="hochmontan" and hs_zukunft in ["submontan","untermontan", "unter- & obermontan"] and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="51" and hs_heute =="hochmontan" and hs_zukunft =="obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18"
    if sto_heute=="51" and hs_heute =="untermontan" and hs_zukunft =="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="52" and hs_heute =="untermontan" and hs_zukunft =="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18*"
    if sto_heute=="52" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "52 collin"
    if sto_heute=="52" and hs_heute =="obermontan" and hs_zukunft =="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute=="52" and hs_heute =="obermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14 collin"
    if sto_heute=="53" and hs_heute =="subalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "62 collin"
    if sto_heute=="65" and hs_heute =="obermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute=="19L" and hs_heute =="obermontan" and hs_zukunft =="collin mit Buche" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "3L/4L"
    if sto_heute=="29A" and hs_heute =="obermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "29A collin"
    if sto_heute=="41*" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "41* collin"
    if sto_heute=="46M" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "46M collin"
    if sto_heute=="50P" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7S collin"
    if sto_heute=="53*" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34b"
    if sto_heute=="53*" and hs_heute =="untermontan" and hs_zukunft =="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute=="53VM" and hs_heute =="subalpin" and hs_zukunft in ["untermontan", "unter- & obermontan", "submontan"] and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "19L"
    if sto_heute=="53VM" and hs_heute =="subalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34a"
    if sto_heute=="58Bl" and hs_heute =="subalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "47H collin"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft =="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "1"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "1 collin"
    if sto_heute=="59C" and hs_heute =="obersubalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34* collin"
    if sto_heute=="60A" and hs_heute =="subalpin" and hs_zukunft =="collin mit Buche" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "50 collin"
    if sto_heute=="51C" and hs_heute in ["hochmontan", "obermontan"] and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "51 collin"
    if sto_heute=="51Re" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "51 collin"
    if sto_heute=="53*" and hs_heute in ["hochmontan", "obermontan", "untermontan"] and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "53* collin"
    if sto_heute=="56" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "45 collin"
    if sto_heute=="56" and hs_heute =="hochmontan" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute=="65" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "68 collin"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "41* collin"
    if sto_heute=="25*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "25* collin"
    if sto_heute=="29A" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "29A collin"
    if sto_heute=="32C" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "32C collin"
    if sto_heute=="32C" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "28 collin"
    if sto_heute=="32V" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "32C collin"
    if sto_heute=="32V" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "32C"
    if sto_heute=="40*" and hs_heute in ["obersubalpin", "untermontan"] and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute=="59" and hs_heute =="obersubalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "19a"
    if sto_heute=="32S" and hs_heute =="subalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "28"
    if sto_heute=="32S" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "28 collin"
    if sto_heute=="40PBl" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "40PBl collin"
    if sto_heute=="40PBl" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "34* collin"
    if sto_heute=="41*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "41* collin"
    if sto_heute=="46M" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "1h"
    if sto_heute=="50P" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "20"
    if sto_heute=="51Re" and hs_heute =="hochmontan" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3" and codetannenareal in [0,1,2]:
        nais_zukunft_out = "51"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3" and codetannenareal==3:
        nais_zukunft_out = "54A"
    if sto_heute=="49*" and hs_heute =="subalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "26h"
    if sto_heute=="49*Ta" and hs_heute =="hochmontan" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "26h"
    if sto_heute=="59H" and hs_heute =="subalpin" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18"
    if sto_heute=="59H" and hs_heute =="obersubalpin" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18"
    if sto_heute=="60A" and hs_heute =="subalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "20"
    if sto_heute=="51" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "51 collin"
    if sto_heute=="51" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "7a collin"
    if sto_heute=="53" and hs_heute in ["obermontan", "untermontan"] and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "62"
    if sto_heute=="29A" and hs_heute =="obermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "29A collin"
    if sto_heute=="51C" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a"
    if sto_heute=="51Re" and hs_heute =="hochmontan" and hs_zukunft=="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="51Re" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            if tannenareal_heute== 3:
                nais_zukunft_out = "54A collin"
            else:
                nais_zukunft_out = "51 collin"
        else:
            nais_zukunft_out = "7a collin"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "55* collin"
    if sto_heute=="60*Ta" and hs_heute =="obermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute=="19" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "6"
    if sto_heute=="19" and hs_heute in ["hochmontan"] and hs_zukunft in ["collin"] and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "6 collin"
    if sto_heute=="19" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "6 collin"
    if sto_heute=="19" and hs_heute =="hochmontan" and hs_zukunft=="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8d"
    if sto_heute=="55*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            nais_zukunft_out = "55* collin"
        else:
            nais_zukunft_out = "1 collin"
    if sto_heute=="55*" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "1"
    if sto_heute=="47Re" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "25a"
    if sto_heute=="18*" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute=="18*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14 collin"
    if sto_heute=="18*" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute=="18*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14 collin"
    if sto_heute=="50*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "50* collin"
        else:
            nais_zukunft_out = "9a collin"
    if sto_heute=="57C" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"] and codetannenareal in [1,2]:
            nais_zukunft_out = "51 collin"
        elif instandortregionplain in ["2b","3"] and codetannenareal==3:
            nais_zukunft_out = "55 collin"
    if sto_heute=="53*s" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            nais_zukunft_out = "53* collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute=="59A" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if codetannenareal==3:
            if instandortregionplain in ["2b","3"]:
                nais_zukunft_out = "50 collin"
            else:
                nais_zukunft_out = "7S collin"
        else:
            if instandortregionplain in ["2b", "3"]:
                nais_zukunft_out = "50 collin"
            else:
                nais_zukunft_out = "7S collin"
    if sto_heute=="59A" and hs_heute =="subalpin" and hs_zukunft=="hochmontan" and instandortregion =="R, J, M, 1, 2, 3":
        if codetannenareal==3:
            nais_zukunft_out = "50Re"
        else:
            nais_zukunft_out = "50"
    if sto_heute=="40*" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute=="40*" and hs_heute =="obermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute=="40*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute=="40*" and hs_heute =="obermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute=="53*" and hs_heute =="obermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if codetannenareal == 3:
            nais_zukunft_out = "53* collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute=="53*" and hs_heute =="submontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if codetannenareal == 3:
            nais_zukunft_out = "53* collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute=="53*" and hs_heute =="obermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute=="53*" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute=="69" and hs_heute in ["obermontan", "untermontan"] and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["J", "M"]:
            nais_zukunft_out = "38"
        else:
            nais_zukunft_out = "40*"
    if sto_heute=="69" and hs_heute in ["obermontan", "untermontan"] and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute=="59E" and hs_heute =="obersubalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "53Ta"
    if sto_heute=="59H" and hs_heute =="obersubalpin" and hs_zukunft=="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="59H" and hs_heute =="obersubalpin" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a"
    if sto_heute=="59H" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a collin"
    if sto_heute=="59H" and hs_heute in ["obersubalpin","hochmontan"] and hs_zukunft in ["collin","submontan","untermontan"] and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain in ["2b","3"]:
        if tannenareal_heute in [1,2]:
            nais_zukunft_out = "51 collin"
        else:
            nais_zukunft_out = "54A collin"
    if sto_heute=="59R" and hs_heute =="obersubalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34* collin"
    if sto_heute=="59R" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34* collin"
    if sto_heute=="67*" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "38 collin"
    if sto_heute == "53*s" and hs_heute == "subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "53* collin"
    if sto_heute == "59E" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "53* collin"
    if sto_heute == "10a" and hs_heute == "untermontan" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "10a"
    if sto_heute == "47" and hs_heute == "obermontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "3"
    if sto_heute=="32*" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "32* collin"
        else:
            nais_zukunft_out = "26 collin"
    if sto_heute == "19" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "6 collin"
    if sto_heute == "47Re" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "25a"
    if sto_heute == "18*" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute == "18*" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute == "57C" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if codetannenareal == 3:
            nais_zukunft_out = "55 collin"
        else:
            nais_zukunft_out = "51 collin"
    if sto_heute == "59A" and hs_heute == "subalpin" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        if codetannenareal == 3:
            nais_zukunft_out = "50Re"
        else:
            nais_zukunft_out = "50"
    if sto_heute == "40*" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute == "53*" and hs_heute == "untermontan" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute == "53*" and hs_heute == "submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "53* collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute == "69" and hs_heute == "submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute == "69" and hs_heute == "untermontan" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "38"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '10a', 'untermontan', 'submontan']:
        nais_zukunft_out='10a'
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '47', 'obermontan', 'untermontan']:
        nais_zukunft_out='3'
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '19', 'hochmontan', 'collin']:
        nais_zukunft_out='6 collin'
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '69', 'submontan', 'collin']:
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "62 collin"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '69', 'untermontan', 'submontan']:
        nais_zukunft_out = "38"
    #***************************
    #S
    if sto_heute=="24" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="24" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="25a" and hs_heute =="hyperinsubrisch" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="32*" and hs_heute =="collin mit Buche" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "27"
    if sto_heute=="32V" and hs_heute =="collin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "32C"
    if sto_heute=="32V" and hs_heute =="collin mit Buche" and hs_zukunft=="hyperinsubrisch" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "32C"
    if sto_heute=="42C" and hs_heute =="obersubalpin" and hs_zukunft=="subalpin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42C"
    if sto_heute=="47" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="47" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="47" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a med"
    if sto_heute=="56" and hs_heute == "hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "27"
    if sto_heute=="56" and hs_heute == "subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "27"
    if sto_heute=="58" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="58" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42C"
    if sto_heute=="59" and hs_heute =="obersubalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42V"
    if sto_heute=="59*" and hs_heute =="obersubalpin" and hs_zukunft=="subalpin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "47*"
    if sto_heute=="AV" and hs_heute =="obersubalpin" and hs_zukunft=="subalpin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "AV"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42r"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42r"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42r med"
    if sto_heute=="60" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="60" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="19LP" and hs_heute =="unter- & obermontan" and hs_zukunft=="submontan" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "19LP"
    if sto_heute=="25a" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="25as" and hs_heute =="collin" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as med"
    if sto_heute=="25as" and hs_heute =="collin mit Buche" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as med"
    if sto_heute=="25au" and hs_heute =="collin mit Buche" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au med"
    if sto_heute=="25au" and hs_heute =="collin" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au med"
    if sto_heute=="32*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "27"
    if sto_heute=="32C" and hs_heute =="collin" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "32C med"
    if sto_heute=="32C" and hs_heute =="collin mit Buche" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "32C med"
    if sto_heute=="32V" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "28 med"
    if sto_heute=="33V" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "33m"
    if sto_heute=="40P" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "40Pt"
    if sto_heute=="40P" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "40P med"
    if sto_heute=="42C" and hs_heute =="obersubalpin" and hs_zukunft=="hochmontan" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42C"
    if sto_heute=="47*" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3LV"
    if sto_heute=="47*" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3LV"
    if sto_heute=="47*" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="47*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "33a"
    if sto_heute=="47D" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="47D" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="47D" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="47DRe" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="47H" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as"
    if sto_heute=="47H" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as"
    if sto_heute=="47H" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as med"
    if sto_heute=="47M" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "34a"
    if sto_heute=="47Re" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="50*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25b"
    if sto_heute=="55*" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q med"
    if sto_heute=="57Bl" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="57Bl" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="57C" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="57C" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="57C" and hs_heute =="obersubalpin" and hs_zukunft=="unter- & obermontan" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "19a"
    if sto_heute=="57V" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="57V" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="58Bl" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as"
    if sto_heute=="58Bl" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="58C" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="58C" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="59*" and hs_heute =="obersubalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3a"
    if sto_heute=="59*" and hs_heute =="obersubalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="59*" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3a"
    if sto_heute=="59*" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="59*" and hs_heute =="obersubalpin" and hs_zukunft=="unter- & obermontan" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "4"
    if sto_heute=="60A" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="60A" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="57V" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4"]:
        nais_zukunft_out = "42V"
    if sto_heute=="57V" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 5"]:
        nais_zukunft_out = "42t"
    if sto_heute == "46M" and hs_heute in ["hochmontan", "collin mit Buche"] and hs_zukunft == "mediterran" and instandortregion == "R 5":
        nais_zukunft_out = "42V med"
    if sto_heute == "46M" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R 5":
        nais_zukunft_out = "42V"
    if sto_heute == "46M" and hs_heute =="hochmontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R 5":
        nais_zukunft_out = "42V"
    if sto_heute == "46M" and hs_heute =="hochmontan" and hs_zukunft == "unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "3"
    if sto_heute == "46M" and hs_heute =="unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 5":
        nais_zukunft_out = "42V"
    if sto_heute == "42Q" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R 5":
        nais_zukunft_out = "42Q"
    if sto_heute == "42Q" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    #
    if sto_heute == "24" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25a"
    if sto_heute == "25a" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25a"
    if sto_heute == "25a" and hs_heute =="hochmontan" and hs_zukunft == "mediterran" and instandortregion == "R 4":
        nais_zukunft_out = "25a"
    if sto_heute == "58" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "55* collin"
    if sto_heute == "58Bl" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25as"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "59" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        if inslope >=3:#57C
            if codetannenareal<=2:#47M
                nais_zukunft_out = "34a"
            else:
                nais_zukunft_out = "34a"
        else:#57V
            nais_zukunft_out = "42V"
    if sto_heute == "70" and hs_heute in ["obersubalpin", "subalpin"] and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "70" and hs_heute in ["obersubalpin", "subalpin"] and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "71" and hs_heute in ["obersubalpin", "subalpin"] and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "47*Lä" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "48 collin"
    if sto_heute == "AV" and hs_heute in ["obersubalpin"] and hs_zukunft in ["untermontan", "obermontan"] and instandortregion == "R 4":
        nais_zukunft_out = "AV"
    if sto_heute == "32C" and hs_heute in ["hyperinsubrisch"] and hs_zukunft =="collin" and instandortregion == "R 5":
        nais_zukunft_out = "32C collin"
    if sto_heute == "33m" and hs_heute in ["hyperinsubrisch"] and hs_zukunft =="collin" and instandortregion == "R 5":
        nais_zukunft_out = "33m"
    if sto_heute == "42C" and hs_heute in ["hyperinsubrisch"] and hs_zukunft =="collin" and instandortregion == "R 5":
        nais_zukunft_out = "42C"
    if sto_heute == "47*" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "4"
    if sto_heute == "57Bl" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "24*"
    if sto_heute == "57C" and hs_heute =="obersubalpin" and hs_zukunft in ["collin", "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "3L/4L"
    if sto_heute == "57V" and hs_heute =="obersubalpin" and hs_zukunft in ["collin", "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "3L/4L"
    if sto_heute == "57V" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "19a"
    if sto_heute == "58" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "3s"
    if sto_heute == "58Bl" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "47H"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft in ["collin", "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "42Q"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "3s"
    if sto_heute == "70" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "68"
    if sto_heute == "70" and hs_heute =="subalpin" and hs_zukunft in ["collin", "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "42r"
    if sto_heute == "16" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["J","M"]:
            nais_zukunft_out = "39 collin"
        elif instandortregionplain in ["1","2a", "2b","3"]:
            nais_zukunft_out = "40* collin"
        else:
            nais_zukunft_out = "25e collin"
    if sto_heute == "32V" and hs_heute =="obermontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "28 collin"
    if sto_heute == "40*" and hs_heute =="submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute == "41*" and hs_heute =="submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "41* collin"
    if sto_heute == "47H" and hs_heute =="obermontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "25as"
    if sto_heute == "56" and hs_heute =="obermontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["J", "M", "2a", "1"]:
            nais_zukunft_out = "45"
        else:
            nais_zukunft_out = "45"
    if sto_heute == "57S" and hs_heute =="subalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if inslope>=2:
            nais_zukunft_out = "46"
        else:
            nais_zukunft_out = "46*"
    if sto_heute == "57V" and hs_heute =="subalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if inslope>=2:
            nais_zukunft_out = "19"
        else:
            nais_zukunft_out = "46"
    if sto_heute == "58" and hs_heute =="subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "1h"
    if sto_heute == "59" and hs_heute =="obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            nais_zukunft_out = "48 collin"
        else:
            nais_zukunft_out = "22 collin"
    if sto_heute == "59H" and hs_heute =="obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if codetannenareal <= 2:
            if inlage == 4:
                nais_zukunft_out = "19"
            else:
                nais_zukunft_out = "18"
        else:
            nais_zukunft_out = "18"
    if sto_heute == "60" and hs_heute =="subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "20"
    if sto_heute == "67" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "67" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "69" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "69" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "70" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "70" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "71" and hs_heute =="subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "71"
    if sto_heute == "71" and hs_heute =="obermontan" and hs_zukunft == "mediterran" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute == "18w" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["J","M","1","2a"]:
            nais_zukunft_out = "17 collin"
        else:
            nais_zukunft_out = "17"
    if sto_heute == "18w" and hs_heute =="hochmontan" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "18w" and hs_heute =="subalpin" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "32*" and hs_heute =="subalpin" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "32*"
    if sto_heute == "40*" and hs_heute =="submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute == "46M" and hs_heute =="obermontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "46M collin"
        else:
            nais_zukunft_out = "1 collin"
    if sto_heute == "58LLä" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "55* collin"
        else:
            nais_zukunft_out = "1 collin"
    if sto_heute == "58LLä" and hs_heute =="obersubalpin" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "55*Lä"
    if sto_heute == "60*Ta" and hs_heute =="obermontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "67G" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "67G" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "69G" and hs_heute in ["subalpin","obersubalpin"] and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            if instandortregionplain in ["J", "M"]:
                nais_zukunft_out = "38 collin"
            else:
                nais_zukunft_out = "40* collin"
    if sto_heute == "70G" and hs_heute in ["subalpin","obersubalpin"] and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "71G" and hs_heute == "obermontan" and hs_zukunft == "mediterran" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45 collin"
    if sto_heute == "71G" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "71G"
    if sto_heute == "59A" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25au"
    if sto_heute == "70G" and hs_heute in ["subalpin", "obersubalpin"] and hs_zukunft in ["collin" , "collin mit Buche"] and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "71G" and hs_heute == "obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "44"
    if sto_heute == "70G" and hs_heute in ["subalpin", "obersubalpin"] and hs_zukunft in ["collin" , "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "42r"
    if sto_heute == "70G" and hs_heute == "obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "68"
    if sto_heute == "46M" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R 5":
        nais_zukunft_out = "42V"
    if sto_heute == "46M" and hs_heute == "unter- & obermontan" and hs_zukunft == "mediterran" and instandortregion == "R 5":
        nais_zukunft_out = "42V med"
    if sto_heute == "57C" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "19"
    if sto_heute == "70G" and hs_heute =="obersubalpin" and hs_zukunft in ["collin" , "collin mit Buche"] and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "70G" and hs_heute =="subalpin" and hs_zukunft in ["collin" , "collin mit Buche"] and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    #rcp45
    if sto_heute == "47*Lä" and hs_heute =="subalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 4":
        nais_zukunft_out = "19a"
    if sto_heute == "57C" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "57C"
    if sto_heute == "57V" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "57V"
    if sto_heute == "58" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "58"
    if sto_heute == "58Bl" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "58Bl"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "58C"
    if sto_heute == "56" and hs_heute == "hochmontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute == "58C" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "1h"
    if sto_heute == "59" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "48"
    if sto_heute == "59L" and hs_heute == "obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "1h"
    if sto_heute == "70" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "68"
    if sto_heute == "71" and hs_heute == "obermontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute == "18*" and hs_heute == "hochmontan" and hs_zukunft == "obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "18*"
    if sto_heute == "18*" and hs_heute == "hochmontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if inlage==4:
            nais_zukunft_out = "15"
        else:
            nais_zukunft_out = "14"
    if sto_heute == "18w" and hs_heute == "hochmontan" and hs_zukunft == "obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "18w"
    if sto_heute == "18w" and hs_heute == "hochmontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "18w" and hs_heute == "subalpin" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "40*" and hs_heute == "hochmontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute == "52" and hs_heute == "obermontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if inlage == 4:
            nais_zukunft_out = "15"
        else:
            nais_zukunft_out = "14"
    if sto_heute == "53*" and hs_heute == "obermontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute == "58LLä" and hs_heute == "obersubalpin" and hs_zukunft == "subalpin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "58LLä"
    if sto_heute == "67G" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "65 collin"
    if sto_heute == "67G" and hs_heute == "subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute == "69G" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute == "69G" and hs_heute == "subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute == "70G" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "70G" and hs_heute == "subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "70G" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "68"
    if sto_heute == "71G" and hs_heute == "obermontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute == "71G" and hs_heute in ["subalpin","obersubalpin"] and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "71G"
    if sto_heute == "70G" and hs_heute == "obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R 5":
        if inradiation ==1:
            nais_zukunft_out = "42r"
        else:
            nais_zukunft_out = "68"
    #rcp26
    if sto_heute == "57Bl" and hs_heute == "obersubalpin" and hs_zukunft == "subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "57Bl"
    if sto_heute == "70" and hs_heute == "obersubalpin" and hs_zukunft == "subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "70"
    #neue Runde
    if sto_heute == "24" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25a"
    if sto_heute == "32*" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "27"
    if sto_heute == "40P" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "40Pt"
    if sto_heute == "40PBl" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "40PBlt"
    if sto_heute == "58" and hs_heute == "obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "58Bl" and hs_heute == "obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "68" and hs_heute == "hochmontan" and hs_zukunft == "untermontan" and instandortregion == "R 4":
        nais_zukunft_out = "68"
    if sto_heute == "AV" and hs_heute == "subalpin" and hs_zukunft in ["untermontan", "obermontan"] and instandortregion == "R 4":
        nais_zukunft_out = "AV"
    if sto_heute == "32*" and hs_heute == "hochmontan" and hs_zukunft =="mediterran" and instandortregion == "R 5":
        nais_zukunft_out = "27"
    if sto_heute == "40PBl" and hs_heute == "hochmontan" and hs_zukunft =="mediterran" and instandortregion == "R 5":
        nais_zukunft_out = "25as"
    if sto_heute in ["58", "58Bl"] and hs_heute == "obersubalpin" and "collin" in hs_zukunft and instandortregion == "R 5":
        nais_zukunft_out = "42Q"
    if sto_heute == "70" and hs_heute == "obersubalpin" and hs_zukunft =="collin mit Buche" and instandortregion == "R 5":
        nais_zukunft_out = "42r"
    if sto_heute == "25*" and hs_heute =="submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "25* collin"
    if sto_heute == "71" and hs_heute =="obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45 collin"
    if sto_heute == "71" and hs_heute =="obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45 collin"
    if sto_heute == "32*" and hs_heute =="obermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "32*"
    if sto_heute == "40*" and hs_heute =="collin" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    #rcp26
    if sto_heute == "42Q" and hs_heute =="collin" and hs_zukunft == "hochmontan" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "70G" and hs_heute == "obersubalpin" and hs_zukunft == "subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "70G"
    if sto_heute == "18*" and hs_heute =="obermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "18*"
    if sto_heute == "18w" and hs_heute =="obermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "18w"
    if sto_heute == "19" and hs_heute =="obermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "19"
    if sto_heute == "40*" and hs_heute =="collin" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute == "40*" and hs_heute =="collin" and hs_zukunft == "obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute == "40*" and hs_heute =="collin" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    #LI
    if sto_heute == "24*" and hs_heute =="untermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    return nais_zukunft_out
def heuteempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_heute].isin(["a","b","c"])]
        extrdf2=extrdf[extrdf[sto_zukunft].isin(["a","b"])]
        extrdf3=extrdf2[extrdf2["grtreeid"].notnull()]
        treelist=extrdf3["grtreeid"].unique().tolist()#).replace("[","").replace("]","").replace(",","").replace("'","")
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def heutebedingtempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_heute].isin(["a","b","c"])]
        extrdf2=extrdf[extrdf[sto_zukunft]=="c"]
        extrdf3=extrdf2[extrdf2["grtreeid"].notnull()]
        treelist=extrdf3["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def heutegefaehrdet(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_heute].isin(["a","b","c"])]
        extrdf2=extrdf[extrdf[sto_zukunft]!="a"]
        extrdf3 = extrdf2[extrdf2[sto_zukunft] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_zukunft] != "c"]
        extrdf5=extrdf4[extrdf4["grtreeid"].notnull()]
        treelist=extrdf5["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def heuteachtung(naismatrixdf,sto_heute, sto_zukunft):
    treelist = []
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf = naismatrixdf[naismatrixdf[sto_heute].isin(["a", "b", "c"])]
        extrdf2 = extrdf[extrdf[sto_zukunft].isin(["a", "b", "c"])]
        if len(extrdf2)>0 and "Ailanthus altissima" in extrdf2["Namelat"].unique().tolist():
            treelist = ["Ailanthus altissima"]
    else:
        treelist=["notinnaismatrix"]
    return treelist
def zukunftempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_zukunft].isin(["a","b"])]
        extrdf2 = extrdf[extrdf[sto_heute] != "a"]
        extrdf3 = extrdf2[extrdf2[sto_heute] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_heute] != "c"]
        treelist=extrdf4["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def zukunftbedingtempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_zukunft]=="c"]
        extrdf2 = extrdf[extrdf[sto_heute] != "a"]
        extrdf3 = extrdf2[extrdf2[sto_heute] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_heute] != "c"]
        treelist=extrdf4["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def zukunftachtung(naismatrixdf,sto_heute, sto_zukunft):
    treelist = []
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf = naismatrixdf[naismatrixdf[sto_zukunft].isin(["a", "b", "c"])]
        extrdf2 = extrdf[extrdf[sto_heute] != "a"]
        extrdf3 = extrdf2[extrdf2[sto_heute] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_heute] != "c"]
        if len(extrdf4)>0 and "Ailanthus altissima" in extrdf4["Namelat"].unique().tolist():
            treelist = ["Ailanthus altissima"]
    else:
        treelist=["notinnaismatrix"]
    return treelist
def logikUebergang(x,y):
    u=""
    if x=="a":
        if y=="a":
            u="a"
        elif y=="b":
            u="a"
        elif y=="c":
            u="b"
        elif y in ["","ex"]:
            u="c"
    elif x=="b":
        if y=="a":
            u="b"
        elif y=="b":
            u="b"
        elif y=="c":
            u="b"
        elif y in ["","ex"]:
            u="c"
    elif x=="c":
        if y=="a":
            u="b"
        elif y=="b":
            u="c"
        elif y=="c":
            u="c"
        elif y in ["","ex"]:
            u=""
    elif x=="ex":
        if y=="a":
            u="c"
        elif y=="b":
            u="c"
        elif y=="c":
            u=""
        elif y in ["","ex"]:
            u=""
    elif x=="":
        if y=="a":
            u="c"
        elif y=="b":
            u="c"
        elif y=="c":
            u=""
        elif y in ["","ex"]:
            u=""
    return u
def uebergangstandortbedeutung(baumart, standort1column, standort2column):
    outue=""
    bedeutung1=str(naismatrix_gr_df.loc[naismatrix_gr_df[naismatrix_gr_df["grtreeid"] == baumart].index, str(standort1column)].values[0])
    bedeutung2=str(naismatrix_gr_df.loc[naismatrix_gr_df[naismatrix_gr_df["grtreeid"] == baumart].index, str(standort2column)].values[0])
    if bedeutung1 in ["a"] and bedeutung2 in ["a", "b"]:
        outue="a"
    elif bedeutung1 in ["a"] and bedeutung2 in ["c"]:
        outue="b"
    elif bedeutung1 in ["a"] and bedeutung2 not in ["a","b","c"]:
        outue="c"
    elif bedeutung1 in ["b"] and bedeutung2 in ["a","b","c"]:
        outue="b"
    elif bedeutung1 in ["b"] and bedeutung2 not in ["a","b","c"]:
        outue="c"
    elif bedeutung1 in ["c"] and bedeutung2 in ["a"]:
        outue="b"
    elif bedeutung1 in ["c"] and bedeutung2 in ["b","c"]:
        outue="c"
    elif bedeutung1 in ["c"] and bedeutung2 not in ["a","b","c"]:
        outue="ex"
    elif bedeutung1 not in ["a","b","c"] and bedeutung2 in ["a","b"]:
        outue="c"
    elif bedeutung1 not in ["a","b","c"] and bedeutung2 in ["c"]:
        outue="ex"
    elif bedeutung1 not in ["a","b","c"] and bedeutung2 not in ["a","b","c"]:
        outue="ex"
    return outue
#*************************************

#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi"
naismatrixdf=pd.read_excel(codeworkspace+"/"+"Matrix_Baum_inkl_collin_20210412_mit AbkuerzungenCLEAN.xlsx", dtype="str", engine='openpyxl')
projectionswegedf=pd.read_excel(codeworkspace+"/"+"L_Projektionswege_im_Klimawandel_18022020_export.xlsx", dtype="str", engine='openpyxl')
#gr_tree_abbreviations_df=pd.read_excel(codeworkspace+"/"+"Baumarten_LFI_export.xls", dtype=str)
#gr_tree_abbreviations_extract_df=gr_tree_abbreviations_df[gr_tree_abbreviations_df["Abkürzung_BK"].notnull()]
climatescenario="rcp85"
#climatescenario="rcp45"
#climatescenario="rcp26"

#*******************************************
#clean NAIS matrix table
#*******************************************
#create a dictionary of NaiS-Standortstypen
nais_matrix_columsdict={}
nais_matrix_columsdict_inv={}
nais_matrix_standorte_list=[]
id=0
for col in naismatrixdf.columns[8:].tolist():
    if col[-1]==" ":
        colnew = col
        while colnew[-1]==" ":
            colnew=colnew[:-1]
        naismatrixdf.rename(columns={col:colnew}, inplace=True)
        col=colnew
    if col not in nais_matrix_standorte_list:
        nais_matrix_standorte_list.append(col)
        nais_matrix_columsdict.update({id:col})
        nais_matrix_columsdict_inv.update({col: id})
    id+=1
joblib.dump(nais_matrix_standorte_list,projectspace+"/GL/"+"nais_matrix_standorte_list.sav")

#*******************************************
#projections pathways Projektionswege Data cleaning
#*******************************************
for index, row in projectionswegedf.iterrows():
    sto=row["Standortstyp_heute"]
    if "  " in sto:
        sto=sto.replace("  ", " ")
        projectionswegedf.loc[index, "Standortstyp_heute"]=sto
    if sto[-1]==" ":
        stonew=sto[:-1]
        projectionswegedf.loc[index, "Standortstyp_heute"]=stonew
for index, row in projectionswegedf.iterrows():
    stoz = row["Standortstyp_Zukunft"]
    if "  " in stoz:
        stoz=stoz.replace("  ", " ")
        projectionswegedf.loc[index, "Standortstyp_Zukunft"]=stoz
    if stoz[-1] == " ":
        stoznew = stoz[:-1]
        projectionswegedf.loc[index, "Standortstyp_Zukunft"] = stoznew
for index, row in projectionswegedf.iterrows():
    storeg = row["Standortsregionen"]
    if storeg == "R, J, M, 1, 2, 3 osa bis co":
        projectionswegedf.loc[index, "Standortsregionen"]="R, J, M, 1, 2, 3"
    if storeg == "R J, M,1, 2 Beginn co ":
        projectionswegedf.loc[index, "Standortsregionen"]="R, J, M, 1, 2, 3"
    if storeg == "R 5 ":
        projectionswegedf.loc[index, "Standortsregionen"]="R 5"
    if storeg == "R 4 ":
        projectionswegedf.loc[index, "Standortsregionen"]="R 4"
for index, row in projectionswegedf.iterrows():
    if row["Hoehenstufe_Zukunft"]=="hochmontan Reliktareal der Tanne":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"] = "hochmontan"
        projectionswegedf.loc[index, "Tannenareal_Zukunft"] = "Reliktareal"
    if row["Hoehenstufe_Zukunft"]=="hochmontan Hauptareal der Tanne":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"] = "hochmontan"
        projectionswegedf.loc[index, "Tannenareal_Zukunft"] = "Hauptareal"
    if row["Hoehenstufe_Zukunft"]=="hochmontan Nebenareal der Tanne":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"] = "hochmontan"
        projectionswegedf.loc[index, "Tannenareal_Zukunft"] = "Nebenareal"
#list forest types
standortstypen_projektionspfade_heute_list=projectionswegedf["Standortstyp_heute"].unique().tolist()
standortstypen_projektionspfade_zukunft_list=projectionswegedf["Standortstyp_Zukunft"].unique().tolist()
#correct some entries with "\n" in altitudinal vegetation belts
for index, row in projectionswegedf.iterrows():
    if "\n" in row["Hoehenstufe_heute"]:
        projectionswegedf.loc[index, "Hoehenstufe_heute"]=row["Hoehenstufe_heute"].replace("\n","")
#list altitudinal vegetation belts
hoehenstufen_projektionspfade_heute_list=projectionswegedf["Hoehenstufe_heute"].unique().tolist()
hoehenstufen_projektionspfade_zukunft_list=projectionswegedf["Hoehenstufe_Zukunft"].unique().tolist()
#correct names of future altiutudinal vegetation belts
for index, row in projectionswegedf.iterrows():
    if " Zukunft" in row["Hoehenstufe_Zukunft"]:
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"]=row["Hoehenstufe_Zukunft"].replace(" Zukunft","")
#change other wrong values
for index, row in projectionswegedf.iterrows():
    if row["Hoehenstufe_heute"]=="Obersubalpin":
        projectionswegedf.loc[index, "Hoehenstufe_heute"]="obersubalpin"
    if row["Hoehenstufe_heute"]=="hyperinsubrisch ":
        projectionswegedf.loc[index, "Hoehenstufe_heute"]="hyperinsubrisch"
for index, row in projectionswegedf.iterrows():
    if row["Hoehenstufe_Zukunft"]=="hyperinsubrisch Zukunft":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"]="hyperinsubrisch"
    if row["Hoehenstufe_Zukunft"]=="collin mit Buche Zukunft":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"]="collin mit Buche"
    if row["Hoehenstufe_Zukunft"]=="collin Zukunft":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"]="collin"
for index, row in projectionswegedf.iterrows():
    if row["Hangneigung"]=="> 70%":
        projectionswegedf.loc[index, "Hangneigung"]=4
    if row["Hangneigung"]=="< 70%":
        projectionswegedf.loc[index, "Hangneigung"]=3
    if row["Hangneigung"]=="> als 60% ":
        projectionswegedf.loc[index, "Hangneigung"]=3
    if row["Hangneigung"]=="< als 60% ":
        projectionswegedf.loc[index, "Hangneigung"]=2
    if row["Hangneigung"]=="> 20%":
        projectionswegedf.loc[index, "Hangneigung"]=2
    if row["Hangneigung"]=="< 20%":
        projectionswegedf.loc[index, "Hangneigung"]=1
    else:
        projectionswegedf.loc[index, "Hangneigung"] = 0
#list altitudinal vegetation belts
hoehenstufen_projektionspfade_heute_list=projectionswegedf["Hoehenstufe_heute"].unique().tolist()
hoehenstufen_projektionspfade_zukunft_list=projectionswegedf["Hoehenstufe_Zukunft"].unique().tolist()
#check Standortsregionen
standortsregionen_projektionspfade_list=projectionswegedf["Standortsregionen"].unique().tolist()

#standortsregionen_combination_list=combinations_df["Standortre"].unique().tolist()
#exemption no mosaic/uebergang
kein_mosaic_uebergang_list=["3*/4*", "3L/4L", "3L/4L hyp", "3L/4L  med", "3L/4L med"]#, "50*(51)"]#, "67/67G","69/69G", "70/70G","71/71G"]

#pairs of changes in altitudinal vegetation belts
pairsofchangesinaltitudinalvegetationbelts_inprojektionspfade=[]
for index, row in projectionswegedf.iterrows():
    if [row["Hoehenstufe_heute"],row["Hoehenstufe_Zukunft"]] not in pairsofchangesinaltitudinalvegetationbelts_inprojektionspfade:
        pairsofchangesinaltitudinalvegetationbelts_inprojektionspfade.append([row["Hoehenstufe_heute"],row["Hoehenstufe_Zukunft"]])
#list of Standortregion
standortsregion_list_inprojektionspfade=projectionswegedf["Standortsregion"].unique().tolist()
#check if NAIS Standortstyp in NAISmatrix is not in Projektionspfade:
projektionspfadestandortstyp_heute_notin_NAISmatrix=[]
for sto in standortstypen_projektionspfade_heute_list:
    if sto not in nais_matrix_standorte_list:
        projektionspfadestandortstyp_heute_notin_NAISmatrix.append(sto)
projektionspfadestandortstyp_zukunft_notin_NAISmatrix=[]
for sto in standortstypen_projektionspfade_zukunft_list:
    if sto not in nais_matrix_standorte_list:
        projektionspfadestandortstyp_zukunft_notin_NAISmatrix.append(sto)
#correct wrong values of Standortstyp Zukunft
for index, row in projectionswegedf.iterrows():
    if row["Standortstyp_Zukunft"]=="41*collin":
        projectionswegedf.loc[index, "Standortstyp_Zukunft"]="41* collin"
    if row["Standortstyp_Zukunft"]=="43Scollin":
        projectionswegedf.loc[index, "Standortstyp_Zukunft"]="43S collin"
    if "  " in row["Standortstyp_Zukunft"]:
        print(row["Standortstyp_Zukunft"])

#*******************************************
#preprocessing
#*******************************************

combinations_df=gpd.read_file(projectspace+"/GL/stok_gdf_attributed_"+climatescenario+".gpkg", layer='stok_gdf_attributed_'+climatescenario)
#combinations_df['storeg']='1'
#Lage
combinations_df['lage']=3
combinations_df.loc[combinations_df['meanslopeprc']<10, 'lage']=1
len(combinations_df)
combinations_df.columns
combinations_df=combinations_df[['wg_haupt','wg_zusatz', 'kantonseinheit', 'nais', 'nais1', 'nais2', 'mo', 'ue','hs1975','taheute','storeg', 'tahs','tahsue', 'meanslopeprc', 'slpprzrec', 'rad', 'radiation', 'HS_de', 'Code', 'Subcode','geometry']]
combinations_df.columns
combinations_df.rename(columns={"HS_de":"hs_de","Subcode":"subcode","Code":"code"}, inplace=True)
combinations_df.columns
combinations_df.loc[combinations_df["tahsue"].isna(),"tahsue"]="_"
#combinations_df=combinations_df[combinations_df['nais1']!="_"]
len(combinations_df)
combinations_df=combinations_df.astype({'storeg': 'str','subcode': int})
#combinations_df=combinations_df.astype({'mo': int,'ue': int})
#combinations_df=combinations_df.astype({'nais1': 'str','tahs': 'str', 'nais2':'str','tahsue':'str'})
combinations_df.dtypes
#add columns
combinations_df["naiszuk1"]=""
combinations_df["naiszuk2"]=""
combinations_df["hszukcor"]=""
combinations_df["storegco"]=""
combinations_df["tazuk"]=""
combinations_df=combinations_df.astype({'hszukcor': str,'storegco': str, 'tazuk':str,'naiszuk1':str,'naiszuk2':str})
combinations_df.dtypes

for index, row in combinations_df.iterrows():
    if '(' in row['nais']:# and row['nais1']=='':
        combinations_df.loc[index, 'nais1']=row['nais'].replace('(',' ').replace(')','').replace('/',' ').strip().split()[0]
        combinations_df.loc[index, 'nais2'] = row['nais'].replace('(', ' ').replace(')', '').replace('/', ' ').strip().split()[1]
        combinations_df.loc[index, 'ue'] = 1
    elif '/' in row['nais']:# and row['nais1']=='':
        combinations_df.loc[index, 'nais1']=row['nais'].replace('(',' ').replace(')','').replace('/',' ').strip().split()[0]
        combinations_df.loc[index, 'nais2'] = row['nais'].replace('(', ' ').replace(')', '').replace('/', ' ').strip().split()[1]
        combinations_df.loc[index, 'mo'] = 1
    else:
        combinations_df.loc[index, 'nais1'] = row['nais']
        combinations_df.loc[index, 'nais2'] = '_'

#check for collin in tahsue
test=combinations_df[combinations_df['tahsue']=='collin']
combinations_df.loc[combinations_df["nais"]=='9a(29A)',"tahsue"]="submontan"
combinations_df.loc[combinations_df["nais"]=='9a(29C)',"tahsue"]="submontan"
combinations_df.loc[combinations_df["nais"]=='14(29C)',"tahsue"]="untermontan"

#*******************************************
#loop through pandas data frame and correct Standortstypen, Mosaik, Uebergang, Standortregion
#*******************************************
#correct unter-/obermontan
combinations_df.loc[combinations_df["hs_de"]=="unter-/obermontan", "hs_de"] = "unter- & obermontan"
#translate abbreviations
combinations_df['tahs'].unique().tolist()
combinations_df['tahsue'].unique().tolist()
combinations_df.loc[combinations_df["tahsue"]=='', "tahsue"] = "_"
#combinations_df=combinations_df[combinations_df["hs_de"]!='_']
#combinations_df=combinations_df[combinations_df["hs_de"]!='-']
len(combinations_df)


#test if some nais types are not in the Projektionswege table
print("NAIS Typen 1 nicht in Projektionspfade: ")
for item in combinations_df['nais1'].unique().tolist():
    if item not in standortstypen_projektionspfade_heute_list:
        print(item)
print("NAIS Typen 2 nicht in Projektionspfade: ")
for item in combinations_df['nais2'].unique().tolist():
    if item not in standortstypen_projektionspfade_heute_list:
        print(item)
print("NAIS Typen 1 nicht in NAIS-Matrix: ")
for item in combinations_df['nais1'].unique().tolist():
    if item not in nais_matrix_standorte_list:
        print(item)
print("NAIS Typen 2 nicht in NAIS-Matrix: ")
for item in combinations_df['nais2'].unique().tolist():
    if item not in nais_matrix_standorte_list:
        print(item)

#synchro uebergang vs mosaic
combinations_df.loc[((combinations_df["mo"]==1)&(combinations_df["ue"]==0)),"ue"]=1

#check empty values
nohs1list=combinations_df[combinations_df["tahs"]==""]['nais1'].unique().tolist()
len(nohs1list)
nohs2list=combinations_df[((combinations_df["tahsue"]=="")&(combinations_df["ue"]==1))]['nais2'].unique().tolist()
len(nohs2list)

#check combination of forest type and altitudinal vegetation belt today
region_foresttype_belt_inprojektionspfade=[]
for index, row in projectionswegedf.iterrows():
    if [row["Standortsregionen"],row["Standortstyp_heute"],row["Hoehenstufe_heute"]] not in region_foresttype_belt_inprojektionspfade:
        region_foresttype_belt_inprojektionspfade.append([row["Standortsregionen"],row["Standortstyp_heute"],row["Hoehenstufe_heute"]])
#correct Standortregion
print("Korrigiere Standortregion ...")
for index, row in combinations_df.iterrows():
    #if index%10000==0:
    #    print(index)
    nais=row['nais1']
    storeg=give_standortregionencombi_from_projektionspfade(row["storeg"])
    #storeg = give_standortregionencombi_from_projektionspfade(row["Standortre"])
    if nais in nais_matrix_standorte_list:
        pathwaysquery=projectionswegedf[projectionswegedf["Standortstyp_heute"]==nais]
        if storeg not in pathwaysquery["Standortsregionen"].unique().tolist() and len(pathwaysquery["Standortsregionen"].unique().tolist())>0:
            combinations_df.loc[index, "storegco"] = pathwaysquery["Standortsregionen"].unique().tolist()[0]
        else:
            combinations_df.loc[index, "storegco"] = storeg
    else:
        if nais!="_":
            print(nais+" not in nais_matrix_standorte_list")
#check empty storegco values
combinations_df["storegco"].unique().tolist()
combinations_df.loc[((combinations_df["storegco"]=="")&(combinations_df["storeg"]=="1")),"storegco"]='R, J, M, 1, 2, 3'
combinations_df.loc[((combinations_df["storegco"]=="")&(combinations_df["storeg"]=="M")),"storegco"]='R, J, M, 1, 2, 3'
combinations_df.loc[((combinations_df["storegco"]=="")&(combinations_df["storeg"]=="2a")),"storegco"]='R, J, M, 1, 2, 3'
combinations_df.loc[((combinations_df["storegco"]=="")&(combinations_df["storeg"]=="2b")),"storegco"]='R, J, M, 1, 2, 3'
combinations_df.loc[((combinations_df["storegco"]=="")&(combinations_df["storeg"]=="3")),"storegco"]='R, J, M, 1, 2, 3'
#check=combinations_df[combinations_df["storegco"]==""]
#combinations_df["storegco"].unique()

#correct future altitudinal vegetation belts (divide belt and fir area)
combinations_df["hszukcor"]=combinations_df["hs_de"]
combinations_df.loc[combinations_df["hs_de"].isin(['hochmontan im Tannen-Hauptareal','hochmontan im Tannen-Nebenareal','hochmontan im Tannen-Reliktareal']), "hszukcor"]="hochmontan"
combinations_df.loc[~combinations_df["hs_de"].isin(['hochmontan im Tannen-Hauptareal','hochmontan im Tannen-Nebenareal','hochmontan im Tannen-Reliktareal']), "hszukcor"]=combinations_df["hs_de"]
combinations_df.loc[combinations_df["hs_de"]=='hochmontan im Tannen-Hauptareal',"tazuk"]="Hauptareal"
combinations_df.loc[combinations_df["hs_de"]=='hochmontan im Tannen-Nebenareal',"tazuk"]="Nebenareal"
combinations_df.loc[combinations_df["hs_de"]=='hochmontan im Tannen-Reliktareal',"tazuk"]="Reliktareal"
combinations_df.loc[combinations_df["taheute"]==1,"tazuk"]="Hauptareal"
#combinations_df.loc[((combinations_df["tazuk"]=='')&(combinations_df["taheute"]==1)),"tazuk"]="Hauptareal"
#combinations_df.loc[((combinations_df["tazuk"]=='')&(combinations_df["taheute"]==2)),"tazuk"]="Nebenareal"
#combinations_df.loc[((combinations_df["tazuk"]=='')&(combinations_df["taheute"]==3)),"tazuk"]="Reliktareal"

##correct altitudinal vegetation belts according projections pathways
for index, row in combinations_df.iterrows():
    if [row["storegco"],row['nais1'], row["tahs"]] not in region_foresttype_belt_inprojektionspfade:
        listpotentialbelts=[]
        for item in region_foresttype_belt_inprojektionspfade:
            if item[0]==row["storegco"] and item[1]==row['nais1']:
                listpotentialbelts.append(item[2])
        if len(listpotentialbelts)>0:
            combinations_df.loc[index, "tahs"] = listpotentialbelts[-1]
        else:
            if [row["storegco"], row['nais1'],row["hs_de"]] in region_foresttype_belt_inprojektionspfade:
                combinations_df.loc[index, "tahs"] = row['hs_de']
    if row['nais2']!="" and [row["storegco"],row['nais1'], row["tahsue"]] not in region_foresttype_belt_inprojektionspfade:
        listpotentialbelts=[]
        for item in region_foresttype_belt_inprojektionspfade:
            if item[0]==row["storegco"] and item[1]==row['nais2']:
                listpotentialbelts.append(item[2])
        if len(listpotentialbelts)>0:
            combinations_df.loc[index, "tahsue"] = listpotentialbelts[-1]
        else:
            if [row["storegco"], row['nais2'],row["hs_de"]] in region_foresttype_belt_inprojektionspfade:
                combinations_df.loc[index, "tahsue"] = row['hs_de']




##correct special cases
#for index, row in combinations_df.iterrows():
#    if row ['nais1'] in ["3","4"] and row["storegco"]=="R, J, M, 1, 2, 3":
#        combinations_df.loc[index,"tahs"]="untermontan"
#    if row ['nais1'] in ["3","4"] and row["storegco"] in ["R 4", "R 5", "R Mendrisiotto"]:
#        combinations_df.loc[index,"tahs"]="unter- & obermontan"
#    if row ['nais1'] in ["19L","19LP"] and row["storegco"] in ["R 4", "R 5", "R Mendrisiotto"]:
#        combinations_df.loc[index,"tahs"]="unter- & obermontan"
#    if row ['nais1'] in ["19L"] and row["storegco"] =="R, J, M, 1, 2, 3":
#        combinations_df.loc[index,"tahs"]="obermontan"
#    if row ['nais1'] in ["25as", "25au"] and row["storeg"] in ["4", "3"]:
#        combinations_df.loc[index,"tahs"]="collin"
#    if row ['nais1'] in ["25as", "25au"] and row["storeg"] in ["5", "5a", "5b", "Me"]:
#        combinations_df.loc[index,"tahs"]="collin mit Buche"
#    if row ['nais1'] in ["19L", "19LP"] and row["tahs"] =="subalpin" and row["storegco"] =="R, J, M, 1, 2, 3":
#        combinations_df.loc[index,"tahs"]="obermontan"
#    if row ['nais1'] in ["19L", "19LP"] and row["tahs"] =="subalpin" and row["storegco"] in ["R 4", "R 5", "R Mendrisiotto"]:
#        combinations_df.loc[index,"tahs"]="unter- & obermontan"
#    if row ['nais1'] in ["19LP"] and row["tahs"] =="hochmontan" and row["storegco"] in ["R 4", "R 5", "R Mendrisiotto"]:
#        combinations_df.loc[index,"tahs"]="unter- & obermontan"
#    #if row ['nais1'] in ["33m", "42C", "42Q"] and row["tahs"] =="hochmontan" and row["storeg"] in ["4"]:
#    #    combinations_df.loc[index,"tahs"]="collin"
#    #if row ['nais1'] in ["33m", "42C", "42Q"] and row["tahs"] =="hochmontan" and row["storeg"] in ["5","5a","5b", "Me"]:
#    #    combinations_df.loc[index,"tahs"]="collin mit Buche"
#    if row ['nais1'] in ["59A", "59C", "59E"] and row["tahs"] =="hochmontan" and row["storegco"] =="R, J, M, 1, 2, 3":
#        combinations_df.loc[index,"tahs"]="obersubalpin"
#    if row ['nais1'] in ["59A", "59C", "59E"] and row["tahs"] =="hochmontan" and row["storegco"] =="R, J, M, 1, 2, 3":
#        combinations_df.loc[index,"tahs"]="obersubalpin"

#check if future altitudinal vegetation belt is not higher than present
combinations_df.loc[((combinations_df["tahs"] == "collin")&(combinations_df["hszukcor"].isin(["submontan", "untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahs"] == "collin mit Buche")&(combinations_df["hszukcor"].isin(["submontan", "untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahs"] == "hyperinsubrisch")&(combinations_df["hszukcor"].isin(["submontan", "untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahs"] == "submontan")&(combinations_df["hszukcor"].isin(["untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahs"] == "untermontan")&(combinations_df["hszukcor"].isin(["obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahs"] == "obermontan")&(combinations_df["hszukcor"].isin(["hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahs"] == "unter- & obermontan")&(combinations_df["hszukcor"].isin(["hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahs"] == "hochmontan")&(combinations_df["hszukcor"].isin(["subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahs"] == "subalpin")&(combinations_df["hszukcor"].isin(["obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]

combinations_df.loc[((combinations_df["tahsue"] == "collin")&(combinations_df["hszukcor"].isin(["submontan", "untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahsue"] == "collin mit Buche")&(combinations_df["hszukcor"].isin(["submontan", "untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahsue"] == "hyperinsubrisch")&(combinations_df["hszukcor"].isin(["submontan", "untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahsue"] == "submontan")&(combinations_df["hszukcor"].isin(["untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahsue"] == "untermontan")&(combinations_df["hszukcor"].isin(["obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahsue"] == "obermontan")&(combinations_df["hszukcor"].isin(["hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahsue"] == "unter- & obermontan")&(combinations_df["hszukcor"].isin(["hochmontan", "subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahsue"] == "hochmontan")&(combinations_df["hszukcor"].isin(["subalpin", "obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["tahsue"] == "subalpin")&(combinations_df["hszukcor"].isin(["obersubalpin"]))), "hszukcor"]=combinations_df["tahs"]

#check "obermontan", "untermontan" vs "unter- & obermontan"
combinations_df['hszukcor'].unique().tolist()
combinations_df['tahs'].unique().tolist()
combinations_df['tahsue'].unique().tolist()
#combinations_df.loc[combinations_df["hszukcor"]=="unter-/obermontan", "hszukcor"]="unter- & obermontan"
#combinations_df.loc[combinations_df["tahs"]=="unter-/obermontan", "hszukcor"]="unter- & obermontan"
#combinations_df.loc[combinations_df["tahsue"]=="unter-/obermontan", "hszukcor"]="unter- & obermontan"
#combinations_df.loc[((combinations_df["tahs"].isin(["untermontan", "obermontan"]))&(combinations_df["storegco"].isin(["R 4", "R 5", "R Mendrisiotto"]))), "tahs"]="unter- & obermontan"
#combinations_df.loc[((combinations_df["tahsue"].isin(["untermontan", "obermontan"]))&(combinations_df["storegco"].isin(["R 4", "R 5", "R Mendrisiotto"]))), "tahsue"]="unter- & obermontan"
#combinations_df.loc[((combinations_df["tahs"]=="unter- & obermontan")&(combinations_df["hszukcor"].isin(["untermontan", "obermontan"]))), "hszukcor"]="unter- & obermontan"
#combinations_df.loc[((combinations_df["tahs"].isin(["untermontan", "obermontan"]))&(combinations_df["hszukcor"]== "unter- & obermontan")), "hszukcor"]=combinations_df["tahs"]
#len(combinations_df[combinations_df["tahs"].isna()==True])
#len(combinations_df[combinations_df["hszukcor"].isna()==True])
#len(combinations_df[combinations_df["hszukcor"]=="_"])
##combinations_df.loc[((combinations_df[combinations_df["tahs"].isna()==True])&(combinations_df[combinations_df["hszukcor"].isin(["submontan", "untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"])])), "tahs"]=combinations_df["hszukcor"]
#combinations_df.loc[((combinations_df["tahs"]=="_")&(combinations_df["hszukcor"]!="_")), "tahs"]=combinations_df["hszukcor"]
#combinations_df["tahs"].unique().tolist()
##leere=combinations_df[combinations_df["tahs"].isna()==True]
#combinations_df=combinations_df[combinations_df["tahs"].isna()==False]

#correct altitudinal vegetation belts in input file
#pairs of changes in altitudinal vegetation belts
pairsofforesttypesandaltitudinalvegetationbelts_inprojektionspfade=[]
for index, row in projectionswegedf.iterrows():
    if [row["Standortsregionen"],row["Standortstyp_heute"],row["Hoehenstufe_heute"], row["Hoehenstufe_Zukunft"]] not in pairsofforesttypesandaltitudinalvegetationbelts_inprojektionspfade:
        pairsofforesttypesandaltitudinalvegetationbelts_inprojektionspfade.append([row["Standortsregionen"],row["Standortstyp_heute"],row["Hoehenstufe_heute"],row["Hoehenstufe_Zukunft"]])
len(pairsofforesttypesandaltitudinalvegetationbelts_inprojektionspfade)
combinations_df["hszukcor"].unique().tolist()
combinations_df.loc[((combinations_df["hszukcor"]=="-")&(combinations_df["tahs"].isin(["submontan", "untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))),"hszukcor"]=combinations_df["tahs"]
combinations_df.loc[((combinations_df["hszukcor"]=="_")&(combinations_df["tahs"].isin(["submontan", "untermontan", "obermontan", "unter- & obermontan", "hochmontan", "subalpin", "obersubalpin"]))),"hszukcor"]=combinations_df["tahs"]
combinations_df["tahs"].unique().tolist()

#convert geopandas to pandas
#combinations_gdf=combinations_df.copy()
#combinations_gdf.columns
##test=combinations_df.groupby(['NaiS_LFI', 'mo', 'ue', 'taheute', 'storeg','slpprzrec', 'radiation', 'lage', 'tahs', 'nais1','nais2', 'tahsue', 'hs_de', 'code', 'subcode'])
#test1=combinations_df[['mo', 'ue', 'taheute', 'storeg','slpprzrec', 'radiation', 'lage', 'tahs', 'nais1','nais2', 'tahsue', 'subcode','hszukcor','storegco','tazuk']]
#combinations_df=test1.drop_duplicates(['mo', 'ue', 'taheute', 'storeg','slpprzrec', 'radiation', 'lage', 'tahs', 'nais1','nais2', 'tahsue', 'subcode','hszukcor','storegco','tazuk'])[['mo', 'ue', 'taheute', 'storeg','slpprzrec', 'radiation', 'lage', 'tahs', 'nais1','nais2', 'tahsue', 'subcode','hszukcor','storegco','tazuk']]
#len(combinations_df)
#combinations_df["naiszuk1"]=""
#combinations_df["naiszuk2"]=""

#save pandas data frame
#combinations_df.to_csv(projectspace+"/combinations_df.csv")
joblib.dump(combinations_df, projectspace+"/GL/combinations_df"+climatescenario+".sav")
combinations_df.columns

#***********************************************************************
#iterate trough combinations dataframe and calculate future forest type
#***********************************************************************
#combinations_df["naiszuk1"]=""
#combinations_df["naiszuk2"]=""
extractprojektionswegestoreg2b3=projectionswegedf[projectionswegedf["Standortsregion"].isin(["2b","2b, 3","3"])]
extractprojektionswegestoreg2b3combinationslist=[]
extractprojektionswegestoreg2b=projectionswegedf[projectionswegedf["Standortsregion"].isin(["2b","2b, 3"])]
extractprojektionswegestoreg2bcombinationslist=[]
extractprojektionswegestoreg3=projectionswegedf[projectionswegedf["Standortsregion"].isin(["3","2b, 3"])]
extractprojektionswegestoreg3combinationslist=[]
for index, row in extractprojektionswegestoreg2b3.iterrows():
    if [row["Hoehenstufe_heute"],row["Standortstyp_heute"],row["Standortsregion"],row["Hoehenstufe_Zukunft"]] not in extractprojektionswegestoreg2b3combinationslist:
        extractprojektionswegestoreg2b3combinationslist.append([row["Hoehenstufe_heute"],row["Standortstyp_heute"],row["Standortsregion"],row["Hoehenstufe_Zukunft"]])
for index, row in extractprojektionswegestoreg2b.iterrows():
    if [row["Hoehenstufe_heute"],row["Standortstyp_heute"],row["Hoehenstufe_Zukunft"]] not in extractprojektionswegestoreg2bcombinationslist and row["Standortsregion"] in ["2b","2b, 3"]:
        extractprojektionswegestoreg2bcombinationslist.append([row["Hoehenstufe_heute"],row["Standortstyp_heute"],row["Hoehenstufe_Zukunft"]])
for index, row in extractprojektionswegestoreg3.iterrows():
    if [row["Hoehenstufe_heute"],row["Standortstyp_heute"],row["Hoehenstufe_Zukunft"]] not in extractprojektionswegestoreg3combinationslist and row["Standortsregion"] in ["3","2b, 3"]:
        extractprojektionswegestoreg3combinationslist.append([row["Hoehenstufe_heute"],row["Standortstyp_heute"],row["Hoehenstufe_Zukunft"]])
hochmontandirektzucollin=projectionswegedf[((projectionswegedf["Hoehenstufe_heute"]=="hochmontan")&(projectionswegedf["Hoehenstufe_Zukunft"]=="collin"))]
hochmontandirektzucollinlist=hochmontandirektzucollin["Standortstyp_heute"].unique().tolist()
len(hochmontandirektzucollinlist)
print("Berechne zukuenftige Standortstypen ...")
print("all done")