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