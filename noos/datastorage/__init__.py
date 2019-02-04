from datetime import datetime

import click
from flask.cli import with_appcontext

from elasticsearch_dsl import Index, Document, Date, Integer, Keyword, Text, Ip, analyzer
import elasticsearch_dsl as es
from elasticsearch_dsl.connections import connections
from .user_db import Users, init_user_db

connections.create_connection(hosts=['localhost'])
INDEX_NAME="noos"

from uuid import uuid4
def uuid():
    return uuid4().hex


class Proposition(Document):

    ip = Ip()
    cause = Text(fields={'raw': Keyword()})
    content = Text(analyzer=analyzer('french'))
    keywords = Keyword()
    uid = Keyword()
    date = Date()

    def __str__(self):
        return """
        ---
        {}
        {}
        {}
        --- 
        """.format(self.uid, self.cause, self.content)

    @staticmethod
    def simple_search(query, start, limit):
        s = Proposition.search()[start:start+limit].query("match", content=query)
        count = s.count()
        results = s.execute()
        return {"count":count, "hits": results.hits}


    @staticmethod
    def dump_propositions():
        s = Proposition.search()[0:10000]
        for d in s.execute():
            yield d

    class Index:
        name = INDEX_NAME


def init_app(app):

    app.teardown_appcontext(user_db.close_db)

    app.cli.add_command(init_es)
    app.cli.add_command(populate_es)
    app.cli.add_command(clean_es)
    app.cli.add_command(test_query)
    app.cli.add_command(get_all_propositions)

    app.cli.add_command(user_db.init_db_command)
    app.cli.add_command(user_db.init_users)
    app.cli.add_command(user_db.db_stats)



@click.command('init-es')
@with_appcontext
def init_es():
    Proposition.init()
    click.echo("Elasticsearch schema initialized")


@click.command('clean-es')
@with_appcontext
def clean_es():
    click.echo("deleting index")
    idx = Index(INDEX_NAME)
    idx.delete(ignore=404)

@click.command('populate-es')
@click.option('--csv-file')
@with_appcontext
def populate_es(csv_file):
    import csv
    click.echo("adding a test proposition")
    user = Users.get_one_by('username', 'noos')
    p = Proposition(ip="127.0.0.1",
                    cause="test",
                    content="ceci est juste une proposition",
                    uid=user.uuid,
                    data=datetime.now())
    p.save()

    with open(csv_file) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] is '' or row[0].startswith("@"):
                continue
            else:
                click.echo(row[1])
                p = Proposition(ip="127.0.0.1",
                                cause="test",
                                content=row[1],
                                keywords=[k.strip() for k in row[2].split(",")],
                                uid=user.uuid,
                                date=datetime.now())
                p.save()


@click.command('query-es')
@click.option('--query')
@with_appcontext
def test_query(query):
    s = Proposition\
        .search()\
        .query("match", content=query)
    for p in s.scan():
        click.echo(p.content)

@click.command('get-all-propositions')
@click.option('--output')
@with_appcontext
def get_all_propositions(output):
    import json
    data = [p.to_dict() for p in Proposition.dump_propositions()]
    with open(output,"w") as f:
        json.dump(data,f, default=lambda x: x.isoformat()) #  default=dangerous hack to serialize datetime objects




