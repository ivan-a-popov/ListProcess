import re
import sys
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QMessageBox
from PyQt5.QtWidgets import QFileDialog, QFormLayout, QLineEdit
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.btn1 = QPushButton('Browse')
        self.btn2 = QPushButton('Browse')
        self.btn3 = QPushButton('Start process')
        self.source = QLineEdit()
        self.result = QLineEdit()
        self.msg1 = QLabel('Select file to process:')
        self.msg2 = QLabel('Select file to save result:')
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('List Process')
        self.setGeometry(200, 200, 480, 280)  # (x, y, width, height)
        self.center()
        self.set_layout()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_layout(self):

        self.btn1.clicked.connect(self.open_file)
        self.btn2.clicked.connect(self.save_file)
        self.btn3.clicked.connect(self.start)

        layout = QFormLayout()
        layout.addWidget(self.msg1)
        layout.addRow('Source file:', self.source)
        layout.addWidget(self.btn1)
        layout.addWidget(QLabel(''))
        layout.addWidget(self.msg2)
        layout.addRow('Result file:', self.result)
        layout.addWidget(self.btn2)
        layout.addWidget(QLabel(''))
        layout.addWidget(self.btn3)
        self.setLayout(layout)

    def open_file(self):
        """Source file open function."""
        file, check = QFileDialog.getOpenFileName(None, "Source file",
                                                  "list.txt", "Text Files (*.txt)")
        if check:
            self.source.insert(file)
            self.input_file = file

    def save_file(self):
        """Result file select function."""
        file, check = QFileDialog.getSaveFileName(None, "File to save result",
                                                  "result.txt", "Text Files (*.txt)")
        if check:
            self.result.insert(file)
            self.output_file = file

    def start(self):
        logic = MainLogic(self.input_file, self.output_file)
        msg = QMessageBox()
        msg.setWindowTitle('List Process')
        try:
            logic.run()
        except Exception:
            msg.setText("Error processing file")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
        else:
            msg.setText("File processed successfully")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()


def cut(data: list, delimiter: str, steps: int, index: int) -> list:
    separated = []
    for i in range(steps):
        try:
            next_index = data.index(delimiter, index)
        except ValueError:
            separated.append(data[index:])
            break
        else:
            separated.append(data[index:next_index])
            index = next_index + 1
    return separated


class MainLogic:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.result = []
        self.p = re.compile(r'section')  # section start pattern

    def run(self):
        with open(self.input_file, 'r') as f:
            lines = f.readlines()
        self.delimiter = lines[0]
        # Not sure what this data means, but we suppose that file starts with certain string (like "12.2")
        # If it then appears in the file, it's always between sections (not inside the section)
        # We'll call this string the main delimiter

        chunks = cut(lines, self.delimiter, len(lines), 1)  # first, we split file to chunks between main delimiter

        blocks = []  # separate blocks inside the chunks
        for n in range(len(chunks)):
            block = cut(chunks[n], '\n', 1, 1)
            blocks.append(cut(chunks[n], '\n', len(chunks[n]), len(block)))

        separate_blocks = []  # finally, we'll get blocks as items of this list all separate

        for block in blocks:
            for each in block:
                separate_blocks.append(each)

        self.result = [self.delimiter, '\n']
        self.get_result(separate_blocks, {})

        with open(self.output_file, 'w') as f:
            f.writelines(self.result)
        return

    def get_result(self, blocks: list, names: dict) -> None:

        if not blocks:  # end of recursion -- result ready
            for n in names:  # write the last section
                for line in names[n]:
                    self.result.append(line)
            return

        block = blocks[0]

        if not block:  # empty block means that here was the delimiter in original file
            for n in names:
                for line in names[n]:
                    self.result.append(line)
                self.result.append('\n')
            blocks.remove(block)
            self.result.append(self.delimiter)
            self.result.append('\n')
            names = {}
            self.get_result(blocks, names)

        elif bool(self.p.match(block[0])):
            if names:  # if it's not the first section, write previous
                for n in names:
                    for line in names[n]:
                        self.result.append(line)
                    self.result.append('\n')
            self.result.append(block.pop(0))
            names = {block[1]: block}
            blocks.remove(block)
            self.get_result(blocks, names)

        elif block[1] in names:
            names[block[1]][7] = names[block[1]][7][:-1]
            add = block[7] if block[7][-1] == '\n' else block[7]+'\n'  # for the last string of input file
            names[block[1]][7] += (';' + add)
            blocks.remove(block)
            self.get_result(blocks, names)

        elif block[1] not in names:
            num = len(names)+1
            block[0] = f"{num})\n"
            names[block[1]] = block
            blocks.remove(block)
            self.get_result(blocks, names)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = AppWindow()
    sys.exit(app.exec_())
