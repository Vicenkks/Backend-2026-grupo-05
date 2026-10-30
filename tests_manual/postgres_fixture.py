"""Disposable PostgreSQL databases owned exclusively by this test invocation."""
from contextlib import contextmanager
import os
from uuid import uuid4
import psycopg2
from psycopg2 import sql
from sqlalchemy import URL
from dotenv import load_dotenv


@contextmanager
def databases():
    load_dotenv()
    options = dict(host=os.getenv('DB_HOST', 'localhost'),
                   port=int(os.getenv('DB_PORT', '5432')),
                   user=os.getenv('DB_USER', 'coworking'),
                   password=os.getenv('DB_PASSWORD', 'desarrollo_local'))
    connection = psycopg2.connect(dbname='postgres', **options)
    connection.autocommit = True
    names = []
    try:
        for _ in range(2):
            name = 'coworking_test_' + uuid4().hex
            with connection.cursor() as cursor:
                cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
            names.append(name)
        urls = [URL.create('postgresql+psycopg2', username=options['user'],
                           password=options['password'], host=options['host'],
                           port=options['port'], database=name).render_as_string(hide_password=False)
                for name in names]
        yield urls
    finally:
        for name in names:
            with connection.cursor() as cursor:
                cursor.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(name)))
        connection.close()
