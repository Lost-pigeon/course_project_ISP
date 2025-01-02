SELECT id_service, name_service, connections, disconnections, month, year
FROM filippov_lab1.product_report
WHERE year = $reportYear AND month = $reportMonth;