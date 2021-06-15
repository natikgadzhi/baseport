import click
from basecampy3 import Basecamp3

@click.group(help="Baseport exports Basecamp 3 to-do lists to CSVs.")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.group(help="Project operations")
@click.pass_context
def projects(ctx):
    pass

@projects.command(name="ls", help="List all available Basecamp projects and theid IDs")
@click.pass_context
def projects_ls(ctx):
    bc3 = Basecamp3()

    for project in bc3.projects.list():
        print(f"{project.name}: {project.id}")


@cli.group(help="To-Do lists operations")
@click.pass_context
def todos(ctx):
    pass

@todos.command(name="ls", help="List all available to-do lists in a project")
@click.option("-p", "--project", "project_id", required=True, help="Project ID", type=int)
@click.pass_context
def todos_ls(ctx, project_id):
    bc3 = Basecamp3()
    project = bc3.projects.get(project_id)
    todoset = project.todoset

    for todolist in todoset.list():
        print(todolist)

@todos.command(name="show", help="List all todos in one or all lists in a project")
@click.option("-p", "--project", "project_id", required=True, help="Project ID", type=int)
@click.option("-l", "--list", "list_id", help="To-do list ID", type=int)
@click.pass_context
def todos_show(ctx, project_id, list_id):
    bc3 = Basecamp3()
    project = bc3.projects.get(project_id)
    todoset = project.todoset

    if list_id is not None:
        lists = [todoset.get(list_id)]
    else:
        lists = list(todoset.list())

    print(f"Showing items from {len(lists)} to-do lists:")

    for todolist in lists:
        print(f"## {todolist.name}")

        for todo in todolist.list():
            print(f"  - {todo.title}")

        for group in todolist.list_groups():
            group_list = group._endpoint._api.todolists.get(todolist=group)
            print(f"  - GROUP: {group_list.name}")

            for todo in group_list.list():
                print(f"    - {todo.title}")


@todos.command(name="export", help="Export all todos in one or all lists into a CSV file")
@click.option("-p", "--project", "project_id", required=True, help="Project ID", type=int)
@click.option("-l", "--list", "list_id", help="To-do list ID", type=int)
@click.option("-o", "--out", help="Path to the output CSV file", default="basecamp-export.csv")
@click.pass_context
def todos_export(ctx, project_id, list_id):



    pass



if __name__ == '__main__':
    cli(obj={})