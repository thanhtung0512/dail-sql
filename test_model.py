import sqlite3

def get_sql_for_database(path_db=None, cur=None):
    close_in_func = False
    if cur is None:
        con = sqlite3.connect(path_db)
        cur = con.cursor()
        close_in_func = True

    # Get table names
    table_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    cur.execute(table_query)
    table_names = [row[0] for row in cur.fetchall()]
    print(f"✅ Tables found: {table_names}")

    column_names_original = []
    for tid, table_name in enumerate(table_names):
        pragma_query = f"PRAGMA table_info('{table_name}');"
        cur.execute(pragma_query)
        columns = cur.fetchall()
        print(f"🔍 Columns in table '{table_name}': {columns}")
        for col in columns:
            column_names_original.append((tid, col[1]))  # col[1] = column name

    if close_in_func:
        cur.close()

    return {
        "table_names_original": table_names,
        "column_names_original": column_names_original
    }

if __name__ == "__main__":
    # Replace with your actual path
    path_db = "./database/employees_db/employees_db.sqlite"

    schema = get_sql_for_database(path_db)
    print("\n🔑 Final schema:")
    print(schema)
