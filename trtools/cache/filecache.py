import os
import types
import glob

import pandas as pd

class FileCache(object):
    """
        Basically a replacement for the HDF5Store. It stores as flat files.
    """
    def __init__(self, cache_dir, filename_func=None):
        self.cache_dir = cache_dir
        if filename_func:
            self.get_filename = types.MethodType(filename_func, self)
        FileCache.create_dir(cache_dir)

    @staticmethod
    def create_dir(dir):
        if not os.path.isdir(dir):
            os.makedirs(dir)

    def get_filename(self, name):
        filename = os.path.join(self.cache_dir, name)
        return filename

    def put(self, name, obj):
        filename = self.get_filename(name)
        pd.save(obj, filename)

    def get(self, name):
        filename = self.get_filename(name)
        obj = pd.load(filename)
        obj.name = name
        return obj

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.put(key, value)

    def __contains__(self, key):
        filepath = self.get_filename(key)
        return os.path.exists(filepath)

    def __len__(self):
        return len(self.keys())

    def __repr__(self):
        output = '%s\nCache path: %s\n' % (type(self), self.cache_dir)

        if len(self) > 0:
            output += '\n'.join(self.keys())
        else:
            output += 'Empty'

        return output

    def keys(self):
        dir = self.cache_dir
        keys = os.listdir(dir)
        return keys

def leveled_filename(fc, name):
    subdir = os.path.join(fc.cache_dir, name[0])
    FileCache.create_dir(subdir)
    return os.path.join(subdir, name)

class LeveledFileCache(FileCache):
    def __init__(self, cache_dir):
        super(LeveledFileCache, self).__init__(cache_dir, 
                                               filename_func=leveled_filename)

    def keys(self):
        pat = self.cache_dir + '/*/*'
        files = glob.glob(pat)
        return [os.path.basename(f) for f in files]
