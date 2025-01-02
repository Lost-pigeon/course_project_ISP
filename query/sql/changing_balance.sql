SELECT
    c.First_name,
    c.Last_name,
    bsh.Balance_change_date,
    bsh.New_balance,
    bsh.Old_balance,
    bsh.Status_balance
FROM
    contract c
JOIN
    balance_sheet_history bsh
    ON c.Contract_num = bsh.B_Contract_num
WHERE
    c.Contract_num = $prod_category
ORDER BY
    bsh.Balance_change_date DESC;
