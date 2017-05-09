STUFFS
======
Aaron Laursen

a Semantically-Tagged, Unorganized, Future File-System: STUFFS
---------------------------------------------------------------

STUFFS is a simple tag-based file-system experimenting with new ways to view,
organize, and search for your files. Traditional hierarchal paths are replaced
by sets of tags applied to your files, allowing for out-of-order and partial
sets to "filter" your files and show you the ones you want.

Files and tags are stored in an SQLite3 database mapped to a fuse file-system. 
"Directories" are dynamically generated and contain every file existing in the
intersection of the tags in the path.

Otherwise, the system is pretty-much backwards compatible and can be used like
a traditional, hierarchal system. 

Run-as:
-------

    STUFFS.py < mountpoint > [database_location]

i.e.

    STUFFS /mnt $HOME/STUFFS.db

Requirements:
-------------

-Python3

-SQLite3

-SQLAlchemy

-FUSEpy

Layout:
-------

All tags show up in the root directory. All files in the system can be found in `/ALLFILES`.
Under every tag combination, one can found all files tagged with the
intersection of the tags in the path, as well as any tag not in the path which
is applied to at least one of the files in the path.

How to use:
-----------

Create a file:

    touch myfile

Create a tag:

    mkdir /mytag

add a tag:

    mv myfile mytag/

delete a tag:

    rmdir mytag/

add tags:

    mv myfile /mytag/mytag2/mytag3

remove tags (depending on the shell, the ! may need to be escaped):

    mv myfile /!mytag

view everything tagged as "mytag"

    ls /mytag/

etc...

Some things to note:
--------------------

- Files and tags get unique names, so `mkdir mytag; ls` may output "mytag%9876%" 
where "9876" is an internal ID, and `touch myfile;ls` may output "myfile@8360@"

 - On the plus side, this means that you don't need the full path, so 
"/tag1%907%/tag2%5267%/tag3%83%/file@47@", "/tag1%907%/file@47@", and 
"/file@47@", all point to the same "file@47@".

 - This also means that something pointing to "/file@47@" will allways point to 
"file@47@" regardless of what you tag it as...


License, reuse, etc.
--------------------

This software was originally written by Aaron Laursen <aaronlaursen@gmail.com>.

This software is licensed under the ISC (Internet Systems Consortium) license.
The specific terms are below, and allow pretty much any reasonable use. If you, 
for some reason, need it in a different licence, send me an email, and we'll see
what I can do. 

However, the author would appreciate but does not require (except as permitted
by the ISC license):

- Notification (by email preferably <aaronlaursen@gmail.com>) of use in
products, whether open-source or commercial. 

- Contribution of patches or pull requests in the case of
  improvements/modifications

- Credit in documentation, source, etc. especially in the case of large-scale
  projects making heavy use of this software.

### ISC license

Copyright (c) 2013, Aaron Laursen <aaronlaursen@gmail.com>

Permission to use, copy, modify, and/or distribute this software for any purpose with or 
without fee is hereby granted, provided that the above copyright notice and this permission 
notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH 
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND 
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR 
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, 
DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS 
ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

