import os
import time
from typing import Union
from pathlib import Path


def delete_old_files(path: Union[None, Path] = None):
    current_time = time.time()
    if path is None:
        local_dir = os.path.dirname(__file__)
        abs_dir = os.path.join(os.getcwd(), local_dir)
        path = abs_dir
    for f in os.listdir(path):
        creation_time = os.path.getctime(Path(path, f))
        if os.path.splitext(f)[1].lower() == '.png':
            if (current_time - creation_time) >= 20:
                os.unlink(Path(path, f))
                print('{} removed'.format(f))
