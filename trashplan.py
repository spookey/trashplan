import arrow
import click
import ics
import requests

CLI_PROG = 'trashplan'
CLI_VERS = '0.0.1'
URL_CAL = (
    'https://www.stadtreinigung-leipzig.de/leistungen/'
    'abfallentsorgung/abfallkalender-entsorgungstermine.html'
)


def download(lid):
    with requests.get(URL_CAL, params={
            'lid': lid, 'loc': '', 'ical': True,
    }) as req:
        if req.ok:
            return req.text
    return None


def generate(ical, only_future=False):
    table = {}
    timeline = ics.Calendar(ical).timeline
    if only_future:
        timeline = timeline.start_after(arrow.now())

    for event in sorted(timeline):
        name = event.name
        table[name] = table.get(name, [])
        table[name].append(arrow.get(event.begin))
    return table


def process(table, date_format, head_indent, main_indent):
    def fmt(val, indent=0):
        if isinstance(val, arrow.arrow.Arrow):
            val = val.format(date_format)
        return '{}{}'.format(' ' * abs(indent), val)

    res = []
    for head, elems in sorted(table.items()):
        res.append(fmt(head, head_indent))
        res.extend(fmt(elem, main_indent) for elem in elems)
        res.append('')
    return '\n'.join(res).rstrip()


@click.command()
@click.version_option(prog_name=CLI_PROG, version=CLI_VERS)
@click.argument(
    'lid', type=int, required=True
)
@click.option(
    '-df', '--date-format', type=str, help='Custom date format string.',
    default='YYYY-MM-DD',
)
@click.option(
    '-hi', '--head-indent', type=int, help='Indentation for headings.',
    default=0,
)
@click.option(
    '-mi', '--main-indent', type=int, help='Indentation for content.',
    default=4,
)
@click.option(
    '-of', '--only-future', is_flag=True, help='Include only future dates.',
)
def main(lid, only_future, **fmtargs):
    ical = download('x{:d}'.format(lid))
    if not ical:
        click.secho('Could not download calendar file!', fg='red')
        return 1

    result = process(generate(ical, only_future), **fmtargs)
    click.echo(result)
    return 0


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    exit(main())
