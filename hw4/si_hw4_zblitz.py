# -*- coding: utf-8 -*-
#!/usr/bin/python -tt
import re
import csv
from collections import defaultdict
from pprint import pprint


def write_log_entries(filename, list_of_rows_to_write):
    row_counter = 0
    with open(filename, 'w+', newline = '') as f:
        row_writer = csv.DictWriter(f, delimiter='\t', quotechar='"', extrasaction='ignore',
                                    fieldnames=["IP", "Ignore1", "Ignore2", "Timestamp", "Ignore3", "HTTP_Verb",
                                                "HTTP_Status", "HTTP_Duration", "URL", "Browser_Type",
                                                "Top_Level_Domain"])
        row_writer.writeheader()
        for row in list_of_rows_to_write:
            row_writer.writerow(row)
            row_counter = row_counter + 1

    print("Wrote {} rows to {}".format(row_counter, filename))


# Function read_log_file:
#   Input: the file name of the log file to process
#   Output:  A two-element tuple with element 0 a list of valid rows, and element 1 a list of invalid rows
def read_log_file(filename):
    valid_entries   = []
    invalid_entries = []

    with open(filename, 'r', newline='') as input_file:
        log_data_reader = csv.DictReader(input_file, delimiter='\t', quotechar ='"', skipinitialspace=True,
                                         fieldnames=["IP","Ignore1","Ignore2","Timestamp","Ignore3","HTTP_Verb","HTTP_Status","HTTP_Duration","URL","Browser_Type"])
        for row in log_data_reader:
            ### PUT YOUR CODE HERE to test for a valid line and set not_a_valid_line to True if a condition isn't met
            not_a_valid_line = False
            status = row['HTTP_Status'] #setting status equal to the row's status value
            verb = row["HTTP_Verb"] #setting verb equal to the row's verb value
            
            if status == '200': #if the row's status is equal to 200
                match = re.search(r'^(GET|POST)\s+(https*:\/\/([a-zA-Z]+[-.a-zA-Z0-9]*\.)([a-zA-Z]{2,4})[/:]*[0-9]*.*)', verb) #using regex to find a match to the value of the verb in the row
                if match == None: #if the rows status is equal to 200 but there is no match
                    not_a_valid_line = True #this value is now true
                else:
                    valid_entries.append(row) #otherwise, the row is valid and appended to a list of valid entries
                    top_lev_d = match.group(4) #equal to the top level domain 
            else:
                invalid_entries.append(row) #if the row's status is not equal to 200, the row is invalid and is added to the list of invalid entries
            if not_a_valid_line: #if not_a_valid_line is true
                invalid_entries.append(row) #the line is invalid and the row is appended to the invalid entries list
                continue

            row['Top_Level_Domain'] = top_lev_d.lower() #setting the value of row['Top_Level_Domain'] equal to the row's top level domain in lowercase

    return (valid_entries, invalid_entries) #returns a tuple of lists

def main():
    valid_rows, invalid_rows = read_log_file(r'access_log.txt')

    write_log_entries('valid_access_log_zblitz.txt', valid_rows) #writing the valid rows
    write_log_entries('invalid_access_log_zblitz.txt', invalid_rows) #writing the invalid rows

# This is boilerplate python code: it tells the interpreter to execute main() only
# if this module is being run as the main script by the interpreter, and
# not being imported as a module.
if __name__ == '__main__':
    main()

