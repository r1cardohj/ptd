import sqlite3
from pathlib import Path
import click
from itertools import zip_longest
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

DATABASE = Path.home() / 'pdt.db'
SPAN_WIDTH = 36


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def get_all_todo():
    with get_db() as db:
        rows = db.execute('select id, title, status from todo').fetchall()

    return rows


init_sql = """CREATE TABLE IF NOT EXISTS todo(  
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    title TEXT NOT NULL UNIQUE, 
    deadline DATE,  
    status INTEGER NOT NULL CHECK (status IN (0, 1, 2, 3)) DEFAULT 0,  
    create_dt TEXT NOT NULL DEFAULT (datetime('now')),  
    modify_dt TEXT NOT NULL DEFAULT (datetime('now'))  
);"""


@click.group()
def cli():
    pass


@cli.command()
def init():
    with get_db() as db:
        db.execute(init_sql)


@cli.command()
def add():
    title = click.prompt('Please enter a title', type=str)
    deadline = click.prompt('Please enter a deadline', type=click.DateTime())
    with get_db() as db:
        db.execute("INSERT INTO todo (title, deadline) VALUES (?, ?)", (title, deadline))


def render_items():
    rows = get_all_todo()
    todo_items = []
    in_progress_items = []
    done_items = []
    for row in rows:
        if row['status'] == 0:
            todo_items.append(row)
        if row['status'] == 1:
            in_progress_items.append(row)
        if row['status'] == 2:
            done_items.append(row)
    for todo, in_progress, done in zip_longest(todo_items, in_progress_items, done_items):
        render_one_row(todo, in_progress, done)


def render_one_row(todo, in_progress, done):
    if todo:
        todo_text = f'({todo["id"]}){todo["title"]}'
        todo_title = f"{todo_text:^36}"
        click.echo(click.style(todo_title, bg='red'), nl=False)
    else:
        click.echo(f'{' ':^36}', nl=False)
    if in_progress:
        in_progress_text = f'({in_progress["id"]}){in_progress["title"]}'
        in_progress_title = f"{in_progress_text:^36}"
        click.echo(click.style(in_progress_title, bg='yellow'), nl=False)
    else:
        click.echo(f'{' ':^36}', nl=False)

    if done:
        done_text = f'({done["id"]}){done["title"]}'
        done_title = f"{done_text:^36}"
        click.echo(click.style(done_title, bg='green'))
    else:
        click.echo(f'{' ':^36}')


@cli.command()
def show():
    click.echo(click.style('-' * SPAN_WIDTH, fg='red'), nl=False)
    click.echo(click.style('-' * SPAN_WIDTH, fg='yellow'), nl=False)
    click.echo(click.style('-' * SPAN_WIDTH, fg='green'))
    click.echo(click.style(f'{'todo':^36}', fg='red', bold=True), nl=False)
    click.echo(click.style(f'{'in progress':^36}', fg='yellow', bold=True), nl=False)
    click.echo(click.style(f'{'done':^36}', fg='green', bold=True))
    render_items()
    click.echo(click.style('-' * SPAN_WIDTH, fg='red'), nl=False)
    click.echo(click.style('-' * SPAN_WIDTH, fg='yellow'), nl=False)
    click.echo(click.style('-' * SPAN_WIDTH, fg='green'))


@cli.command()
@click.argument('id', type=int)
def start(id):
    with get_db() as db:
        item = db.execute('SELECT * from todo WHERE id = ?', (id,)).fetchone()
        if item and item['status'] == 0:
            db.execute('UPDATE todo SET status = 1 WHERE id = ?', (id,))


@cli.command()
@click.argument('id', type=int)
def done(id):
    with get_db() as db:
        item = db.execute('SELECT * from todo WHERE id = ?', (id,)).fetchone()
        if item and item['status'] == 1:
            db.execute('UPDATE todo SET status = 2 WHERE id = ?', (id,))


@cli.command()
@click.argument('id', type=int)
def drop(id):
    with get_db() as db:
        db.execute('DELETE FROM todo WHERE id = ?', (id,))


if __name__ == '__main__':
    cli()
