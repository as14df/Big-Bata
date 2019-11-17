# Big-Bata

## Aufgabenstellung

Mit dem folgenden Workflow soll es möglich werden, Addressen anhand der von OpenAddresses.io
bereitgestellten Daten zu validieren. 

Die Address-Daten können als Zip-Datei heruntergeladen werden,
deren Inhalt in den folgenden Abbildungen dargestellt wird.

![Alt text](Images/address_data_folders.png "Workflow")
![Alt text](Images/address_data.png "Workflow") 

Um Addressen anhand dieser Daten validieren zu können,
soll der folgende Workflow realisiert werden:

* Sammeln von Daten aus OpenAddresses.io
* Speicherung der Rohdaten (CSV-Dateien) in HDFS (nach Ländern gegliedert)
* Optimierung, Reduzierung und Bereinigung der Rohdaten
* Exportierung der Adressdaten in eine Endbenutzerdatenbank (z.B. MySQL,MongoDB....)
* Bereitstellung eines einfachen HTML-Frontends:
  * aus der Endbenutzerdatenbank lesen
  * Benutzereingaben verarbeiten (Straße, Ort, Postleitzahl....)
  * Validierung von Benutzereingaben anhand von OpenAddress-Daten am Ende des Vorgangs.
  * Anzeigen des Ergebnisses (echte oder nicht echte Adresse)
* Der gesamte Daten-Workflow muss innerhalb eines ETL Workflow-Tools (Airflow/Pentaho) implementiert und automatisch ausgeführt werden.


## Umsetzung

### ETL Workflow

Der ETL-Workflow wird mit dem Tool Airflow realisiert.
Er implementiert dabei den im Folgenden dargestellten Ablauf

* Herunterladen der Address-Daten als Zip-Datei und entpacken.

* Kopieren der relevanten Daten (nur Csv-Dateien und Länder-Ordner) ins HDFS

* Extrahieren der nötigen Daten in eine neue Hive-Tabelle (Land,Stadt,Postleitzahl,Straße,Hausnummer)

* Exportieren der Hive-Tabelle in eine MySql-Datenbank

* Validierung der Daten durch eine NodeJs-Webseite mit Zugriff auf die MySql-Datenbank

![Alt text](Images/workflow.png "Workflow")

### Airflow Tasks

Im Folgenden werden die jeweiligen Airflow Tasks beschrieben, mit welchen der o.g. Ablauf implementiert wird

Task | Beschreibung
----------- | -------
rm_local_import_dir | löscht den import Ordner falls vorhanden
create_local_import_dir | erstellt einen neuen import ordner
download_address_data | Lädt sie Daten als Zip-datei herunter
unzip_adress_data | Entpackt die Zip-Datei
create_hive_table_address_data | erstellt eine Hive Tabelle für die Address Daten, die nach Jahr,Monat,Tag,Land partitioniert ist
create_hdfs_address_data_dir_X | erstellt für jedes Land einen Ordner im HDFS
dummy0 | wartet bis alle Ordner erstellt wurden
hdfs_put_address_data_X | Kopiert alle Csv-Dateien aus jedem Land Ordner in den jeweiligen HDFS Ordner
dummy1 | wartet, bis alle Daten ins HDFS kopier wurden
hive_add_partition_address_data_X | Fügt den Inhalt jedes Land Ordners als partition in die Hive-Tabelle ein
dummy2 | wartet, bis alle partitionen zur Hive-Tabelle hinzugefügt wurden sind
create_hive_table_final_address_data | erstellt eine Tabelle, die die bereinigten Daten beinhalten wird
hive_insert_overwrite_final_address_data | kopiert die spalten Country,City,Postcode,Street,Number,Hash ind die finale Tabelle
create_table_remote | erstellt eine neue tabelle in der Mysql datenbank für die bereinigten Daten falls noch nicht 
delete_from_remote | löscht alle alten daten aus der tabelle falls vorhanden
hive_to_mysql_X | kopiert alle Daten aus der Hive tabelle nacheinander nach Ländern in die MySql tabelle  

## Projektaufbau

### Container

Für die Realisierung werden die folgenden vier Docker Container verwendet:

Container | Beschreibung | DockerHub
------|-----|-----
hadoop | Container mit Hive und Hadoop|
airflow | Container mit Airflow|
mysql | Container mit Mysql Datenbank| https://hub.docker.com/repository/docker/as14df/mysql
webapp | Container mit NodeJs Webseite| https://hub.docker.com/repository/docker/as14df/node-web-app

### Ordner und Dateien

asds|hghj|df|sdf
---|----|---|---
Airflow | Beinhaltet alle Dags und Operatoren | |
| address_validation.py | Beinhaltet den DAG |
| hdfs_operators.py | Definiert alle vorhandenen Operatoren |
| hdfs_put_operator.py | Kopier alle Csv-Dateien und alle Länder-Ordner ins HDFS |
| zip_file_operator.py | Entpackt eine Zip-Datei |
Images | Beinhaltet Bilder für die README.md | |
SqlQueries | Beinhaltet alle DDL Sql-Queries | |
| Hive | Beinhaltet alle DDL Sql-Queries für Hive |
|| address_data.sql | Beinhaltet das Create Statement der address_data Tabelle
|| address_data_alter.sql | Beinhaltet das Alter Statement der address_data Tabelle
|| final_address_data.sql | Beinhaltet das Create Statement der final_address_data Tabelle
|| final_address_data_overwrite.sql | Beinhaltet das Insert Overwrite Statement der final_address_data Tabelle
| MySql | Beinhaltet alle DDL Sql-Queries für MySql |
|| final_address_data.sql | Beinhaltet das Create Statement der final_address_data Tabelle
WebApp | Beinhaltet die relevanten Dateien für die Webseite | |
| index.ejs | Beinhaltet den HTML Code der Webseite |
| server.js | Beinhaltet den Server Code der Webseite |
README.md | Beinhaltet die Dokumentation des Projekts ||


