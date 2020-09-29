import mysql.connector
import re
from collections import Counter
import json
from unidecode import unidecode
import time

def get_stop_word_dict():
    with open('all_stop_words.json') as f:
        stop_terms = json.load(f)
    return stop_terms
def is_stop_word(word, language, stop_word_dict):
    return word in stop_word_dict[language] or len(word) <= 1
def get_decade_list(start_decade, end_decade):
    """Creates list of decades

    Makes a list of all decades between the decades 
    given in the args. Includes the start_decade
    and excludes 

    Args:
        start_decade: integer of decade to start
           list from.
        end_decade: integer of decade to end list at.

    Returns:
        An integer array  list of all decades.
    """
    decade_list = []
    for decade in range(start_decade, end_decade, 10):
        decade_list.append(decade)
    return decade_list

def get_top_100(lang, decade):
    # select all titles for the language and decade
    query = "select title from master_help where lang=\"" + lang + "\" and decade=\"" + str(decade/10) + "\";"
    db_cursor.execute(query)
    result = db_cursor.fetchall()
    all_terms = []
    for row in result:
        title = unidecode(row[0].lower())
        # remove unwanted characters from titles
        title = re.sub(r'[^\w\s]', '', title)
        #print(title)
        these_terms = title.split()
        all_terms += these_terms
    term_counts = Counter(all_terms)
    top_100 = term_counts.most_common(100)
    return top_100

# connect to webc database
print("Connecting to database ...")
webc_db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "root",
    database = "webc"
)
print("Done.\n")
# create database cursor
db_cursor = webc_db.cursor()
# get a list of decades
decades = get_decade_list(1500, 1800)

# get languages in database
langs = {'eng':"English", 'spa':"Spanish", 'ita':"Italian", 'fre':"French", 'lat':"Latin", 
         'dut':"Dutch", 'ger':"German"}
select_langs = ['eng']
# get top 100 words every decade
all_terms = []
for lang in select_langs:
    for decade in decades:
        top_100 = get_top_100(lang, decade)
        for tup in top_100:
            term = tup[0]
            all_terms.append(term)
# get frequency
term_counter = Counter(all_terms).most_common()
# determine stop words
print("Printing to file...")
f = open('term_freq.csv', 'w')
f.write('term,count,stop_word\n')
f_stop = open('stop_word_freq.csv', 'w')
f_stop.write('term,count\n')
f_other = open('other_word_freq.csv', 'w')
f_other.write('term,count\n')

stop_word_dict = get_stop_word_dict()
print(len(stop_word_dict['eng']))

stop_words = []
other_words = []
# sum of all frequencies by type
sw_sum = 0
ow_sum = 0
# sum2 of all frequencies > 1 by type
sw_sum2 = 0
ow_sum2 = 0
# minimum frequencies by type
sw_min = len(decades)
ow_min = sw_min
# maximum frequencies by type
sw_max = 0
ow_max = 0
# count of words by type
sw_count = 0
ow_count = 0
# count of words where frequency > 1 by type
sw_count2 = 0
ow_count2 = 0

for tup in term_counter:
    term = tup[0]
    frequency = tup[1]
    if is_stop_word(term, 'eng', stop_word_dict):
        stop_words.append(tup)
        f.write(term + "," + str(frequency) + ",yes\n")
        f_stop.write(term + "," + str(frequency))
        sw_sum += frequency
        sw_count += 1
        if frequency < sw_min:
            sw_min = frequency
        if frequency > sw_max:
            sw_max = frequency
        if frequency > 1:
            sw_sum2 += frequency
            sw_count2 += 1;
    else:
        other_words.append(tup)
        f.write(term + "," + str(frequency) + ",no\n")
        f_other.write(term + "," + str(frequency))
        ow_sum += frequency
        ow_count += 1
        if frequency < ow_min:
            ow_min = frequency
        if frequency > ow_max:
            ow_max = frequency
        if frequency > 1:
            ow_sum2 += frequency
            ow_count2 += 1;

sw_avg = sw_sum/sw_count
ow_avg = ow_sum/ow_count

sw_avg2 = sw_sum2/sw_count2
ow_avg2 = ow_sum2/ow_count2


print("# stop words: " + str(sw_count) + "\n\tavg: " + str(sw_avg) +
      "\n\tmin: " + str(sw_min) + "\n\tmax: " + str(sw_max))
print("# other words: " + str(ow_count) + "\n\tavg: " + str(ow_avg) +
      "\n\tmin: " + str(ow_min) + "\n\tmax: " + str(ow_max))
print("Where frequency > 1 ...")
print("# stop words: " + str(sw_count2) + ", avg: " + str(sw_avg2))
print("# other words: " + str(ow_count2) + ", avg: " + str(ow_avg2))

