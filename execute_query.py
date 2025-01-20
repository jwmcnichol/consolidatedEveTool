


def execute_query(server, database, query, params):
    import pyodbc
    conn_str = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Trusted_Connection=yes;"
    )

    try:
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                # print(result)
                return [row for row in result]  # Convert result to a list of tuples

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return []