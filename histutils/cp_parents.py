#!/usr/bin/env python
def cp_parents(files, target_dir:Path):
    """
    This function requires Python >= 3.6.

    This acts like bash cp --parents in Python
    inspiration from
    http://stackoverflow.com/questions/15329223/copy-a-file-into-a-directory-with-its-original-leading-directories-appended

    example
    source: /tmp/e/f
    dest: /tmp/a/b/c/d/
    result: /tmp/a/b/c/d/tmp/e/f

    cp_parents('/tmp/a/b/c/d/boo','/tmp/e/f')
    cp_parents('x/hi','/tmp/e/f/g')  --> copies ./x/hi to /tmp/e/f/g/x/hi
    """
#%% make list if it's a string
    if isinstance(files,(str,Path)):
        files = [files]
#%% cleanup user
    files = (Path(f).expanduser() for f in files)   #relative path or absolute path is fine
    target_dir = Path(target_dir).expanduser()
#%% work
    for f in files:
        newpath = target_dir / f.parent #to make it work like cp --parents, copying absolute paths if specified
        newpath.mkdir(parents=True, exist_ok=True)
        copy2(f, newpath)

#cp_parents('/tmp/a/b/c/d/boo','/tmp/e/f')
#cp_parents('x/hi','/tmp/e/f/g')  --> copies ./x/hi to /tmp/e/f/g/x/hi

if __name__ == '__main__':
    from sys import argv
    cp_parents(argv[1], argv[2])
