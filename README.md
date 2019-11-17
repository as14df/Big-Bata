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
* Extrahieren der nötigen Daten in eine neue Hive-Tabelle (Land, Stadt, Postleitzahl, Straße, Hausnummer)
* Exportieren der Hive-Tabelle in eine MySql-Datenbank
* Validierung der Daten durch eine NodeJs-Webseite mit Zugriff auf die MySql-Datenbank

![Alt text](Images/workflow.png "Workflow")

### Airflow Tasks

Im Folgenden werden die jeweiligen Airflow Tasks beschrieben, mit welchen der o.g. Ablauf implementiert wird

Task | Beschreibung
----------- | -------
rm_local_import_dir | Löscht den import Ordner "/home/airflow/openaddresses/" falls vorhanden
create_local_import_dir | Erstellt einen neuen import ordner "/home/airflow/openaddresses/"
download_address_data | Lädt die Daten als Zip-datei herunter "/home/airflow/openaddresses/openaddr-collected-europe.zip"
unzip_adress_data | Entpackt die Zip-Datei in den Ordner "/home/airflow/openaddresses/openaddr-collected-europe"
create_hive_table_address_data | Erstellt die Hive Tabelle "address_data" für die Address Daten, die nach Jahr, Monat, Tag, Land partitioniert ist
create_hdfs_address_data_dir_X | Erstellt für jedes Land einen Ordner im HDFS mit dem Schema "/user/hadoop/openaddresses/raw/*Jahr*/*Monat*/*Tag*/*Land*"
dummy0 | Wartet, bis alle Ordner erstellt wurden
hdfs_put_address_data_*Land* | Kopiert alle Csv-Dateien aus jedem Ordner in den jeweiligen HDFS Ordner
dummy1 | Wartet, bis alle Daten ins HDFS kopier wurden
hive_add_partition_address_data_*Land* | Fügt den Inhalt jedes Ordners als partition in die Hive-Tabelle ein
dummy2 | Wartet, bis alle partitionen zur Hive-Tabelle hinzugefügt worden sind
create_hive_table_final_address_data | Erstellt die Tabelle "final_address_data", die die bereinigten Daten beinhalten wird
hive_insert_overwrite_final_address_data | Kopiert die spalten Country, City, Postcode, Street, Number, Hash in die Tabelle "final_address_data"
create_table_remote | Erstellt die Tabelle "final_address_data" in der Mysql Datenbank für die bereinigten Daten, falls noch nicht vorhanden
delete_from_remote | Löscht alle alten Daten aus der Tabelle "final_address_data" falls vorhanden
hive_to_mysql_*Land* | kopiert alle Daten aus der Hive Tabelle "final_address_data" nacheinander nach Ländern in die MySql tabelle "final_address_data" 

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

||     |     ||
|---|----|---|---|
|Airflow | Beinhaltet alle Dags und Operatoren | ||
|| address_validation.py | Beinhaltet den DAG ||
|| hdfs_operators.py | Definiert alle vorhandenen Operatoren ||
|| hdfs_put_operator.py | Kopiert alle Csv-Dateien und alle Länder-Ordner ins HDFS ||
|| zip_file_operator.py | Entpackt eine Zip-Datei ||
|Images | Beinhaltet Bilder für die README.md | ||
|SqlQueries | Beinhaltet alle DDL Sql-Queries | ||
|| Hive | Beinhaltet alle DDL Sql-Queries für Hive ||
||| address_data.sql | Beinhaltet das Create-Statement der address_data Tabelle|
||| address_data_alter.sql | Beinhaltet das Alter-Statement der address_data Tabelle|
||| final_address_data.sql | Beinhaltet das Create-Statement der final_address_data Tabelle|
||| final_address_data_overwrite.sql | Beinhaltet das Insert-Overwrite-Statement der final_address_data Tabelle|
|| MySql | Beinhaltet alle DDL Sql-Queries für MySql ||
||| final_address_data.sql | Beinhaltet das Create-Statement der final_address_data Tabelle|
|WebApp | Beinhaltet die relevanten Dateien für die Webseite | ||
|| index.ejs | Beinhaltet den HTML Code der Webseite ||
|| server.js | Beinhaltet den Server Code der Webseite ||
|README.md | Beinhaltet die Dokumentation des Projekts |||


