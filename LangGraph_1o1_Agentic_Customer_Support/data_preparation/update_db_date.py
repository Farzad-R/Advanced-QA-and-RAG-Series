import shutil
import sqlite3
import pandas as pd
from pyprojroot import here
from IPython.display import display


def update_dates(file: str, backup_file: str):
    """
    Update date fields in the flights and bookings tables to current time.

    This function copies a backup of the SQLite database file, reads the data from
    the flights and bookings tables, calculates the difference between the most recent
    flight departure time and the current time, and shifts all date fields accordingly.

    Args:
        file (str): Path to the SQLite database file to update.
        backup_file (str): Path to the backup SQLite database file.

    Returns:
        None: The function modifies the database in-place.
    """
    # Convert the flights to present time for our tutorial
    shutil.copy(backup_file, file)
    conn = sqlite3.connect(file)
    cursor = conn.cursor()

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    ).name.tolist()
    tdf = {}
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)

    example_time = pd.to_datetime(
        tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)
    ).max()
    print("example_time:", example_time)
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)
    print("current_time:", current_time)
    time_diff = current_time - example_time
    print("time_diff:", time_diff)

    tdf["bookings"]["book_date"] = (
        pd.to_datetime(tdf["bookings"]["book_date"].replace(
            "\\N", pd.NaT), utc=True)
        + time_diff
    )

    datetime_columns = [
        "scheduled_departure",
        "scheduled_arrival",
        "actual_departure",
        "actual_arrival",
    ]
    display(tdf["flights"][datetime_columns].head())
    for column in datetime_columns:
        tdf["flights"][column] = (
            pd.to_datetime(tdf["flights"][column].replace(
                "\\N", pd.NaT)) + time_diff
        )

    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        display(df.head())
    del df
    del tdf
    conn.commit()
    conn.close()

    return file


if __name__ == "__main__":

    local_file = here("data/travel2.sqlite")
    # The backup lets us restart for each tutorial section
    backup_file = here("data/travel2.backup.sqlite")
    update_dates(local_file, backup_file)
