
import type_id_lists
import ESItutils
import queries_list
import requests
from allRegions import all_regions_dict
import region_lists
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

directory_path = 'C:/Users/jwmcn/Downloads/'


def history_tool_main_start():
    region_package = get_regions()
    type_id_package = type_id_selection(region_package)
    for item in type_id_package:
        print(item, 'in package')
    for item in region_package:
        print(item)
    master_df = retrieve_history_data(region_package, type_id_package)


def get_regions():
    regions_choice_menu_dict = {
        '1': 'From predefined set',
        '2': 'Manual Entry',
        '3': 'All regions'
    }
    for key, value in regions_choice_menu_dict.items():
        print(f"{key}: {value}")
    regions_config_choice = input('Choose region selection method: ')
    regions_choice_dispatch = {
        '1': use_region_set,
        '2': enter_regions,
        '3': use_all_regions
    }
    regions_output_raw = regions_choice_dispatch[regions_config_choice]()
    print('raw ', regions_output_raw)
    regions_output = list(regions_output_raw)
    print('Selected regions:', regions_output)
    print(regions_output)
    return regions_output


def enter_regions():
    regions_entered = []
    stop = 'x'
    while True:
        count = 0
        for key, value in all_regions_dict.items():
            print(f"{key:<20}\t{value:<10}", end="\t")
            count += 1
            if count % 3 == 0:
                print()
        picked_region = input("Enter a region ID: ")
        if picked_region == stop:
            break
        regions_entered.append(picked_region)
        print(regions_entered)
    return regions_entered


def use_all_regions():
    return list(all_regions_dict.values())


def use_region_set():
    ESItutils.list_dicts_in_module(region_lists)
    picked_set = input("Enter a set: ")
    chosen_regions = getattr(region_lists, picked_set)
    return chosen_regions


def enter_type_ids():
    type_ids_entered = []
    stop = 'x'
    while True:
        id_choice = input('Enter a typeID: ')
        if id_choice == stop:
            break
        type_ids_entered.append(id_choice)


def get_all_active_ids(regions):
    all_active_ids = []
    for region in regions:
        active_ids = ESItutils.get_active_type_ids(region)
        all_active_ids.extend(active_ids)
    return all_active_ids


def type_id_selection(region):
    types_choice_menu_dict = {
        '1': 'Preconfigured list',
        '2': 'Configure based on SQL Query',
        '3': 'All active ids in region(s) ',
        '4': 'Enter IDs manually '
    }
    for key, value in types_choice_menu_dict.items():
        print(f"{key}: {value}")
    list_config_choice = input('Choose list source: ')
    types_choice_dispatch = {
        '1': local_list_config,
        '2': query_list_from_db,
        '3': lambda: get_all_active_ids(region),
        '4': enter_type_ids
    }
    raw_type_id_output = types_choice_dispatch[list_config_choice]()
    return ESItutils.split_list(raw_type_id_output, 499)


def local_list_config():
    print('Configure local typeID list...')
    import inspect
    lists_in_type_id_lists = {
        name: value for name, value in inspect.getmembers(type_id_lists)
        if isinstance(value, list)
    }
    if not lists_in_type_id_lists:
        print("No lists found.")
        return None
    print("Available lists: ")
    for i, list_name in enumerate(lists_in_type_id_lists.keys(), 1):
        print(f"{i}. {list_name}")
    while True:
        try:
            choice = int(input("Enter number of list:  "))
            if 1 <= choice <= len(lists_in_type_id_lists):
                selected_list_name = list(lists_in_type_id_lists.keys())[choice - 1]
                selected_list = lists_in_type_id_lists[selected_list_name]
                print(f"Picked: {selected_list_name}")
                return selected_list
            else:
                print("Invalid selection. Please choose a number from the list.")
        except ValueError:
            print("Please enter a valid number.")


def query_list_from_db():  # update this hardcoded stuff
    query_names = ESItutils.list_lists_in_module(queries_list)
    for name in query_names:
        print(name)
    query_picked = input('enter name of query')
    queried_list = ESItutils.execute_query(query_picked[1], query_picked[2], query_picked[0], ())
    return ESItutils.split_list(queried_list, 499)


def retrieve_history_data(regions_set, ids_set):
    master_df = pd.DataFrame()
    start_time = datetime.now()
    total_counter = 0
    for region in regions_set:
        print(len(ids_set), 'query lists created')
        tr_counter = 0
        for type_list in ids_set:
            print('type_list is:', type_list)
            print('ids_set is:', ids_set)
            region_history = get_multiple_market_histories_parallel(type_list, region)
            loop_df = process_market_data(region_history, region)
            master_df = pd.concat([master_df, loop_df], ignore_index=True)
            tr_counter += 1
            total_counter += 1
            print(tr_counter, 'of', len(ids_set))
            print(total_counter)
    ESItutils.write_csv(master_df)
    print(f"Completed in: {datetime.now() - start_time}")


def get_multiple_market_histories_parallel(type_ids, region_id, max_threads=20):
    histories = {}
    start_time = datetime.now()
    with ThreadPoolExecutor(max_threads) as executor:
        future_to_type_id = {
            executor.submit(get_market_history, type_id, region_id): type_id
            for type_id in type_ids
        }
        for counter, future in enumerate(as_completed(future_to_type_id), start=1):  # create enumerate(
            type_id = future_to_type_id[future]
            try:
                histories[type_id] = future.result()
                print(
                    f"Fetched {counter}/{len(type_ids)}: TypeID {type_id} in Region {region_id} | Time: {datetime.now() - start_time}")
            except Exception as e:
                print(f"Failed to fetch TypeID {type_id}: {e}")
    return histories


def get_market_history(type_id, region_id=10000002):
    url = f"https://esi.evetech.net/latest/markets/{region_id}/history/?type_id={type_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def process_market_data(histories, region):
    all_data = []
    for type_id, history in histories.items():
        for entry in history:
            entry['type_id'] = type_id
            all_data.append(entry)
    df = pd.DataFrame(all_data)
    df['Region'] = region
    return df


def get_names_for_ids(type_ids):
    query_template = """
           SELECT typeID, typeName 
           FROM [eve.SDEmount.full.09202024].[dbo].[invTypes]
           WHERE typeID IN ({})
       """
    ids_string = ', '.join(map(str, type_ids))  # becausse we have to stringify for IN
    query = query_template.format(ids_string)
    server = 'localhost'
    database = 'eve.SDEmount.full.09202024'
    try:
        result = ESItutils.execute_query(server, database, query, params=None) # 0 params
        print(result)
        return result
    except Exception as e:
        print(f"Error fetching names for IDs: {e}")
        return []

# test_list = [17115, 34]
# get_names_for_ids(test_list)
history_tool_main_start()
