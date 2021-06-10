import os
import time


def delete_old_files():
    current_time = time.time()

    for f in os.listdir():
        creation_time = os.path.getctime(f)
        if os.path.splitext(f)[1].lower() == '.png':
            if (current_time - creation_time) >= 120:
                os.unlink(f)
                print('{} removed'.format(f))
