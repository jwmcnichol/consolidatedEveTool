import ordersTool_Con
import historyTool_Con


def market_history_tool():
    market_history_data = historyTool_Con.main()
    print(market_history_data)
    pass


def market_order_tool():
    market_order_data = ordersTool_Con.main()
    print(market_order_data)



def loyalty_point_tool():
    print("Running Loyalty Point Calculator...")
    # Add logic for loyalty point calculations here


def table_traverser_tool():
    print("Running Table Browser/Traverser...")
    # Add logic for table traversal and directed graph creation here


def intel_resolver_tool():
    print("Running Character/Corporation Intel Resolver...")
    # Add logic for character and corporation lookups here


def exit_tool():
    print("Exiting the tool suite. Fly safe!")
    return False  # Signal to exit the main loop



MENU = {
    "1": ("Market History Getter", market_history_tool),
    "2": ("Current Market Order Getter", market_order_tool),
    "3": ("Loyalty Point Calculator", loyalty_point_tool),
    "4": ("Table Browser/Traverser (Directed Graphs)", table_traverser_tool),
    "5": ("Character/Corporation Intel Resolver", intel_resolver_tool),
    "0": ("Exit", exit_tool),
}


def display_menu():

    print("\n=== EVE Online ESI Tool Suite ===")
    for key, (description, _) in MENU.items():
        print(f"{key}. {description}")


def main_a():
    print('fired 1')
    while True:
        print('fired')
        display_menu()
        choice = input("Select an option: ")
        action = MENU.get(choice)

        if action:
            _, func = action
            if func() is False:  # Check for exit signal
                break
        else:
            print("try again")


# Entry Point
# if __name__ == "__main__":
#     main_a()

main_a()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# market orders
# needs to know which items to look for
# needs lists
# needs to know what kind of orders
# structure
# needs scopes
# meeds list of structures

# region
# needs list of regions
# output is df
