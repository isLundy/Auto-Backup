try:
    from PySide6.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton, QComboBox,
        QLineEdit, QStyle, QFrame, QToolTip, QFileDialog, QCheckBox, QGraphicsDropShadowEffect,
        QStackedWidget)
    from PySide6.QtGui import QIcon, QPainter, QColor, QBrush
    from PySide6.QtCore import (Qt, QSize, QTimer, QTime, Slot, Property, QEasingCurve, QPropertyAnimation,
        QPointF, QRectF, QParallelAnimationGroup)
except:
    from PySide2.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton, QComboBox,
        QLineEdit, QStyle, QFrame, QToolTip, QFileDialog, QCheckBox, QGraphicsDropShadowEffect,
        QStackedWidget)
    from PySide2.QtGui import QIcon, QPainter, QColor, QBrush
    from PySide2.QtCore import (Qt, QSize, QTimer, QTime, Slot, Property, QEasingCurve, QPropertyAnimation,
        QPointF, QRectF, QParallelAnimationGroup)

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
import math


class AutoBackup:
    def __init__(self):
        # settings json file
        # self.settings_json = Path(__file__).absolute().parent.joinpath('settings.json').as_posix()
        self.settings_json = '/Users/lundy/HuStudio/Work/Github/autoBackup/settings.json'
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.threading_actived = False
        self.last_block_time = None


    # create threading
    def start_threading(self):
        # create threading
        if self.user_settings()['enabled']:
            self.add_sched()
            self.sched_threading = threading.Thread(target=self.scheduler.run)
            self.sched_threading.daemon = True
            self.sched_threading.start()
            self.threading_actived = True


    def interval_time(self):
        interval = self.user_settings()['timer']

        return interval


    # add scheduler
    def add_sched(self, interval=None):
        if not interval:
            interval = self.interval_time()

        self.scheduler.enter(interval, 1, self.copy_and_sched)
        self.next_time = self.scheduler.queue[0].time


    # default value
    def default_settings(self):
        settings = {
                    'display': '',
                    'enabled': True,
                    'timer': 20,
                    'maximum_files': 20,
                    'backup_dir_index': 0,
                    'custom_dir': ''
                    }

        return settings


    # user settings
    def user_settings(self):
        with open(self.settings_json) as st:
            settings = json.load(st)

        return settings


    # backup directories
    def backup_dirs(self):
        if Path(nuke.root().name()).absolute().is_file():
            cur_project_dir = Path(nuke.root().name()).absolute().parent.joinpath('Auto-Backup').as_posix()
        else:
            cur_project_dir = ''
        nuke_temp_dir = Path(nuke.tcl('getenv NUKE_TEMP_DIR')).absolute().joinpath('Auto-Backup').as_posix()
        custom_dir = self.user_settings()['custom_dir']

        return [cur_project_dir, nuke_temp_dir, custom_dir]


    # copy and sched
    def copy_and_sched(self):
        self.copy_to_backup_dir()
        self.add_sched()


    # copy
    def copy_to_backup_dir(self):
        print('----copy_to_backup_dir----')
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
            backup_dir = self.backup_dirs()[self.user_settings()['backup_dir_index']]

            if backup_dir:
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
                    while len(files) > self.user_settings()['maximum_files']:
                        files.pop(0).unlink()



class ToggleSwitchButton(QCheckBox):
    def __init__(self, start_state=False):
        super().__init__()

        # window size
        self.box_width = 120
        self.box_height = self.box_width / 2
        self.resize(self.box_width, self.box_height)

        # bg color
        self.off_color = QColor(142, 142, 142)
        self.on_color = QColor(255, 149, 0)

        # circle
        self.circle_color = QColor(242, 242, 242)
        self.radius_factor = 0.8

        # animation property
        self.anim_curve = QEasingCurve.OutBounce
        self.anim_duration = 300

        # circle animation
        self._pos_factor = 0
        self.anim_1 = QPropertyAnimation(self, b"pos_factor", self)
        self.anim_1.setEasingCurve(self.anim_curve)
        self.anim_1.setDuration(self.anim_duration)

        # bg color animation
        self._bg_color = self.off_color
        self.anim_2 = QPropertyAnimation(self, b"bg_color", self)
        self.anim_2.setEasingCurve(self.anim_curve)
        self.anim_2.setDuration(self.anim_duration)

        # animation group
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.anim_1)
        self.anim_group.addAnimation(self.anim_2)

        # emit a signal
        self.clicked.connect(self.start_anim)

        # first start
        if start_state:
            self._pos_factor = 1
            self._bg_color = self.on_color


    @Property(float)
    def pos_factor(self):
        return self._pos_factor


    @pos_factor.setter
    def pos_factor(self, value):
        self._pos_factor = value
        self.update()


    @Property(QColor)
    def bg_color(self):
        return self._bg_color


    @bg_color.setter
    def bg_color(self, color):
        self._bg_color = color
        self.update()


    # mouse area
    def hitButton(self, pos):
        return self.contentsRect().contains(pos)


    # start animation
    def start_anim(self, state):
        # stop animation
        self.anim_group.stop()

        if state:
            self.anim_1.setEndValue(1)
            self.anim_2.setEndValue(self.on_color)
        else:
            self.anim_1.setEndValue(0)
            self.anim_2.setEndValue(self.off_color)

        # start animation
        self.anim_group.start()


    # paint
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        # roundeedRect
        rect = QRectF(0, 0 , self.width(), self.height())
        corner = min(self.height() / 2, self.width() / 2)

        # circle radius
        radius = min(self.height(), self.width()) / 2 * self.radius_factor

        # circle cneter x
        lengths = max(self.width() - self.height(), 0)
        circle_center_x = min(self.height() / 2, self.width() / 2) + lengths * self._pos_factor

        # circle center
        circle_center = QPointF(circle_center_x, self.height() / 2)

        # paint bg
        p.setBrush(self._bg_color)
        p.drawRoundedRect(rect, corner, corner)

        # paint circle
        p.setBrush(self.circle_color)
        p.drawEllipse(circle_center, radius, radius)

        # end paint
        p.end()


class AutoBackup_UI(QWidget):
    def __init__(self):
        super().__init__()
        self.task = autoBackup

        # init ui
        self.set_ui()
        self.set_window()


    # show ui
    def show_ui(self):
        self.create_timer_obj()
        self.set_all_values()
        self.show()
        self.set_focus()


    # start QTimer
    def create_timer_obj(self):
        # timer obj
        self.timer_obj = QTimer()
        self.timer_obj.timeout.connect(self.update_timer_display)
        self.timer_obj.setInterval(1000)


    # set ui
    def set_ui(self):
        # definition icon
        # icon_path = Path(__file__).absolute().parent.joinpath('icon').as_posix()
        icon_path = '/Users/lundy/HuStudio/Work/Github/autoBackup/icon'
        self.icon_settings = QIcon(f'{icon_path}/autoBackup_gear.svg')
        self.icon_advance = QIcon(f'{icon_path}/autoBackup_advance.svg')

        self.icon_folder = QIcon(f'{icon_path}/autoBackup_folder.svg')
        self.icon_folder_gear = QIcon(f'{icon_path}/autoBackup_folder_gear.svg')
        self.icon_restore = QIcon(f'{icon_path}/autoBackup_restore.svg')
        self.icon_cancel = QIcon(f'{icon_path}/autoBackup_cancel.svg')
        self.icon_save = QIcon(f'{icon_path}/autoBackup_save.svg')

        self.icon_immediately = QIcon(f'{icon_path}/autoBackup_immediately.svg')
        self.icon_delete = QIcon(f'{icon_path}/autoBackup_delete.svg')

        self.icon_exit = QIcon(f'{icon_path}/autoBackup_exit.svg')
        self.icon_size = QSize(14, 14)

         # timer display
        self.timer_display_label = QLabel()
        nuke_font_size = int(nuke.toNode('preferences')['UIFontSize'].getValue())
        self.timer_display_label.setStyleSheet(f"font-size: {nuke_font_size * 2}px")

        # ToggleSwitchButton
        self.toggle_switch = ToggleSwitchButton(self.task.user_settings()['enabled'])
        switch_width = 50
        self.toggle_switch.setFixedSize(switch_width, switch_width / 2)
        self.toggle_switch.clicked.connect(self.toggle_switch_changed)

        # divider
        self.h_line = QFrame()
        self.h_line.setFrameShape(QFrame.HLine)

        # setttings button
        self.settings_button = QPushButton(' Settings')
        self.settings_button.setIcon(self.icon_settings)
        self.settings_button.setCheckable(True)
        self.settings_button.clicked.connect(self.hide_or_show_widgets)

        # advance button
        self.advance_button = QPushButton(' Advance')
        self.advance_button.setIcon(self.icon_advance)
        self.advance_button.setCheckable(True)
        self.advance_button.clicked.connect(self.hide_or_show_widgets)

        # option layout
        option_hBox = QHBoxLayout()
        option_hBox.addStretch()
        option_hBox.addWidget(self.settings_button)
        option_hBox.addWidget(self.advance_button)
        option_hBox.addStretch()

        # general layout
        general_vBox = QVBoxLayout()
        general_vBox.addWidget(self.timer_display_label, alignment=Qt.AlignHCenter)
        general_vBox.addWidget(self.toggle_switch, alignment=Qt.AlignHCenter)
        general_vBox.addWidget(self.h_line)
        general_vBox.addLayout(option_hBox)
        general_vBox.setSpacing(20)

        # timer
        self.timer_label = QLabel('Timer:')

        self.timer_spinbox = QSpinBox()
        self.timer_spinbox.setFixedSize(48, 24)
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
        self.maximum_files_spinbox.setFixedSize(48, 24)
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
                                            f'''\n\nNuke Temp Dir:\n{nuke.tcl('getenv NUKE_TEMP_DIR')}'''
                                            )

        # open backup dir
        self.backup_dir_open_button = QPushButton()
        self.backup_dir_open_button.setIcon(self.icon_folder)
        self.backup_dir_open_button.setFixedWidth(QPushButton().sizeHint().height())
        self.backup_dir_open_button.setToolTip('<b>Open</b>')
        self.backup_dir_open_button.clicked.connect(self.open_backup_dir)

        self.backup_dir_display_lineedit = QLineEdit()
        self.backup_dir_display_lineedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.backup_dir_display_lineedit.setAlignment(Qt.AlignRight)
        self.backup_dir_display_lineedit.setReadOnly(True)
        self.backup_dir_display_lineedit.setVisible(False)
        self.backup_dir_display_lineedit.setStyleSheet("""
                                                        .QLineEdit[readOnly="true"] {
                                                            color: rgb(142, 142, 142)
                                                        }
                                                        """)

        # choose backup dir
        self.backup_dir_choose_button = QPushButton()
        self.backup_dir_choose_button.setIcon(self.icon_folder_gear)
        self.backup_dir_choose_button.setFixedWidth(QPushButton().sizeHint().height())
        self.backup_dir_choose_button.setToolTip('<b>Choose</b>')
        self.backup_dir_choose_button.clicked.connect(self.choose_backup_dir)
        self.backup_dir_choose_button.setVisible(False)

        # dialog pushbutton
        self.restore_button = QPushButton(' Restore defaults')
        self.restore_button.setIcon(self.icon_restore)
        self.restore_button.setIconSize(self.icon_size)
        self.restore_button.clicked.connect(self.restore_default_values)

        self.cancel_button = QPushButton(' Cancel')
        self.cancel_button.setIcon(self.icon_cancel)
        self.cancel_button.setIconSize(self.icon_size)
        self.cancel_button.clicked.connect(self.cancel_changed)

        self.save_button = QPushButton(' Save')
        self.save_button.setIcon(self.icon_save)
        self.save_button.setIconSize(self.icon_size)
        self.save_button.clicked.connect(self.save_user_values)

        # grid layout
        grid_layout = QGridLayout()

        timer_hBox = QHBoxLayout()
        timer_hBox.addWidget(self.timer_spinbox)
        timer_hBox.addWidget(self.timer_minutes_label)
        timer_hBox.setSpacing(2)
        grid_layout.addWidget(self.timer_label, 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addLayout(timer_hBox, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)

        grid_layout.addWidget(self.maximum_files_label, 2, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(self.maximum_files_spinbox, 2, 1, Qt.AlignLeft | Qt.AlignVCenter)

        backup_dir_vBox_1 = QVBoxLayout()
        backup_dir_vBox_1.addWidget(self.backup_dir_combobox)
        backup_dir_vBox_1.addWidget(self.backup_dir_display_lineedit)
        backup_dir_vBox_1.setSpacing(8)
        backup_dir_vBox_2 = QVBoxLayout()
        backup_dir_vBox_2.addWidget(self.backup_dir_open_button)
        backup_dir_vBox_2.addWidget(self.backup_dir_choose_button)
        backup_dir_vBox_2.setSpacing(4)
        grid_layout.addWidget(self.backup_dir_label, 3, 0, Qt.AlignRight | Qt.AlignTop)
        grid_layout.addLayout(backup_dir_vBox_1, 3, 1, Qt.AlignLeft | Qt.AlignTop)
        grid_layout.addLayout(backup_dir_vBox_2, 3, 2, Qt.AlignLeft | Qt.AlignTop)

        grid_layout.setHorizontalSpacing(2)
        grid_layout.setVerticalSpacing(20)

        # set horizontal layout
        settings_hBox_1 = QHBoxLayout()
        settings_hBox_1.addStretch()
        settings_hBox_1.addLayout(grid_layout)
        settings_hBox_1.addStretch()

        # set horizontal layout 2
        settings_hBox_2 = QHBoxLayout()
        settings_hBox_2.addWidget(self.restore_button)
        settings_hBox_2.addStretch()
        settings_hBox_2.addWidget(self.cancel_button)
        settings_hBox_2.addWidget(self.save_button)

        # setttings layout
        setttings_vBox = QVBoxLayout()
        setttings_vBox.addSpacing(5)
        setttings_vBox.addLayout(settings_hBox_1)
        setttings_vBox.addSpacing(40)
        setttings_vBox.addStretch()
        setttings_vBox.addLayout(settings_hBox_2)
        setttings_vBox.addSpacing(5)

        self.settings_widgets = QWidget()
        self.settings_widgets.setLayout(setttings_vBox)

        # immediately button
        self.immediately_button = QPushButton(' Immediately backup once')
        self.immediately_button.setIcon(self.icon_immediately)
        self.immediately_button.setFixedWidth(200)

        # clear button
        self.delete_button = QPushButton(' Delete backup files')
        self.delete_button.setIcon(self.icon_delete)
        self.delete_button.setFixedWidth(200)

        # advance layout
        advance_vBox = QVBoxLayout()
        advance_vBox.addSpacing(5)
        advance_vBox.addWidget(self.immediately_button, alignment=Qt.AlignHCenter)
        advance_vBox.addWidget(self.delete_button, alignment=Qt.AlignHCenter)
        advance_vBox.addSpacing(5)
        advance_vBox.setSpacing(20)

        self.advance_widgets = QWidget()
        self.advance_widgets.setLayout(advance_vBox)

        # stacked
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.settings_widgets)
        self.stacked_widget.addWidget(self.advance_widgets)

        # stacked shadow
        # stacked style sheet
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(60)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 32))
        self.stacked_widget.setGraphicsEffect(shadow)
        self.stacked_widget.setStyleSheet("""
                                            .QStackedWidget {
                                                border-width: 1px;
                                                border-style: solid;
                                                border-radius: 12px;
                                                border-color: rgb(56, 56, 56);
                                                background-color: rgb(56, 56, 56);
                                            }
                                            """)

        # divider 2
        self.h_line_2 = QFrame()
        self.h_line_2.setFrameShape(QFrame.HLine)

        # exit button
        self.exit_button = QPushButton(' Exit')
        self.exit_button.setIcon(self.icon_exit)
        self.exit_button.clicked.connect(self.close)

        # exit layout
        exit_vBox = QVBoxLayout()
        exit_vBox.addWidget(self.h_line_2)
        exit_vBox.addWidget(self.exit_button, alignment=Qt.AlignRight)
        exit_vBox.setSpacing(20)

        # main layout (vertical layout)
        self.main_layout = QVBoxLayout()
        self.main_layout.addSpacing(10)
        self.main_layout.addLayout(general_vBox)
        self.main_layout.addWidget(self.stacked_widget)
        self.main_layout.addStretch()
        self.main_layout.addLayout(exit_vBox)
        self.main_layout.addSpacing(5)
        self.main_layout.setSpacing(20)
        self.main_layout.setStretchFactor(self.stacked_widget, 1)

        # set layout and style sheets
        self.setLayout(self.main_layout)
        self.setStyleSheet("""
                            .QFrame {
                                color: rgba(255, 255, 255, 50)
                            }

                            .QPushButton:checked {
                                border-width: 1px;
                                border-style: solid;
                                border-radius: 6px;
                                border-color: rgb(255, 149, 0);
                                background-color: rgba(255, 149, 0, 32);
                                color: rgba(255, 255, 255, 230);
                            }
                            """)

        # minimum width
        self.minimum_width = self.main_layout.totalSizeHint().width() * 1.3

        # hide widgets
        self.stacked_widget.setVisible(False)
        
        # minimum height
        # self.minimum_height = self.main_layout.totalSizeHint().height()


    # create QTime()
    def create_time_obj(self):
        remaining = math.ceil(self.task.next_time - time.time())
        if remaining > 0:
            hours, remainder = divmod(remaining, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.remaining_time = QTime(int(hours), int(minutes), int(seconds))


    # update timer display
    @Slot()
    def update_timer_display(self):
        if self.remaining_time != QTime(0, 0, 0, 0):
            self.remaining_time = self.remaining_time.addSecs(-1)
            self.timer_display_label.setText(self.remaining_time.toString("h:mm:ss"))
            # print(self.remaining_time.toString("h:mm:ss"))
        else:
            self.create_time_obj()
            self.timer_display_label.setText(self.remaining_time.toString("h:mm:ss"))
            # print(self.remaining_time)


        print('-'*100)
        print('checked:', self.toggle_switch.isChecked())
        for thread in threading.enumerate():
            print(thread)
        print(threading.active_count(), self.task.sched_threading.is_alive())
        # print(self.task.sched_threading)


    # record block time and cancel old event
    def recorde_and_cancel(self):
        queue = self.task.scheduler.queue
        if queue:
            self.task.last_block_time = self.task.scheduler.queue[0].time

        for event in self.task.scheduler.queue:
                self.task.scheduler.cancel(event)


    # check state of threading ans last block time of sched
    def check_threading_and_sched(self):
        if (self.task.threading_actived
            and self.task.sched_threading.is_alive()
            and self.task.last_block_time
            and 0 < self.task.last_block_time - time.time() < self.task.interval_time()):

            self.task.add_sched()
            print(1)
        else:
            self.task.start_threading()
            print(2)


    # timer and timer display and timer start
    def time_display_and_start(self):
        self.create_time_obj()
        self.timer_display_label.setText(self.remaining_time.toString("h:mm:ss"))
        self.timer_obj.start()


    # enable or disable
    @Slot()
    def toggle_switch_changed(self, state):
        self.timer_display_label.setEnabled(state)

        # write to settings json
        if state:
            timer_display = ''
        else:
            self.timer_obj.stop()
            timer_display = self.timer_display_label.text()

        settings = self.task.user_settings()
        settings['display'] = timer_display
        settings['enabled'] = state
        with open(self.task.settings_json, 'w+') as st:
            json.dump(settings, st, indent=4)

        # check sched and threading
        if state:
            self.check_threading_and_sched()
            self.time_display_and_start()
        else:
            # record block time and cancel old event
            self.recorde_and_cancel()

    # hide or show, resize windows
    @Slot()
    def hide_or_show_widgets(self, state):
        self.stacked_widget.setVisible(state)

        if self.sender() == self.settings_button:
            if self.stacked_widget.isVisible():
                self.stacked_widget.setCurrentIndex(0)

            if self.advance_button.isChecked():
                self.advance_button.setChecked(False)

        elif self.sender() == self.advance_button:
            if self.stacked_widget.isVisible():
                self.stacked_widget.setCurrentIndex(1)

            if self.settings_button.isChecked():
                self.settings_button.setChecked(False)

        QTimer.singleShot(0, self.resize_window)


    # backup_dir_combobox slot
    @Slot()
    def backup_dir_combobox_changed(self, index):
        if index == 2:
            self.backup_dir_display_lineedit.setVisible(True)
            self.backup_dir_choose_button.setVisible(True)
        else:
            self.backup_dir_display_lineedit.setVisible(False)
            self.backup_dir_choose_button.setVisible(False)

        QTimer.singleShot(0, self.resize_window)


    # open backup dir
    @Slot()
    def open_backup_dir(self):
        index = self.backup_dir_combobox.currentIndex()

        if index == 0 or index == 1:
            backup_dir = self.task.backup_dirs()[index]
        else:
            backup_dir = self.backup_dir_display_lineedit.text()

        if backup_dir and not Path(backup_dir).is_dir():
            Path(backup_dir).mkdir(parents=True, exist_ok=True)

        if backup_dir:
            nukescripts.start(backup_dir)


    # choose a backup directory
    @Slot()
    def choose_backup_dir(self):
        custom_dir = nuke.getFilename('Choose a backup directory', '*/')

        if custom_dir:
            if Path(custom_dir).is_dir():
                self.backup_dir_display_lineedit.setText(custom_dir)
            elif Path(custom_dir).is_file():
                nuke.message('Please choose a <span style="color: rgb(255, 69, 58)">directory</span>.')


    # restore default settings
    @Slot()
    def restore_default_values(self):
        default = self.task.default_settings()

        self.timer_spinbox.setValue(default['timer'])
        self.maximum_files_spinbox.setValue(default['maximum_files'])
        self.backup_dir_combobox.setCurrentIndex(0)
        self.backup_dir_display_lineedit.setText('')


    # cancel and restore to user settings
    @Slot()
    def cancel_changed(self):
        # hide widgets
        self.settings_button.setChecked(False)
        self.stacked_widget.setVisible(False)
        QTimer.singleShot(0, self.resize_window)

        # restore to user settings
        self.set_settings_values()


    # save user settings
    @Slot()
    def save_user_values(self):
        state = self.toggle_switch.isChecked()
        if state:
            timer_display = ''
        else:
            timer_display = self.timer_display_label.text()

        settings = {
                    'display': timer_display,
                    'enabled': state,
                    'timer': self.timer_spinbox.value(),
                    'maximum_files': self.maximum_files_spinbox.value(),
                    'backup_dir_index': self.backup_dir_combobox.currentIndex(),
                    'custom_dir': self.backup_dir_display_lineedit.text()
                    }

        # write to file
        with open(self.task.settings_json, 'w+') as st:
            json.dump(settings, st, indent=4)

        # record block time and cancel old event
        self.recorde_and_cancel()

        # create new event
        if state:
            self.check_threading_and_sched()
            self.time_display_and_start()

        # hide settings
        self.settings_button.setChecked(False)
        self.stacked_widget.setVisible(False)
        QTimer.singleShot(0, self.resize_window)


    # set window
    def set_window(self):
        # size, position, title and pin
        self.setMinimumWidth(494)
        self.adjustSize()

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width()/2 - self.width()/2, 0)

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle('Auto Backup')


    # update window size
    def resize_window(self):
        self.resize(self.width(), self.main_layout.totalMinimumSize().height())


    # only settings values, exclude toogle switch
    def set_settings_values(self):
        user = self.task.user_settings()

        # user setttings
        self.timer_spinbox.setValue(user['timer'])
        self.maximum_files_spinbox.setValue(user['maximum_files'])
        self.backup_dir_combobox.setCurrentIndex(user['backup_dir_index'])
        self.backup_dir_display_lineedit.setText(user['custom_dir'])


    # set user settings
    def set_all_values(self):
        user = self.task.user_settings()

        if user['enabled']:
            self.toggle_switch.setChecked(True)
            self.time_display_and_start()
        else:
            self.timer_display_label.setText(user['display'])
            self.timer_display_label.setEnabled(False)

        self.set_settings_values()


    # set focus
    def set_focus(self):
        for button in self.findChildren(QPushButton):
            button.setFocusPolicy(Qt.TabFocus)

        self.setFocus()


    # stop timer display
    def closeEvent(self, event):
        self.timer_obj.stop()
        super().closeEvent(event)


    # keyboard press
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

        super().keyPressEvent(event)


    def resizeEvent(self, event):
        pass


# ui instance
autoBackup_ui_instance = None

def show():
    global autoBackup_ui_instance
    autoBackup_ui_instance = AutoBackup_UI()
    autoBackup_ui_instance.show_ui()

# sched instance
autoBackup = AutoBackup()
autoBackup.start_threading()
show()
