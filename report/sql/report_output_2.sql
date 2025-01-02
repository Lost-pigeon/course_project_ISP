SELECT contract_num, first_name, last_name,  sum_balance
FROM filippov_lab1.client_report
WHERE year = $reportYear AND month = $reportMonth;