"""
ui2py_main.py
Author = SDEarl (https://github.com/SDEarl)
Converts PYQT5 Designer UI file to Python PY file

    Due to the use of PyQt5, this project is licensed under:
    GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007
    See LICENSE file for more information
"""

import sys
import os
import subprocess
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from ui2py_gui import Ui_MainWindow


class MainUi(QObject):

    version = '1.0.0'

    def __init__(self):
        super(MainUi, self).__init__()
        app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self.widget_actions()

        self.MainWindow.show()
        sys.exit(app.exec_())

    def widget_actions(self):
        self.ui.button_about.clicked.connect(self.show_about)
        self.ui.button_notes.clicked.connect(self.show_notes)
        self.ui.button_convert.clicked.connect(self.validate_input)
        self.ui.text_box_input_file.returnPressed.connect(self.validate_input)
        self.ui.button_input_browse.clicked.connect(self.input_file_browse)
        self.ui.button_output_browse.clicked.connect(self.output_file_browse)

    def input_file_browse(self):
        input_file = QtWidgets.QFileDialog.getOpenFileName(
            filter='PyQt5 Designer UI Files (*.ui)'
        )
        input_file = input_file[0]
        self.ui.text_box_input_file.clear()
        self.ui.text_box_input_file.setText(input_file)

    def output_file_browse(self):
        output_file = QtWidgets.QFileDialog.getSaveFileName(filter='Python File (*.py)')
        output_file = output_file[0]
        self.ui.text_box_output_file.clear()
        self.ui.text_box_output_file.setText(output_file)

    def clear_text_box(self):
        self.ui.text_edit_info_box.clear()

    def update_text_box(self, text):
        self.ui.text_edit_info_box.append(text)

    def validate_input(self):
        """
        Checks the input and output file text boxes for valid content.

        :return: None
        """
        self.clear_text_box()
        print('Validating input....')
        input_file = self.ui.text_box_input_file.text()
        input_file = input_file.replace("\\", "/")
        work_file_path = input_file.rsplit('/', 1)[0]  # Index[0] returns data left
        # of the last slash
        if not os.path.isdir(work_file_path):
            self.update_text_box('Input file path is not valid.  '
                                 'Please try again.')
            return
        if input_file == "":
            self.update_text_box('Please select or enter a file to convert.')
            return
        elif not os.path.isfile(input_file):
            self.update_text_box('Input File is not valid.')
            return
        else:
            self.update_text_box('Input file is valid.')

        output_file = self.ui.text_box_output_file.text()
        output_file = output_file.replace("\\", "/")
        out_file_path = output_file.rsplit('/', 1)[0]
        # Index[0] returns data left of the last slash
        print(f'Output File Path: {out_file_path}')
        file_path_valid = os.path.isdir(out_file_path)
        print('File Path Valid:', file_path_valid)

        if output_file == "":
            out_file = input_file.rsplit('.', 1)[0]  # Grab the file name less extension
            # from the input file
            output_file = str(f'{out_file}.py')  # Add the file extension
            self.convert(work_file_path, input_file, output_file)
            return
        elif output_file != "":
            if not os.path.isdir(out_file_path):
                self.update_text_box(f'Output file path ({out_file_path}) is not valid.  '
                                     'Please try again.')
                return
            if os.path.isfile(output_file):
                decision = self.show_warning('Selected File Exists!\n'
                                             'Do You Want to Overwrite Existing File?')
                if decision == 'cancel':
                    return
                else:
                    self.convert(work_file_path, input_file, output_file)
            else:
                out_file_ext = output_file.rsplit('.', 1)[-1].lower()  # Grab the file extension
                if not out_file_ext == 'py':
                    output_file = str(f'{output_file}.py')
                    self.convert(work_file_path, input_file, output_file)
                else:
                    self.convert(work_file_path, input_file, output_file)

    def convert(self, work_file_path, in_file, out_file):
        print('Entered convert method.')
        out_file_path = out_file.rsplit('/', 1)[0]
        os.chdir(work_file_path)
        self.update_text_box("Converting....")
        print("Converting....")

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(f'pyuic5 -x -o {out_file} {in_file}',
                                       startupinfo=startupinfo)
            print("Ran Subprocess")
        except Exception as error:
            self.update_text_box(error)
            self.show_warning('An error has occurred and the conversion was not completed.\n'
                              'Please check the status window for more information.')
            print(error)
        else:
            process.wait(5.0)
            if not os.path.isfile(out_file):
                self.update_text_box("Conversion failed!")
                self.show_warning('An error has occurred and the conversion was not completed.\n'
                                  'Please check your inputs and try again.')
            else:
                self.update_text_box("Conversion complete!")
                self.update_text_box(f"See {out_file_path}\\ for converted file.")
                print("Conversion complete")

    def show_about(self):
        QtWidgets.QMessageBox.about(
            self.MainWindow, 'About', 'UI2PY - Convert PyQt5 Designer UI files to PY\n'
                                      f'Version: {self.version}'
        )

    def show_warning(self, message):
        """
        Displays a warning message box.

        :param self:
        :param message: Message text that you wish to display.
        :return: String based on button click 'ok' or 'cancel'
        """

        msg = QtWidgets.QMessageBox(self.MainWindow)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle("Warning!")
        msg.setStyleSheet("QLabel{color: red}")
        msg.setText(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msg.show()
        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.Ok:
            return "ok"
        else:
            return "cancel"

    def show_notes(self):
        """
        Displays a window with containing informational notes about the program.

        :return: None
        """
        msg = QtWidgets.QMessageBox(self.MainWindow)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Notes")
        msg.setText('1. If you do not specify an existing or new output \".py\" '
                    'file one will be created with the same name '
                    'as the input file and in the same location.\n\n'
                    '2. Existing files typed in having the same name as the input file will '
                    'be overwritten without asking permission unless you use '
                    'the "Save As" dialog.\n\n')
        msg.setStyleSheet('font: 10 pt "Arial";')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.show()


if __name__ == '__main__':
    MainUi()
