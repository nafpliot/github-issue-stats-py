from gh_issue_stats import GhIssueStats
import argparse
from env_default import env_default

if __name__ == "__main__":
    parser = argparse.ArgumentParser("GitHub Issue Stats PY")
    required_grp = parser.add_argument_group('required arguments')
    required_grp.add_argument("-t", "--token", help="login token for Github", action=env_default('GH_TOKEN'), required=True)
    required_grp.add_argument("-r", "--repository", help="the GH repository we want to parse", required=True)
    required_grp.add_argument("-d", "--date", help="the date we want to start retrieving information. Format: YYYY-MM-DD", required=True)
    parser.add_argument("-e", "--endpoint", help="the GraphQL endpoint to connect to", default="https://api.github.com/graphql")
    parser.add_argument("-gs", "--general_stats", help="gather some general issue stats", action="store_true")
    parser.add_argument("-mi", "--month_issues", help="find how many issues are per month", action="store_true")
    parser.add_argument("-di", "--day_issues", help="find how many issues are per day", action="store_true")
    parser.add_argument("-ai", "--author_issues", help="find how many issues are per author", action="store_true")
    parser.add_argument("-ac", "--author_comments", help="find how many comments are per author", action="store_true")
    parser.add_argument("-at", "--author_text", help="find how many times the given text is met in comments per author", nargs="+")
    parser.add_argument("-li", "--label_issues", help="find how many issues are with a given label", nargs="+")
    parser.add_argument("-fr", "--filter_results", help="limit the number of results. Default is 10, that means in queries that involve users only the top 10 of them will be displayed",
                        type=int, default=10)
    parser.add_argument("-ft", "--filter_time", help="set the start and end time of a workday (UTC). E.g. `-ft 07:00 15:00. This affects the issue assign meantime", nargs="+")
    parser.add_argument("-p", "--plot", help="plot the diagrams in browser", action="store_true")

    args = parser.parse_args()
    gh_issue_stats = GhIssueStats(args.token, args.endpoint, args.repository)
    gh_issue_stats.get_issue_nodes(args.date)

    if args.general_stats:
        issue_count = gh_issue_stats.find_issue_count()
        issue_close_meantime = gh_issue_stats.find_issue_close_meantime()
        assign_issue_meantime = gh_issue_stats.find_issue_assign_meantime(args.filter_time)
        # merge dicts to plot them in one table
        issue_stats = {**issue_count, **issue_close_meantime, **assign_issue_meantime}
        if args.plot:
            gh_issue_stats.make_chart(issue_stats, chart_type="Table", title="Issue Stats", filename="charts/general_stats.html")

    if args.month_issues:
        issues_per_month = gh_issue_stats.find_issues_per_month()
        if args.plot:
            gh_issue_stats.make_chart(issues_per_month, chart_type="Bar", title="Issues / Month", filename="charts/month_issues.html")

    if args.day_issues:
        issues_per_day = gh_issue_stats.find_issues_per_day()
        if args.plot:
            gh_issue_stats.make_chart(issues_per_day, chart_type="Bar", title="Issues / Day", filename="charts/day_issues.html")

    if args.author_issues:
        issues_per_author = gh_issue_stats.find_issues_per_author(args.filter_results)
        if args.plot:
            gh_issue_stats.make_chart(issues_per_author, chart_type="Pie", title="Issues per user", filename="charts/author_issues.html")

    if args.author_comments:
        comments_per_author = gh_issue_stats.find_comments_per_author(args.filter_results)
        if args.plot:
            gh_issue_stats.make_chart(comments_per_author, chart_type="Pie", title="Comments per user", filename="charts/author_comments.html")

    if args.author_text:
        comment_text_per_author = gh_issue_stats.find_comment_text_per_author(args.author_text, args.filter_results)
        if args.plot:
            gh_issue_stats.make_chart(comment_text_per_author, chart_type="Pie", title=f"Keyword(s) in comments per author | {args.author_text}", filename="charts/author_text.html")

    if args.label_issues:
        issues_per_label = gh_issue_stats.find_issues_per_label(args.label_issues)
        if args.plot:
            gh_issue_stats.make_chart(issues_per_label, chart_type="Pie", title=f"Issues per label(s) | {args.label_issues}", filename="charts/label_issues.html")
