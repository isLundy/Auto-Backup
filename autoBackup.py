from pathlib import Path
from datetime import datetime
import threading
import sched
import time
import shutil
import json
import re
import nuke


class AutoBackup:
    def __init__(self):
        if self.backup_user()['enabled']:
            self.scheduler = sched.scheduler(time.time, time.sleep)
            self.scheduler.enter(self.backup_user()['timer']*0.15, 1, self.copy_to_backup_dir)
            sched_copy = threading.Thread(target=self.scheduler.run)
            sched_copy.daemon = True
            sched_copy.start()



    # default value
    def backup_default(self):
        settings = {
                    'enabled': True,
                    'timer': 20,
                    'max_num_files': 10,
                    'backup_dir_index': 0,
                    'custom_dir': ''
                    }

        return settings



    # user settings
    def backup_user(self):
        with open('/Users/lundy/HuStudio/Work/Github/Auto-Backup/settings.json') as st:
            settings = json.load(st)

        return settings



    # backup directories
    def backup_dirs(self):
        if Path(nuke.root().name()).absolute().is_file():
            cur_project_dir = Path(nuke.root().name()).absolute().parent.joinpath('Auto-Backup').as_posix()
        else:
            cur_project_dir = ''
        nuke_temp_dir = Path(nuke.tcl('getenv NUKE_TEMP_DIR')).absolute().joinpath('Auto-Backup').as_posix()
        custom_dir = self.backup_user()['custom_dir']

        return [cur_project_dir, nuke_temp_dir, custom_dir]



    # copy
    def copy_to_backup_dir(self):
        # .nk file
        nk = Path(nuke.root().name()).absolute()

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
            backup_dir = self.backup_dirs()[self.backup_user()['backup_dir_index']]

            if not Path(backup_dir).is_dir():
                Path(backup_dir).mkdir(parents=True, exist_ok=True)

            # new file
            new = Path(backup_dir).joinpath(f'{src_stem}_{src_mtime}.nk')

            # copy to Auto-Backup dir
            if not new.is_file():
                shutil.copy2(src, new)
                print(f'Auto Bckup Successful~ {new.name}')

                # find the bakcup file
                pattern = re.compile(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.nk$') # match time.nk at the end
                pattern_2 = re.compile(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}') # match time

                files = [file for file in Path(backup_dir).glob('*.nk') if pattern.search(file.name)]
                files = sorted(files, key=lambda x:datetime.strptime(pattern_2.search(x.name).group(), date_format), reverse=True)

                # delete old file
                while len(files) > self.backup_user()['max_num_files']:
                    files.pop().unlink()

            self.scheduler.enter(self.backup_user()['timer']*0.15, 1, self.copy_to_backup_dir)



test = AutoBackup()