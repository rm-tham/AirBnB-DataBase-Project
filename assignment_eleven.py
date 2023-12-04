""" This program asks the user for their name, politely greets them,
asks them for their home currency, asks them to enter a header for the
menu, prints a currency table, then provides them with a menu with the
copyright and header at the top. The user is prompted to input an
option, and the program provides an unique polite message to the user's
response accordingly.
"""
import copy
import csv
from enum import Enum

conversions = {
    "USD": 1,
    "EUR": .9,
    "CAD": 1.4,
    "GBP": .8,
    "CHF": .95,
    "NZD": 1.66,
    "AUD": 1.62,
    "JPY": 107.92
}
home_currency = ""
filename = './AB_NYC_2019.csv'


class DataSet:
    copyright = "No copyright has been set."

    class Categories(Enum):
        LOCATION = 0
        PROPERTY_TYPE = 1

    class Stats(Enum):
        MIN = 2
        AVG = 1
        MAX = 3

    def __init__(self, header=""):
        try:
            self.header = header
        except ValueError:
            self.header = ""
        self._data = None
        self._labels = {DataSet.Categories.LOCATION: set(),
                        DataSet.Categories.PROPERTY_TYPE: set()}
        self._active_labels = {DataSet.Categories.LOCATION: set(),
                               DataSet.Categories.PROPERTY_TYPE: set()}

    def get_labels(self, category: Categories):
        return list(self._labels[category])

    def get_active_labels(self, category: Categories):
        return list(self._active_labels[category])

    @staticmethod
    def bubble_sort(list_to_sort: list):
        """ Recursively sort the parameter list_to_sort. """
        list_being_sorted = copy.deepcopy(list_to_sort)

        length = len(list_being_sorted)
        if length == 1:
            return list_being_sorted

        for i in range(length):
            for j in range(0, length - 1):
                if list_being_sorted[j] > list_being_sorted[j + 1]:
                    (list_being_sorted[j], list_being_sorted[j + 1]) = \
                        (list_being_sorted[j + 1], list_being_sorted[j])

        sorted_list = DataSet.bubble_sort(list_being_sorted[0:length - 1])
        largest = list_being_sorted[-1]
        sorted_list.append(largest)

        return sorted_list

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, header: str):
        if type(header) == str and len(header) <= 30:
            self._header = header
        else:
            self._header = ""
            raise ValueError

    class EmptyDatasetError(Exception):
        pass

    class NoMatchingItems(Exception):
        pass

    def _initialize_sets(self):
        """ Populate the dictionaries _labels and _active_labels with
        the appropriate labels from self._data.
        """
        if self._data is None:
            raise DataSet.EmptyDatasetError

        location_set = {unit_info[0] for unit_info in self._data}
        property_type_set = {unit_info[1] for unit_info in self._data}
        self._labels = {DataSet.Categories.LOCATION: location_set,
                        DataSet.Categories.PROPERTY_TYPE: property_type_set}
        self._active_labels = copy.deepcopy(self._labels)

    def _cross_table_statistics(self, descriptor_one: str,
                                descriptor_two: str):
        """ Return the minimum, average, and maximum rent of the
        borough and property type, if there are valid entries with a
        match.

        Key Arguments:
            descriptor_one (str): represents the borough type
            descriptor_two (str): represents the property type
        """
        if self._data is None:
            raise DataSet.EmptyDatasetError

        rent_list = [descriptor[2] for descriptor in self._data
                     if descriptor_one == descriptor[0] and
                     descriptor_two == descriptor[1]]

        if not rent_list:
            raise DataSet.NoMatchingItems

        min_rent = float(min(rent_list))
        max_rent = float(max(rent_list))
        avg_rent = float(sum(rent_list) / len(rent_list))

        return min_rent, avg_rent, max_rent,

    def print_cross_table(self, location_labels: list,
                          property_labels: list, num: int):
        """ Creates the table under the header of the cross table.

        Key Arguments:
            location_labels (list): a list containing the location
            labels
            property_labels (list): a list of the property labels
            num (int): the index corresponding to the element in the
            tuple based on whether we would like to the minimum,
            maximum, or average rent
        """
        for location_label in location_labels:
            print(f"{location_label:20}", end='')
            for property_type in property_labels:
                try:
                    property_price = self._cross_table_statistics(
                        location_label, property_type
                    )
                    avg_price = property_price[num]
                    print(f"$ {avg_price:<20.2f}", end='')
                except DataSet.NoMatchingItems:
                    not_applicable = "N/A"
                    print(f"$ {not_applicable:20}", end='')
                continue
            print()

    def display_cross_table(self, stat: Stats):
        """ Print a table of rates for each borough and property type.
        The values will depend on the input for the parameter stat.

        Key Arguments:
            stat (Stats): a Stats datatype that determines whether the
            average, minimum, or maximum rates will be shown
        """
        if self._data is None:
            raise DataSet.EmptyDatasetError

        location_labels = list(self._labels[DataSet.Categories.LOCATION])
        property_labels = list(self._labels[DataSet.Categories.PROPERTY_TYPE])

        sorted_location_labels = DataSet.bubble_sort(location_labels)
        sorted_property_labels = DataSet.bubble_sort(property_labels)

        print(f"                    ", end='')
        for property_type in sorted_property_labels:
            print(f"{property_type:<22}", end='')
        print()

        if stat == DataSet.Stats.AVG:
            self.print_cross_table(sorted_location_labels,
                                   sorted_property_labels, 1)
        elif stat == DataSet.Stats.MIN:
            self.print_cross_table(sorted_location_labels,
                                   sorted_property_labels, 0)
        elif stat == DataSet.Stats.MAX:
            self.print_cross_table(sorted_location_labels,
                                   sorted_property_labels, 2)

    def _table_statistics(self, row_category: Categories, label: str):
        """ Given a category from the Categories Enum, the string
        matching one of the items in the category, calculate the
        minimum, maximum, and average rent of the properties in that
        category.

        Key Arguments:
            row_category (Categories): a category from the Categories
            Enum
            label (str): the label we would like to find the minimum,
            maximum, and average rent values for
        """
        if row_category == DataSet.Categories.PROPERTY_TYPE:
            filtered_rent_list = [descriptor[2] for descriptor in self._data
                                  if (label == descriptor[0]) and
                                  (descriptor[1] in
                                   self.get_active_labels(row_category))]

            if not filtered_rent_list:
                return None
            else:
                min_rent = float(min(filtered_rent_list))
                max_rent = float(max(filtered_rent_list))
                avg_rent = float(
                    sum(filtered_rent_list) / len(filtered_rent_list)
                )
                return min_rent, avg_rent, max_rent,
        elif row_category == DataSet.Categories.LOCATION:
            filtered_rent_list = [descriptor[2] for descriptor in self._data
                                  if (label == descriptor[1]) and
                                  (descriptor[0] in
                                   self.get_active_labels(row_category))]

            if not filtered_rent_list:
                return None
            else:
                min_rent = float(min(filtered_rent_list))
                max_rent = float(max(filtered_rent_list))
                avg_rent = float(
                    sum(filtered_rent_list) / len(filtered_rent_list))
                return min_rent, avg_rent, max_rent,

    def display_field_table(self, rows: Categories):
        """ Display a table of the minimum, maximum, and average rent
        for each item in the row category (the data should be filtered).

        Key Arguments:
            rows (Categories): the row category from Categories Enum
        """
        if self._data is None:
            raise DataSet.EmptyDatasetError

        active_location_labels = list(
            self.get_active_labels(DataSet.Categories.LOCATION)
        )
        active_property_labels = list(
            self.get_active_labels(DataSet.Categories.PROPERTY_TYPE)
        )

        sorted_active_location = DataSet.bubble_sort(active_location_labels)
        sorted_active_property = DataSet.bubble_sort(active_property_labels)

        given_labels = list(self.get_active_labels(rows))
        sorted_given_labels = DataSet.bubble_sort(given_labels)

        if rows == DataSet.Categories.LOCATION:
            print("The following data are from properties matching these "
                  "criteria: ")
            for active_label in sorted_active_property:
                print(f"- {active_label}")
        elif rows == DataSet.Categories.PROPERTY_TYPE:
            print("The following data are from properties matching these "
                  "criteria: ")
            for active_label in sorted_active_location:
                print(f"- {active_label}")

        minimum_string = "Minimum"
        average_string = "Average"
        maximum_string = "Maximum"
        print(f"        {minimum_string:>18}   {average_string:>18} "
              f"  {maximum_string:>18}", end='')
        print()
        for label in sorted_given_labels:
            if rows == DataSet.Categories.LOCATION:
                prices = self._table_statistics(
                    DataSet.Categories.PROPERTY_TYPE,
                    label
                )
                if prices is None:
                    na_string = "N/A"
                    print(
                        f"{label:<18} {na_string:<18} "
                        f"  {na_string:<18}   {na_string:<18}"
                    )
                else:
                    print(
                        f"{label:<18} $ {prices[0]:<18.2f} "
                        f"$ {prices[1]:<18.2f} $ {prices[2]:<18.2f}"
                    )
            elif rows == DataSet.Categories.PROPERTY_TYPE:
                prices = self._table_statistics(
                    DataSet.Categories.LOCATION,
                    label
                )
                if prices is None:
                    na_string = "N/A"
                    print(
                        f"{label:<18} {na_string:<18} "
                        f"{na_string:<18} {na_string:<18}"
                    )
                else:
                    print(
                        f"{label:<18} $ {prices[0]:<18.2f} "
                        f"$ {prices[1]:<18.2f} $ {prices[2]:<18.2f}"
                    )

    def load_file(self):
        """ Load data from file and initialize labels. """
        with open(filename, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            data_list = [(row[1], row[2], float(row[3])) for row in csv_reader
                         if row[3] != 'price']
            file_length = len(data_list)
        self._data = data_list
        self._initialize_sets()
        return file_length

    def toggle_active_label(self, category: Categories, descriptor: str):
        """ Add a label to _active_labels if it is not there. Remove a
        label from _active_labels if it is initially in this list.

        Key Arguments:
            category (Categories): a member of the Categories Enum
            descriptor (str): the descriptor the user would like to
            add or remove
        """
        is_in_active_labels = False
        descriptor_in_labels = False
        for label in self.get_labels(category):
            if descriptor == label:
                descriptor_in_labels = True

        if descriptor_in_labels:
            for label in self.get_active_labels(category):
                if label == descriptor:
                    is_in_active_labels = True

            if is_in_active_labels:
                self._active_labels[category].remove(descriptor)
            else:
                self._active_labels[category].add(descriptor)
        else:
            raise KeyError


def currency_converter(quantity: float, source_curr: str, target_curr: str):
    """ Convert source currency to target currency.

    Key Arguments:
        quantity (float): the amount of the original currency
        source_curr (str): represents the source currency
        target_curr (str): represents the currency after exchange
    """
    converted_quantity = (quantity
                          * (1 / conversions[source_curr])
                          * conversions[target_curr])
    return converted_quantity


def currency_options(base_curr: str):
    """ Print out a table of options for converting base_curr to all
    other string currencies.

    Key Arguments:
        base_curr (str): the home currency of the user
    """
    print(f"{base_curr:9}", end="")
    for currency in conversions:
        if currency == base_curr:
            continue
        else:
            print(f"{currency:9}", end="")
    print()

    for i in range(10, 100, 10):
        print(f"{i:<9.2f}", end="")
        for currency in conversions:
            if currency == base_curr:
                continue
            else:
                converted_currency = currency_converter(i, base_curr, currency)
                print(f"{converted_currency:<9.2f}", end="")
        print()


def manage_filters(dataset: DataSet, category: DataSet.Categories):
    """ Print a menu-like list of all labels for a given category,
    indicating which ones are currently active. Allow user to change a
    label from active to inactive or inactive to active until user is
    finished with making choices.

    Key Arguments:
        dataset (Dataset): an object of the class DataSet
        category (Dataset.Categories): a member of the Enum Categories
    """
    making_choices = True
    while making_choices:
        print("The following labels are in the dataset:")
        for num, label in enumerate(dataset.get_labels(category), 1):
            label_status = "ACTIVE" if label in dataset.get_active_labels(
                category) else "INACTIVE"
            print(f"{num}. {label:<20} {label_status:<20}")

        response = input("Please select an item to toggle or enter a blank"
                         " line when you are\nfinished. ")
        if response == '':
            break
        else:
            index = int(response) - 1
            try:
                dataset.toggle_active_label(
                    category, dataset.get_labels(category)[index])
            except IndexError:
                print("Please select a number from the list")


def print_menu():
    """ Print out the nine choices and the numbers associated with
    them.
    """
    print("Main Menu")
    print("1 - Print Average Rent by Location and Property Type")
    print("2 - Print Minimum Rent by Location and Property Type")
    print("3 - Print Maximum Rent by Location and Property Type")
    print("4 - Print Min/Avg/Max by Location")
    print("5 - Print Min/Avg/Max by Property Type")
    print("6 - Adjust Location Filters")
    print("7 - Adjust Property Type Filters")
    print("8 - Load Data")
    print("9 - Quit")


def menu(dataset: DataSet):
    """ Print the currency table, then print out menu with the
    copyright and header on the top. Ask user to select an option,
    catch errors, and provide a unique polite message for each selection
    until they enter 9 to indicate that they want to quit the menu.

    Key arguments:
        dataset (DataSet): an object of the class DataSet
    """
    print(f"Options for converting from {home_currency}: ")
    currency_options(home_currency)
    print(DataSet.copyright)
    show_menu = True
    while show_menu:
        print()
        print(dataset.header)
        print_menu()
        try:
            response = int(input("What is your choice? "))
        except ValueError:
            print("Please enter in a number only")
            continue
        if response == 1:
            try:
                dataset.display_cross_table(DataSet.Stats.AVG)
            except DataSet.EmptyDatasetError:
                print("Please Load a Dataset First")
        elif response == 2:
            try:
                dataset.display_cross_table(DataSet.Stats.MIN)
            except DataSet.EmptyDatasetError:
                print("Please Load a Dataset First")
        elif response == 3:
            try:
                dataset.display_cross_table(DataSet.Stats.MAX)
            except DataSet.EmptyDatasetError:
                print("Please Load a Dataset First")
        elif response == 4:
            try:
                dataset.display_field_table(DataSet.Categories.LOCATION)
            except DataSet.EmptyDatasetError:
                print("Please Load a Dataset First")
        elif response == 5:
            try:
                dataset.display_field_table(DataSet.Categories.PROPERTY_TYPE)
            except DataSet.EmptyDatasetError:
                print("Please Load a Dataset First")
        elif response == 6:
            try:
                manage_filters(dataset, DataSet.Categories.LOCATION)
            except DataSet.EmptyDatasetError:
                print("Please Load a Dataset First")
        elif response == 7:
            try:
                manage_filters(dataset, DataSet.Categories.PROPERTY_TYPE)
            except DataSet.EmptyDatasetError:
                print("Please Load a Dataset First")
        elif response == 8:
            num_lines = dataset.load_file()
            print(str(num_lines) + " lines loaded")
        elif response == 9:
            print("Goodbye! Thank you for using this database")
            break
        else:
            print("Please enter a number between 1 and 9")


def greeting():
    """ Obtain the user's name. """
    my_name = input("\nPlease enter your name: ")
    print("Hi ", my_name, ", welcome to Foothill's database project.",
          sep='')


def ask_home_currency():
    """ Ask for user's home currency until user enters in a valid
    currency.
    """
    global home_currency
    invalid_currency = True
    while invalid_currency:
        home_currency = input("What is your home currency? ")
        for currency in conversions:
            if home_currency == currency:
                invalid_currency = False
            else:
                continue


def main():
    """ Greet user, ask user for their home currency, ask user to enter
    header for the menu, print table of options for currency
    conversions, print menu with header and copyright at the top, and
    print a unique polite message to the user based on the user's choice
    until user enters the number 9 to quit the menu.
    """
    greeting()
    ask_home_currency()
    DataSet.copyright = "\nCopyright Michelle Tham"
    air_bnb = DataSet()
    while True:
        header = input("Please enter a header for the menu:\n")
        try:
            air_bnb.header = header
            break
        except ValueError:
            continue
    menu(air_bnb)


if __name__ == "__main__":
    main()

"""
Please enter your name: Michelle
Hi Michelle, welcome to Foothill's database project.
What is your home currency? AUD
Please enter a header for the menu:
Final Airbnb Database
Options for converting from AUD: 
AUD      USD      EUR      CAD      GBP      CHF      NZD      JPY      
10.00    6.17     5.56     8.64     4.94     5.86     10.25    666.17   
20.00    12.35    11.11    17.28    9.88     11.73    20.49    1332.35  
30.00    18.52    16.67    25.93    14.81    17.59    30.74    1998.52  
40.00    24.69    22.22    34.57    19.75    23.46    40.99    2664.69  
50.00    30.86    27.78    43.21    24.69    29.32    51.23    3330.86  
60.00    37.04    33.33    51.85    29.63    35.19    61.48    3997.04  
70.00    43.21    38.89    60.49    34.57    41.05    71.73    4663.21  
80.00    49.38    44.44    69.14    39.51    46.91    81.98    5329.38  
90.00    55.56    50.00    77.78    44.44    52.78    92.22    5995.56  

Copyright Michelle Tham

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 1
Please Load a Dataset First

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 8
48895 lines loaded

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 1
                    Entire home/apt       Private room          Shared room           
Bronx               $ 127.51              $ 66.79               $ 59.80               
Brooklyn            $ 178.33              $ 76.50               $ 50.53               
Manhattan           $ 249.24              $ 116.78              $ 88.98               
Queens              $ 147.05              $ 71.76               $ 69.02               
Staten Island       $ 173.85              $ 62.29               $ 57.44               

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 2
                    Entire home/apt       Private room          Shared room           
Bronx               $ 28.00               $ 0.00                $ 20.00               
Brooklyn            $ 0.00                $ 0.00                $ 0.00                
Manhattan           $ 0.00                $ 10.00               $ 10.00               
Queens              $ 10.00               $ 10.00               $ 11.00               
Staten Island       $ 48.00               $ 20.00               $ 13.00               

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 3
                    Entire home/apt       Private room          Shared room           
Bronx               $ 1000.00             $ 2500.00             $ 800.00              
Brooklyn            $ 10000.00            $ 7500.00             $ 725.00              
Manhattan           $ 10000.00            $ 9999.00             $ 1000.00             
Queens              $ 2600.00             $ 10000.00            $ 1800.00             
Staten Island       $ 5000.00             $ 300.00              $ 150.00              

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 4
The following data are from properties matching these criteria: 
- Entire home/apt
- Private room
- Shared room
                   Minimum              Average              Maximum
Bronx              $ 0.00               $ 87.50              $ 2500.00           
Brooklyn           $ 0.00               $ 124.38             $ 10000.00          
Manhattan          $ 0.00               $ 196.88             $ 10000.00          
Queens             $ 10.00              $ 99.52              $ 10000.00          
Staten Island      $ 13.00              $ 114.81             $ 5000.00           

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 5
The following data are from properties matching these criteria: 
- Bronx
- Brooklyn
- Manhattan
- Queens
- Staten Island
                   Minimum              Average              Maximum
Entire home/apt    $ 0.00               $ 211.79             $ 10000.00          
Private room       $ 0.00               $ 89.78              $ 10000.00          
Shared room        $ 0.00               $ 70.13              $ 1800.00           

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 6
The following labels are in the dataset:
1. Queens               ACTIVE              
2. Brooklyn             ACTIVE              
3. Staten Island        ACTIVE              
4. Manhattan            ACTIVE              
5. Bronx                ACTIVE              
Please select an item to toggle or enter a blank line when you are
finished. 3
The following labels are in the dataset:
1. Queens               ACTIVE              
2. Brooklyn             ACTIVE              
3. Staten Island        INACTIVE            
4. Manhattan            ACTIVE              
5. Bronx                ACTIVE              
Please select an item to toggle or enter a blank line when you are
finished. 1
The following labels are in the dataset:
1. Queens               INACTIVE            
2. Brooklyn             ACTIVE              
3. Staten Island        INACTIVE            
4. Manhattan            ACTIVE              
5. Bronx                ACTIVE              
Please select an item to toggle or enter a blank line when you are
finished. 

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 5
The following data are from properties matching these criteria: 
- Bronx
- Brooklyn
- Manhattan
                   Minimum              Average              Maximum
Entire home/apt    $ 0.00               $ 217.95             $ 10000.00          
Private room       $ 0.00               $ 93.29              $ 9999.00           
Shared room        $ 0.00               $ 70.48              $ 1000.00           

Final Airbnb Database
Main Menu
1 - Print Average Rent by Location and Property Type
2 - Print Minimum Rent by Location and Property Type
3 - Print Maximum Rent by Location and Property Type
4 - Print Min/Avg/Max by Location
5 - Print Min/Avg/Max by Property Type
6 - Adjust Location Filters
7 - Adjust Property Type Filters
8 - Load Data
9 - Quit
What is your choice? 
"""
