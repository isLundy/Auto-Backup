try:
    from PySide6.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton)
    from PySide6.QtGui import QCursor
    from PySide6.QtCore import Qt, QSize
except:
    from PySide2.QtWidgets import (QWidget, QApplication, QLabel, QGridLayout, QSpinBox,
        QSizePolicy, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton)
    from PySide2.QtGui import QCursor
    from PySide2.QtCore import Qt, QSize
import sys

class AutoBackup(QWidget):
    def __init__(self):
        super().__init__()

        self.set_ui()
        self.set_window()
        self.setFocus()

    def set_ui(self):
        grid_layout = QGridLayout()

        # timer
        self.timer_label = QLabel('Timer: ')

        self.timer_box = QSpinBox()
        self.timer_box.setFixedWidth(50)
        self.timer_box.setValue(20)
        self.timer_box.setRange(1, 480)
        self.timer_box.setToolTip(
                                '''Minimum: 1'''
                                '''\nMaximum: 480'''
                                '''\n\n(480=60*8 Hope you never work overtime~)'''
                                )

        self.timer_minutes_label = QLabel('minutes')

        grid_layout.addWidget(self.timer_label, 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(self.timer_box, 0, 1, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(self.timer_minutes_label, 0, 2, Qt.AlignLeft | Qt.AlignVCenter)

        # maximum files
        self.maximum_files_label = QLabel('Maximum files: ')
        self.maximum_files_box = QSpinBox()
        self.maximum_files_box.setFixedWidth(50)
        self.maximum_files_box.setValue(20)
        self.maximum_files_box.setRange(1, 100)
        self.maximum_files_box.setToolTip(
                                    '''Minimum: 1'''
                                    '''\nMaximum: 100''')

        grid_layout.addWidget(self.maximum_files_label, 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(self.maximum_files_box, 1, 1, Qt.AlignRight | Qt.AlignVCenter)

        # set horizontal layout
        grid_layout.setHorizontalSpacing(2)
        grid_layout.setVerticalSpacing(16)
        grid_layout.setColumnMinimumWidth(1, 50)

        hBox_layout_1 = QHBoxLayout()
        hBox_layout_1.addStretch()
        hBox_layout_1.addLayout(grid_layout)
        hBox_layout_1.addStretch()

        # push button
        self.restore_button = QPushButton('Restore defaults')
        self.cancel_button = QPushButton('Cancel')
        self.save_button = QPushButton('Save')

        # set horizontal layout 2
        hBox_layout_2 = QHBoxLayout()
        hBox_layout_2.addWidget(self.restore_button)
        hBox_layout_2.addStretch()
        hBox_layout_2.addWidget(self.cancel_button)
        hBox_layout_2.addWidget(self.save_button)


        # main layout (vertical layout)
        main_layout = QVBoxLayout()
        main_layout.addLayout(hBox_layout_1)
        main_layout.addSpacing(44)
        main_layout.addStretch()
        main_layout.addLayout(hBox_layout_2)
        main_layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        # set layout
        self.setLayout(main_layout)

        # test
        self.total_size = main_layout
        print(self.total_size.totalSizeHint())



    def set_window(self):
        # size, position, title and pin
        self.resize(self.total_size.totalMinimumSize())

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width()/2 - self.width()/2, 0)

        self.setWindowTitle('Auto Backup')

        self.setWindowFlag(Qt.WindowStaysOnTopHint)



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()       
        

app = QApplication(sys.argv)
test = AutoBackup()
test.show()

sys.exit(app.exec())