### Create the sqlite databases from your .sql/csv/xlsx files.

1. To prepare the SQL DB from a `.sql` file, Copy the file into `data/sql` directory and in the terminal, from the project folder, execute:
```
sudo apt install sqlite3
```

Now create a database called `sqldb`:
```
sqlite3 data/sqldb.db
.read data/sql/<name of your sql database>.sql
```
Example:
```
.read data/sql/Chinook_Sqlite.sql
```

This command will create a SQL database named `sqldb.db` in the `data` directory. Verify that it created the database
```
SELECT * FROM <any Table name in your sql database> LIMIT 10;
```
Example:
```
SELECT * FROM Artist LIMIT 10;
```

2. To prepare a SQL DB from your CSV and XLSX files, copy your files in `data/csv_xlsx` and in the terminal, from the project folder, execute:
```
python src/prepare_csv_xlsx_sqlitedb.py
```

This command will create a SQL database named `csv_xlsx_sqldb.db` in the `data` directory.

3. To prepare a vectorDB from your CSV and XLSX files, copy your files in `data/for_upload` and in the terminal, from the project folder, execute:
```
python src/prepare_csv_xlsx_vectordb.py
```
