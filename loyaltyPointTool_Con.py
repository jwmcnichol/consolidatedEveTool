import ESItutils
import pandas as pd
import requests
import write_csv
import pyodbc
import market_history_by_type_id
from execute_query import execute_query
import ESItutils
database = 'eve.SDEmount.full.Current'
server = 'localhost'
masterTable = 'industryCombined'

bpcIDQuery = """
        select iapBlueprintID, productName 
        FROM industryCombined
        WHERE productTypeID = ?
    """

##dbissues

# vexor_navy = 17843
# 17634	Caracal Navy Issue
# 17636	Raven Navy Issue
# 17703	Imperial Navy Slicer
# 17709	Omen Navy Issue
# 17713	Stabber Fleet Issue
# 17715	Gila
# 17718	Phantasm
# 17720	Cynabal
# 17722	Vigilant
# 17726	Apocalypse Navy Issue

gallente_ships = [
    17728,
    17841,
    17843,
    29344,
    32307,
    33151,
    37456,
    72869,
    73796
]


# {'average': 47365000.0, 'date': '2024-12-06', 'highest': 48340000.0, 'lowest': 46000000.0, 'order_count': 51, 'volume': 54}

def lpMain():
    publish_dict = {}
    type_ids_list = type_ids_input()
    for type_id in type_ids_list:
        history_data = market_history_by_type_id.most_recent_data(type_id)
        finished_product_cost = history_data['average']
        bpc_xwalk_id = get_bpc_id_from_product_ID(type_id)
        bpc_type_id = bpc_xwalk_id[0]
        typeName = bpc_xwalk_id[1]
        mats_cost_array = find_mats_cost(bpc_type_id)
        mats_cost_value = sum(mats_cost_array["rowValue"])
        bpc_type_id = bpc_lookup(type_id)
        bpc_values = type_id_lp_store_lookup(bpc_type_id)
        bpc_lp_value = bpc_values[0]
        bpc_isk_value = bpc_values[1]
        total_cost = mats_cost_value + bpc_isk_value
        lp_derived_value = (finished_product_cost - total_cost) / bpc_lp_value
        print('ITEM:        ', typeName)
        print('JITA PRICE:  ', finished_product_cost)
        print('JITA VOL:    ', history_data['volume'])
        # print('BP ISK COST: ', bpc_isk_value)
        # print('BP LP COST:  ', bpc_lp_value)
        # print('MATS COST:   ', mats_cost_value)
        # print('ISK COST SUM ', mats_cost_value + bpc_isk_value)
        # print('(', finished_product_cost, "-", total_cost, ')', '/', bpc_lp_value)
        print('LP PREMIUM   ', lp_derived_value)
        # publish_dict[typeName]=lp_derived_value
    for key in publish_dict:
        print(f"item: {key}, derived lp value: {publish_dict[key]}")


def type_ids_input():
    check_for_list = input('use a list? yn')
    if check_for_list == 'y':
        list_names = {
            '1': gallente_ships
        }
        for number in list_names:
            print(f"Key: {number}, Value: {list_names[number]}")
        choice = input('press the number')
        type_ids = list_names[choice]
        return type_ids
    else:
        type_ids = []
        while (input_loop := input('enter id. x to stop/send: ').strip().lower()) != 'x':
            type_ids.append(input_loop)
        return type_ids


def find_mats_cost(bpc_xwalk_id):
    mats_df = get_material_ids_from_db(bpc_xwalk_id)
    price_array = get_price_array(mats_df)
    mats_total_value = compute_mats_value(price_array)
    return mats_total_value


def compute_mats_value(price_array):
    price_array["rowValue"] = price_array["materialQty"] * price_array["materialPrice"]
    return price_array


bpcIDQuery = """
        select iapBlueprintID, productName 
        FROM industryCombined
        WHERE productTypeID = ?
    """


def get_bpc_id_from_product_ID(type_id):
    print(bpcIDQuery)
    bpc_data = (execute_query(server, database, bpcIDQuery, params=(type_id,)))

    print(bpc_data)
    bpc_id = bpc_data[0][0]
    bpc_name = bpc_data[0][1]
    return bpc_id, bpc_name


def get_price_array(mats_df):
    prices = []
    for material in mats_df["materialTypeID"]:
        material_price = ESItutils.get_esi_type_id_price(material)
        prices.append(material_price)
    mats_df["materialPrice"] = prices
    # print(mats_df, 'from get price array')
    return mats_df


def get_material_ids_from_db(type_id):
    table = 'industryCombined'
    query = f"""
                 SELECT materialTypeID, materialQty, productName
                 FROM {table}
                 WHERE iapBlueprintID = {type_id}
                 and materialTypeID NOT IN (888888, 999999)
                 """
    conn_str = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Trusted_Connection=yes;"
    )
    try:
        with pyodbc.connect(conn_str) as conn:
            df = pd.read_sql(query, conn)
            return df
    except Exception as e:
        print(f"i sleep: {e}")
        return []





def fetch_loyalty_offers(corporation_id):
    endpoint = f"https://esi.evetech.net/dev/loyalty/stores/{corporation_id}/offers/"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for corporation ID {corporation_id}: {e}")
        return None
    try:
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return [row for row in result]  # Convert result to a list of tuples

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return []


def bpc_lookup(type_id):
    query = """
                SELECT 
                iapBlueprintID
                FROM industryCombined
                WHERE productTypeID = ?
            """
    conn_str = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Trusted_Connection=yes;"
    )
    try:
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (type_id,))  # Use ? as the placeholder
                result = cursor.fetchone()
                if result:
                    # print(result)
                    return result[0]  # Return the first column of the result
                else:
                    return None  # Return None if no result found
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return None


def type_id_lp_store_lookup(type_id):
    query = """
                  SELECT lp_cost, isk_cost
                  FROM lpOffersFW
                  WHERE type_ID = ?
                  AND isk_cost > 0
              """
    conn_str = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Trusted_Connection=yes;"
    )
    try:
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (type_id,))  # Use ? as the placeholder
                result = cursor.fetchone()
                if result:
                    # print(result)
                    return list(result)  # Return the first column of the result
                else:
                    return None  # Return None if no result found
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return None


def retrieve_lp_offers():
    corps = {
        "corporations": [
            {"id": 1000181, "name": "Federal Defense Union"},
            {"id": 1000179, "name": "24th Imperial Crusade"},
            {"id": 1000180, "name": "State Protectorate"},
            {"id": 1000182, "name": "Tribal Liberation Force"},
            {"id": 1000436, "name": "Malakim Zealots"},
            {"id": 1000437, "name": "Commando Guri"},

        ]
    }
    all_offers = []
    for corp in corps["corporations"]:
        corp_id = corp["id"]
        corp_name = corp["name"]
        print(f"Fetching offers for: {corp_name} (ID: {corp_id})")
        offers = fetch_loyalty_offers(corp_id)
        if offers:
            for offer in offers:
                offer["corporation_name"] = corp_name
                offer["corporation_id"] = corp_id
                all_offers.append(offer)
    if all_offers:
        df = pd.DataFrame(all_offers)
        print("\nCollected Data:")
        print(df.head())
        ESItutils.write_csv(df)
    else:
        print("\nNo data collected.")


