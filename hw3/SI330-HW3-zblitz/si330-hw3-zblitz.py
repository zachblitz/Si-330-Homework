import profile
import csv

# Here, we are reusing the document distance code
from docdist_dict import (get_words_from_string, count_frequency, vector_angle)

#CHANGE 1
#Changed this file above so that it creates a dictionary
#Time reduced from 94.76 seconds to 15.23 seconds
#Instead of iterating through a list, it is significantly faster to use a dictionary

# As a convention, "constant" variable names are usually written in all-caps
OUTPUT_FILE = 'sentence-database-hw3-zblitz.csv'

MASTER_FILE = 'Sentences_Table_MasterList.csv'
SENTENCE_DB_FILE = 'Sentence_Database_Without_ID.csv'
# MASTER_FILE = 'Sentences_Table_MasterList.csv'
# SENTENCE_DB_FILE = 'Sentence_Database_Without_ID.csv'

def main():
    global MASTER_FILE, SENTENCE_DB_FILE

    # we will be collecting each row of the output file in this list
    output = []
    row_count = 0

    # looping through the SENTENCE_DB_FILE to process each row
    for row in get_csv_rows(SENTENCE_DB_FILE):
        set_sentence_id(row) #IN THE SENTENCE_DB_FILE, IF THE ROW'S SENTENCE MATCHES THE SENTENCE IN THE MASTER FILE,
        replace_target_with_blank(row) #Replacing target word with 'XXXXX' and storing its value in "Sentence_With_Blank" Column

        if row['SentID_GM'] != 'NA':
            lookup_similar_id(row) # setting these values ( row['SimilarTo_SentID_GM'] and row['SimilarTo_Sentence'])
            find_alternate_sentence(row) #setting these values ( row['Alternate_SimilarTo_SentID_GM'] and row['Alternate_SimilarTo_Sentence'])
            find_unique_targets(row)# finding the unique target words and saving it to row['SimilarTo_Targets']

        output.append(row)
        row_count += 1
        print(row_count)

        write_output_file(output)

def set_sentence_id(row):
    '''
        If you look at the SENTENCE_DB_FILE, each row has a Sentence with a missing SentID_GM
        SentID_GM can be found in the MASTER_FILE
        So, we use the MASTER_FILE data to find SentID_GM for each Sentence

        # -------------------------------------------------------------------------
        # Implement a better way to "lookup" SentID_GM,
        # without looping through each row again and again
        #
        # Ask yourself:
        # -------------
        #   - Is "list" the best data structure for "lookup / search"?
        #   - What is the 'type' of running time for the current implementation?
        #     Is it linear or quadratic?
        #
        # -------------------------------------------------------------------------

    '''

    for record in get_csv_rows(MASTER_FILE):
        # record is a row in MASTER_FILE
        if record['Sentence_with_Target'].strip() == row['Sentence'].strip():
            # found a matching sentence!
            row['SentID_GM'] = record['SentID_GM'] #setting the input's ['SentID_GM'] equal to the 'SentID_GM' of the row in the master file if the sentences match
            break

        else:
            # the default value
            row['SentID_GM'] = 'NA'


def replace_target_with_blank(row):
    '''
        Each row in SENTENCE_DB_FILE has a "Target" word like "[education]".
        In this function, we replace the target word with "XXXXX", and
        store its value in "Sentence_With_Blank" column

        # -------------------------------------------------------------------------
        # Implement a better way to replace the Target word with XXXXX,
        # without looping through the words
        #
        # Ask yourself:
        # -------------
        #   - Is there an inbuilt python function,
        #     that can be used to substitute a word with another word?
        #
        # -------------------------------------------------------------------------

    '''

    new_words = []

    # Here, we split the sentence into words and loop through it till we find the target
    for word in row['Sentence'].split():# splitting the value of row['Sentence'] into a list of its words
        if word[0]=='[' and (word[-1]==']' or word[-2:]=='].') and word[1:-1]==row['Targ']: #if the first element in the word is equal to [ and the last element of the word is equal to ] or ]. and the word matches the target word in the sentence, new words.append('XXXXX')
            new_words.append('XXXXX')
        else:
            new_words.append(word)#otherwise it just appends the word

    row['Sentence_With_Blank'] = ' '.join(new_words)


def lookup_similar_id(row):
    '''
        The MASTER_FILE also has a column 'SimilarTo_SentID_GM',
        which is the sentence ID of a similar sentence in the MASTER_FILE.

        In this function, we lookup the similar sentence for the given 'row',
        using the data in the MASTER_FILE

        # -------------------------------------------------------------------------
        # Implement a better way to find similar sentence,
        # without looping through the each row again and again
        #
        # Ask yourself:
        # -------------
        #   - Is "list" the best data structure for "lookup / search"?
        #   - What is the 'type' of running time for the current implementation?
        #     Is it linear or quadratic?
        #   - Can I reuse something from a previous step?
        #
        # -------------------------------------------------------------------------

    '''

    similar_to = None

    #Change 2 - get each similar ID and find similar sentence, using a dictionary is faster
    # Time reduced from 14.37 to 10.44 seconds
    similar_id = row['SentID_GM'] #setting similar_id equal to 'SentID_GM'
    if similar_id in similar_dictionary:#if it is in the dictionary, setting the variable similar_to equal to the value of [similar_id]['SimilarTo_SentID_GM'] from the similar dictionary
        similar_to = similar_dictionary[similar_id]['SimilarTo_SentID_GM']

    if similar_to is not None: #if the variable similar_to is nont equal to None
        if similar_to in similar_dictionary: #if similar to is in similar dictionary
            row['SimilarTo_SentID_GM'] = similar_to #setting the row['SimilarTo_SendID_GM'] equal to the value of similar to
            row['SimilarTo_Sentence'] = similar_dictionary[similar_to]['Sentence_with_Target'] #setting the row['SimilarTo_Sentence'] equal to the value of [similar_to]['Sentence_With_Target'] in the similar dictionary


def find_alternate_sentence(row):
    '''
        Just like SimilarTo_Sentence and SimilarTo_SentID_GM, we will determine
        Alternate_SimilarTo_Sentence and Alternate_SimilarTo_SentID_GM
        by calculating the cosine distance between two sentences
        using the **document distance** code that we discussed in the previous class

        # -------------------------------------------------------------------------
        # Your aim in this function is to speed up the code using a simple trick
        # and a modification
        #
        # Biggest hint: look at the other files in the folder
        #
        # Ask yourself:
        # -------------
        #   - Why are the functions called here, so slow?
        #   - Is there something you learned in the class about "document distance" problem,
        #     that can be used here?
        #   - Is there a step which can be taken out of the 'for' loop?
        #
        # -----
        # Bonus:
        # ------
        # This code calculates the cosine distance between the given row's Sentence
        # and the Sentence_with_Target all the rows in MASTER_FILE.
        # This is repeated for each 'row' in SENTENCE_DB_FILE.
        # In first iteration, you already calculate the cosine distance of
        # "I go to school because I want to get a good [education]."
        # and all the rows in the MASTER_FILE
        # and that includes "I go to school because I want to get a good [education]."
        # This is repeated in 2nd iteration for "I go to school because I want to get a good [education].".
        #
        # Can you cache (store) these calculations for future iterations?
        # What would be the best data structure for caching?
        # Try to further optimize the code using a cache
        # -------------------------------------------------------------------------

    '''

    # find alternate similar sentence using document distance
    similar_sentence = None
    for record in get_csv_rows(MASTER_FILE):
        # record is a row in MASTER_FILE

        if record['SentID_GM'] == row['SentID_GM']: #if the SentID_GM matches in both the master file and the
            # ignore the same sentence
            continue

        # get frequency mapping for row['Sentence']
        row_word_list = get_words_from_string(row['Sentence'])
        row_freq_mapping = count_frequency(row_word_list)

        # get frequency mapping for record['Sentence_with_Target']
        record_word_list = get_words_from_string(record['Sentence_with_Target'])
        record_freq_mapping = count_frequency(record_word_list)

        distance = vector_angle(row_freq_mapping, record_freq_mapping) #calculating the distance
        if 0 < distance < 0.75:
            if (not similar_sentence) or (distance < similar_sentence['distance']):
                similar_sentence = {
                    'distance': distance,
                    'Sentence_with_Target': record['Sentence_with_Target'],
                    'SentID_GM': record['SentID_GM']
                }#creating a similar sentence dictionary with distance equal the distance, Sentence_with_Target equal to the data in the ['Sentence_with_Target'] column for each row in the Master File and setting SentID_GM equal to the data in the ['SentID_GM'] column for each row in the Master File

    if similar_sentence and similar_sentence['SentID_GM'] != row.get('SimilarTo_SentID_GM'):
        row['Alternate_SimilarTo_SentID_GM']  = similar_sentence['SentID_GM'] #setting the row['Alternate_SimilarTo_SentID_GM'] equal to the value of ['SentID_GM'] from the similar sentence dictionary
        row['Alternate_SimilarTo_Sentence']  = similar_sentence['Sentence_with_Target']#setting the row['Alternate_SimilarTo_Sentence'] equal to the value of ['Sentence_with_Target'] from the similar sentence dictionary


def find_unique_targets(row):
    '''
        This steps finds [target] word in "SimilarTo_Sentence" and "Alternate_SimilarTo_Sentence",
        selects only unique target word(s), and saves it in `row['SimilarTo_Targets']`

        # -------------------------------------------------------------------------
        # Implement a better way to find unique target words,
        # without looping through the words
        #
        # Ask yourself:
        # -------------
        #   - Can you use regular expressions to do this?
        #   - What is the data structure that stores only unique values?
        #     Can it be used here instead of checking "if target not in targets:"?
        #     Try searching the web for "python get unique values from a list".
        #
        # -------------------------------------------------------------------------

    '''

    # find unique targets from similar sentences
    targets = []
    for key in ('SimilarTo_Sentence', 'Alternate_SimilarTo_Sentence'):
        for word in row.get(key, '').split():#getting each word
            if word.startswith('[') and word.endswith(']'):
                target = word[1:-1]#finding the target word
                if target not in targets:#seeing if the word is in the target list or not
                    targets += [target]#adding [target] to the end of the list

            elif word.startswith('[') and word.endswith('].'):#the target word could have a period at the end so this takes that into account
                target = word[1:-2]#next few lines are same as steps directly above
                if target not in targets:
                    targets += [target]

    row['SimilarTo_Targets'] = ','.join(targets)


def get_csv_rows(filename):
    '''Read the CSV file using DictReader and then append all rows in a list'''
    with open(filename, 'r', newline='') as input_file:
        reader = csv.DictReader(input_file, delimiter=',', quotechar='"')

        data = []
        for row in reader:
            data.append(row)

        return data

#CHANGE 2 AND 3 #creating two dictionaries as opposed to lists
#Time reduced from 10.44 seconds to 10.36 seconds
sentence_dictionary = {}
similar_dictionary = {}

for row in get_csv_rows(MASTER_FILE):
    similar_dictionary[row['SentID_GM']] = row
    sentence_dictionary[row['Sentence_with_Target'].strip()] = row

def write_output_file(output):
    '''Write output into a new CSV file. Uses the OUTPUT_FILE variable to determine the filename.'''
    global OUTPUT_FILE
    with open(OUTPUT_FILE, 'w', newline='') as output_file_obj:
        sentence_db_writer = csv.DictWriter(output_file_obj,
                                fieldnames=["SentID_GM", "Sentence", "Targ", "Sentence_With_Blank",
                                        "SimilarTo_Sentence", "SimilarTo_SentID_GM",
                                        "Alternate_SimilarTo_Sentence", "Alternate_SimilarTo_SentID_GM",
                                        "SimilarTo_Targets"],
                                extrasaction="ignore", delimiter=",", quotechar='"')

        sentence_db_writer.writeheader()

        for row in output:
            sentence_db_writer.writerow(row) #writing in all the data


if __name__ == '__main__':
    profile.run('main()')
    # main()

###################### Before the change ################################
#     37996681
#     function
#     calls in 94.767
#     seconds
#
#     Ordered
#     by: standard
#     name
#
#     ncalls
#     tottime
#     percall
#     cumtime
#     percall
#     filename: lineno(function)
#     87824
#     0.110
#     0.000
#     0.110
#     0.000: 0(acos)
# 13554987
# 14.574
# 0.000
# 14.574
# 0.000: 0(append)
# 1
# 0.000
# 0.000
# 94.765
# 94.765: 0(exec)
# 45617
# 0.050
# 0.000
# 0.050
# 0.000: 0(get)
# 11625627
# 12.007
# 0.000
# 12.007
# 0.000: 0(isalnum)
# 187
# 0.000
# 0.000
# 0.000
# 0.000: 0(join)
# 10257840
# 10.751
# 0.000
# 10.751
# 0.000: 0(len)
# 99
# 0.000
# 0.000
# 0.000
# 0.000: 0(lower)
# 363464
# 2.156
# 0.000
# 2.224
# 0.000: 0(next)
# 463
# 0.002
# 0.000
# 0.002
# 0.000: 0(nl_langinfo)
# 463
# 0.038
# 0.000
# 0.045
# 0.000: 0(open)
# 99
# 0.002
# 0.000
# 0.002
# 0.000: 0(print)
# 364
# 0.004
# 0.000
# 0.004
# 0.000: 0(reader)
# 1
# 0.001
# 0.001
# 0.001
# 0.001: 0(setprofile)
# 275
# 0.001
# 0.000
# 0.001
# 0.000: 0(split)
# 87824
# 0.133
# 0.000
# 0.133
# 0.000: 0(sqrt)
# 96614
# 0.093
# 0.000
# 0.093
# 0.000: 0(strip)
# 7262
# 0.030
# 0.000
# 0.030
# 0.000: 0(utf_8_decode)
# 99
# 0.001
# 0.000
# 0.001
# 0.000: 0(writer)
# 5049
# 0.087
# 0.000
# 0.247
# 0.000: 0(writerow)
# 1
# 0.000
# 0.000
# 94.765
# 94.765 < string >: 1( < module >)
# 463
# 0.002
# 0.000
# 0.004
# 0.000
# _bootlocale.py: 23(getpreferredencoding)
# 99
# 0.000
# 0.000
# 0.000
# 0.000
# codecs.py: 185(__init__)
# 364
# 0.001
# 0.000
# 0.001
# 0.000
# codecs.py: 259(__init__)
# 364
# 0.002
# 0.000
# 0.002
# 0.000
# codecs.py: 308(__init__)
# 7262
# 0.038
# 0.000
# 0.068
# 0.000
# codecs.py: 318(decode)
# 363100
# 4.311
# 0.000
# 8.503
# 0.000
# csv.py: 106(__next__)
# 99
# 0.001
# 0.000
# 0.002
# 0.000
# csv.py: 130(__init__)
# 99
# 0.001
# 0.000
# 0.007
# 0.000
# csv.py: 140(writeheader)
# 5049
# 0.010
# 0.000
# 0.010
# 0.000
# csv.py: 144(_dict_to_list)
# 50490
# 0.110
# 0.000
# 0.160
# 0.000
# csv.py: 150( < genexpr >)
# 5049
# 0.022
# 0.000
# 0.278
# 0.000
# csv.py: 152(writerow)
# 364
# 0.002
# 0.000
# 0.006
# 0.000
# csv.py: 80(__init__)
# 364
# 0.000
# 0.000
# 0.000
# 0.000
# csv.py: 89(__iter__)
# 725836
# 0.952
# 0.000
# 0.966
# 0.000
# csv.py: 92(fieldnames)
# 263472
# 9.644
# 0.000
# 16.589
# 0.000
# docdist1.py: 148(inner_product)
# 87824
# 0.925
# 0.000
# 17.757
# 0.000
# docdist1.py: 174(vector_angle)
# 175648
# 31.658
# 0.000
# 58.484
# 0.000
# docdist1.py: 69(get_words_from_string)
# 175648
# 3.898
# 0.000
# 6.024
# 0.000
# docdist1.py: 96(count_frequency)
# 88
# 0.070
# 0.001
# 4.860
# 0.055
# optimize_this.py: 101(lookup_similar_id)
# 88
# 1.520
# 0.017
# 86.300
# 0.981
# optimize_this.py: 142(find_alternate_sentence)
# 1
# 0.004
# 0.004
# 94.765
# 94.765
# optimize_this.py: 15(main)
# 88
# 0.001
# 0.000
# 0.002
# 0.000
# optimize_this.py: 212(find_unique_targets)
# 364
# 1.384
# 0.004
# 10.340
# 0.028
# optimize_this.py: 249(get_csv_rows)
# 99
# 0.020
# 0.000
# 0.319
# 0.003
# optimize_this.py: 261(write_output_file)
# 99
# 0.147
# 0.001
# 3.271
# 0.033
# optimize_this.py: 38(set_sentence_id)
# 99
# 0.002
# 0.000
# 0.004
# 0.000
# optimize_this.py: 70(replace_target_with_blank)
# 1
# 0.000
# 0.000
# 94.767
# 94.767
# profile: 0(main())
# 0
# 0.000
# 0.000
# profile: 0(profiler)

###################### After the change ################################
  #        62811793 function calls in 230.234 seconds

  #  Ordered by: standard name

  #  ncalls  tottime  percall  cumtime  percall filename:lineno(function)
  # 2105997    2.257    0.000    2.257    0.000 :0(acos)
  # 4247037    4.578    0.000    4.578    0.000 :0(append)
  #     150    0.000    0.000    0.000    0.000 :0(endswith)
  #       1    0.000    0.000  230.234  230.234 :0(exec)
  #  955251    1.313    0.000    1.313    0.000 :0(get)
  #     912    0.002    0.000    0.002    0.000 :0(join)
  # 8482518   11.386    0.000   11.386    0.000 :0(len)
  #     459    0.001    0.000    0.001    0.000 :0(lower)
  # 4243085   22.737    0.000   23.363    0.000 :0(next)
  #    1372    0.007    0.000    0.007    0.000 :0(nl_langinfo)
  #    1372    0.131    0.000    0.152    0.000 :0(open)
  #     459    0.013    0.000    0.013    0.000 :0(print)
  #     913    0.010    0.000    0.010    0.000 :0(reader)
  #       1    0.001    0.001    0.001    0.001 :0(setprofile)
  # 4213359    8.277    0.000    8.277    0.000 :0(split)
  # 2105997    2.512    0.000    2.512    0.000 :0(sqrt)
  #    2462    0.003    0.000    0.003    0.000 :0(startswith)
  # 1115462    1.014    0.000    1.014    0.000 :0(strip)
  # 4211994   12.832    0.000   12.832    0.000 :0(translate)
  #   80262    0.270    0.000    0.270    0.000 :0(utf_8_decode)
  #     459    0.006    0.000    0.006    0.000 :0(writer)
  #  106029    2.476    0.000    6.585    0.000 :0(writerow)
  #       1    0.000    0.000  230.234  230.234 <string>:1(<module>)
  #    1372    0.008    0.000    0.014    0.000 _bootlocale.py:23(getpreferredencoding)
  #     459    0.001    0.000    0.001    0.000 codecs.py:185(__init__)
  #     913    0.002    0.000    0.002    0.000 codecs.py:259(__init__)
  #     913    0.004    0.000    0.006    0.000 codecs.py:308(__init__)
  #   80262    0.356    0.000    0.627    0.000 codecs.py:318(decode)
  # 4242172   46.619    0.000   91.765    0.000 csv.py:106(__next__)
  #     459    0.003    0.000    0.010    0.000 csv.py:130(__init__)
  #     459    0.005    0.000    0.035    0.000 csv.py:140(writeheader)
  #  106029    0.270    0.000    0.270    0.000 csv.py:144(_dict_to_list)
  # 1060290    2.798    0.000    4.109    0.000 csv.py:150(<genexpr>)
  #  106029    0.596    0.000    7.452    0.000 csv.py:152(writerow)
  #     913    0.005    0.000    0.015    0.000 csv.py:80(__init__)
  #     913    0.001    0.000    0.001    0.000 csv.py:89(__iter__)
  # 8483431   10.397    0.000   10.432    0.000 csv.py:92(fieldnames)
  # 4211994   13.382    0.000   13.382    0.000 docdist_dict.py:109(count_frequency)
  # 6317991   19.158    0.000   19.158    0.000 docdist_dict.py:137(inner_product)
  # 2105997   16.268    0.000   40.195    0.000 docdist_dict.py:151(vector_angle)
  # 4211994   14.086    0.000   35.191    0.000 docdist_dict.py:93(get_words_from_string)
  #       1    0.000    0.000  230.234  230.234 profile:0(main())
  #       0    0.000             0.000          profile:0(profiler)
  #     453    0.002    0.000    0.002    0.000 si330-hw3-zblitz.py:106(lookup_similar_id)
  #     453   19.368    0.043  163.925    0.362 si330-hw3-zblitz.py:143(find_alternate_sentence)
  #       1    0.020    0.020  230.233  230.233 si330-hw3-zblitz.py:20(main)
  #     453    0.009    0.000    0.016    0.000 si330-hw3-zblitz.py:213(find_unique_targets)
  #     913   14.824    0.016  111.248    0.122 si330-hw3-zblitz.py:250(get_csv_rows)
  #     459    0.292    0.001    7.840    0.017 si330-hw3-zblitz.py:270(write_output_file)
  #     459    1.925    0.004   58.387    0.127 si330-hw3-zblitz.py:43(set_sentence_id)
  #     459    0.011    0.000    0.020    0.000 si330-hw3-zblitz.py:75(replace_target_with_blank)

############################### Questions ################################
# Part 1
# 1. Without any speed improvements, the program ran at 94.765 seconds
# 2. After the program runs, a new csv (Sentence_Database_With_ID is created)
# 3. According to the profiler output, docdist1.py:69(get_words_from_string) takes the most time to run at 31.66 seconds
# 4. See above

#Part 2
# 1. CHANGE 1, Changed this file above so that it creates a dictionary, Time reduced from 94.76 seconds to 15.23 seconds, Time reduction factor = 6.2, Instead of iterating through a list, it is significantly faster to use a dictionary
# 2. Change 2 - get each similar ID and find similar sentence, using a dictionary is faster than list, Time reduced from 14.37 to 10.44 seconds, Time reduction factor = 1.38, setting these values ( row['SimilarTo_SentID_GM'] and row['SimilarTo_Sentence'])
# 3. Change 3 - creating two dictionaries as opposed to lists to write all of the rows to the output file, Time reduced from 10.44 seconds to 10.36 seconds, Time reduction factor = 1.01,

#Part 3
# 1. With the full input files, the final runtime was 230.234 seconds
# 2. After the speed improvements, the function with the highest total time was csv.py:106(__next__) with a time of 46.619 seconds
# 3. I learned from this homework that the data structure you put your information in is very crucial to the runtime. In the future, it is better to use dictionaries as opposed to lists because they run significantly faster. It is also an important skill to be able to look at code and figure out how to make it more efficient - being able to understand someone elses code is arguably harder than creatively generating your own code.