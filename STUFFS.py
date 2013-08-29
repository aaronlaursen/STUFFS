#!/usr/bin/python

from sqlalchemy import Table, Column, Integer, ForeignKey, BLOB, \
        Boolean, String, create_engine, MetaData
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from time import time
from stat import S_IFDIR, S_IFLNK, S_IFREG
from hashlib import md5
from fuse import Operations, LoggingMixIn, FUSE, FuseOSError
from sys import argv
from errno import ENOENT


#database stuff

from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute('PRAGMA synchronous=OFF')
    cursor.execute('PRAGMA temp_store = MEMORY;')
    cursor.close()

DBPATH="fs.db" if len(argv) <=2 else argv[2]
db = create_engine('sqlite:///'+DBPATH,connect_args={'check_same_thread':False})
db.echo = False
Base = declarative_base(metadata=MetaData(db))
Session = scoped_session(sessionmaker(bind=db))
#session=Session()

Table('use'
    , Base.metadata
    , Column('file_id', Integer, ForeignKey('files.id'))
    , Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Datum(Base):
    __tablename__='data'
    def __init__(self):
        self.datum=bytes()
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('files.id'))
    datum = Column(BLOB)

class File(Base):
    __tablename__ = 'files'
    def __init__(self):
        pass
    id = Column(Integer, primary_key=True)
    attrs = Column(String)
    name = Column(String)
    data = relationship("Datum"
                    , collection_class=list
                    )
    tags = relationship("Tag"
                    , secondary="use"
                    , backref=backref("files", collection_class=set)
                    , collection_class=set
                    )

class Tag(Base):
    __tablename__ = 'tags'
    def __init__(self, txt):
        self.name=txt
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    attrs = Column(String)

Base.metadata.create_all()

def mkfile(name, session, mode=0o770, tags=None):
    f = File()
    session.add(f)
    if tags !=None:
        f.tags |= set(tags)
    now=time()
    a = {'st_mode':(S_IFREG | mode)
                , 'st_nlink':1
                , 'st_size':0
                , 'st_ctime':now
                , 'st_mtime':now
                , 'st_atime':now
                , 'uid':0
                , 'gid':0
                }
    f.attrs = convertAttr(a)
    f.name=name
    addBlock(f,session)
    #f.data=bytes()
    #print("****new file tags:", tags)
    return f

def mktag(txt, session, mode=0o777):
    t=Tag(txt)
    session.add(t)
    now=time()
    a = {'st_mode':(S_IFDIR | mode)
                , 'st_nlink':1
                , 'st_size':0
                , 'st_ctime':now
                , 'st_mtime':now
                , 'st_atime':now
                , 'uid':0
                , 'gid':0
                }
    t.attrs = convertAttr(a)
    return t

'''
def getAttrTag(obj, attr, session):
    q=session.query(Tag).filter(Tag.in_(obj.tags), Tag.name.like("attr::"+attr+"::%") )
    return q.first()

def setAttrTag(obj, attr, value, session):
    obj.tags.discard(getAttrTag(obj,attr,session))
    t=getTagsByTxts("attr::"+attr+"::"+value)
#'''


def convertAttr(attrs):
    attrdata=( ('st_mode',int)
            , ('st_nlink',int)
            , ('st_size',int)
            , ('st_ctime',float)
            , ('st_mtime',float)
            , ('st_atime',float)
            , ('uid', int)
            , ('gid', int)
            )
    if type(attrs) == type(dict()):
        s=''
        for i in range(len(attrdata)):
            s+=str(attrs[attrdata[i][0]])
            s+=','
        return s[:-1]
    if type(attrs) == type(''):
        attrs=attrs.split(',')
        d={attrdata[i][0]:attrdata[i][1](attrs[i]) for i in range(len(attrdata))}
        return d
    return None

def getIdFromString(s):
    t={'%':Tag,'@':File}
    if len(s) <3: return 0, File
    if s[-1] not in ('%','@'):
        return 0, File
    if len(s.split(s[-1]))<3:
        return 0, File
    i=s.split(s[-1])[-2]
    if not i.isdigit():
        return 0, File
    return int(i), t[s[-1]]

def genDisplayName(obj):
    if obj.__tablename__=='files':
        name=obj.name
        s='@'
    elif obj.__tablename__=='tags':
        name=obj.name
        s='%'
    name += s + str(obj.id) +s
    return name

def getByID(id_, session, typ=File):
    return session.query(typ).get(int(id_))

def getFilesByTags(tags,session):
    q=session.query(File)
    for t in tags:
        q=q.filter(File.tags.contains(t))
    return q.all()

def getTagsByTxts(txts,session):
    q=session.query(Tag).filter(Tag.name.in_(txts))
    return q.all()

def getFilesByTagTxts(txts,session):
    tags=getTagsByTxts(txts,session)
    return getFilesByTags(tags,session)

def getTagsByFiles(files):
    tags=set()
    for f in files:
        tags |= f.tags
    return tags

def getTagsFromPath(path,session):
    #print("----------------------")
    #print("%"+path+"%")
    tagnames=set(path.split('/'))
    tagnames.discard('')
    #print(tagnames)
    #print("----------------------")
    if type(tagnames)==type(None): return set()
    if len(tagnames)==0: return set()
    idtags=set()
    for t in tagnames:
        id_,typ = getIdFromString(t)
        tag=getByID(id_, session, Tag)
        if tag: idtags.add(tag)
    nametags=set(getTagsByTxts(tagnames,session))
    return idtags | nametags

def getEndTagFromPath(path,session):
    #if path=='/': return None
    path=path.strip('/')
    path=path.split("/")
    tagname=path[-1]
    if tagname=='': return None
    id_, typ = getIdFromString(tagname)
    tag=getByID(id_, session, Tag)
    if tag: return tag
    return getTagsByTxts(tagname,session)[0]

def getFileByNameAndTags(name,tags,session):
    q=session.query(File).filter(File.name==name)
    for t in tags:
        q=q.filter(File.tags.contains(t))
    return q.first()

def getFileFromPath(path,session):
    path=path.strip('/')
    pieces=path.split('/')
    fstring=pieces[-1]
    fid,typ=getIdFromString(fstring)
    f=getByID(fid, session, File)
    if f: return f
    path = ""
    for p in pieces[:-1]: path +=p+"/"
    return getFileByNameAndTags(fstring,getTagsFromPath(path,session),session)

def getSubByTags(tags,session):
    if len(tags)==0:return genEverything(session)
    subfiles=set(getFilesByTags(tags,session))
    subtags=getTagsByFiles(subfiles)
    subtags=subtags-tags
    #print("{}{}{}{}{}{}{}")
    #print(subfiles,subtags)
    #print("{}{}{}{}{}{}{}")
    return subfiles | subtags

def genSub(path,session):
    tags=getTagsFromPath(path,session)
    #print("\n tags from subpath", path,tags,"\n")
    sub=getSubByTags(tags,session)
    #print("############")
    #print(sub)
    #print("############")
    return sub

def genSubDisplay(path,session):
    sub=genSub(path,session)
    return [genDisplayName(x) for x in sub]

def getAttrByObj(obj):
    return convertAttr(obj.attrs)

def getObjByPath(path,session):
    if path[-1]=='/':
        return getEndTagFromPath(path,session)
    objname=path.split('/')[-1]
    #print("============")
    #print(objname)
    #print(getIdFromString(objname))
    #print("============")
    id_, typ = getIdFromString(objname)
    obj = getByID(id_, session,typ)
    if obj: return obj
    pathpieces=path.rsplit('/',1)
    opts=genSub(pathpieces[0]+'/',session)
    for o in opts:
        if o.name==pathpieces[1]: return o
    return getFileFromPath(path,session)

def genEverything(session):
    stuff=set()
    q=session.query(File)
    stuff |= set(q.all())
    q=session.query(Tag)
    stuff |= set(q.all())
    #print("------stuff:",stuff)
    return stuff

def genDisplayEverything(session):
    stuff=genEverything(session)
    return [genDisplayName(obj) for obj in stuff]

def getAttrByPath(path,session):
    obj=getObjByPath(path,session)
    if not obj: return None
    return getAttrByObj(obj)

def rmObj(obj,session):
    session.delete(obj)

def rmByPath(path,session):
    obj=getObjByPath(path,session)
    if not obj: return None
    rmObj(obj,session)

def addBlock(f,session):
    block=Datum()
    session.add(block)
    f.data.append(block)
    #block.parent_id=f.id
    session.flush()
    return f

def delBlock(f,session):
    session.delete(f.data.pop())
    session.flush
    return f

#fuse stuff
class SpotFS(LoggingMixIn, Operations):
    def __init__(self):
        self.fd=0
        #self.session=Session()
        self.blocksize=64*1024

    def getattr(self, path, fh=None):
        #print("getattr:", path, fh)
        session=Session()
        attr=None
        if path.strip()=='/':
            attr= {'st_mode':(S_IFDIR | 0o777)
                , 'st_nlink':2
                , 'st_size':0
                , 'st_ctime':time()
                , 'st_mtime':time()
                , 'st_atime':time()
                , 'uid':0
                , 'gid':0
                }
        if not attr: attr=getAttrByPath(path,session)
        #print("+++++++++")
        #print(attr)
        #print("+++++++++")
        if not attr:
            raise FuseOSError(ENOENT)
        return attr

    def mkdir(self,path,mode):
        session=Session()
        path=path.strip('/')
        path=path.split('/')
        txt=path[-1]
        mktag(txt, session, mode)
        session.commit()

    def readdir(self,path,fh=None):
        #print("readdir")
        session=Session()
        if path=='/': return ['.','..']+genDisplayEverything(session)
        return ['.','..']+genSubDisplay(path,session)

    def chmod(self, path, mode):
        session=Session()
        obj=getObjByPath(path,session)
        if not obj: return
        attrs=convertAttr(obj.attrs)
        attrs['st_mode'] |=mode
        obj.attrs=convertAttr(attrs)
        session.commit()
        return 0

    def chown(self, path,uid,gid):
        session=Session()
        obj=getObjByPath(path,session)
        if not obj: return
        attrs=convertAttr(obj.attrs)
        attrs['uid']=uid
        attrs['gid']=gid
        obj.attrs=convertAttr(attrs)
        session.add(obj)
        session.commit()

    def create(self,path,mode):
        #print("creat reached:",path,mode)
        session=Session()
        tpath, name = path.rsplit("/",1)
        tags=getTagsFromPath(path,session)
        mkfile(name,session,tags=tags)
        session.commit()
        self.fd +=1
        return self.fd

    def open(self,path,flags):
        #print("open reached:",path,flags)
        self.fd+=1
        return self.fd

    def read(self,path,size,offset,fh):
        #print("read")
        session=Session()
        f=getFileFromPath(path,session)
        if not f: return ""
        #print(":-:-:",f.data[offset:offset+size])
        #return f.data[offset:offset+size]
        data=bytes()
        blockoffs=offset//self.blocksize
        offset=offset%self.blocksize
        while size >0:
            #print(data)
            if blockoffs>=len(f.data): break
            data+=f.data[blockoffs].datum[offset:min(self.blocksize,size+offset)]
            size-=(self.blocksize-offset)
            blockoffs+=1
            offset=0
            #print("Loop!")
        #print(len(data))
        #print(data)
        #print(data.decode())
        return data.decode().encode()

    def write(self,path,data,offset,fh):
        #print("write")
        #print(data)
        #print(type(data))
        session=Session()
        f=getFileFromPath(path,session)
        if not f: return
        #f.data=f.data[:offset]+data
        size=len(data)
        attrs=convertAttr(f.attrs)
        attrs['st_size']=offset+size
        f.attrs=convertAttr(attrs)
        blockoffs=offset//self.blocksize
        offset=offset%self.blocksize
        #print("offset:",offset)
        start=0
        while start<size:
            while blockoffs>=len(f.data):
                f=addBlock(f,session)
            f.data[blockoffs].datum=f.data[blockoffs].datum[:offset]+data[start:start+min(size-start,self.blocksize-offset)]
            start+=min(size-start,self.blocksize-offset)
            offset=0
            blockoffs+=1
            #print("loop!")
        session.commit()
        #print(size)
        return size

    def truncate(self, path, length, fh=None):
        #print("truncate")
        session=Session()
        f=getFileFromPath(path,session)
        if not f: return
        #f.data=f.data[:length]
        numblocks=(length+self.blocksize-1)//self.blocksize
        while numblocks>len(f.data):
            f=addBlock(f,session)
        while numblocks>len(f.data):
            f=delBlock(f,session)
        if numblocks>0:
            f.data[-1].datum=f.data[-1].datum[:length%self.blocksize]
        attrs=convertAttr(f.attrs)
        attrs['st_size']=length
        f.attrs=convertAttr(attrs)
        session.commit()

    def utimens(self, path, times=None):
        now=time()
        atime, mtime = times if times else (now,now)
        session=Session()
        f=getFileFromPath(path,session)
        if not f: return
        attrs=convertAttr(f.attrs)
        attrs['st_atime']=atime
        attrs['st_mtime']=mtime
        f.attrs=convertAttr(attrs)
        session.commit()

    def rmdir(self,path):
        session=Session()
        rmByPath(path,session)
        session.commit()

    def unlink(self, path):
        session=Session()
        rmByPath(path,session)
        session.commit()

    def rename(self, old, new):
        session=Session()
        tags=getTagsFromPath(new,session)
        f=getObjByPath(old,session)
        f.tags=set(tags)
        session.commit()

    def readlink(self, path):
        return self.read(path,float("inf"),0,None)

if __name__ == "__main__":
    if len(argv) < 2:
        print('usage: %s <mountpoint> [database]' % argv[0])
        exit(1)
    fuse = FUSE(SpotFS(), argv[1], foreground=True)

