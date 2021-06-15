import click
import basecampy3

@click.command(help="Baseport exports Basecamp 3 to-do lists to CSVs.")
@click.option("-p", "--project", required=True, help="Basecamp Project URL to export.")
@click.option("-o", "--out", help="Output CSV file name. Will be generated from the project name if left blank.")
def main():
    print("hello world!")

    