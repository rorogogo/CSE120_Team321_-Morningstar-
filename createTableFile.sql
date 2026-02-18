DROP TABLE IF EXISTS shipments_raw;

CREATE TABLE shipments_raw (
  ship_category                       TEXT,
  ship_method                         TEXT,
  ship_from_plant_id                  TEXT,
  ship_from_warehouse                 TEXT,
  product_type                        TEXT,
  container_type                      TEXT,
  product                             TEXT,
  pack_years_shipped                  TEXT,
  po_number                           TEXT,
  ship_to_customer_id                 TEXT,
  hot_load                            TEXT,
  shipping_advise                     TEXT,
  ship_advise_date                    TEXT,
  requested_ship_date                 TEXT,
  advise_prior_to_req_ship_work_days  TEXT,
  bol_date                            TEXT,
  last_scanned_date                   TEXT,
  scanned_prior_to_req_ship_work_days TEXT,
  shipping_performance                TEXT,
  containers_shipped                  TEXT,
  num_scanned_containers              TEXT,
  lbs_shipped                         TEXT,
  carrier                             TEXT,
  ship_to_name_first_line             TEXT,
  ship_to_address_first_line          TEXT,
  ship_to_address_second_line         TEXT,
  ship_to_city                        TEXT,
  ship_to_state_code                  TEXT,
  ship_to_zip_code                    TEXT,
  ship_to_country                     TEXT
);

.mode csv
.import --skip 1 '2023 to 111725 Shipping_History_wScanData.csv' shipments_raw

---------------------------CHATGPT GETS FULL CREDIT FROM HERE--------------------------------
DROP TABLE IF EXISTS shipments;

CREATE TABLE shipments (
  ship_category      TEXT,
  ship_method        TEXT,
  ship_from_plant_id TEXT,
  ship_from_warehouse TEXT,
  product_type       TEXT,
  container_type     TEXT,
  product            TEXT,
  pack_years_shipped TEXT,
  po_number          TEXT,
  ship_to_customer_id TEXT,
  hot_load           INTEGER,          -- YES/NO -> 1/0
  shipping_advise    TEXT,
  ship_advise_date   TEXT,             -- keep as TEXT unless you standardize dates
  requested_ship_date TEXT,
  advise_prior_work_days INTEGER,
  bol_date           TEXT,
  last_scanned_date  TEXT,
  scanned_prior_work_days INTEGER,
  shipping_performance TEXT,
  containers_shipped INTEGER,
  num_scanned_containers INTEGER,
  lbs_shipped        INTEGER,          -- commas removed
  carrier            TEXT,
  ship_to_name_first_line TEXT,
  ship_to_address_first_line TEXT,
  ship_to_address_second_line TEXT,
  ship_to_city       TEXT,
  ship_to_state_code TEXT,
  ship_to_zip_code   TEXT,
  ship_to_country    TEXT
);

INSERT INTO shipments (
  ship_category, ship_method, ship_from_plant_id, ship_from_warehouse,
  product_type, container_type, product, pack_years_shipped, po_number,
  ship_to_customer_id, hot_load, shipping_advise, ship_advise_date,
  requested_ship_date, advise_prior_work_days, bol_date, last_scanned_date,
  scanned_prior_work_days, shipping_performance, containers_shipped,
  num_scanned_containers, lbs_shipped, carrier, ship_to_name_first_line,
  ship_to_address_first_line, ship_to_address_second_line, ship_to_city,
  ship_to_state_code, ship_to_zip_code, ship_to_country
)
SELECT
  ship_category,
  ship_method,
  ship_from_plant_id,
  ship_from_warehouse,
  product_type,
  container_type,
  product,
  pack_years_shipped,
  po_number,
  ship_to_customer_id,
  CASE
    WHEN UPPER(TRIM(hot_load)) = 'YES' THEN 1
    WHEN UPPER(TRIM(hot_load)) = 'NO'  THEN 0
    ELSE NULL
  END AS hot_load,
  shipping_advise,
  ship_advise_date,
  requested_ship_date,
  CAST(REPLACE(REPLACE(advise_prior_to_req_ship_work_days, '(', ''), ')', '') AS INTEGER),
  bol_date,
  last_scanned_date,
  CAST(REPLACE(REPLACE(scanned_prior_to_req_ship_work_days, '(', ''), ')', '') AS INTEGER),
  shipping_performance,
  CAST(containers_shipped AS INTEGER),
  CAST(num_scanned_containers AS INTEGER),
  CAST(REPLACE(lbs_shipped, ',', '') AS INTEGER),
  carrier,
  ship_to_name_first_line,
  ship_to_address_first_line,
  ship_to_address_second_line,
  ship_to_city,
  ship_to_state_code,
  ship_to_zip_code,
  ship_to_country
FROM shipments_raw;

--Test
SELECT COUNT(*) FROM shipments_raw;
SELECT COUNT(*) FROM shipments;

SELECT ship_category, carrier, containers_shipped, lbs_shipped
FROM shipments
LIMIT 5;
