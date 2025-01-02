SELECT
    los.id_service AS id_service,
    los.Name_service,
    los.Internet_speed,
    los.Price_service
FROM list_of_services los
JOIN (
    SELECT
        ul.service_id,
        MAX(ul.list_id) AS max_list_id
    FROM user_list ul
    JOIN user_orders uo ON ul.order_id = uo.order_id
    WHERE uo.user_id = $user_id
    GROUP BY ul.service_id
) AS latest_services ON los.id_service = latest_services.service_id
JOIN user_list ul ON ul.service_id = latest_services.service_id AND ul.list_id = latest_services.max_list_id
WHERE ul.status_service = 1;
