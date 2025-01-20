import requests
from requests_oauthlib import OAuth2Session
import pandas as pd
import os
client_id = '447925756fd74ca2abb84d395899ab5a'
client_secret = 'X3o20yXaFA25AmvwSsF6vGJKtUINLgHIUgqUVDu4'
base_url = "https://esi.evetech.net/latest/"
# structure_id = 1043929239463 #azbel
scopes = ['esi-markets.structure_markets.v1']
structure_page_number = 1
structure_page_size = 1000
# region_directory_path = 'C:/Users/jwmcn/Downloads/'
import getAccessToken
import write_json_to_csv
import os


def get_structure_orders(structure_id):
    access_token = getAccessToken.get_access_token(client_id,client_secret,scopes)
    endpoint_url = f"{base_url}markets/structures/{structure_id}/"
    market_df = send_structure_get(access_token, endpoint_url)
    write_json_to_csv.write_json_to_csv(market_df)

def send_structure_get(access_token, endpoint_url):
    df = pd.DataFrame()

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'page': structure_page_number
    }
    response = requests.get(endpoint_url, params=params, headers=headers)
    xpages = int(response.headers.get('x-pages')) + 1
    container_list = []
    for i in range(0, xpages):
        params = {
            'page': i
        }
        response = requests.get(endpoint_url, params=params, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            for item in response_json:
                container_list.append(item)
    df_out = pd.DataFrame(container_list)
    return df_out

def function_select(function):
    if function in functions_menu_list:
        result = functions_menu_list[function]()
        return result
    else:
        return "Brrt."


def structure_flow():
    chosen_structure_id = structure_select()
    get_structure_orders(chosen_structure_id)


def structure_select():
    for k,v in structure_menu_dict.items():
        print(k, v)
    structure_menu_input = input("Enter number: ")
    structure_id_map = structure_menu_dict[structure_menu_input]
    structure_id_choice = structure_ids_dict[structure_id_map]
    print("picked structure name: ", structure_id_map, "id: ", structure_id_choice)
    return structure_id_choice


def start():
    while True:
        for key, value in functions_menu_list.items():
            print(f"{key}: {value}")
        function_choice = input("Press a number: ")
        picked_function = function_select(function_choice)
        print(picked_function)


def region_flow():
    region_picked = region_input()
    file_name = f"{region_picked[1]}Orders.csv"
    specify_type_choice = input('specify type? yn')
    if specify_type_choice == 'y':
        specified_type = int(input('enter type_id:'))
        orders_data = get_region_orders_for_type(region_picked[0], specified_type)
        # refactor to accomodate list
    else:
        orders_data = get_region_orders(region_picked[0])
    orders_df = pd.DataFrame(orders_data)
    write_json_to_csv.write_json_to_csv(orders_df)

def region_input():
    try:
        for key, value in regions_dict.items():
            print(f"{key}: {value}")
        region_choice = input("Enter name of region ")
        region_choice_value = regions_dict[region_choice]
        print(region_choice_value, " picked")
        return region_choice_value, region_choice
    except KeyError:
        print("Invalid region name, attention to details is important")
        return


def get_region_orders(region_id):
    url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/"
    print(url)
    region_page_number = 1
    params = {
        'page': region_page_number
    }
    response = requests.get(url, params=params)
    print(response)
    xpages = int(response.headers.get('x-pages')) + 1
    print(xpages)
    container_list = []
    for i in range(0, xpages):
        params = {
            'page': i
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            response_json = response.json()
            for item in response_json:
                container_list.append(item)
    df_out = pd.DataFrame(container_list)
    return df_out

test_list = [18, 19, 20]


def get_region_orders_for_list(region_id, type_id_list): #redo
    url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/"
    print(url)
    region_page_number = 1
    params = {
        'page': region_page_number
    }
    response = requests.get(url, params=params)
    print(response)
    xpages = int(response.headers.get('x-pages')) + 1
    print(xpages)
    container_list = []

    for i in range(0, xpages):
        params = {
            'page': i,
            'type_id': type_id
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            response_json = response.json()
            for item in response_json:
                print(item)
                container_list.append(item)
    df_out = pd.DataFrame(container_list)
    return df_out


def get_region_orders_for_type(region_id, type_id):
    url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/"
    print(url)
    region_page_number = 1
    params = {
        'page': region_page_number
    }
    response = requests.get(url, params=params)
    print(response)
    xpages = int(response.headers.get('x-pages')) + 1
    print(xpages)
    container_list = []
    for i in range(0, xpages):
        params = {
            'page': i,
            'type_id': type_id
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            response_json = response.json()
            for item in response_json:
                print(item)
                container_list.append(item)
    df_out = pd.DataFrame(container_list)
    return df_out


functions_menu_list = {
        '1': region_flow,
        '2': structure_flow,
        # 2'3': get_by_system,
}

structure_ids_dict = {
    'actee_azbel': 1043929239463,
    'actee_athanor': 1043929283669
}

structure_menu_dict = {
    '1': 'actee_azbel',
    '2': 'actee_athanor'
}

regions_dict = {
                'A-R00001': '11000001',
                'A-R00002': '11000002',
                'A-R00003': '11000003',
                'A821-A': '10000019',
                'ADR01': '12000001',
                'ADR02': '12000002',
                'ADR03': '12000003',
                'ADR04': '12000004',
                'ADR05': '12000005',
                'Aridia': '10000054',
                'B-R00004': '11000004',
                'B-R00005': '11000005',
                'B-R00006': '11000006',
                'B-R00007': '11000007',
                'B-R00008': '11000008',
                'Black Rise': '10000069',
                'Branch': '10000055',
                'C-R00009': '11000009',
                'C-R00010': '11000010',
                'C-R00011': '11000011',
                'C-R00012': '11000012',
                'C-R00013': '11000013',
                'C-R00014': '11000014',
                'C-R00015': '11000015',
                'Cache': '10000007',
                'Catch': '10000014',
                'Cloud Ring': '10000051',
                'Cobalt Edge': '10000053',
                'Curse': '10000012',
                'D-R00016': '11000016',
                'D-R00017': '11000017',
                'D-R00018': '11000018',
                'D-R00019': '11000019',
                'D-R00020': '11000020',
                'D-R00021': '11000021',
                'D-R00022': '11000022',
                'D-R00023': '11000023',
                'Deklein': '10000035',
                'Delve': '10000060',
                'Derelik': '10000001',
                'Detorid': '10000005',
                'Devoid': '10000036',
                'Domain': '10000043',
                'E-R00024': '11000024',
                'E-R00025': '11000025',
                'E-R00026': '11000026',
                'E-R00027': '11000027',
                'E-R00028': '11000028',
                'E-R00029': '11000029',
                'Esoteria': '10000039',
                'Essence': '10000064',
                'Etherium Reach': '10000027',
                'Everyshore': '10000037',
                'F-R00030': '11000030',
                'Fade': '10000046',
                'Feythabolis': '10000056',
                'Fountain': '10000058',
                'G-R00031': '11000031',
                'Geminate': '10000029',
                'Genesis': '10000067',
                'Great Wildlands': '10000011',
                'H-R00032': '11000032',
                'Heimatar': '10000030',
                'Immensea': '10000025',
                'Impass': '10000031',
                'Insmother': '10000009',
                'J7HZ-F': '10000017',
                'K-R00033': '11000033',
                'Kador': '10000052',
                'Khanid': '10000049',
                'Kor-Azor': '10000065',
                'Lonetrek': '10000016',
                'Malpais': '10000013',
                'Metropolis': '10000042',
                'Molden Heath': '10000028',
                'No Name': '13000001',
                'Oasa': '10000040',
                'Omist': '10000062',
                'Outer Passage': '10000021',
                'Outer Ring': '10000057',
                'Paragon Soul': '10000059',
                'Period Basis': '10000063',
                'Perrigen Falls': '10000066',
                'Placid': '10000048',
                'Pochven': '10000070',
                'Providence': '10000047',
                'Pure Blind': '10000023',
                'Querious': '10000050',
                'Scalding Pass': '10000008',
                'Sinq Laison': '10000032',
                'Solitude': '10000044',
                'Stain': '10000022',
                'Syndicate': '10000041',
                'Tash-Murkon': '10000020',
                'Tenal': '10000045',
                'Tenerifis': '10000061',
                'The Bleak Lands': '10000038',
                'The Citadel': '10000033',
                'The Forge': '10000002',
                'The Kalevala Expanse': '10000034',
                'The Spire': '10000018',
                'Tribute': '10000010',
                'UUA-F4': '10000004',
                'Vale of the Silent': '10000003',
                'Venal': '10000015',
                'Verge Vendor': '10000068',
                'VR-01': '14000001',
                'VR-02': '14000002',
                'VR-03': '14000003',
                'VR-04': '14000004',
                'VR-05': '14000005',
                'Wicked Creek': '10000006'
                }


# main()

# get_region_orders_for_type(10000002, 18)