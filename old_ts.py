"""
"""
import mysql.connector
import re
from collections import Counter
import json
from unidecode import unidecode
import time

def get_stop_word_dict():
    with open('all_stop_words.json') as f:
        stop_terms = json.load(f)
    # print(stop_terms)
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

def get_langs_from_db():
    # get languages in database
    db_cursor.execute("select lang from master_help group by lang;")
    result  = db_cursor.fetchall()
    langs = []
    for row  in result:
        if row[0] != '':
            langs.append(row[0])
    return langs

def get_top_term(lang, decade, stop_word_dict):
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
	for term in these_terms:
            if not is_stop_word(term, lang, stop_word_dict):
                all_terms.append(term)
    term_counts = Counter(all_terms)
    return term_counts.most_common(1)[0]

def get_all_top_terms(langs, decades, print_rows=True):
    stop_word_dict = get_stop_word_dict()
    top_terms = []
    # iterate through each decade for each lang
    for lang in langs:
    # print("Getting most common words that exist in each decade...")
        for decade in decades:
             # print(decade)
             term = get_top_term(lang, decade, stop_word_dict)
             long_lang = langs[lang]
             term_string = term[0] + "\tcommon\t" + long_lang + "\t" + str(decade) + "\t" + str(term[1]) + "\n"
             top_terms.append(term_string)
             if(print_rows):
                 print(term_string)
    return top_terms

def get_term_file(file_name, top_terms):
    f = open(file_name, 'w')
    f.write("term\tterm_key\tlanguage\tdecade\tcount\n")
    for line in top_terms:
        f.write(line)
    f.close()

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
    return term_counts.most_common(100)

def get_all_terms(lang, decades):
    all_terms = []
    all_count_dicts = {}
    for decade in decades:
        all_count_dicts.update(get_top_100(lang,decade))
    for term in all_count_dicts
    return all_terms

def get_frequency(all_terms):
    return Counter(all_terms).most_common()

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

print("Getting all terms for English...")
t0 = time.time()
all_terms = get_all_terms('eng', decades) 
print(len(all_terms))
#eng_1650 = get_top_100('eng', 1650)
#print(eng_1650)
print("Time:")
print(time.time()-t0)
print("Done.\n")

print("Getting frequencies..")
frequencies = get_frequency(all_terms)

print("Printing to file...")
f = open('term_freq.csv', 'w')
f.write('term,count,stop_word\n')
stop_words = []
other_words = []
stop_word_dict = get_stop_word_dict()

sw_sum = 0
ow_sum = 0
sw_count = 0
ow_count = 0


for tup in frequencies:
    term = tup[0]
    frequency = tup[1]
    if is_stop_word(term, 'eng', stop_word_dict):
        stop_words.append(tup)
        f.write(term + "," + str(frequency) + ",yes\n")
        sw_sum += frequency
        sw_count += 1
    else:
        other_words.append(tup)
        f.write(term + "," + str(frequency) + ",no\n")
	ow_sum += frequency
        ow_count += 1

sw_avg = sw_sum/sw_count
ow_avg = ow_sum/ow_count

print("# stop words: " + str(sw_count) + ", avg: " + str(sw_avg))
print("# other words: " + str(ow_count) + ", avg: " + str(ow_avg))

