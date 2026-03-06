SELECT
    ship_to_customer_id,
    product,

    strftime('%Y-%m',
        substr(substr(requested_ship_date,6),7,4) || '-' ||
        substr(substr(requested_ship_date,6),1,2) || '-' ||
        substr(substr(requested_ship_date,6),4,2)
    ) AS month,

    SUM(containers_shipped) AS demand

FROM shipments

GROUP BY
    ship_to_customer_id,
    product,
    month

ORDER BY
    ship_to_customer_id,
    product,
    month;