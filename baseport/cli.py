from typing import Union

from .comments import Comments
from .util import *

from pprint import pprint

import click

# Type alias for CLi command result: may be an exit code or none
CommandResult = Union[int, None]

@click.group(help="Baseport exports Basecamp 3 to-do lists to CSVs.")
def cli():
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
    bc3 = create_basecamp_client()
    if bc3 is None:
        return 1

    click.echo("Rendering all available projects:")
    for project in bc3.projects.list():
        click.echo(f"  - {project.name}: {project.id} {project.app_url}")


@todos.command(name="ls", help="List all available to-do lists in a project")
@click.option("-p", "--project", "project_id", required=True, help="Project ID", type=int)
def todos_ls(project_id: int) -> CommandResult:
    """
    CLI command to list all to-to lists in a project.
    `baseport todos ls --project PROJECT_ID`
    """
    bc3 = create_basecamp_client()
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
    """
    CLI command to show all the to-dos in a particular project, in one or all to-do lists.
    `baseport todos show --project PROJECT_ID --list LIST_ID`
    """
    bc3 = create_basecamp_client()
    if bc3 is None:
        return 1

    project = bc3.projects.get(project_id)
    todoset = project.todoset

    lists = [todoset.get(list_id)] if list_id is not None else list(todoset.list())
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
    bc3 = create_basecamp_client()
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

    # print(list(todos[0].comments())[1]._values['content'])

    # Preprocess todos for export
    todos = format_todos(todos, formatter)
    export_todos_to_csv(out, todos)

if __name__ == "__main__":
    cli()
