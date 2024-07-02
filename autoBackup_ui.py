try:
    from PySide6.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton, QComboBox,
        QLineEdit, QStyle, QFrame, QToolTip, QFileDialog)
    from PySide6.QtGui import QCursor, QIcon
    from PySide6.QtCore import Qt, QSize
except:
    from PySide2.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton, QComboBox,
        QLineEdit, QStyle, QFrame, QToolTip, QFileDialog)
    from PySide2.QtGui import QCursor, QIcon
    from PySide2.QtCore import Qt, QSize

from pathlib import Path
# import nuke
# import nukescripts
import sys

class AutoBackup_UI(QWidget):

    def __init__(self):
        super().__init__()

        # definition icon
        self.icon_folder = QIcon('icon_folder.svg')
        self.icon_folder_gear = QIcon('icon_folder_gear.svg')
        self.icon_restore = QIcon('icon_restore.svg')
        self.icon_close = QIcon('icon_close.svg')
        self.icon_save = QIcon('icon_save.svg')
        self.icon_size = QSize(14, 14)

        # start ui
        self.set_ui()
        self.set_window()
        self.setFocus()

    def set_ui(self):

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

        self.maximum_files_box = QSpinBox()
        self.maximum_files_box.setFixedWidth(48)
        self.maximum_files_box.setRange(1, 100)
        self.maximum_files_box.setValue(20)
        self.maximum_files_box.setToolTip(
                                    '''Minimum: 1'''
                                    '''\nMaximum: 100''')

        # backup path
        self.backup_path_label = QLabel('Backup Directory:')
        self.backup_path_label.setFixedHeight(QComboBox().sizeHint().height()*0.9)

        self.backup_path_combobox = QComboBox()
        self.backup_path_combobox.addItems(['Current Project Dir', 'Nuke Temp Dir', 'Custom'])
        self.backup_path_combobox.setToolTip(
                                            '''Current Project Dir:\n[Current project dir]/Auto-Backup'''
                                            '''\n\nNuke Temp Dir:\n/private/var/tmp/nuke-u501/Auto-Backup'''
                                            )
        self.backup_path_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.backup_path_combobox.currentIndexChanged.connect(self.backup_path_combobox_Changed)

        self.backup_path_open_button = QPushButton()
        self.backup_path_open_button.setIcon(self.icon_folder)
        self.backup_path_open_button.setFixedWidth(QPushButton().sizeHint().height())
        self.backup_path_open_button.setToolTip('Open')
        self.backup_path_open_button.clicked.connect(self.open_backup_dir)

        self.backup_path_dir_label = QLabel()
        self.backup_path_dir_label.setStyleSheet("padding-right: 2px; padding-left: 2px")
        self.backup_path_dir_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.backup_path_dir_label.setDisabled(True)

        self.backup_path_dir_lineedit = QLineEdit()
        self.backup_path_dir_lineedit.setAlignment(Qt.AlignRight)
        self.backup_path_dir_lineedit.setReadOnly(True)
        self.backup_path_dir_lineedit.setVisible(False)

        self.backup_path_choose_button = QPushButton()
        self.backup_path_choose_button.setIcon(self.icon_folder_gear)
        self.backup_path_choose_button.setFixedWidth(QPushButton().sizeHint().height())
        self.backup_path_choose_button.setToolTip('Choose')
        self.backup_path_choose_button.clicked.connect(self.choose_backup_dir)
        self.backup_path_choose_button.setVisible(False)

        # grid layout
        grid_layout = QGridLayout()
        self.timer_hBox = QHBoxLayout()
        self.timer_hBox.addWidget(self.timer_spinbox)
        self.timer_hBox.addWidget(self.timer_minutes_label)
        self.timer_hBox.setSpacing(2)
        grid_layout.addWidget(self.timer_label, 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addLayout(self.timer_hBox, 0, 1, Qt.AlignLeft | Qt.AlignVCenter)

        grid_layout.addWidget(self.maximum_files_label, 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(self.maximum_files_box, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)

        self.backup_path_vBox_1 = QVBoxLayout()
        self.backup_path_vBox_1.addWidget(self.backup_path_combobox)
        self.backup_path_vBox_1.addWidget(self.backup_path_dir_label)
        self.backup_path_vBox_1.addWidget(self.backup_path_dir_lineedit)
        self.backup_path_vBox_1.setSpacing(4)
        self.backup_path_vBox_2 = QVBoxLayout()
        self.backup_path_vBox_2.addWidget(self.backup_path_open_button)
        self.backup_path_vBox_2.addWidget(self.backup_path_choose_button)
        self.backup_path_vBox_2.setSpacing(4)
        grid_layout.addWidget(self.backup_path_label, 2, 0, Qt.AlignRight | Qt.AlignTop)
        grid_layout.addLayout(self.backup_path_vBox_1, 2, 1, Qt.AlignLeft | Qt.AlignTop)
        grid_layout.addLayout(self.backup_path_vBox_2, 2, 2, Qt.AlignLeft | Qt.AlignTop)

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
        main_layout.addLayout(hBox_layout_1)
        main_layout.addSpacing(40)
        main_layout.addStretch()
        main_layout.addLayout(hBox_layout_2)

        # set layout
        self.setLayout(main_layout)

        # total size
        self.total_size = main_layout.totalSizeHint()



    def set_window(self):
        # size, position, title and pin
        self.resize(self.total_size)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width()/2 - self.width()/2, 0)

        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowTitle('Auto Backup')

    def backup_path_dir_text(self):
        cur_project_dir = Path(nuke.root().name()).absolute().parent.joinpath('Auto-Backup').as_posix()
        nuke_temp_dir = Path(nuke.tcl('getenv NUKE_TEMP_DIR')).absolute().joinpath('Auto-Backup').as_posix()
        custom_dir = self.backup_path_dir_lineedit.text()

        return [cur_project_dir, nuke_temp_dir, custom_dir]


    def backup_path_combobox_Changed(self, index):
        if index != 2:
            self.backup_path_dir_label.setText(self.backup_path_dir_text()[index])
            self.backup_path_dir_label.setVisible(True)
            self.backup_path_dir_lineedit.setVisible(False)
            self.backup_path_choose_button.setVisible(False)
        else:
            self.backup_path_dir_label.setVisible(False)
            self.backup_path_dir_lineedit.setVisible(True)
            self.backup_path_choose_button.setVisible(True)

        # self.backup_path_dir_label.setText(self.backup_path_dir_text()[index])


    def open_backup_dir(self):
        backup_dir = self.backup_path_dir_text()[self.backup_path_combobox.currentIndex()]

        if not Path(backup_dir).is_dir():
            Path(backup_dir).mkdir(parents=True, exist_ok=True)

        nukescripts.start(backup_dir)



    def choose_backup_dir(self):
        custom_dir = nuke.getFilename('Choose a backup directory')

        if custom_dir:
            if Path(custom_dir).is_dir():
                self.backup_path_dir_lineedit.setText(custom_dir)
            elif Path(custom_dir).is_file():
                nuke.message('Please choose a <span style="color: rgb(255, 69, 58)">directory</span>.')



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


    def resizeEvent(self, event):
        print(self.size())

        

# app = QApplication(sys.argv)
test = AutoBackup_UI()
test.show()
# sys.exit(app.exec())