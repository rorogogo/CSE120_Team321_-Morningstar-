-- This much time is left between shipping order issue and required delevery deadline:
SELECT '';
SELECT 'all averages';
SELECT '';
SELECT 
  AVG(advise_prior_work_days) AS avg_advise_prior_days
FROM shipments
WHERE advise_prior_work_days IS NOT NULL;
SELECT '';

SELECT '';
SELECT 'each sender warehouse average';
SELECT '';
SELECT 
  ship_from_warehouse,
  COUNT(*) AS total_shipments,
  ROUND(AVG(advise_prior_work_days), 2) AS avg_advise_prior_days
FROM shipments
WHERE advise_prior_work_days IS NOT NULL
GROUP BY ship_from_warehouse
ORDER BY avg_advise_prior_days DESC;

--SELECT 
  --ship_from_warehouse,
  --AVG(advise_prior_work_days) AS avg_advise_prior_days
--FROM shipments
--WHERE advise_prior_work_days IS NOT NULL
--GROUP BY ship_from_warehouse
--ORDER BY avg_advise_prior_days DESC;
SELECT '';

SELECT '';
SELECT '===== HOT LOAD COUNT BY YEAR =====';
SELECT '';

SELECT
  SUBSTR(requested_ship_date, -4) AS ship_year,
  COUNT(*) AS total_hot_loads
FROM shipments
WHERE hot_load = 1
GROUP BY ship_year
ORDER BY ship_year;

SELECT '';

SELECT '';
SELECT '===== HOT LOAD COUNT BY SENDER WAREHOUSE =====';
SELECT '';

SELECT
  ship_from_warehouse AS warehouse,
  COUNT(*) AS total_hot_loads
FROM shipments
WHERE hot_load = 1
GROUP BY ship_from_warehouse
ORDER BY total_hot_loads DESC;

SELECT '';

SELECT '';
SELECT '===== HOT LOAD COUNT BY RECEIVER (SHIP TO NAME) =====';
SELECT '';

SELECT
  ship_to_name_first_line AS receiver,
  COUNT(*) AS total_hot_loads
FROM shipments
WHERE hot_load = 1
GROUP BY ship_to_name_first_line
ORDER BY total_hot_loads DESC;

SELECT '';

SELECT '';
SELECT '===== PERCENTAGE OF HOT LOADS BY YEAR =====';
SELECT '';

SELECT
  SUBSTR(requested_ship_date, -4) AS ship_year,
  COUNT(*) AS total_shipments,
  SUM(CASE WHEN hot_load = 1 THEN 1 ELSE 0 END) AS hot_loads,
  ROUND(
    100.0 * SUM(CASE WHEN hot_load = 1 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS percent_hot_loads
FROM shipments
WHERE requested_ship_date IS NOT NULL
GROUP BY ship_year
ORDER BY ship_year;

SELECT '';

SELECT '';
SELECT '===== PERCENTAGE OF HOT LOADS BY SENDER WAREHOUSE =====';
SELECT '';

SELECT
  ship_from_warehouse AS warehouse,
  COUNT(*) AS total_shipments,
  SUM(CASE WHEN hot_load = 1 THEN 1 ELSE 0 END) AS hot_loads,
  ROUND(
    100.0 * SUM(CASE WHEN hot_load = 1 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS percent_hot_loads
FROM shipments
GROUP BY ship_from_warehouse
ORDER BY percent_hot_loads DESC;

SELECT '';

SELECT '';
SELECT '===== PERCENTAGE OF HOT LOADS BY RECEIVER (SHIP TO NAME) =====';
SELECT '';

SELECT
  ship_to_name_first_line AS receiver,
  COUNT(*) AS total_shipments,
  SUM(CASE WHEN hot_load = 1 THEN 1 ELSE 0 END) AS hot_loads,
  ROUND(
    100.0 * SUM(CASE WHEN hot_load = 1 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS percent_hot_loads
FROM shipments
GROUP BY ship_to_name_first_line
ORDER BY percent_hot_loads DESC;

SELECT '';

