# my_ugit

This is a small implementation of a Git-like version control system in Python following the Nikita's tutorial -- [ugit: DIY Git in Python](https://www.leshenko.net/p/ugit/#)

## What features does ugit have

+ `ugit init`
+ `ugit add`
+ `ugit commit -m`
+ `ugit checkout`
+ `ugit branch`
+ `ugit push`
+ `ugit merge`
+ `ugit merge-base`
+ `ugit fetch`
+ `ugit reset`
+ `ugit tag`
+ `ugit log`
+ `ugit diff -cache`
+ `ugit k`
+ `ugit status`
+ `ugit show`

:construction: ugit function introduction is WIP :construction:

## How to use ugit

1. clone the repos.

```
$ git clone repo_link https://github.com/ZhuohaoHe/my_ugit.git
```

2. use setup.py to install this package. (need `setuptools` package)

```
$ python3 setup.py
```

3. use development mode, if you want to edit the source and run it immediately.

```
$ python3 setup.py develop --user
```

4. and now, just type `ugit` in CLI to use it.

```
$ ugit
```

## What's in the ugit folder?

```
├── setup.py : use setup.py to make my own python package
└── ugit
    ├── cli.py : in charge of parsing and processing user input. 
    ├── base.py : the basic higher-level logic of ugit to implement higher-level structures for storing directories
    ├── data.py : contains the code that actually touches files on disk to manages the data in .ugit directory
    ├── diff.py : contain the code that deals with computing differences between objects
    └── remote.py: contain all remote synchronization code
```

## Acknowledgements

thanks to the Nikita's tutorial -- [ugit: DIY Git in Python](https://www.leshenko.net/p/ugit/#)

Comments in the code source from Nikita's tutorial, [Python doc](https://docs.python.org), [git-scm doc](https://git-scm.com/doc), [W3Shools](https://www.w3schools.com/python), [Stack Overflow](https://stackoverflow.com) and myself :yum:.
