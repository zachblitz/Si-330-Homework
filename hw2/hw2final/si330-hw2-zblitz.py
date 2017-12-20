import csv
from collections import defaultdict
from pprint import pprint

#worked extensively together with Sam Karmin and Nate Wellek

def new_file():
    with open("world_bank_country_data.txt", "r", newline="") as input_file:
        country_reader = csv.DictReader(input_file, delimiter = "\t", quotechar ='"')
        with open("two_thousand_dates.csv", "w", newline = '') as output_file:
            country_writer = csv.DictWriter(output_file, fieldnames = ["Country Name", "Date", "Transit: Railways, (million passenger-km)",
                                          "Transit: 'Passenger cars (per 1,000 people)",
                                          'Business: Mobile phone subscribers',
                                          'Business: Internet users (per 100 people)',
                                          "Health: Mortality, under-5 (per '1,000 live births)",
                                          'Health: Health expenditure per capita (current US$)',
                                          'Health: Health expenditure, total (% GDP)', 'Population: Total (count)',
                                          'Population: Urban (count)', "Population:: Birth rate, crude (per 1,000)",
                                          "Health: Life expectancy at birth, female (years)",
                                          "Health: Life expectancy at birth, male (years)",
                                          "Health: Life expectancy at birth, total (years)",
                                          "Population: Ages 0-14 (% of total)", "Population: Ages 15-64 (% of total)",
                                          'Population: Ages 65+ (% of total)', "Finance: GDP (current US$)",
                                          "Finance: GDP per capita (current US$)"],
                                                 extrasaction = 'ignore',
                                                 delimiter = ',', quotechar = '"')
            country_writer.writeheader()
            for row in country_reader:
                date = row["Date"]
                if date[-5:] == "/2000":
                    country_writer.writerow(row)

go = new_file()


def read_directed_graph_from_csv(filename, source_column, dest_column, weight_column):
    graph = defaultdict(list) # returns an empty list if looking up key that doesn't exist
    with open(filename, 'r', newline = '') as input_file:
        graph_file_reader = csv.DictReader(input_file, delimiter=',', quotechar = '"')
        for row in graph_file_reader:
            country = row['Country Origin Name']
            destination = row['Country Dest Name']
            weight = row['2000 [2000]']

            try:
                if country not in graph:
                    if weight == '..':
                        weight = 0
                    else:
                        weight = float(weight)

                    graph[country]= [(destination , weight)]
                else:
                    if weight == '..':
                        weight = 0
                    else:
                        weight = float(weight)
                    graph[country].append((destination, weight))
            except ValueError:
                pass
    return graph

migration_graph = read_directed_graph_from_csv("world_bank_migration.csv", "Country Origin Name", "Country Dest Name", "2000 [2000]")
# print(migration_graph["Canada"][0:5])


def sort_migration_graph(x):
    sorted_dictionary = {}
    for x in migration_graph:
        y = migration_graph[x]
        sorted_y = sorted(y, key = lambda x: x[1], reverse = True)
        sorted_dictionary[x] = sorted_y
    return sorted_dictionary

sorted_migration_graph = sort_migration_graph(migration_graph)#
#pprint(sorted_migration_graph)


def create_final_csv_file(regions_file, clean_text_file_in_csv_format):
    country_tuple_list = []
    country_list = []
    user_pop_year_country = []


    with open('two_thousand_dates.csv', "r", newline="") as input_file:
        file_reader = csv.DictReader(input_file, delimiter=",", quotechar='"')
        for row in file_reader:
            country_name = row["Country Name"]
            # print(country_name)
            country_list.append(country_name)
            year = row["Date"][-4:]
            # print(year)
            population = row["Population: Total (count)"]
            new_pop = population.replace(",", "")
            mobile_users = row["Business: Mobile phone subscribers"]
            new_mobile_users = mobile_users.replace(",", "")

            if new_mobile_users != '':
                new_mobile_users = float(new_mobile_users)
                mobile_users_per_capita = round(new_mobile_users/float(new_pop),2)
                user_pop_tuple = (mobile_users_per_capita, int(new_pop), year, country_name)
                user_pop_year_country.append(user_pop_tuple)
            else:
                new_mobile_users = 'NA'
                mobile_users_per_capita = 'NA'
                user_pop_tuple = (mobile_users_per_capita, int(new_pop),year, country_name)
                user_pop_year_country.append(user_pop_tuple)

    with open("world_bank_regions.txt", "r", newline="") as input_file:
        regions_reader = csv.DictReader(input_file, delimiter="\t", quotechar='"')
        for row in regions_reader:
            country = row['Country']
            region = row['Region']
            if country in country_list:
                country_tuple = (region, country)
                country_tuple_list.append(country_tuple)


    with open('world-bank-output-hw2-zblitz.csv', 'w') as output_file:
        bank_data_output_writer = csv.DictWriter(output_file, fieldnames=['Region', 'Country Name', 'Mobile users per capita','Population', 'Year', 'Migration: Top 3 destinations','Migration: Top 3 sources'], extrasaction='ignore', delimiter=',', quotechar='"')
        bank_data_output_writer.writeheader()

        humor = {}
        data = {}
        for tuple in country_tuple_list:
            region = tuple[0]
            country = tuple[1]
            if country in country_list:
                humor[country] = region

        for guy in user_pop_year_country:
            mobile_users_per_capita = guy[0]
            population = guy[1]
            year = guy[2]
            country_name = guy[3]

            if country_name in humor:
                if country_name not in sorted_migration_graph:
                    data["Region"] = humor[country_name]
                    data["Country Name"] = country_name
                    data["Mobile users per capita"] = 'NA'
                    data["Population"] = population
                    data["Year"] = year
                    data["Migration: Top 3 destinations"] = []
                    data["Migration: Top 3 sources"] = []
                else:
                    migration_tuple = sorted_migration_graph[country_name]
                    data["Region"] = humor[country_name]
                    data["Country Name"] = country_name
                    data["Mobile users per capita"] = mobile_users_per_capita
                    data["Population"] = population
                    data["Year"] = year
                    data["Migration: Top 3 destinations"] = migration_tuple[:3]
                    countries_list = []
                    for x in sorted_migration_graph.keys():
                        name = x
                        item = sorted_migration_graph[x]
                        for tup in item:
                            a,b = tup
                            if a == country_name:
                                countries_list.append((name,b))
                        sorted_countries_list = sorted(countries_list, key = lambda x: x[1], reverse = True)
                        top_3_sources = sorted_countries_list[:3]
                    data["Migration: Top 3 sources"] = top_3_sources

                    bank_data_output_writer.writerow(data)


final_csv = create_final_csv_file('world_bank_regions.txt','two_thousand_dates.csv',)



def nodes_and_edges(location_file, world_bank_migration):
    with open(location_file, "r", newline="") as input_file:
        location_reader = csv.DictReader(input_file, delimiter=",", quotechar='"')
        location_list_tuples = []
        country_list = []
        for row in location_reader:
            country = row['Country Name']
            if country == "United States of America (the)":
                country = "United States"
                latitude = row['Latitude']
                longitude = row['Longitude']
                cll = (country, latitude, longitude)
                country_list.append(country)
                location_list_tuples.append(cll)
            elif country == "United Kingdom of Great Britain and Northern Ireland (the)":
                country = "United Kingdom"
                latitude = row['Latitude']
                longitude = row['Longitude']
                cll = (country, latitude, longitude)
                country_list.append(country)
                location_list_tuples.append(cll)
            else:
                country = row['Country Name']
                latitude = row['Latitude']
                longitude = row['Longitude']
                cll = (country, latitude, longitude)
                country_list.append(country)
                location_list_tuples.append(cll)



    DATA = {}
    with open('si330-hw2-nodes-zblitz.csv', 'w') as output_file:
        nodes_writer = csv.DictWriter(output_file,
                                                 fieldnames=['Country', 'Latitude', 'Longitude'], extrasaction='ignore',
                                                 delimiter=',', quotechar='"')
        nodes_writer.writeheader()
        for tup in location_list_tuples:
            country = tup[0]
            latitude = tup[1]
            longitude = tup[2]
            DATA["Country"] = country
            DATA["Latitude"] = latitude
            DATA["Longitude"] = longitude
            nodes_writer.writerow(DATA)


    with open(world_bank_migration, "r", newline="") as input_file:
        migration_reader = csv.DictReader(input_file, delimiter=",", quotechar='"')
        dog = []
        for x in migration_reader:
            country_name = x['Country Origin Name']
            destination = x['Country Dest Name']
            count = (x['2000 [2000]'])
            try:
                if count == '..':
                    pass
                else:
                    count = int(count)
                    tuple = (country_name, destination, count)
                    if country_name in country_list:
                        if destination in country_list:
                            dog.append(tuple)
            except:
                ValueError

        sorted_dog = sorted(dog, key = lambda x: x[2], reverse = True)[:1000]
    with open('si330-hw2-nodes-zblitz.csv', 'r', newline='') as input_file:
        another_dictionary = {}
        node_reader = csv.DictReader(input_file, delimiter=",", quotechar='"')
        for x in node_reader:
            country = x["Country"]
            lat = x["Latitude"]
            long = x["Longitude"]
            another_dictionary[country] = (lat, long)
    with open('si330-hw2-edges-zblitz.csv', 'w') as output_file:
        last = {}
        edges_writer = csv.DictWriter(output_file,
                                                 fieldnames=['start_country', 'end_country', 'start_lat', 'start_long', 'end_lat', 'end_long', 'count'], extrasaction='ignore',
                                                 delimiter=',', quotechar='"')
        edges_writer.writeheader()
        for x in sorted_dog:
            source = x[0]
            dest = x[1]
            last["start_country"] = source
            last["start_country"] = source
            last["end_country"] = dest
            last["end_country"] = dest
            last["count"] = x[2]
            last["start_lat"] = another_dictionary[source][0]
            last["start_long"] = another_dictionary[source][1]
            last["end_lat"] = another_dictionary[dest][0]
            last["end_long"] = another_dictionary[dest][1]
            edges_writer.writerow(last)



step_six_call = nodes_and_edges('locations.csv','world_bank_migration.csv')
