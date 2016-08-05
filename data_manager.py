import csv
import os
import fnmatch
import glob
import subprocess
from flask import request, flash
from stop_words import get_stop_words
import stash_api
import settings
import shutil
from nltk.stem.lancaster import LancasterStemmer
from datetime import datetime


# called by parse_csv
# checks is passed in string is in list of modules to be ignored
def ignore_module(entity):
    # list to be expanded
    ignore_list = {'bower.json': ' ', '.gitignore': ' ', 'README.md': ' '}
    if entity in ignore_list:
        return True
    else:
        return False


# called by result view
# reads opened csv file
# returns a list of the headers, and a dictionary of each row
def parse_csv(folder, filename):
    data_dict = []  # list of dictionaries, one dict for each row
    key_list = []  # list of row headers / keys

    try:
        csv_file = open(os.path.join(folder, filename), 'rt')
    except (FileNotFoundError, IOError):
        return ([], [])

    reader = csv.reader(csv_file)
    for i, row in enumerate(reader):
        temp_dict = {}
        if i == 0:
            key_list = row  # if first row of file, fill key_list with headers
        else:
            if not row:
                break  # if codemaat produces blank csv's
            # fill temp dict with each value in the row
            if not ignore_module(row[0]):
                for j, key in enumerate(key_list):
                    temp_dict[key] = row[j]  # pair respective header w/ value
                data_dict.append(temp_dict)
    csv_file.close()

    return (data_dict, key_list)


# called by merge_csv
# parses module names/lines of code from lines.csv
def get_lines_list(repo_name):
    lines_list = []  # list of dictionaries, one dict for each row

    try:
        with open("lines_" + repo_name + ".csv") as lines_file:
            lines_reader = csv.DictReader(lines_file)
            for row in lines_reader:
                # create a dict with name and num lines; add it to list
                lines_list.append({'entity': row['filename'],
                                  'lines': row['code']})
    except IOError:
        print("file not found")

    return lines_list


# called by merge_csv
# combines data from lines.csv with metrics.csv
def get_merge_list(repo_name, lines_list):
    merge_list = []  # list of dictionaries, one dict for each row

    try:
        with open("metrics_" + repo_name + ".csv", "rt") as revs_file:
            revs_reader = csv.DictReader(revs_file)
            for row in revs_reader:
                # for each entity in metrics, look for it in lines_list
                for module in lines_list:
                    if row['entity'] in module['entity']:
                        # add new dict w/ name, revs, and lines to merge_list
                        merge_list.append({
                            'entity': row['entity'],
                            'n-revs': row['n-revs'],
                            'lines': module['lines']})
    except IOError:
        print("file not found")

    return merge_list


# called by generate_data/generate_data_hotspot
# retrieves combined data from lines.csv & merge.csv
# writes combined data into new hotspots.csv file
def merge_csv(repo_name):
    lines_list = get_lines_list(repo_name)
    merge_list = get_merge_list(repo_name, lines_list)

    try:
        with open("hotspots_" + repo_name + ".csv", "wt") as hotspot_file:
            # create a new csv file
            fieldnames = ['entity', 'n-revs', 'lines']  # use these as headers
            writer = csv.DictWriter(hotspot_file, fieldnames=fieldnames)
            writer.writeheader()  # write fieldnames into header row
            for row in merge_list:
                # write each row from merge_list into new csv file
                writer.writerow(row)
    except IOError:
        print("file not found")
        return


# called by get_word_frequency to handle adding / incrementing
# words to the frequency word_list
def parse_word(stem, word, word_list, stop_words):
    # skip adding if word is in stop_words
    if word in stop_words or len(word) == 1:
        return

    # add the word into the word_list
    entry = [x for x in word_list if x["stem"] == stem]
    if entry:
        entry[0]['freq'] += 1
        if word in entry[0]['text']:
            entry[0]['text'][word] += 1
        else:
            entry[0]['text'][word] = 1
    else:
        word_list.append({'stem': stem, 'text': {word: 1}, 'freq': 1})


# aqcuires list of all words from commit messages
# creates a list of dictionaries of words paired with frequency of occurrence
def get_word_frequency(folder, filename):
    try:
        logfile = open(os.path.join(folder, filename), 'rt')
    except UnicodeError:
        logfile = io.open(os.path.join(folder, filename),
            'rt', encoding='utf-8')
    except (FileNotFoundError, IOError):
        return []
    log_list = logfile.read().split()

    word_list = []
    stemmer = LancasterStemmer()

    # define stop_words here rather than in a loop
    stop_words = get_stop_words('en')

    for word in log_list:
        # Strip, Stem, and then parse word into word_list
        word = word.strip("\"'/;:?{}[]!.,()").lower()
        stem = stemmer.stem(word)
        parse_word(stem, word, word_list, stop_words)

    # Sort and return selection of the word_list
    sorted_word_list = sorted(word_list, key=lambda x: x['freq'], reverse=True)

    textFreqPairs = []
    for word in sorted_word_list[:100]:
        key = max(word['text'].keys(), key=(lambda k: word['text'][k]))
        textFreqPairs.append({'text': key, 'freq': word['freq']})

    logfile.close()
    return (textFreqPairs, [])  # blank array for keys variable
