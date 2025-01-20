import os
import pyodbc
import requests
import ast
import region_lists


def all_market_data(type_id):
    data = get_market_history(type_id, region_id=10000002)
    return data


def execute_query(server, database, query, params):
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
                return [row for row in result]  # convert rows to tuples
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return []


def get_esi_type_id_price(type_id, region_id=10000002):
    base_url = "https://esi.evetech.net/latest/markets/{}/orders/"
    query_params = {
        'datasource': 'tranquility',
        'order_type': 'sell',
        'page': 1
    }
    url = base_url.format(region_id)
    query_params['type_id'] = type_id
    response = requests.get(url, params=query_params)
    response.raise_for_status()
    orders = response.json()
    if orders:
        min_price = min(order['price'] for order in orders)

    else:
        min_price = None
    return min_price


def get_file_name():
    file_name_string = input('Enter file name with extension: ')
    # print('dynamic naming disabled in debug')
    # file_name_string = 'allNoduleHistoriesJita.csv'
    return file_name_string


def get_market_history(type_id, region_id=10000002):
    print(type_id)
    url = f"https://esi.evetech.net/latest/markets/{region_id}/history/?type_id={type_id}"
    response = requests.get(url)
    response.raise_for_status()
    print(response)
    return response.json()


def get_multiple_market_histories(type_ids, region_id=10000002):
    counter = 0
    print(type_ids, region_id)
    print("warning selected regions list may be corrupt, double check dict entries")
    histories = {}
    for type_id in type_ids:
        counter = counter + 1
        print(type_id, region_id, counter, "of", len(type_ids))
        try:
            histories[type_id] = get_market_history(type_id, region_id)
        except requests.HTTPError as e:
            print(f"Failed to fetch data for type ID {type_id}: {e}")
    return histories


def most_recent_data(type_id):
    history_entries = all_market_data(type_id)
    history_len = len(history_entries) - 1
    most_recent_entry = history_entries[history_len]
    print(most_recent_entry)
    return most_recent_entry


def process_market_data(histories, region):
    print(histories)
    all_data = []
    for type_id, history in histories.items():
        for entry in history:
            entry['type_id'] = type_id
            all_data.append(entry)
    df = pd.DataFrame(all_data)
    df['Region'] = region
    # write_csv(df)
    print(df)
    return df


def split_list(input_list, segment_size):
    if segment_size <= 0:
        raise ValueError("Segment size must be positive.")
    print(input_list)
    return [input_list[i:i + segment_size] for i in range(0, len(input_list), segment_size)]


def write_csv(df):
    directory_path = 'C:/Users/jwmcn/Downloads/'
    file_name = get_file_name()
    file_path = os.path.join(directory_path, file_name)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print('deketed old file')
        except OSError as e:
            print(f"Error deleting {file_name}: {e}")
    csv_file_path = file_path
    df.to_csv(csv_file_path, index=False)
    print("dataframe completed")
    print("dataframe parsed")
    print("wrote csv to disk")
    print("locatiom =", csv_file_path)
    return file_name


def write_json_to_csv(market_df):
    directory_path = 'C:/Users/jwmcn/Downloads/'
    file_name = 'currentStructureOrders.csv'
    file_path = os.path.join(directory_path, file_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print('deketed old file')
        except OSError as e:
            print(f"Error deleting {file_name}: {e}")
    csv_file_path = file_path
    market_df.to_csv(csv_file_path, index=False)
    print("dataframe completed")
    print("dataframe parsed")
    print("wrote csv to disk")


def enumerate_function_returns(file_path=None):
    if file_path is None:
        file_path = os.path.abspath(__file__)
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
    function_returns = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            return_type = "None"
            for body_node in ast.walk(node):
                if isinstance(body_node, ast.Return) and body_node.value:
                    return_type = type(body_node.value).__name__
                    break
            function_returns.append((function_name, return_type))
    return function_returns


def list_lists_in_module(module):
    lists_found = [
        name for name, obj in vars(module).items()
        if isinstance(obj, list) and not name.startswith("__")
    ]
    return lists_found


def list_dicts_in_module(module):
    dicts_found = [
        name for name, obj in vars(module).items()
        if isinstance(obj, dict) and not name.startswith("__")
    ]
    for name in dicts_found:
        print(name)
    return dicts_found


def func_enum():
    functions = enumerate_function_returns()  # Analyze the current script
    for func_name, ret_type in functions:
        print(f"Function: {func_name}, Returns: {ret_type}")


def get_active_type_ids(region_id):
    print('checking active orders for', region_id)
    url = f"https://esi.evetech.net/latest/markets/{region_id}/types/"
    params = {'page': 1}
    active_type_ids = []
    response = requests.get(url, params=params)
    response.raise_for_status()
    x_pages = int(response.headers.get('x-pages', 1))
    for page in range(1, x_pages + 1):
        print(f"Page: {page} of {x_pages}")
        params['page'] = page
        response = requests.get(url, params=params)
        if response.status_code == 200:
            active_type_ids.extend(response.json())
        else:
            print(f"Failed to fetch page {page}: {response.status_code}")
            break
    print(len(active_type_ids), " active types found")
    # print(active_type_ids)
    return active_type_ids

def get_names_for_ids(type_ids):
    query_template = """
           SELECT typeID, typeName 
           FROM [eve.SDEmount.full.09202024].[dbo].[publishedShips0924]
           WHERE typeID IN ({})
       """
    ids_string = ', '.join(map(str, type_ids)) # becausse we have to stringify for IN
    query = query_template.format(ids_string)

    # Database connection details
    server = 'localhost'
    database = 'eve.SDEmount.full.09202024'


    try:
        result = execute_query(server, database, query)
        return result
    except Exception as e:
        print(f"Error fetching names for IDs: {e}")
        return []

# func_enum()
