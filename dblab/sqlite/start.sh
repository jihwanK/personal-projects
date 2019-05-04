#!/bin/bash

while read line;
do
    #echo $line
    #python main.py $line $line
    sqlite3 example.db $line
    #echo $result $line > result
done < input.sql
