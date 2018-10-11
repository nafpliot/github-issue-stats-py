# GitHub Issue Stats py

GitHub Issue Stats py is a Python 3 command line tool / library that retrieves GitHub (or GitHub Enterprise) issue data, and creates useful stats and charts.

Q: What are we using to retrieve the data?  
A: GitHub's [GraphQL API](https://developer.github.com/v4/)

Q: How the charts are plotted?  
A: By using [Plotly](https://plot.ly/). That also means that you can easily export them to plot.ly!

The statistics that can be retrieved / plotted at the moment are:
- General Stats
    - Total issue count
    - Issue open - close meantime
    - Issue assign meantime
- How many issues are opened per month
- How many issues are opened per day
- How many issues are opened per user
- How many comments are made per user
- How many times a given text is found in a comments per user
- How many issues are found with the given label(s)

# Some screenshots

(The data is taken from our friends of the [reicast-emulator](https://github.com/reicast/reicast-emulator) project)

![general_stats](https://user-images.githubusercontent.com/19995558/46548032-2981f100-c8ce-11e8-932a-56d80fada51c.png)
![issues_per_month](https://user-images.githubusercontent.com/19995558/46548029-2981f100-c8ce-11e8-8041-585cb02cd67a.png)
![issues_per_day](https://user-images.githubusercontent.com/19995558/46548030-2981f100-c8ce-11e8-8d35-81782866b913.png)
![issues_per_user](https://user-images.githubusercontent.com/19995558/46548026-28e95a80-c8ce-11e8-87b8-76a0dc244b8e.png)
![comments_per_user](https://user-images.githubusercontent.com/19995558/46548025-28e95a80-c8ce-11e8-86b3-daa7e95c32fe.png)
![keywords_in_comments](https://user-images.githubusercontent.com/19995558/46548027-2981f100-c8ce-11e8-906b-a2172e79113e.png)
![issues_per_label](https://user-images.githubusercontent.com/19995558/46548024-28e95a80-c8ce-11e8-8f0c-e65552784c8c.png)

# Usage

There are two ways to use the tool, using the CLI, or importing the modules in your project. The later might provide you with more flexibility. **Remember: running the tool might take some time to retrieve the data. Especially if you have a lot of issues! _(wait... that sounded weird)_**

## Using the CLI

After you download the project just run the `gh-issue-stats-cli.py` with the parameters that you want. You can run it with `-h` to see all available.
Too bored? Let me do that for you:
```
usage: GitHub Issue Stats PY [-h] -t TOKEN -r REPOSITORY -d DATE [-e ENDPOINT]
                             [-gs] [-mi] [-di] [-ai] [-ac]
                             [-at AUTHOR_TEXT [AUTHOR_TEXT ...]]
                             [-li LABEL_ISSUES [LABEL_ISSUES ...]]
                             [-fr FILTER_RESULTS]
                             [-ft FILTER_TIME [FILTER_TIME ...]] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -e ENDPOINT, --endpoint ENDPOINT
                        the GraphQL endpoint to connect to
  -gs, --general_stats  gather some general issue stats
  -mi, --month_issues   find how many issues are per month
  -di, --day_issues     find how many issues are per day
  -ai, --author_issues  find how many issues are per author
  -ac, --author_comments
                        find how many comments are per author
  -at AUTHOR_TEXT [AUTHOR_TEXT ...], --author_text AUTHOR_TEXT [AUTHOR_TEXT ...]
                        find how many times the given text is met in comments
                        per author
  -li LABEL_ISSUES [LABEL_ISSUES ...], --label_issues LABEL_ISSUES [LABEL_ISSUES ...]
                        find how many issues are with a given label
  -fr FILTER_RESULTS, --filter_results FILTER_RESULTS
                        limit the number of results. Default is 10, that means
                        in queries that involve users only the top 10 of them
                        will be displayed
  -ft FILTER_TIME [FILTER_TIME ...], --filter_time FILTER_TIME [FILTER_TIME ...]
                        set the start and end time of a workday (UTC). E.g.
                        `-ft 07:00 15:00. This affects the issue assign
                        meantime
  -p, --plot            plot the diagrams in browser

required arguments:
  -t TOKEN, --token TOKEN
                        login token for Github
  -r REPOSITORY, --repository REPOSITORY
                        the GH repository we want to parse
  -d DATE, --date DATE  the date we want to start retrieving information.
                        Format: YYYY-MM-DD
```

Some notes:
- With `-e` you can choose the GraphQL endpoint. By default the GitHub one is used. If you want to run the tool against your GHE remember to change the endpoint to something like `https://github.[my_company].com/api/graphql`
- Results that involve users need a filter to be set. That's what `-fr` does. Of course you can define in the filter a really high value, but then your charts won't be clear because they will be overfilled with data!
- All the times are UTC.

## Using the module

You can import the tool as a module in your project and use it. An example is demonstrated bellow.

```python
from gh_issue_stats import GhIssueStats

# config zone
login_token = "12312not3123making3123sense"
graphql_endpoint = "https://github.company.com/api/graphql"
repo = "my/repo"
starting_date = "2017-09-01"

gh_issue_stats = GhIssueStats(login_token, graphql_endpoint, repo)
gh_issue_stats.get_issue_nodes(starting_date)

issue_count = gh_issue_stats.find_issue_count()
print(issue_count)

issues_per_approval = gh_issue_stats.find_issues_per_label(["label 1", "label 2", "label 3"])
print(issues_per_approval)
gh_issue_stats.make_chart(issues_per_approval, chart_type="Pie", title="My label", filename="myfile.html")
```

More documentation is coming soon (?)

# Bugs? Ideas?

Feel free to open a new issue / pull request in the GitHub tracker!


