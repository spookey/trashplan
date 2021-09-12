import arrow
import click
import ics
import requests

CLI_PROG = 'trashplan'
CLI_VERS = '0.0.2'
URL_CAL = (
    'https://stadtreinigung-leipzig.de/wir-kommen-zu-ihnen/'
    'abfallkalender/ical.ics'
)


def download(nos):
    with requests.get(URL_CAL, params={
            'position_nos': f'{nos}',
    }) as req:
        content_type = req.headers.get('content-type', '')
        if req.ok and 'text/calendar' in content_type.lower():
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
        ind = ' ' * abs(indent)
        return f'{ind}{val}'

    res = []
    for head, elems in sorted(table.items()):
        res.append(fmt(head, head_indent))
        res.extend(fmt(elem, main_indent) for elem in elems)
        res.append('')
    return '\n'.join(res).rstrip()


@click.command()
@click.version_option(prog_name=CLI_PROG, version=CLI_VERS)
@click.argument(
    'nos', envvar='NOS',
    type=click.IntRange(min=10000, max=999999),
    required=True
)
@click.option(
    '-df', '--date-format', envvar='DATE_FORMAT',
    type=click.STRING,
    default='YYYY-MM-DD',
    help='Custom date format string.',
)
@click.option(
    '-hi', '--head-indent', envvar='HEAD_INDENT',
    type=click.IntRange(min=0),
    default=0,
    help='Indentation for headings.',
)
@click.option(
    '-mi', '--main-indent', envvar='MAIN_INDENT',
    type=click.IntRange(min=0),
    default=4,
    help='Indentation for content.',
)
@click.option(
    '-of', '--only-future', envvar='ONLY_FUTURE',
    is_flag=True,
    help='Include only future dates.',
)
def main(nos, only_future, **fmtargs):
    ical = download(nos)
    if not ical:
        click.secho(
            f'Could not download calendar file for NOS "{nos}"!',
            fg='red'
        )
        return

    generated = generate(ical, only_future)
    processed = process(generated, **fmtargs)
    click.echo(processed)


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
