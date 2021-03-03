import click
from flask import (
    g,
)
from flask.cli import with_appcontext
from neo4j import GraphDatabase, basic_auth

from . import config

DATABASE_USERNAME = config.NEO4J_USERNAME
DATABASE_PASSWORD = config.NEO4J_PASSWORD
DATABASE_URL = config.NEO4J_BOLT_URL


def get_db():
    if not hasattr(g, "neo4j_db"):
        driver = GraphDatabase.driver(DATABASE_URL, auth=basic_auth(DATABASE_USERNAME, DATABASE_PASSWORD))
        g.neo4j_db = driver.session()
    return g.neo4j_db


def close_db(error):
    if hasattr(g, "neo4j_db"):
        g.neo4j_db.close()


def init_db():
    neo4j_db = get_db()
    neo4j_db.run("MATCH (n) RETURN COUNT(n);")
    neo4j_db.run("MATCH (n) DETACH DELETE (n);")
    neo4j_db.run("MATCH (n) RETURN COUNT(n);")


def add_friend(tx, name, friend_name):
    tx.run(
        "MERGE (a:Person {name: $name}) "
        "MERGE (a)-[:KNOWS]->(friend:Person {name: $friend_name})",
        name=name, friend_name=friend_name
    )


def print_friends(tx, name):
    query = tx.run(
        "MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name RETURN friend.name ORDER BY friend.name",
        name=name
    )
    for record in query:
        print(record["friend.name"])


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Neo4j database initialized ...")


@click.command("seed-db")
@with_appcontext
def seed_database():
    """Seed database with sample data."""
    neo4j_db = get_db()
    neo4j_db.write_transaction(add_friend, "Arthur", "Guinevere")
    neo4j_db.write_transaction(add_friend, "Arthur", "Lancelot")
    neo4j_db.write_transaction(add_friend, "Arthur", "Merlin")
    neo4j_db.read_transaction(print_friends, "Arthur")
    click.echo("Neo4j database seeded ...")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_database)
