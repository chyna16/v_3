import csv
import os
import fnmatch
import glob
import subprocess
from flask import request, flash
from stop_words import get_stop_words
import stash_api
import settings
import generator
import shutil
from nltk.stem.lancaster import LancasterStemmer
from datetime import datetime


# called by refresh_repos
def get_dir_list(path):
    dir_list = [item for item in os.listdir(path)
            # if 'path/item' is valid address, add item to list
            if os.path.isdir(os.path.join(path, item))]
    return dir_list


# called by: get_repo_list, refresh_single_repo
# uses git log to get first & last commit dates
def get_commit_dates(repo_dir, repo):
    first_date = subprocess.getoutput('git --git-dir ' +
        os.path.join(repo_dir, repo, '.git') + ' log --pretty=format:"%ad"' +
        ' --no-patch --date=short --reverse | head -1')
    last_date = subprocess.getoutput('git --git-dir ' +
        os.path.join(repo_dir, repo, '.git') +
        ' log --pretty=format:"%ad" --date=short --no-patch | head -1')
    return (first_date, last_date)


# called by: index view
# params: path of repo directory, list of repo folders
def get_repo_list(dir_list, repo_dir):
    repo_list = []
    for repo in dir_list:
        first_date, last_date = get_commit_dates(repo_dir, repo)
        try:
            filename = os.path.join(repo_dir, repo, 'timetag.txt')
            with open(filename, 'rt') as timetag:
                latest_datetime = timetag.read()
                repo_list.append(repo + '|' +
                    latest_datetime + '|' + first_date + '|' + last_date)
        except IOError:
            repo_list.append(repo + '|' + ' ' + '|' + first_date +
                             '|' + last_date)
    return repo_list


# called by: refresh_single_repo, clone_repo
def add_datetime(folder_path):
    with open(os.path.join(folder_path, 'timetag.txt'), 'wt') as timetag:
        d = str(datetime.now()).split('.')[0].split(' ')  # date in string
        timetag.write(d[0])  # add a textfile with current date w/o ms or time


# called by: refresh_repos, index view
def refresh_single_repo(repo_dir, repo):
    clone_url = stash_api.get_repo_url(repo, 'http')
    if not clone_url:
        return  # if function returned false
    else:
        shutil.rmtree(os.path.join(repo_dir, repo))  # delete repository
        clone_repo(clone_url, repo_dir, settings.password)
        from_date, to_date = get_commit_dates(repo_dir, repo)
        csv_path = os.path.join(settings.csv_dir,
            repo + "_" + from_date + "_" + to_date)
        generator.process_log(repo, from_date, to_date, csv_path)


# called by: visualizer at timed intervals
# updates already cloned repositories
def refresh_repos(repo_dir):
    repo_list = get_dir_list(repo_dir)
    for repo in repo_list:
        filename = os.path.join(repo_dir, repo, 'timetag.txt')
        try:
            with open(filename, 'rt') as timetag:
                datetime = timetag.read()
        except IOError:
            datetime = ' '
        project = stash_api.get_repo_detail(repo, 'project', 'key')
        if datetime < stash_api.get_repo_timestamp(project, repo, '1')[0]:
            refresh_single_repo(repo_dir, repo)


# Check repo clone if it doesn't exist and re-clone if it is old
def repo_check_and_update(repo_name, proj_key, to_date, celery_task):
    repo_list = get_repo_list(get_dir_list(settings.repo_dir),
                              settings.repo_dir)
    available_repo = [repo for repo in repo_list
        if repo.split('|')[0] == repo_name]
    remote_last_commit = stash_api.get_repo_timestamp(proj_key,
        repo_name, '1')[0]

    if available_repo == []:
        # if repo doesn't exist, clone it
        repo_url = stash_api.get_repo_url(repo_name, 'http')
        clone_repo(repo_url, settings.repo_dir, settings.password)
    elif (remote_last_commit > available_repo[0].split('|')[1] < to_date):
        # else if local copy is older than latest commit, refresh
        refresh_single_repo(settings.repo_dir, repo_name, celery_task)


# called by visualizer index view
# parses the user given clone url and password; returns combined http url
def get_clone_command(clone_url, password):
    # add password to the string right before the '@'
    char = clone_url.index('@')  # string index of '@'
    command = clone_url[:char] + ':' + password + clone_url[char:]
    return command


# called by visualizer index view
# calls git clone command with an appropriate url
def clone_repo(clone_url, location, password):
    if 'http' in clone_url:
        # if using http url, apply password to url
        clone_cmd = get_clone_command(clone_url, password)
    else:
        clone_cmd = clone_url
    repo = clone_url.split('/').pop().split('.')[0]
    os.system('git clone ' + clone_cmd + ' ' + os.path.join(location, repo))
    add_datetime(os.path.join(location, repo))
