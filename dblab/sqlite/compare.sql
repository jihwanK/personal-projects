.header on
.mode column

SELECT * FROM (SELECT name, day FROM CUSTOMERS LEFT JOIN RESERVATION USING (customer_id)) AS qwe
    WHERE NOT EXISTS (
        SELECT name, day FROM (SELECT name, day FROM CUSTOMERS LEFT JOIN RESERVATION USING (customer_id) ORDER BY name DESC) AS asd
        WHERE 
            CASE 
                WHEN qwe.name IS NULL AND asd.name IS NULL
                THEN 1
                WHEN qwe.name IS NULL AND asd.name IS NOT NULL
                THEN 0
                WHEN qwe.name IS NOT NULL AND asd.name IS NULL
                THEN 0
                ELSE qwe.name = asd.name
            END
);

