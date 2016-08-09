# Viacom Version Visualizer

![V3 Logo](https://stash.mtvi.com/projects/ME/repos/v3/browse/static/images/V3_Logo.svg)

This web based application is for obtaining more insight towards you/your team's work by analyzing your repositories and highlighting any deficiencies and potential problems in your code. With this app, you are able to view your repository from a developmental and technical standpoint, allowing you to easily find areas to improve on.

## Getting Started

### System
Running V3 is best done on a Mac or Linux environment. If you are working on a Windows machine, I'd recommend using VirtualBox running your favorite recent flavor of Linux (Ubuntu is always a safe bet).

### Prerequisites
1. Download Codemaat from [Adam Tornhill's website](http://www.adamtornhill.com/code/crimescenetools.htm) and add it to your environment.

2. Also ensure that you have
    * Java v1.6+
    * Python 2.7
    * Python 3
    * cloc (count lines of code)
    * Pip
    * git

3. Next [download and install RabbitMQ](http://www.rabbitmq.com/download.html). We will use their default configuration so make sure that you have it up and running.

### Stop, Cloning Time!
1. Finally time to clone V3 to your local destination of choice using the stash link.

2. Setup and activate a Virtual environment and load requirements.txt found int the project folder. [How?](http://docs.python-guide.org/en/latest/dev/virtualenvs/) (Make sure the default python version is python 3)

3. In the virtual environment install csvcat on python2.7 (pip2 install csvcat)

4. Next Create two folders, repos and csv, in a location of greatest convenience (usually siblings with the V3 folder).

5. Now copy and rename settings.template.py to settings.py and put in the path to the two folders you just created, the path to Codemaat, the path to the cloned version of V3 (DO NOT put V3 in the repos folder), and your stash credentials into the file.

### Running V3

Oh boy, here we go! Open up two console windows that are in the V3 directory with the virtual environment activated and run these commands:

Terminal 1:
<code>
celery -A visualizer.celery worker
</code>

Terminal 2:
<code>
python visualizer.py
</code>

If both are running without error, navigate to [localhost:5000](localhost:5000)

## Using V3

Upon reaching the home page, there are three tabs to navigate though:

* Available Repositories
* Stash Repositories
* Clone A Repository

### Available Repositories

Select from the list of locally available repositories. Any new repositories cloned from the 'Clone A Repository' or 'Stash Repositories' tab will be added to this list. When selecting a repository, use the 'Refresh' button to update the repository on the server and obtain the latest version. Use the 'Next' button to begin analyzing your repository.

### Find a Repository

Displays a list of available projects from MTVI directory on stash. Projects are listed by the project key's name. Once a project is selected, you will be redirected to the list of remote repositories in the project. Selecting a repository will begin to clone the repository locally, then begin analysis.

### Clone a repository

You can upload a remote repository of your choosing, as long you provide an authentic stash clone URL and password. If the repository already exists, this process will be skipped. After cloning is complete, the repository will be added to the list of available repositories. Support for github repositories will be added soon.

## Analyzing

Once a repository is selected, analysis will begin. Depending on the size of your repository, this process may take a few seconds to a minute. Once analysis is complete, you will be returned to a page of available visualizations. Select one from the available list.

## Interpretation is Key

When using this application, please understand that some modules may be intentionally built in a certain way. Many of the results in these visualizations are for theoretical use, and less of a fact checker. For example, a module having a lot of lines of code doesn't always mean there's something wrong with it, but it definitely is an area to check out.

## Visualizations

### Hotspots

When analyzing hotspots, the graph is shown as a bubble chart. The size of the bubble depends on the number of lines of code, while the hue is related to the amount of revisions made. A combination of a small bubble with a dark hue of red are the modules that you should bring to your attention.

### Word Cloud

When using the word cloud, The size of words are related to the amount of times they were used in commit messages. Bigger and lighter red means more frequent, while smaller and darker red means less frequent. Mouse over each word to see how many times that word was used. Use the more common words to gauge you or your team's progress on their work.

### Metrics

Orginazational Metrics are for predicting possible issues regarding quality of your code. Each module shows the number of unique authors that worked on it, and the number of revisions made to that module. Modules with a high number of authors and revisions together may be a sign of quality issues.

### Coupling

Coupling analyzes the connections between modules made in the current repository. The degree, which is the average amount of times the two modules are changed together, is shown as a percentage. The higher the percent, the greater amount of times those modules were committed together. Average revisions shows the average number of times those two modules were revised.

### Module Churn

Using the module churn allows you to compare the amount of lines added and deleted in each module of the selected repository. Use this to see how your code has evolved over time. Modules with a high number of lines and a low number of deletions are areas of interest.
