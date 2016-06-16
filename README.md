Viacom Value Visualizer
This web based application is for obtaining more insight towards you/your team's work by analyzing your repositories and highlighting any deficiences and potential problems in your code.

Upon reaching the home page, there are three tabs to navigate though.

Clone a repository
You can upload a remote repository of your choosing, as long you provide an authentic stash clone URL and password. If the repository already exists, this process will be skipped. After cloning is complete, the repository will be added to the list of available repositories.

Available Repositories
Select from the list of locally available repositories. Any new repositories cloned from the 'Clone A Repository' or 'Stash Repositories' tab will be added to this list.

Stash Repositories
Displays a list of available projects from MTVI directory on stash. Projects are listed by project key. Once a project is selected, you will be redirected to the list of remote repositories in the project. Selecting a repository will begin to clone the repository locally, then begin analysis.

Analysing
Once a repository is selected, analysis will begin via codemaat. Depending on the size of your repository, this process may take a few seconds to a minute. Once analysis is complete, you will be returned to a page of available visualizations. Select one from the available list.

Interpertation is Key
When using this application, please understand that some modules may be intentionally built in a certain way. Many of the results in these visualizations are for theoretical use, and less of a fact checker. For example, a module having a lot of lines of code doesn't always mean there's something wrong with it, but it definitely is an area to check out.

Hotspots
When anaylzing hotspots, the graph is shown as a bubble chart. The size of the bubble depends on the amount of lines of code added, while the hue is related to the amount of revisions made. A combination of a small bubble with a dark hue of red are the modules that you should bring to your attention.

Word Cloud
When using the word cloud, The size of words are related to the amount of times they were used in commit messages. Bigger and lighter red means more frequent, while smaller and darker red means less frequent. Use the more common words to gauge you or your team's progress on their work.

Metrics
Orginazational Metrics are for predicting possible issues regarding quality of your code. Each module shows the number of unique authors that worked on it, and the number of revisions made to that module. Modules with a high number of authors and revisions together may be a sign of quality issues.

Coupling
Coupling analyzes the connections between modules made in the current repository. The degree, which is the average amount of times the two modules are changed together, is shown as a percentage. The higher the percent, the greater amount of times those modules were committed together. Average revisions shows the average number of times those two modules were revised.