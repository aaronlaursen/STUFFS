STUFFS
======

Semantic File-System (Honors project 2013/2014)

Run-as:

./STUFFS < mountpoint > [database_location]


Some things to note:

- Files and tags get unique names, so `mkdir mytag; ls` may output "mytag%9876%" where "9876" is an internal ID, 
and `touch myfile;ls` may output "myfile@8360@"
 - On the plus side, this means that you don't need the full path, so "/tag1%907%/tag2%5267%/tag3%83%/file@47@", 
"/tag1%907%/file@47@", "/file@47@", "/someTagThatDoesntEvenExist/file@47@" all point to the same "file@47@".
 - This also means that something pointing to "/file@47@" will allways point to "file@47@" regardless of what 
you tag it as...
