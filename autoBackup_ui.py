try:
    from PySide6.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton, QComboBox,
        QLineEdit, QStyle)
    from PySide6.QtGui import QCursor, QIcon
    from PySide6.QtCore import Qt, QSize
except:
    from PySide2.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton, QComboBox,
        QLineEdit, QStyle)
    from PySide2.QtGui import QCursor, QIcon
    from PySide2.QtCore import Qt, QSize
import sys

class AutoBackup(QWidget):

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
        self.timer_label = QLabel('Timer: ')

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
        self.maximum_files_label = QLabel('Maximum files: ')

        self.maximum_files_box = QSpinBox()
        self.maximum_files_box.setFixedWidth(48)
        self.maximum_files_box.setRange(1, 100)
        self.maximum_files_box.setValue(20)
        self.maximum_files_box.setToolTip(
                                    '''Minimum: 1'''
                                    '''\nMaximum: 100''')

        # backup path
        self.backup_path_label = QLabel('Backup path: ')

        self.backup_path_combobox = QComboBox()
        self.backup_path_combobox.addItems(['Project Dir', 'Nuke Temp Dir', 'Custom'])
        self.backup_path_combobox.currentIndexChanged.connect(self.backup_path_combobox_Changed)

        self.backup_path_open_button = QPushButton()
        self.backup_path_open_button.setIcon(self.icon_folder)
        self.backup_path_open_button.setFixedWidth(QPushButton().sizeHint().height())

        self.backup_path_dir_label = QLabel()
        self.backup_path_dir_label.setDisabled(True)
        self.backup_path_dir_label.setText('0')

        self.backup_path_choose_button = QPushButton()
        self.backup_path_choose_button.setIcon(self.icon_folder_gear)
        self.backup_path_choose_button.setFixedWidth(QPushButton().sizeHint().height())
        self.backup_path_choose_button.setVisible(False)

        # grid layout
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.timer_label, 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.timer_hBox = QHBoxLayout()
        self.timer_hBox.addWidget(self.timer_spinbox)
        self.timer_hBox.addWidget(self.timer_minutes_label)
        self.timer_hBox.setSpacing(2)
        grid_layout.addLayout(self.timer_hBox, 0, 1, Qt.AlignLeft | Qt.AlignVCenter)

        grid_layout.addWidget(self.maximum_files_label, 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(self.maximum_files_box, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)

        grid_layout.addWidget(self.backup_path_label, 2, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(self.backup_path_combobox, 2, 1)
        grid_layout.addWidget(self.backup_path_open_button, 2, 2, Qt.AlignLeft | Qt.AlignVCenter)

        grid_layout.addWidget(self.backup_path_dir_label, 3, 1, Qt.AlignCenter)
        grid_layout.addWidget(self.backup_path_choose_button, 3, 2, Qt.AlignLeft | Qt.AlignVCenter)

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
        # main_layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        # set layout
        self.setLayout(main_layout)

        # total size
        self.total_size = main_layout.totalSizeHint()
        print(self.total_size)



    def set_window(self):
        # size, position, title and pin
        self.resize(self.total_size)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width()/2 - self.width()/2, 0)

        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowTitle('Auto Backup')

    def backup_path_combobox_Changed(self, index):
        self.backup_path_dir_label.setText(str(index))
        if index == 2:
            self.backup_path_choose_button.setVisible(True)
        else:
            self.backup_path_choose_button.setVisible(False)



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()       
        

app = QApplication(sys.argv)
test = AutoBackup()
test.show()
sys.exit(app.exec())
