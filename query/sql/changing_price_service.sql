SELECT
    l.Name_service,
    s.Price_change_history AS Change_date,
    s.Old_price,
    s.New_price
FROM
    service_price_history s
JOIN
    list_of_services l ON s.id_Service_price_history = l.id_service
WHERE
    l.id_service = $prod_category