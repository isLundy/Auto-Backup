from pathlib import Path
from datetime import datetime
import threading
import sched
import time
import shutil
import json
import re
# import nuke



def copy_to_backup():
    # .nk file
    nk = Path('/Users/lundy/Desktop/Temp/Test/Test_comp_v001.nk').absolute()

    if nk.is_file():

        # .nk.autosave file
        nk_autosave = nk.with_name(f'{nk.name}.autosave')

        # Designate to source file
        if nk_autosave.is_file():
            src = nk_autosave
            src_stem = Path(nk_autosave.stem).stem
        else:
            src = nk
            src_stem = nk.stem

        # get time stamp
        date_format = '%Y-%m-%d_%H-%M-%S'
        src_mtime = datetime.fromtimestamp(src.stat().st_mtime).strftime(date_format)

        # create Auto-Backup dir
        backup_dir = nk.parent.joinpath('Auto-Backup')
        Path(backup_dir).mkdir(parents=True, exist_ok=True)

        # new file
        new = Path(backup_dir).joinpath(f'{src_stem}_{src_mtime}.nk')

        # copy to Auto-Backup dir
        if not new.is_file():
            shutil.copy2(src, new)

        # find the bakcup file
        pattern = re.compile(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.nk$') # match time.nk at the end
        pattern_2 = re.compile(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}') # match time

        files = [file for file in Path(backup_dir).glob('*.nk') if pattern.search(file.name)]
        files = sorted(files, key=lambda x:datetime.strptime(pattern_2.search(x.name).group(), date_format), reverse=True)

        # delete old file
        while len(files) > settings['max_num_files']:
            files.pop().unlink()

        print(f'Bckup Successful~ {new.name}')
        scheduler.enter(3, 1, copy_to_backup)



scheduler = sched.scheduler(time.time, time.sleep)

try:
    with open('settings.json') as st:
        settings = json.load(st)
except:
    settings = {
                'enabled': True,
                'timer': 20,
                'max_num_files': 10,
                }

if settings['enabled']:
    scheduler.enter(3, 1, copy_to_backup)
    copy_sched = threading.Thread(target=scheduler.run)
    # copy_sched.daemon = True
    copy_sched.start()

