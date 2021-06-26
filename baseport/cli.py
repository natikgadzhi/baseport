import click
import csv
import json

from typing import Union

from basecampy3 import Basecamp3
from basecampy3.exc import NoDefaultConfigurationFound
from html2text import html2text

# Type alias for CLi command result: may be an exit code or none
CommandResult = Union[int, None]


@click.group(help="Baseport exports Basecamp 3 to-do lists to CSVs.")
def cli(ctx):
    pass


@cli.group(help="Project operations: ls.")
def projects():
    pass


@cli.group(help="To-Do lists operations: ls show, export.")
def todos():
    pass


@projects.command(name="ls", help="List all available Basecamp projects and theid IDs.")
def projects_ls() -> CommandResult:
    """
    CLI command to list all projects in a Basecamp3 account.
    `baseport projects ls`
    """
    bc3 = _create_basecamp_client()
    if bc3 is None:
        return 1

    click.echo("Rendering all available projects:")
    for project in bc3.projects.list():
        click.echo(f"  - {project.name}: {project.id} {project.app_url}")


@todos.command(name="ls", help="List all available to-do lists in a project")
@click.option("-p", "--project", "project_id", required=True, help="Project ID", type=int)
def todos_ls(project_id: int) -> CommandResult:
    bc3 = _create_basecamp_client()
    if bc3 is None:
        return 1

    project = bc3.projects.get(project_id)
    todoset = project.todoset

    click.echo(f"To-do lists in {project.name}:")
    for todolist in todoset.list():
        click.echo(f"  - {todolist.name} {todolist.app_url}")


@todos.command(name="show", help="List all todos in one or all lists in a project")
@click.option("-p", "--project", "project_id", required=True, help="Project ID", type=int)
@click.option("-l", "--list", "list_id", help="To-do list ID", type=int)
def todos_show(project_id: int, list_id: int) -> CommandResult:
    bc3 = _create_basecamp_client()
    if bc3 is None:
        return 1

    project = bc3.projects.get(project_id)
    todoset = project.todoset

    if list_id is not None:
        lists = [todoset.get(list_id)]
    else:
        lists = list(todoset.list())

    click.echo(f"To-dos from {len(lists)} to-do lists:")

    for todolist in lists:
        click.echo(f"## {todolist.name}")

        for todo in todolist.list():
            click.echo(f"  - {todo.title}")

        for group in todolist.list_groups():
            group_list = group._endpoint._api.todolists.get(todolist=group)
            click.echo(f"  - GROUP: {group_list.name}")

            for todo in group_list.list():
                click.echo(f"    - {todo.title}")


@todos.command(name="export", help="Export all todos in one or all lists into a CSV file")
@click.option("-p", "--project", "project_id", required=True, help="Project ID", type=int)
@click.option("-l", "--list", "list_id", help="To-do list ID", type=int)
@click.option("-o", "--out", help="Path to the output CSV file", default="basecamp-export.csv")
@click.option(
    "-f",
    "--formatter",
    help="Use custom formatter to preprocess your exported to-dos. We have default (no formatting) and Zipline (you don't want this).",
    default="default",
)
def todos_export(project_id: int, list_id: int, out: str, formatter: str) -> CommandResult:
    bc3 = _create_basecamp_client()
    if bc3 is None:
        return 1

    project = bc3.projects.get(project_id)
    todoset = project.todoset

    # Load a single to-do list if the ID is provided, or load all to-do lists in the project.
    lists = [todoset.get(list_id)] if list_id is not None else list(todoset.list())
    todos = []

    for todolist in lists:
        todos.extend(todolist.list())

        for group in todolist.list_groups():
            todos.extend(group._endpoint._api.todolists.get(todolist=group).list())

    # Preprocess todos for export
    todos = _format_todos(todos, formatter)
    _export_todos_to_csv(out, todos)


def _create_basecamp_client() -> Union[Basecamp3, None]:
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


def _export_todos_to_csv(out: str, todos: list) -> None:
    """
    Writes the to-dos into a csv file.
    """
    with open(out, "w", newline="") as csvfile:
        csvout = csv.writer(csvfile)

        # Write header row with keys of the dict
        csvout.writerow(todos[0]._values.keys())
        for todo in todos:
            csvout.writerow(todo._values.values())


def _format_todos(todos: list, formatter: str) -> list:
    """
    Formats the list of TODOs with a formatter of choice and returns the list.
    Accepts the list of todos in Basecampy3 format only.
    Currently only works with default or Zipline formatters.
    """
    if formatter == "zipline":
        return _format_todos_zipline(todos)
    else:
        return todos


def _format_todos_zipline(todos: list) -> list:
    for todo in todos:
        todo._values["creator"] = todo._values["creator"]["email_address"].replace("retailzipline.com", "zipline.inc")
        assignees = todo._values["assignees"]

        # Set the first assignee as the assignee on Jira export.
        # Clean up empty arrays, or they'll error out later.
        if len(assignees) != 0:
            todo._values["assignees"] = assignees[0]["email_address"].replace("retailzipline.com", "zipline.inc")
        else:
            todo._values["assignees"] = ""

        todo._values[
            "description"
        ] = f"""\
This issue has been imported from Basecamp automatically. [Here's the original Basecamp To-do!]({todo._values["app_url"]})

{html2text(todo._values["description"])}
        """
    return todos


if __name__ == "__main__":
    cli()
