#!/usr/bin/python2

import sqlalchemy as sql

DBPATH="./tag.db"

def main():
    db = sql.create_engine('sqlite://'+DBPATH)
    db.echo = False
    metadata = sql.BoundMetaData(db)
    initDB(metadata)
    return

def initDB(metadata):
    tables={}
    tables['tags'] = sql.Table(
            'tags'
            , metadata
            , sql.Column('id', sql.Integer, primary_key=True)
            , sql.Column('tag', sql.String)
            , sql.Column('num_uses', sql.Integer)
            )
    tables['files'] = sql.Table(
            'files'
            , metadata
            , sql.Column('id', sql.Integer, primary_key=True)
            , sql.Column('location', sql.String)
            )
    tables['uses'] = sql.Table(
            'uses'
            , metadata
            , sql.Column('id', sql.Integer, primary_key=True)
            , sql.Column('file_id', sql.Integer, sql.ForeignKey('files.id'))
            , sql.Column('tag_id', sql.Integer, sql.ForeignKey('tag.id'))
            )
    sql.metadata.create_all()
    return tables

def insert(data,table):
    i=table.insert()
    i.execute(data)
    return

def addTag(tag, tag_table, num_uses=0):
    data={'tag': tag, 'num_uses':0}
    insert(data, tag_table)


def getTagFromID(id_, table):
    s=sql.select(table.c.id == id_)
    return s.execute().fetchone()

main()


