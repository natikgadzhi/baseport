# Baseport

Baseport is a small CLI tool to export your Basecamp to-dos into a CSV file. We
considered migrating to Jira, and I needed a way to pull all our Basecamp to-dos
into it, so I've written a quick script and thought I'd share it.

## Install

`pip install baseport`

## Usage

```
$ baseport --help
Usage: baseport [OPTIONS] COMMAND [ARGS]...

  Baseport exports Basecamp 3 to-do lists to CSVs.

Options:
  --help  Show this message and exit.

Commands:
  projects  Project operations
  todos     To-Do lists operations

$ baseport todos --help
Usage: baseport todos [OPTIONS] COMMAND [ARGS]...

  To-Do lists operations

Options:
  --help  Show this message and exit.

Commands:
  export  Export all todos in one or all lists into a CSV file
  ls      List all available to-do lists in a project
  show    List all todos in one or all lists in a project

```

To export all of the to-dos in a single project, you'll use something like this:

```
baseport todos export -p PROJECT_ID -o todos.csv
```

### Authentication

Baseport uses [`basecampy3`](https://github.com/phistrom/basecampy3) to talk to
Basecamp API. You'll need a `.conf` file with your OAuth app client_id and
secret, and OAuth token. Luckily, you can just run `bc3 configure` and it'll
guide you through the setup proces.

### Formatting and cleaning your CSV

We needed to do a bit of a company-specific cleanup (given that I needed to
import to-dos to Jira, and clean up our email addresses), so Baseport has
formatter support. You can implement your own formatter and add it to
`_format_todos()` function, and then just pass it in the terminal with
`--formatter` option.

## Contributing

Feel free to open a PR with additional formatters or documentation on how to use
`baseport` for other platform-specific exports.

If you found an issue, please do file it on this repo. I'll do my best to help
you out.

Baseport is not going to be actively maintained or developed, it's a one-off
quick tool I needed for myself, and it did it's job.
