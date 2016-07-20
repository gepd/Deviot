"""
Function for deterministically creating a single hash for a directory of files,
taking into account only file contents and not filenames.

Usage:

from checksumdir import dirhash

dirhash('/path/to/directory', 'md5')

"""

import os
import hashlib
import re

__version__ = '1.0.5'


HASH_FUNCS = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha256': hashlib.sha256,
    'sha512': hashlib.sha512
}


def dirhash(dirname, hashfunc='md5'):
    hash_func = HASH_FUNCS.get(hashfunc)
    if not hash_func:
        raise NotImplementedError('{} not implemented.'.format(hashfunc))

    if not os.path.isdir(dirname):
        raise TypeError('{} is not a directory.'.format(dirname))
    hashvalues = []
    for root, dirs, files in os.walk(dirname, topdown=True):
        if not re.search(r'/\.', root):
            hashvalues.extend([_filehash(os.path.join(root, f),
                                         hash_func) for f in files if not
                               f.startswith('.') and not re.search(r'/\.', f)])
    return _reduce_hash(hashvalues, hash_func)


def _filehash(filepath, hashfunc):
    hasher = hashfunc()
    blocksize = 64 * 1024
    with open(filepath, 'rb') as fp:
        while True:
            data = fp.read(blocksize)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def _reduce_hash(hashlist, hashfunc):
    hasher = hashfunc()
    for hashvalue in sorted(hashlist):
        hasher.update(hashvalue.encode('utf-8'))
    return hasher.hexdigest()
