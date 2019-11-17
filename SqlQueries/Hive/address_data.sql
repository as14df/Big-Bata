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