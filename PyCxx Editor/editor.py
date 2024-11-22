from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QDockWidget,
    QComboBox
)
from PyQt5.QtGui import QColor
from PyQt5.Qsci import (
    QsciScintilla,
    QsciLexerPython,
    QsciLexerCPP,
    QsciLexerHTML,
    QsciLexerCSS,
    QsciLexerJavaScript
)

import google.generativeai as gemini

import os
import subprocess
import shutil
import sys

class GeminiAi:
    def __init__(self, api_key:str, ai_model:str):
        gemini.configure(api_key=api_key)
        self._model = gemini.GenerativeModel(ai_model)
        self._chat = self._model.start_chat() 
    
    def generateAnswer(self,input:str):
        response = self._model.generate_content(input,stream=True)
        return response
    def loadPrompt(self,file_name:str):
        with open(file_name) as file:
            prompt_enhance = file.read()
        return prompt_enhance


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1080, 720)
        self.setWindowTitle('PyCxx IDE')
        self.__folder = QPushButton('Folder')
        self.__folder.setObjectName('btn')
        self.__newfile = QPushButton('New')
        self.__newfile.setObjectName('btn')
        self.__openfile = QPushButton('Open')
        self.__openfile.setObjectName('btn')
        self.__savefile = QPushButton('Save')
        self.__savefile.setObjectName('btn')
        self.__runProg = QPushButton('Run')
        self.__runProg.setObjectName('btn')

        self.menu_bar_layout = QHBoxLayout()
        self.menu_bar_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.menu_bar_layout.addWidget(self.__folder)
        self.menu_bar_layout.addWidget(self.__newfile)
        self.menu_bar_layout.addWidget(self.__openfile)
        self.menu_bar_layout.addWidget(self.__savefile)
        self.menu_bar_layout.addWidget(self.__runProg)

        self.ide = Editor()
        self._ai = GeminiAi("AIzaSyAjBYJJLqpIkWi7owhN_sdMDkd64GqeXoo", "gemini-1.5-flash")
        
        self._prompt_command = QComboBox()
        self._prompt_command.addItem('None')
        self._prompt_command.addItem('explain')
        self._prompt_command.addItem('fixt')
        self._prompt_command.addItem('comment')
        self._prompt = QLineEdit()
        self._prompt.setObjectName('prompt')
        self._send_button = QPushButton('Send')
        self._send_button.setObjectName('send')
        self._send_button.clicked.connect(self.printOutput)


        self._file_tree = QTreeWidget()
        self._file_tree.setObjectName('tree_view')
        self._file_tree.setHeaderHidden(True)
        self._file_tree.itemClicked.connect(self.ide.loadTreeFile)

        self.left_side_layout = QVBoxLayout()
        self.left_side_layout.setObjectName('left_container')
        self.left_side_layout.addLayout(self.menu_bar_layout)
        self.left_side_layout.addWidget(self._file_tree)

        self.prompt_layout = QHBoxLayout()
        self.prompt_layout.addWidget(self._prompt_command)
        self.prompt_layout.addWidget(self._prompt)
        self.prompt_layout.addWidget(self._send_button)

        self.right_side_layout = QVBoxLayout()
        self.right_side_layout.addLayout(self.prompt_layout)
        self.right_side_layout.addWidget(self.ide)

        self._chat_area = QTextEdit()
        self._chat_area.setReadOnly(True)
        self.dock_layout = QDockWidget()
        self.dock_layout.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.dock_layout.setWidget(self._chat_area)
        self.dock_layout.hide()

        self.__folder.clicked.connect(self.showFiles)
        self.__newfile.clicked.connect(self.ide.newFile)
        self.__openfile.clicked.connect(self.openAndShowFilesFolder)
        self.__savefile.clicked.connect(self.ide.saveFile)
        self.__runProg.clicked.connect(self.ide.run_program)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.left_side_layout)
        self.main_layout.addLayout(self.right_side_layout, 80)
        self.main_layout.addWidget(self.dock_layout, 40)
        # self.main_layout.addWidget(self.ide,75)

        self.setLayout(self.main_layout)

    def openAndShowFilesFolder(self):
        self.ide.openFile()
        self.populateTree(os.path.dirname(self.ide.file_path))

    def add_tree_items(self, parent_item, path):
        extension = ['.py', '.c', '.cpp', '.txt',
                     '.md', '.html', '.css', '.js']
        for item_name in os.listdir(path):
            item_path = os.path.join(path, item_name)

            if os.path.isdir(item_path):
                tree_item = QTreeWidgetItem(parent_item)
                tree_item.setText(0, item_name)
                tree_item.setData(0, Qt.UserRole, item_path)
                self.add_tree_items(tree_item, item_path)
                tree_item.setExpanded(False)
            else:
                if any(item_name.endswith(ext) for ext in extension):
                    tree_item = QTreeWidgetItem(parent_item)
                    tree_item.setText(0, item_name)
                    tree_item.setData(0, Qt.UserRole, item_path)

    def showFiles(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.populateTree(folder)

    def populateTree(self, folder):
        self._file_tree.clear()
        if folder:
            self.ide.dir_path = folder
            root_item = QTreeWidgetItem(self._file_tree)
            root_item.setText(0, os.path.basename(folder))
            root_item.setData(0, Qt.UserRole, folder)
            root_item.setExpanded(True)
            self.add_tree_items(root_item, folder)
    
    def collectInput(self):
        if self._prompt_command.currentIndex() == 0: #none
            input_prompt = ''
        elif self._prompt_command.currentIndex() == 1: #explain
            input_prompt = self._ai.loadPrompt('prompt_train/explain.txt')
            print('explain')
        elif self._prompt_command.currentIndex() == 2: #fixt
            input_prompt = self._ai.loadPrompt(r'prompt_train\fixt.txt')
        elif self._prompt_command.currentIndex() == 3: #comment
            pass

        input_command = self._prompt.text()
        input_code = self.ide.text()
        self._prompt.clear()
        final_input = input_prompt + input_command + '\n' + input_code

        return final_input

    def printOutput(self):
        markdown = ""
        self.dock_layout.show()
        self.dock_layout.repaint()
        for chunk in self._ai.generateAnswer(self.collectInput()):
            # self._chat_area.insertPlainText(chunk.text)
            # self._chat_area.repaint()
            markdown += chunk.text 
            self._chat_area.setMarkdown(markdown)
            self._chat_area.repaint()
        self._chat_area.append('\n')


class Editor(QsciScintilla):
    def __init__(self):
        super().__init__()
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, '00000')  # for 0000 digit line of code
        self.setMarginsForegroundColor(QColor("#9da8af"))
        self.setWrapMode(QsciScintilla.WrapWord)
        self.setWrapVisualFlags(QsciScintilla.WrapFlagByText)
        self.setWrapIndentMode(QsciScintilla.WrapIndentIndented)
        self.setFolding(QsciScintilla.PlainFoldStyle)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor('#e6ffe6'))
        self.setAutoIndent(True)

        self.file_path = ''
        self.dir_path = ''

    def loadFile(self, filepath):
        if os.path.isfile(filepath):
            main_file_context = open(filepath, 'r')
            file_text = main_file_context.read()
            self.setText(file_text)
            extension = filepath.split(".")[-1]
            match extension:
                case "py":
                    self.lexer = QsciLexerPython()
                case "c":
                    self.lexer = QsciLexerCPP()
                case "cpp":
                    self.lexer = QsciLexerCPP()
                case "html":
                    self.lexer = QsciLexerHTML()
                case "css":
                    self.lexer = QsciLexerCSS()
                case "js":
                    self.lexer = QsciLexerJavaScript()
                case _:
                    self.lexer = None
            self.setLexer(self.lexer)

    def openFile(self):
        filename, _ = QFileDialog().getOpenFileName()
        self.file_path = filename
        self.dir_path = os.path.dirname(filename)

        self.loadFile(filename)

    def loadTreeFile(self, item, col):
        texts = []
        while item is not None:
            texts.insert(0, item.text(0))
            item = item.parent()
        filename = "/".join(texts[1:])
        filepath = os.path.join(self.dir_path, filename)
        self.file_path = filepath
        self.loadFile(filepath)

    def newFile(self):
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save File', os.getcwd(
        ), 'Python Files (*.py);;C Files (*.c);;C++ Files (*.cpp)')
        if fileName:
            if not os.path.exists(fileName):
                with open(fileName, 'w') as file:
                    file.write('')

    def saveFile(self):
        filename = None
        if not self.file_path:
            self.openFile()
        else:
            filename = self.file_path

        if filename:
            with open(filename, 'w') as file:
                file_text = self.text()
                cleaned_text = file_text.rstrip()
                file.write(cleaned_text)
                # print(self.text())

        print("file saved")

    def is_executable_available(self, executable_name):
        """Check if a given executable is available on the system."""
        return shutil.which(executable_name) is not None

    def run_program(self, file_path):
        """Run the program based on its file type."""
        file_path = self.file_path
        if file_path:
            with open(file_path, 'w') as file:
                # print(self.text())
                file_text = self.text()
                cleaned_text = file_text.rstrip()
                file.write(cleaned_text)
        # Get file extension
        _, file_extension = os.path.splitext(file_path)

    # Determine action based on file type
        if file_extension == ".py":
            # Python file
            if self.is_executable_available("python"):
                print("Python interpreter found. Running the script...")
                # execute_command_in_terminal(f"python {file_path}")
                subprocess.run(["python", file_path])
            else:
                print("Python interpreter not found. Please install Python.")

        elif file_extension in [".c", ".cpp"]:
            # C or C++ file
            compiler = "gcc" if file_extension == ".c" else "g++"
            if self.is_executable_available(compiler):
                print(
                    f"{compiler} compiler found. Compiling and running the program...")
            # Compile the program
                output_file = os.path.join(os.getcwd(), _)
                compile_command = [compiler, file_path, "-o", output_file]
                # execute_command_in_terminal(compile_command)
                compile_process = subprocess.run(compile_command)

            # Check if compilation was successful
                if compile_process.returncode == 0:
                    print("Compilation successful. Running the program...")
                    subprocess.run([output_file])
                # Clean up the compiled output file after running
                    # os.remove(output_file)
                else:
                    print("Compilation failed.")
            else:
                print(f"{compiler} compiler not found. Please install {compiler}.")

        else:
            print("Unsupported file type. Please provide a .py, .c, or .cpp file.")


def load_stylesheet(file_name):
    with open(file_name, 'r') as file:
        return file.read()


def main():
    app = QApplication([])
    stylesheet = load_stylesheet("styles/style.qss")
    app.setStyleSheet(stylesheet)
    editor = UI()
    editor.show()
    app.exec_()


if __name__ == '__main__':
    main()
