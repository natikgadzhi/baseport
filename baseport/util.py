import csv
from typing import Union

import click

from basecampy3 import Basecamp3
from basecampy3.exc import NoDefaultConfigurationFound

from html2text import html2text
from bs4 import BeautifulSoup

def create_basecamp_client() -> Union[Basecamp3, None]:
    """
    Creates a Basecampy3 client object with the default configuration
    and returns it. Wrapped around with a better error handling.
    """
    try:
        return Basecamp3()
    except NoDefaultConfigurationFound:
        click.echo(
            f"""\
        Baseport needs Basecamp3 API authentication tokens to work, and the config file with them wasn't found.

        Running `bc3 configure` will start a Basecamp3 API configuration wizard that will guide you through the setup process.
        Read more here: https://github.com/phistrom/basecampy3#install
        """
        )
        return None


def export_todos_to_csv(out: str, todos: list) -> None:
    """
    Writes the to-dos into a csv file.
    """
    with open(out, "w", newline="") as csvfile:
        csvout = csv.writer(csvfile)

        # Write header row with keys of the dict
        csvout.writerow(todos[0]._values.keys())
        for todo in todos:
            csvout.writerow(todo._values.values())


def format_todos(todos: list, formatter: str) -> list:
    """
    Formats the list of TODOs with a formatter of choice and returns the list.
    Accepts the list of todos in Basecampy3 format only.
    Currently only works with default or Zipline formatters.
    """
    if formatter == "zipline":
        return zipline_format_todos(todos)
    else:
        return todos

def zipline_replace_mentions(content: str) -> str:
    """Replaces Basecamp-style mentions in an HTML string and returns an HTML string."""
    soup = BeautifulSoup(content, "html.parser")

    mentions = soup.select("bc-attachment[content-type='application/vnd.basecamp.mention']")

    for mention in mentions:
        new_mention = soup.new_tag("strong")
        new_mention.string = "@" + mention.find("img")["alt"]
        mention.replace_with(new_mention)

    return str(soup)

def zipline_user_email(user: dict) -> str:
    return f"**@{user['email_address'].replace('retailzipline.com', 'zipline.inc')}**"

def zipline_format_todos(todos: list) -> list:
    for todo in todos:
        todo._values["creator"] = zipline_user_email(todo._values["creator"])
        assignees = todo._values["assignees"]

        # Set the first assignee as the assignee on Jira export.
        # Clean up empty arrays, or they'll error out later.
        if len(assignees) != 0:
            todo._values["assignees"] = zipline_user_email(assignees[0])
        else:
            todo._values["assignees"] = ""

        comments = [f"{zipline_user_email(c._values['creator'])}: {html2text(zipline_replace_mentions(c._values['content']))}" for c in list(todo.comments())]
        comments = "\n".join(comments)

        todo._values[
            "description"
        ] = f"""\
This issue has been imported from Basecamp automatically. [Here's the original Basecamp To-do!]({todo._values["app_url"]})

{html2text(zipline_replace_mentions(todo._values["description"]))}

---

### Comments

{comments}
        """
    return todos
