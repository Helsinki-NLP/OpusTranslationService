#!/usr/bin/env python3
#-*-python-*-

import yaml
import sys
from shutil import copyfile
import ast
import os



# The previous iteration of this script broke vocabulary units with quotes (and probably backslashes) in them,
# this fixes that problem.

# Use the backup made by the previous script version
def fix_vocab(filename):
    if os.path.exists(f'{filename}.bak'):
        copyfile(f'{filename}.bak',filename)
    try:
        input = open(filename, 'r')
        yaml.safe_load(input)
    except:
        print('YAML file is broken - try to fix it!')
        # change the backup extension to indicate that the new script has been used
        print(f'copy {filename} to {filename}.bak_quotes')
        copyfile(filename, f'{filename}.bak_quotes')

        with open(f'{filename}.bak_quotes','r') as broken, open(filename,'w') as fixed:
            for line in broken:
                # validate individual lines: if it ain't broken don't fix it
                try:
                    yaml.safe_load(line)
                    fixed.write(line)
                except:               
                    parts = line.rstrip().split(': ')
                    parts[0] = parts[0].strip('"')
                    vocab = {}
                    vocab[parts[0]] = int(parts[1])
                    #NEL gets made into a complex key (bad for ctranslate2 compatibility), so handle it differently
                    if parts[0] == u'\u0085':
                        fixed.write(f'\"\\x85\": {int(parts[1])}\n')
                    else:
                        fixed.write(yaml.dump(vocab))

    #Remove the old backup, it's kept with a new name
        if os.path.exists(f'{filename}.bak'):
            os.remove(f'{filename}.bak')

if __name__ == "__main__":
    fix_vocab(sys.argv[1])