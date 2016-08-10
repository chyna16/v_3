<img src="http://ec2-52-7-214-244.compute-1.amazonaws.com/static/images/V3_Logo.svg" alt="V3" height="36px"/>

# Viacom Version Visualizer

Inspired by Adam Tornhill's book <i>Your Code as a Crime Scene</i>, this web application is designed to help locate problem areas in your code, find ways to improve it, and eliminate productivity sinks. This is done by analyzing your version-control logs and highlighting aspects of the project's history for you to inspect.

### Why?

1. We want to prioritize the changes we make to large projects in order to reduce complexity and create easy to modify code.

2. This prioritization should be based on how we interact with the project in order to maximize value in the least amount of time.

3. Hard to understand and tricky to modify code slows productivity and degrades system quality.

4. Rather than guessing at which sections of code need to be revised, we want the project to tell us where our work will payoff the most.


## Getting Started
------------------

### System
Running V3 is best done on a Mac or Linux environment. If you are working on a Windows machine, I'd recommend using VirtualBox running your favorite recent flavor of Linux (Ubuntu is always a safe bet).

### Prerequisites
1. Download Codemaat from [Adam Tornhill's website](http://www.adamtornhill.com/code/crimescenetools.htm) and add it to your environment.

2. Also ensure that you have:
    * Java v1.6+
    * Python 2.7
    * Python 3
    * cloc (count lines of code)
    * Pip
    * git

3. Next [download and install RabbitMQ](http://www.rabbitmq.com/download.html). We will use their default configuration so make sure that you have it up and running.

### Stop, Cloning Time!

1. It's finally time to clone V3. Choose a convenient directory and use the link provided by stash to clone the repository with git.

2. Setup and activate a Virtual environment and load <code>requirements.txt</code> found in the project folder. [How?](http://docs.python-guide.org/en/latest/dev/virtualenvs/) (make sure the default python version is python 3)

3. In the virtual environment install <b>csvcat</b> on python2.7

4. Next Create two folders, 'repos' and 'csv', as siblings to the cloned V3  (DO NOT put V3 in the repos folder).

5. Now copy and rename <code>settings.template.py</code> to <code>settings.py</code>.  (DO NOT put V3 in the repos folder), and your stash credentials into the file.

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

## Editing V3
If you would like to get started editing V3, I would recommend looking at an analysis of the project on V3 (meta, I know). Hotspots, in particular, should give you an idea of the main files that you should look at to get started. But, as you may have already figured, <code>visualizer.py</code> contains the main Flask app.


## Visualizations
-----------------

### Interpretation is Key
Each visualization highlights aspects of a project that should be taken as leads for you look into further. There are no definitive rules for what is good or bad. There is no replacement for your intuition, but we can steer it in the right direction.

### Hotspots
When analyzing hotspots, the graph is shown as a bubble chart. The size of the bubble depends on the number of lines of code, while the hue is related to the amount of revisions made. A combination of a small bubble with a dark hue of red are the modules that you should bring to your attention.

### Word Cloud
When using the word cloud, The size of words are related to the amount of times they were used in commit messages. Bigger and lighter red means more frequent, while smaller and darker red means less frequent. Mouse over each word to see how many times that word was used. Use the more common words to gauge you or your team's progress on their work.

### Metrics
Organizational Metrics are for predicting possible issues regarding quality of your code. Each module shows the number of unique authors that worked on it, and the number of revisions made to that module. Modules with a high number of authors and revisions together may be a sign of quality issues.

### Coupling
Coupling analyzes the connections between modules made in the current repository. The degree, which is the average amount of times the two modules are changed together, is shown as a percentage. The higher the percent, the greater amount of times those modules were committed together. Average revisions shows the average number of times those two modules were revised.

### Module Churn
Using the module churn allows you to compare the amount of lines added and deleted in each module of the selected repository. Use this to see how your code has evolved over time. Modules with a high number of lines and a low number of deletions are areas of interest.
