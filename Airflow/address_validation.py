# -*- coding: utf-8 -*-

"""
Title: AddressValidationDag 
Author: Alessa Seeger Inf17084
Description: Practical Exam Big Data Duale Hochschule Baden-Wuerttemberg
"""

# --------------------------------------------------------------------------------
# Load The Dependencies
# --------------------------------------------------------------------------------

from datetime import datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.http_download_operations import HttpDownloadOperator
from airflow.operators.zip_file_operations import UnzipFileOperator
from airflow.operators.hdfs_operations import HdfsPutFileOperator, HdfsGetFileOperator, HdfsMkdirFileOperator, HdfsPutCsvOperator
from airflow.operators.filesystem_operations import CreateDirectoryOperator
from airflow.operators.filesystem_operations import ClearDirectoryOperator
from airflow.operators.hive_operator import HiveOperator
from airflow.operators.hive_to_mysql import HiveToMySqlTransfer
from airflow.operators.mysql_operator import MySqlOperator

import os

# --------------------------------------------------------------------------------
# set default arguments
# --------------------------------------------------------------------------------

coutry_list = ["at", "be", "cz", "de", "ee", "es", "fi", "gr", "it", "lt", "lu", "nl", "pl", "pt", "se", "si", "sk"];

args = {
    'owner': 'airflow'
}

dag = DAG(
        dag_id='address_validation_dag',
        default_args=args,
        description='AddressValidation Import',
        schedule_interval='56 18 * * *',
        start_date=datetime(2019, 11, 11), catchup=False, max_active_runs=1)

# --------------------------------------------------------------------------------
# remove import directory if exists
# --------------------------------------------------------------------------------

rm_local_import_dir = BashOperator(
    task_id='rm_local_import_dir',
    bash_command=os.path.join('rm -rf /home/airflow/openaddresses'),
    dag=dag,
)

# --------------------------------------------------------------------------------
# create import directory
# --------------------------------------------------------------------------------

create_local_import_dir = BashOperator(
    task_id='create_local_import_dir',
    bash_command= os.path.join('mkdir -p /home/airflow/openaddresses/'),
    dag=dag,
)

rm_local_import_dir >> create_local_import_dir

# --------------------------------------------------------------------------------
# download address data
# --------------------------------------------------------------------------------

download_address_data = HttpDownloadOperator(
    task_id='download_address_data',
    download_uri='https://data.openaddresses.io./openaddr-collected-europe.zip',
    save_to=os.path.join('/home/airflow/openaddresses/openaddr-collected-europe.zip'),
    dag=dag,
)

create_local_import_dir >> download_address_data

# --------------------------------------------------------------------------------
# unzip address data
# --------------------------------------------------------------------------------

unzip_address_data = UnzipFileOperator(
    task_id='unzip_address_data',
    zip_file='/home/airflow/openaddresses/openaddr-collected-europe.zip',
    extract_to='/home/airflow/openaddresses/openaddr-collected-europe',
    dag=dag,
)

download_address_data >> unzip_address_data

# --------------------------------------------------------------------------------
# create table
# --------------------------------------------------------------------------------

create_table_address_data='''
CREATE EXTERNAL TABLE IF NOT EXISTS address_data(
    longitude STRING,
    latitude STRING,
    number STRING,
    street STRING,
    unit STRING,
    city STRING,
    district STRING,
    region STRING,
    postcode STRING,
    id INT,
    hash STRING
)
COMMENT 'Address Data'
PARTITIONED BY (partition_year int, partition_month int, partition_day int, partition_country string)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');
'''

create_hive_table_address_data = HiveOperator(
    task_id='create_hive_table_address_data',
    hql=create_table_address_data,
    hive_cli_conn_id='beeline',
    dag=dag)

unzip_address_data >> create_hive_table_address_data

dummy_op0 = DummyOperator(
    task_id='dummy0', 
    dag=dag)

dummy_op1 = DummyOperator(
    task_id='dummy1', 
    dag=dag)

dummy_op2 = DummyOperator(
    task_id='dummy2', 
    dag=dag)

for country in coutry_list:

    # --------------------------------------------------------------------------------
    # create hdfs directory
    # --------------------------------------------------------------------------------

    hadoop_path = os.path.join('/user/hadoop/openaddresses/raw/{{ macros.ds_format(ds, "%Y-%m-%d", "%Y")}}/{{ macros.ds_format(ds, "%Y-%m-%d", "%m")}}/{{ macros.ds_format(ds, "%Y-%m-%d", "%d")}}', country)
    
    print("create folder: " + hadoop_path)
    create_hdfs_address_data_dir = HdfsMkdirFileOperator(
            task_id='create_hdfs_address_data_dir_' + country,
            directory=hadoop_path,
            hdfs_conn_id='hdfs',
            dag=dag,
    )

    create_hive_table_address_data >> create_hdfs_address_data_dir
    create_hdfs_address_data_dir >> dummy_op0

    # --------------------------------------------------------------------------------
    # put all csv files to hdfs
    # --------------------------------------------------------------------------------

    airflow_path = os.path.join('/home/airflow/openaddresses/openaddr-collected-europe', country)

    hdfs_put_address_data = HdfsPutCsvOperator(
        task_id='hdfs_put_address_data_' + country,
        local_file=airflow_path,
        remote_file=hadoop_path,
        hdfs_conn_id='hdfs',
        dag=dag,
    )

    dummy_op0 >> hdfs_put_address_data
    hdfs_put_address_data >> dummy_op1

    # --------------------------------------------------------------------------------
    # add table partitions
    # --------------------------------------------------------------------------------

    hive_add_partition_address_data = HiveOperator(
        task_id='hive_add_partition_address_data_' + country,
        hql='''ALTER TABLE address_data ADD IF NOT EXISTS partition(partition_year={{ macros.ds_format(ds, "%Y-%m-%d", "%Y")}}, partition_month={{ macros.ds_format(ds, "%Y-%m-%d", "%m")}}, partition_day={{ macros.ds_format(ds, "%Y-%m-%d", "%d")}},'''+ "partition_country='" + country + "') LOCATION '/user/hadoop/openaddresses/raw/"+ '''{{ macros.ds_format(ds, "%Y-%m-%d", "%Y")}}/{{ macros.ds_format(ds, "%Y-%m-%d", "%m")}}/{{ macros.ds_format(ds, "%Y-%m-%d", "%d")}}/''' + country + "/';",
        hive_cli_conn_id='beeline',
        dag=dag)

    dummy_op1 >> hive_add_partition_address_data
    hive_add_partition_address_data >> dummy_op2

# --------------------------------------------------------------------------------
# create final table
# --------------------------------------------------------------------------------

create_table_final_address_data='''
CREATE TABLE IF NOT EXISTS final_address_data(
    number STRING,
    street STRING,
    city STRING,
    postcode STRING,
    hash STRING,
    country STRING
)COMMENT 'Final Address Data'
'''

create_hive_table_final_address_data = HiveOperator(
    task_id='create_hive_table_final_address_data',
    hql=create_table_final_address_data,
    hive_cli_conn_id='beeline',
    dag=dag)

dummy_op2 >> create_hive_table_final_address_data

# --------------------------------------------------------------------------------
# insert overwrite final table
# --------------------------------------------------------------------------------

insertoverwrite_final_address_data='''
INSERT OVERWRITE TABLE final_address_data
SELECT
    number,
    street,
    city,
    postcode,
    hash,
    partition_country
FROM
    address_data
WHERE
    partition_year = {{ macros.ds_format(ds, "%Y-%m-%d", "%Y")}} and partition_month = {{ macros.ds_format(ds, "%Y-%m-%d", "%m")}} and partition_day = {{ macros.ds_format(ds, "%Y-%m-%d", "%d")}};
'''

hive_insert_overwrite_final_address_data = HiveOperator(
    task_id='hive_insert_overwrite_final_address_data',
    hql=insertoverwrite_final_address_data,
    hive_cli_conn_id='beeline',
    dag=dag)

create_hive_table_final_address_data >> hive_insert_overwrite_final_address_data

# --------------------------------------------------------------------------------
# create table remote
# --------------------------------------------------------------------------------

create_table_remote = MySqlOperator(
    task_id='create_table_remote',
    sql="CREATE TABLE IF NOT EXISTS final_address_data(number varchar(255),street varchar(255),city varchar(255),postcode varchar(255),hash varchar(255),country varchar(255));",
    mysql_conn_id='mysql_default',
    database='db'
)

hive_insert_overwrite_final_address_data >> create_table_remote

# --------------------------------------------------------------------------------
# clear table remote
# --------------------------------------------------------------------------------

delete_from_remote = MySqlOperator(
    task_id='delete_from_remote',
    sql="DELETE FROM final_address_data;",
    mysql_conn_id='mysql_default',
    database='db'
)

create_table_remote >> delete_from_remote

# --------------------------------------------------------------------------------
# copy table to remote
# --------------------------------------------------------------------------------

previous_task = delete_from_remote
for country in coutry_list:

    hive_to_mysql = HiveToMySqlTransfer(
    task_id='hive_to_mysql_' + country,
    sql="select * from default.final_address_data where country like '" + country + "'",
    hiveserver2_conn_id='hiveserver2',
    mysql_table='db.final_address_data',
    mysql_conn_id='mysql_default',
    )
    previous_task >> hive_to_mysql
    previous_task = hive_to_mysql