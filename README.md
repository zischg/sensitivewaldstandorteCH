# sensitivewaldstandorteCH
Sensitive Waldstandorte und Bestände Schweiz

Dieses Code Repository dokumentiert die Arbeiten zur Entwicklung einer Karte der Baumartenempfehlungen im Klimawandel, einer Karte zu den klimasensitiven Waldstandorten und einer Karte zu den klimasensitiven Bestände.
Die Methode folgt der Prozedur von Tree-App (https://www.tree-app.ch) und wird mit folgenden Schritten umgesetzt:

1. Extraktion aller Waldstandortstypen einer kantonalen Waldstandortskarte und Ableitung einer Tabelle zu allen kartierten Standortstypen (script XX_hoehenstufen_preprocessing.py mit output XX_nais_einheiten_unique.xlsx, XX_ steht für das Kantonskürzel)
2. Alle kantonalen Standortstypen werden in einen NaiS-Standort übersetzt. Dies erfolgt gutachterlich durch M. Frehner und B. Huber (output XX_nais_einheiten_unique_mf.xlsx)
3. Die Tabelle mit den Übersetzungen und Höhenstufenzuweisungen wird mit der kantonalen Standortskarte verknüpft (script XX_hoehenstufen.py). Output ist eine Waldstandortskarte mit den kantonalen EInheiten, den NaiS-Einheiten und zugeweisenen Höhenstufen.
4. Die übersetzte und harmonisierte Karte der Waldstandortstypen wird mit verschiednen Attributen angereichert (Muldenlagen, Hanglagen, Ebenen, Sonnen- und Schattenhänge, Neigung, Standortsregion, Tannenareal), die es zur Berechnung der Projektionswege braucht. Anschliessend wird folgendes berechnet (script X_sensi_treeapp.py):
  -Die zukünftige Höhenstufe wird für jedes Klimaszenario durch räumliche Überlagerung bestimmt,
  -der zukünftige Standortstyp wird auf Basis der Projektionswegetabelle von NaiS (L_Projektionswege_im_Klimawandel_18022020_export.xlsx) und dem zukünftigen Standortstyp berechnet,
  -der Vergleich der Baumartenzusammensetzung des heutigen und zukünftigen Waldstandorstyps ergibt die Karte der BAumartenempfehlungen (NaiS-MAtrix Baumartentabelle Matrix_Baum_inkl_collin_20210412_mit AbkuerzungenCLEAN.xlsx)
  -auf Basis der Baumartenempfehlungen werden die klimasensitiven Standorte berechnet
5. Die beiden Klimaszenarien RCP4.5 und RCP8.5 werden miteinander kombiniert (script XX_sensi_treeappCombiRCP45RCP85.py)
6. Die sensitiven Bestände werden berechnet (script XX_sensitiveBestaende.py)


Beschreibung der Anwendung der Code-Beispiele auf dem Github-repository https://github.com/zischg/sensitivewaldstandorteCH

Das vorliegende Dokument dokumentiert die Anwendung der Python-Scripts auf dem github-repository des Projekts «Sensitive Standorte und Bestände Schweiz». Für jeden Kanton hat es mehrere Input-Daten und Python-Scripts. Die jeweiligen Scripts sind mit dem Kürzel des Kantons bezeichnet (im Folgenden als «XX_» bezeichnet. 
Das Vorgehen ist im Projektbericht im Detail beschrieben und wird hier nicht mehr wiederholt. Hier wird nur die Anwendung der Scripts dokumentiert. Im Wesentlichen teilt sich das Vorgehen auf drei Scripts auf:
1.	Übersetzung der kantonalen Waldstandortkarte in NaiS und Zuweisung der Höhenstufen
2.	Berechnung der Baumartenempfehlungen und sensitiven Standorte
3.	Berechnung der sensitiven Bestände
Zudem gibt es Scripts für das pre-processing der Höhenstufen und Scripts für Tests der Methodik. Diese werden wahrscheinlich nicht wieder benutzt.

1.	Übersetzung der kantonalen Waldstandortkarte in NaiS und Zuweisung der Höhenstufen
Das Script «XX_AG_hoehenstufen.py» liest die kantonale Waldstandortkarte ein. Diese Karte wird angereichert mit Informationen, die für die Berechnung der Baumartenempfehlungen und der sensitiven Standorte gebraucht werden. Für jedes Polygon wird 
•	die mittlere Hangneigung in Prozent berechnet,
•	die mittlere Sonneneinstrahlung im Jahr zugewiesen und klassifiziert,
•	die Höhenstufe laut Vegetationshöhenstufenkarte 1975 zugewiesen, 
•	das Tannenareal (Haupt-, Neben-, Reliktareal) zugewiesen,
•	die Waldstandortregion zugewiesen.
Die Hangneigung kann aus den Swisstopo Geländemodellen berechnet werden. Die Sonneneinstrahlung kann aus dem repository «High resolution maps of climatological parameters for analyzing the impacts of climatic changes on Swiss forests» (https://zenodo.org/records/3527731) heruntergeladen werden. Die Höhenstufe kann von map.geo.admin.ch heruntergeladen werden. Die Tannenareale und die Waldstandortregionen kommen von NaiS.
Die Zuweisung der Information aus den genannten Datengrundlagen erfolgt durch Intersect/spatial join bei Vektor-Daten und durch Rasterstatistik bei Rasterdaten. 
In einem zweiten Schritt wird das Excel-File der Übersetzungstabelle gelesen und auf die Waldstandortkarte übertragen. Ergebnis ist ein Datensatz mit dem Namen «stok_gdf_attributed.gpkg». Dieser Datensatz ist der Input für den nachfolgenden Prozess.

 
2.	Berechnung der Baumartenempfehlungen und sensitiven Standorte
Das Script «XX_sensi_treeapp.py» beinhaltet alle Funktionen zur Berechnung der Projektionswege im Klimawandel. Eingabedaten sind das Output-File «stok_gdf_attributed.gpkg», die NaiS-Baumartenmatrix «Matrix_Baum_inkl_collin_20210412_mit AbkuerzungenCLEAN.xlsx», und die TreeApp-Projektionswegetabelle «L_Projektionswege_im_Klimawandel_18022020_export.xlsx». Die beiden Excel-File sind im Github-repository enthalten.
Im Preprocessing werden die Inputdaten korrigiert und gegeneinander abgeglichen. Zudem wird die Lageinformation (Hanglage oder Ebene) berechnet und hinzugefügt. 
Im Hauptteil des Scripts wird für jedes Klimaszenario (RCP4.5 und RCP8.5) erstens die räumliche Überlagerung mit den zukünftigen Vegetationshöhenstufen gemacht, zweitens der zukünftige Standortstyp berechnet, drittens die Baumartenempfehlung gerechnet und viertens die sensitiven Standorte berechnet. Im Loop der Klimaszenarien wird jeweils ein Loop für alle diese Schritte gestartet, die jede mögliche Kombination aus Standortstyp und Höhenstufen(wechsel) berücksichtigt. Anschliessend wird ein Loop über alle Baumarten gemacht.
Am Ende des Loops werden die Output-Daten geschrieben: 
•	Zukünftige Waldstandortstypen: «XX_rcp45_zukuenftigestandorte.gpkg» oder «XX_rcp85_zukuenftigestandorte.gpkg» 
•	Baumartenbedeutungen: «XX_rcp45_baumartenbedeutungen.gpkg» oder «XX_rcp85_baumartenbedeutungen.gpkg» 
•	Baumartenempfehlungen: «XX_rcp45_baumartenempfehlungen.gpkg» oder «XX_rcp85_baumartenempfehlungen.gpkg» 
•	Sensitive Standorte: «XX_rcp45_sensitivestandorte.gpkg» oder «XX_rcp85_sensitivestandorte.gpkg» 

3.	Berechnung der sensitiven Bestände
Das Script «CH_sensitiveBestaende_Fichte_TBk.py» liest die TBk-Bestandeskarte ein und überlagert diese mit den Baumartenempfehlungen aus dem Script 2. Dieses Script wird auf die gesamte Schweiz angewandt. Dafür müssen die kantonalen Karten in einer Datenbank zu einer nationalen Übersicht zusammengefasst werden. 




