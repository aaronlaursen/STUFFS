#!/usr/bin/python2

import sqlalchemy as sql
import os
from sqlalchemy.orm import sessionmaker
Session = sessionmaker()

DBPATH=os.getcwd()+"/tag.db"



def main():
    db = sql.create_engine('sqlite://'+DBPATH)
    db.echo = False
    Session.configure(bind=db)
    metadata = sql.MetaData(db)
    tables=initDB(metadata)
    return

def initDB(metadata):
    tables={}
    tables['tags'] = sql.Table(
            'tags'
            , metadata
            , sql.Column('id', sql.Integer, primary_key=True)
            , sql.Column('tag', sql.String)
            , sql.Column('num_uses', sql.Integer)
            , sql.Column('hidden', sql.Boolean)
            )
    tables['files'] = sql.Table(
            'files'
            , metadata
            , sql.Column('id', sql.Integer, primary_key=True)
            , sql.Column('data', sql.Binary)
            )
    tables['uses'] = sql.Table(
            'uses'
            , metadata
            , sql.Column('id', sql.Integer, primary_key=True)
            , sql.Column('file_id', sql.Integer, sql.ForeignKey('files.id'))
            , sql.Column('tag_id', sql.Integer, sql.ForeignKey('tag.id'))
            )
    for t in tables:
        t.create()

    sql.mapper(Tag, tables['tags'])
    sql.mapper(File, tables['files'])
    sql.mapper(Use, tables['uses'])
    return tables

class Tag(object):
    def __init__(self, tag=None, num_uses=0):
        self.tag=tag
        self.num_uses=num_uses
class File(object):
    def __init__(self, location=None):
        self.location=location
class Use(object):
    def __init__(self, fileID=None, tagID=none):
        self.file_id=fileID
        self.tag_id=tagID

def insert(data,table):
    table.insert().execute(data)
    return data['id']

def addTag(tag, tag_table, num_uses=0):
    data={'tag': tag, 'num_uses':0}
    insert(data, tag_table)

def addFile(contents, file_table):
    data={'data':contents,}
    insert(data, file_table)

def addUse(FileID, TagID, use_table):
    data={'file_id':FileID, 'tag_id':TagID}
    insert(data, use_table)

def getByID(id_, table):
    s=sql.selectfirst(table.c.id == id_)
    return s.execute()

def deleteByID(id_, table):
    s=sql.delete(table.c.id==id_)
    s.execute()
    return

def deleteUseClean(id_, tables):
    pass

def dincNum_Uses(id_,table):
    session = Session()
    tag = session.query(Tag).selectfirst(table.c.id==id_)
    tag.num_uses -= 1
    new_num=tag.num_uses
    session.flush()
    return new_num

def deleteUsesByFileID(file_id, uses_table):
    s=sql.delete(uses_table.c.file_id == file_id)
    s.execute()
    return


def deleteFileClean(id_,tables):
    deleteUsesByFileID(id_,tables['uses'])




main()
