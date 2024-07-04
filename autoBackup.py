try:
    from PySide6.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton, QComboBox,
        QLineEdit, QStyle, QFrame, QToolTip, QFileDialog)
    from PySide6.QtGui import QCursor, QIcon
    from PySide6.QtCore import Qt, QSize, QTimer
except:
    from PySide2.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton, QComboBox,
        QLineEdit, QStyle, QFrame, QToolTip, QFileDialog)
    from PySide2.QtGui import QCursor, QIcon
    from PySide2.QtCore import Qt, QSize, QTimer

import nuke
import nukescripts
import sys
from pathlib import Path
from datetime import datetime
import shutil
import re
import json
import threading
import sched
import time


class AutoBackup:
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)



    def interval_time(self):
        interval = self.backup_user()['timer']*60

        return interval


    # start timing
    def start_timer(self):
        # check user settings
        if self.backup_user()['enabled']:
            self.scheduler.enter(self.interval_time(), 1, self.copy_to_backup_dir)
            sched_copy = threading.Thread(target=self.scheduler.run)
            sched_copy.daemon = True
            sched_copy.start()



    # default value
    def backup_default(self):
        settings = {
                    'enabled': True,
                    'timer': 20,
                    'maximum_files': 20,
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

            # get Auto-Backup dir
            backup_dir = self.backup_dirs()[self.backup_user()['backup_dir_index']]

            if not Path(backup_dir).is_dir():
                Path(backup_dir).mkdir(parents=True, exist_ok=True)

            # get current time
            date_format = '%Y-%m-%d_%H-%M-%S'
            cur_time = datetime.now().strftime(date_format)

            # new file
            new = Path(backup_dir).joinpath(f'{src_stem}_{cur_time}.nk')

            # find the bakcup file
            pattern = re.compile(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.nk$') # match time.nk at the end
            pattern_2 = re.compile(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}') # match time
            files = [file for file in Path(backup_dir).glob('*.nk') if pattern.search(file.name)]

            # get modify time
            src_mtime = src.stat().st_mtime
            backup_files_mtimes = [file.stat().st_mtime for file in files]

            # copy to Auto-Backup dir
            if src_mtime not in backup_files_mtimes:
                shutil.copy2(src, new)
                print(f'Auto Bckup Successful~ {new.name}')

                files.append(new)

                # delete oldest file
                files = sorted(files, key=lambda x:datetime.strptime(pattern_2.search(x.name).group(), date_format))
                while len(files) > self.backup_user()['maximum_files']:
                    files.pop(0).unlink()

            # looped task
            self.scheduler.enter(self.interval_time(), 1, self.copy_to_backup_dir)



class AutoBackup_UI(QWidget):

    def __init__(self):
        super().__init__()
        self.auto_Backup = AutoBackup()



    def start_ui(self):
        # start ui
        self.set_ui()
        self.set_user_values()
        self.set_window()
        self.show()
        self.setFocus()



    def set_ui(self):
        # definition icon
        self.icon_folder = QIcon('./icon/autoBackup_folder.svg')
        self.icon_folder_gear = QIcon('./icon/autoBackup_folder_gear.svg')
        self.icon_restore = QIcon('./icon/autoBackup_restore.svg')
        self.icon_close = QIcon('./icon/autoBackup_restore.svg')
        self.icon_save = QIcon('./icon/autoBackup_save.svg')
        self.icon_size = QSize(14, 14)

         # timer display
        self.timer_display_label = QLabel('20:00')
        nuke_font_size = int(nuke.toNode('preferences')['UIFontSize'].getValue())
        self.timer_display_label.setStyleSheet(f"font-size: {nuke_font_size*2}px")
        self.update_timer_display()

        # timer obj
        self.timer_obj = QTimer()
        self.timer_obj.timeout.connect(self.update_timer_display)
        self.timer_obj.start(1000)

        # divider
        self.h_line = QFrame()
        self.h_line.setFrameShape(QFrame.HLine)
        self.h_line.setStyleSheet("QFrame {color: rgba(255, 255, 255, 50)}")

        # timer
        self.timer_label = QLabel('Timer:')

        self.timer_spinbox = QSpinBox()
        self.timer_spinbox.setFixedWidth(48)
        self.timer_spinbox.setRange(1, 480)
        self.timer_spinbox.setValue(20)
        self.timer_spinbox.setToolTip(
                                '''Minimum: 1'''
                                '''\nMaximum: 480'''
                                '''\n\n(480=60*8 Hope you never work overtime~)'''
                                )

        self.timer_minutes_label = QLabel('minutes')

        # maximum files
        self.maximum_files_label = QLabel('Maximum Files:')

        self.maximum_files_spinbox = QSpinBox()
        self.maximum_files_spinbox.setFixedWidth(48)
        self.maximum_files_spinbox.setRange(1, 100)
        self.maximum_files_spinbox.setValue(20)
        self.maximum_files_spinbox.setToolTip(
                                    '''Minimum: 1'''
                                    '''\nMaximum: 100''')

        # backup directory
        self.backup_dir_label = QLabel('Backup Directory:')
        self.backup_dir_label.setFixedHeight(QComboBox().sizeHint().height()*0.9)

        self.backup_dir_combobox = QComboBox()
        self.backup_dir_combobox.addItems(['Current Project Dir', 'Nuke Temp Dir', 'Custom'])
        self.backup_dir_combobox.setMinimumWidth(206)
        self.backup_dir_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.backup_dir_combobox.currentIndexChanged.connect(self.backup_dir_combobox_changed)
        self.backup_dir_combobox.setToolTip(
                                            '''Current Project Dir:\n[Current project dir]/Auto-Backup'''
                                            '''\n\nNuke Temp Dir:\n/private/var/tmp/nuke-u501/Auto-Backup'''
                                            )

        self.backup_dir_open_button = QPushButton()
        self.backup_dir_open_button.setIcon(self.icon_folder)
        self.backup_dir_open_button.setFixedWidth(QPushButton().sizeHint().height())
        self.backup_dir_open_button.setToolTip('<b>Open</b>')
        self.backup_dir_open_button.clicked.connect(self.open_backup_dir)

        self.backup_dir_display_label = QLabel()
        self.backup_dir_display_label.setStyleSheet("padding-right: 2px; padding-left: 2px")
        self.backup_dir_display_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.backup_dir_display_label.setEnabled(False)

        self.backup_dir_display_lineedit = QLineEdit()
        self.backup_dir_display_lineedit.setAlignment(Qt.AlignRight)
        self.backup_dir_display_lineedit.setReadOnly(True)
        self.backup_dir_display_lineedit.setVisible(False)

        self.backup_dir_choose_button = QPushButton()
        self.backup_dir_choose_button.setIcon(self.icon_folder_gear)
        self.backup_dir_choose_button.setFixedWidth(QPushButton().sizeHint().height())
        self.backup_dir_choose_button.setToolTip('<b>Choose</b>')
        self.backup_dir_choose_button.clicked.connect(self.choose_backup_dir)
        self.backup_dir_choose_button.setVisible(False)

        # grid layout
        grid_layout = QGridLayout()
        self.timer_hBox = QHBoxLayout()
        self.timer_hBox.addWidget(self.timer_spinbox)
        self.timer_hBox.addWidget(self.timer_minutes_label)
        self.timer_hBox.setSpacing(2)
        grid_layout.addWidget(self.timer_label, 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addLayout(self.timer_hBox, 0, 1, Qt.AlignLeft | Qt.AlignVCenter)

        grid_layout.addWidget(self.maximum_files_label, 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(self.maximum_files_spinbox, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)

        self.backup_dir_vBox_1 = QVBoxLayout()
        self.backup_dir_vBox_1.addWidget(self.backup_dir_combobox)
        self.backup_dir_vBox_1.addWidget(self.backup_dir_display_label)
        self.backup_dir_vBox_1.addWidget(self.backup_dir_display_lineedit)
        self.backup_dir_vBox_1.setSpacing(4)
        self.backup_dir_vBox_2 = QVBoxLayout()
        self.backup_dir_vBox_2.addWidget(self.backup_dir_open_button)
        self.backup_dir_vBox_2.addWidget(self.backup_dir_choose_button)
        self.backup_dir_vBox_2.setSpacing(4)
        grid_layout.addWidget(self.backup_dir_label, 2, 0, Qt.AlignRight | Qt.AlignTop)
        grid_layout.addLayout(self.backup_dir_vBox_1, 2, 1, Qt.AlignLeft | Qt.AlignTop)
        grid_layout.addLayout(self.backup_dir_vBox_2, 2, 2, Qt.AlignLeft | Qt.AlignTop)

        grid_layout.setHorizontalSpacing(2)
        grid_layout.setVerticalSpacing(20)

        # set horizontal layout
        hBox_layout_1 = QHBoxLayout()
        hBox_layout_1.addStretch()
        hBox_layout_1.addLayout(grid_layout)
        hBox_layout_1.addStretch()

        # dialog push button
        self.restore_button = QPushButton('Restore defaults')
        self.restore_button.setIcon(self.icon_restore)
        self.restore_button.setIconSize(self.icon_size)
        self.restore_button.clicked.connect(self.restore_default_values)

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.setIcon(self.icon_close)
        self.cancel_button.setIconSize(self.icon_size)
        self.cancel_button.clicked.connect(self.close)

        self.save_button = QPushButton('Save')
        self.save_button.setIcon(self.icon_save)
        self.save_button.setIconSize(self.icon_size)

        # set horizontal layout 2
        hBox_layout_2 = QHBoxLayout()
        hBox_layout_2.addWidget(self.restore_button)
        hBox_layout_2.addStretch()
        hBox_layout_2.addWidget(self.cancel_button)
        hBox_layout_2.addWidget(self.save_button)

        # main layout (vertical layout)
        main_layout = QVBoxLayout()
        main_layout.addSpacing(10)
        main_layout.addWidget(self.timer_display_label, alignment=Qt.AlignHCenter)
        main_layout.addWidget(self.h_line)

        main_layout.addLayout(hBox_layout_1)
        # main_layout.addSpacing(180)
        main_layout.addStretch()
        main_layout.addLayout(hBox_layout_2)

        main_layout.setSpacing(20)

        # set layout
        self.setLayout(main_layout)

        # total size
        self.total_size = main_layout.totalSizeHint()



    # backup dirs list
    def backup_dir_display_text(self):
        cur_project_dir = '[current project dir]/Auto-Backup'
        nuke_temp_dir = f"{nuke.tcl('getenv NUKE_TEMP_DIR')}/Auto-Backup"
        custom_dir = self.backup_dir_display_lineedit.text()

        return [cur_project_dir, nuke_temp_dir, custom_dir]



    # update timer display
    def update_timer_display(self):
        if self.auto_Backup.scheduler.queue:
            next_time = self.auto_Backup.scheduler.queue[0].time
            remaining_time = (datetime.fromtimestamp(next_time) - datetime.now()).total_seconds()
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_display_text = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            self.timer_display_label.setText(timer_display_text)



    # backup_dir_combobox slot
    def backup_dir_combobox_changed(self, index):
        if index != 2:
            self.backup_dir_display_label.setText(self.backup_dir_display_text()[index])
            self.backup_dir_display_label.setVisible(True)
            self.backup_dir_display_lineedit.setVisible(False)
            self.backup_dir_choose_button.setVisible(False)
        else:
            self.backup_dir_display_label.setVisible(False)
            self.backup_dir_display_lineedit.setVisible(True)
            self.backup_dir_choose_button.setVisible(True)



    # open backup dir
    def open_backup_dir(self):
        index = self.backup_dir_combobox.currentIndex()

        if index == 0 or index == 1:
            backup_dir = self.auto_Backup.backup_dirs()[index]

        else:
            backup_dir =self.backup_dir_display_text()[index]

        if backup_dir and not Path(backup_dir).is_dir():
            Path(backup_dir).mkdir(parents=True, exist_ok=True)

        if backup_dir:
            nukescripts.start(backup_dir)



    # choose a backup directory
    def choose_backup_dir(self):
        custom_dir = nuke.getFilename('Choose a backup directory')

        if custom_dir:
            if Path(custom_dir).is_dir():
                self.backup_dir_display_lineedit.setText(custom_dir)
            elif Path(custom_dir).is_file():
                nuke.message('Please choose a <span style="color: rgb(255, 69, 58)">directory</span>.')



    # keyboard press
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()



    # set user settings
    def set_user_values(self):
        user = self.auto_Backup.backup_user()

        self.timer_spinbox.setValue(user['timer'])
        self.maximum_files_spinbox.setValue(user['maximum_files'])

        index = user['backup_dir_index']
        self.backup_dir_combobox.setCurrentIndex(index)

        if index == 0 or index == 1:
            self.backup_dir_display_label.setText(self.backup_dir_display_text()[index])

        self.backup_dir_display_lineedit.setText(user['custom_dir'])



    # restore default settings
    def restore_default_values(self):
        default = self.auto_Backup.backup_default()

        self.timer_spinbox.setValue(default['timer'])
        self.maximum_files_spinbox.setValue(default['maximum_files'])
        self.backup_dir_combobox.setCurrentIndex(0)
        self.backup_dir_display_lineedit.setText('')



    # set window
    def set_window(self):
        # size, position, title and pin
        self.setMinimumSize(self.total_size * 1.3)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width()/2 - self.width()/2, 0)

        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowTitle('Auto Backup')



    # test
    def resizeEvent(self, event):
        print(self.total_size)
        


# app = QApplication(sys.argv)
autoBackup = AutoBackup_UI()
autoBackup.auto_Backup.start_timer()
autoBackup.start_ui()
# sys.exit(app.exec())