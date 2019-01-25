from .gh_graphql_client import GhGraphQlClient
import plotly
import plotly.graph_objs as go
from datetime import datetime
from collections import Counter


class GhIssueStats:
    def __init__(self, token, api_endpoint, repo):
        self.token = token
        self.api_endpoint = api_endpoint
        self.repo = repo
        self.nodes = None

    def get_issue_nodes(self, date):
        search_filter = f"first:100, type:ISSUE, query:\"repo:{self.repo} is:issue created:>{date} sort:created-asc\""
        search_template = """
{{
    search ({0}) {{
        pageInfo {{
            startCursor
            endCursor
            hasNextPage
        }}
        edges {{
            cursor
            node {{
                ... on Issue {{
                    createdAt
                    closedAt
                    timeline(first:100) {{
                        nodes {{
                            ... on AssignedEvent {{
                                createdAt
                            }}
                        }}
                    }}
                    author {{
                        login
                    }}
                    assignees(first:100) {{
                        nodes {{
                            login
                        }}
                    }}
                    labels(first:100) {{
                        nodes{{
                            name
                        }}
                    }}
                    comments(first:100) {{
                        nodes {{
                            author {{
                                login
                            }}
                            bodyText
                        }}
                    }}
                }}
            }}
        }}
    }}
}}"""
        query = search_template.format(search_filter)
        nodes = []
        has_next_page = True
        after_cursor = None
        gh_graphql_client = GhGraphQlClient(self.token, self.api_endpoint)
        while has_next_page:
            data = gh_graphql_client.run_query(query)
            for edge in data['edges']:
                nodes.append(edge['node'])
            # pagination
            has_next_page = data['pageInfo']['hasNextPage']
            if has_next_page:
                after_cursor = data['pageInfo']['endCursor']
                search_filter = f"first:100, after:\"{after_cursor}\", type:ISSUE, query:\"repo:{self.repo} is:issue created:>{date} sort:created-asc\""
                query = search_template.format(search_filter)
            # hack to bypass GHs 1000 issue limit
            if not has_next_page and (len(nodes) / 1000).is_integer():
                # get creation timestamp of last issue it was returned
                issue_creation_timestamp = datetime.strptime(nodes[-1]['createdAt'], '%Y-%m-%dT%H:%M:%S%z')
                date = issue_creation_timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
                search_filter = f"first:100, type:ISSUE, query:\"repo:{self.repo} is:issue created:>{date} sort:created-asc\""
                query = search_template.format(search_filter)
                has_next_page = True
        self.nodes = nodes
        return(nodes)

    def find_issue_close_meantime(self):
        meantime_list = []
        for node in self.nodes:
            if node['closedAt']:
                meantime = datetime.strptime(node['closedAt'], '%Y-%m-%dT%H:%M:%S%z') - datetime.strptime(node['createdAt'], '%Y-%m-%dT%H:%M:%S%z')
                meantime_list.append(meantime.seconds // 3600)
        close_meantime = {'Close Meantime (hrs)': round(sum(meantime_list) / len(meantime_list), 1)}
        return(close_meantime)

    def find_issue_assign_meantime(self, filter_hours=None, filter_weekends=False):
        meantime_list = []
        for node in self.nodes:
            issue_creation_timestamp = datetime.strptime(node['createdAt'], '%Y-%m-%dT%H:%M:%S%z')
            if filter_hours:
                start_hour = datetime.strptime(filter_hours[0], '%H:%M')
                stop_hour = datetime.strptime(filter_hours[1], '%H:%M')
                if not datetime.time(start_hour) <= datetime.time(issue_creation_timestamp) <= datetime.time(stop_hour):
                    continue
            if filter_weekends:
                if datetime.weekday(issue_creation_timestamp) >= 5:
                    continue
            issue_assign_time_list = []
            issue_assign_time_list = [datetime.strptime(assigned_event['createdAt'], '%Y-%m-%dT%H:%M:%S%z') for assigned_event in node['timeline']['nodes'] if assigned_event]
            if issue_assign_time_list:
                min_issue_assign_time = min(issue_assign_time_list)
                meantime = min_issue_assign_time - issue_creation_timestamp
                meantime_list.append(meantime.seconds // 3600)
        assign_meantime = {'Assign Meantime (hrs)': round(sum(meantime_list) / len(meantime_list), 1)}
        return(assign_meantime)

    def find_issues_per_label(self, filter_labels=None):
        label_list = []
        for node in self.nodes:
            for label in node['labels']['nodes']:
                label_list.append(label['name'])
        label_issue_count = dict(Counter(label_list))
        if filter_labels:
            for filter in filter_labels:
                issues_per_label = {k: v for k, v in label_issue_count.items() if k in filter_labels}
        return(issues_per_label)

    def find_issues_per_assignee(self):
        assignee_list = []
        for node in self.nodes:
            for assignee in node['assignees']['nodes']:
                assignee_list.append(assignee['login'])
        issues_per_assignee = dict(Counter(assignee_list))
        return(issues_per_assignee)

    def find_issue_count(self):
        issue_count = {'Total Issue Count': len(self.nodes)}
        return(issue_count)

    def find_issues_per_month(self):
        creation_date_list = []
        for node in self.nodes:
            creation_date_list.append(datetime.strptime(node['createdAt'], '%Y-%m-%dT%H:%M:%S%z'))
        creation_date_list.sort()
        creation_month_list = [datetime.strftime(date, '%B %Y') for date in creation_date_list]
        issues_per_month = dict(Counter(creation_month_list))
        return(issues_per_month)

    def find_issues_per_day(self):
        creation_date_list = []
        for node in self.nodes:
            creation_date_list.append(datetime.strptime(node['createdAt'], '%Y-%m-%dT%H:%M:%S%z'))
        creation_date_list.sort(key=lambda x: datetime.weekday(x))
        creation_day_list = [datetime.strftime(date, '%A') for date in creation_date_list]
        issues_per_day = dict(Counter(creation_day_list))
        return(issues_per_day)

    def find_issues_per_author(self, max_entries=10):
        author_list = []
        for node in self.nodes:
            author = node['author']['login']
            author_list.append(author)
        issues_per_author = dict(Counter(author_list))
        issues_per_author_sorted = dict(sorted(issues_per_author.items(), key=lambda x: x[1], reverse=True)[:max_entries])
        return(issues_per_author_sorted)

    def find_comments_per_author(self, max_entries=10):
        commenter_list = []
        for node in self.nodes:
            for comment in node['comments']['nodes']:
                # case the author has been deleted
                if comment['author']:
                    commenter_list.append(comment['author']['login'])
        comments_per_author = dict(Counter(commenter_list))
        comments_per_author_sorted = dict(sorted(comments_per_author.items(), key=lambda x: x[1], reverse=True)[:max_entries])
        return(comments_per_author_sorted)

    def find_comment_text_per_author(self, text, max_entries=10):
        commenter_list = []
        for node in self.nodes:
            for comment in node['comments']['nodes']:
                if any(text_element.lower() in comment['bodyText'].lower() for text_element in text):
                    commenter_list.append(comment['author']['login'])
        comment_text_per_author = dict(Counter(commenter_list))
        comment_text_per_author_sorted = dict(sorted(comment_text_per_author.items(), key=lambda x: x[1], reverse=True)[:max_entries])
        return(comment_text_per_author_sorted)

    def make_chart(self, data, chart_type=None, title=None, filename='temp.html'):
        # case sensitive checks for chart_type. fix it.
        labels = list(data.keys())
        values = list(data.values())
        chart_types = ['Pie', 'Table', 'Bar']
        if chart_type == 'Pie':
            trace = go.Pie(labels=labels, values=values)
        elif chart_type == 'Table':
            trace = go.Table(
                header=dict(fill=dict(color='#C2D4FF')),
                cells=dict(values=[labels, values], fill=dict(color='#F5F8FF'), align=['left']*5))
        elif chart_type == 'Bar':
            trace = go.Bar(x=labels, y=values)
        else:
            raise ValueError(f"Invalid chart type. Expected one of: {chart_types}")
        layout = go.Layout(title=title)
        fig = go.Figure(data=[trace], layout=layout)
        plotly.offline.plot(fig, filename=filename, auto_open=True)
