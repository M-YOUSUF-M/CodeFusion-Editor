from PyQt5.QtCore import (

    Qt,

    pyqtSlot,

    QObject,

    QThread,

    pyqtSignal

    # Importing necessary modules from PyQt5.QtCore for Qt functionalities, signals and threads.
)


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

)  # Importing various PyQt5.QtWidgets modules for creating GUI elements like windows, layouts, buttons, text editors, etc.


# Importing QColor from PyQt5.QtGui for color settings.
from PyQt5.QtGui import QColor

from PyQt5.Qsci import (

    QsciScintilla,

    QsciAPIs,

    QsciLexerPython,

    QsciLexerCPP,

    QsciLexerHTML,

    QsciLexerCSS,

    QsciLexerJavaScript

    # Importing QsciScintilla and various lexer modules from PyQt5.Qsci for advanced code editor functionalities.
)


import google.generativeai as gemini  # Importing the Google Gemini AI library.


import os  # Importing the os module for operating system functionalities.
import platform  # Importing the platform module for system functionalities.

# Importing the subprocess module for running external commands.
import subprocess

import shutil  # Importing the shutil module for high-level file operations.

# Importing the sys module for system-specific parameters and functions.
import sys
import builtins
import keyword
import jedi
import inspect


pkg_map = {
    "apt": "sudo apt install {} -y",
    "dnf": "sudo dnf install {} -y",
    "pacman": "sudo pacman -S {}",
    "apk": "sudo apk add {} -y",
    "zypper": "sudo zypper install {} -y",
    "brew": "brew install {} -y",
}

term_map = {
    "konsole": "konsole --hold -e {}",
    "alacritty": "alacritty --hold -e {}",
    "kitty": "kitty --hold --detach -e {}",
    "powershell": "powershell -NoExit -Command {}",
    "gnome-terminal": "gnome-terminal --hold -e {}",
    "xfce-terminal": "xfce-terminal --hold -e {}",
    "xterm": "xterm --hold -e {}",
}


# Defining a class GeminiThreat that inherits from QThread for handling AI operations in a separate thread.
class GeminiThreat(QThread):

    # Defining a pyqtSignal to emit progress updates as strings.
    progress = pyqtSignal(str)

    # Constructor for GeminiThreat, takes chat area and input string as arguments.
    def __init__(self, chat_area: QTextEdit, input: str):

        # Calling the superclass constructor to initialize the QThread.
        super(QThread, self).__init__()

        # Assigning the chat area widget to the instance.
        self.chat_area = chat_area

        self.input_text = input  # Assigning the input text to the instance.

        # self.finished = pyqtSignal() #commented out: Unnecessary signal, QThread already has finished signal.

        # Initializing GeminiAi object with API key and model.
        self.ai = GeminiAi(
            "AIzaSyAjBYJJLqpIkWi7owhN_sdMDkd64GqeXoo", "gemini-1.5-flash")

    # Defining the run method, which is executed when the thread starts.
    def run(self):

        # Initializing an empty string to store the markdown response.
        markdown = ''

        # Iterating through the chunks of the AI response.
        for chunk in self.ai.generateAnswer(self.input_text):

            # self._chat_area.insertPlainText(chunk.text) #commented out:  Replaced by accumulating markdown

            # self._chat_area.repaint() #commented out: Repaint handled by progress signal

            # Appending the text of each chunk to the markdown string.
            markdown += chunk.text

            # Emitting the updated markdown as a progress signal.
            self.progress.emit(markdown)


class GeminiAi:  # Defining a class GeminiAi for interacting with the Google Gemini AI.

    # Constructor for GeminiAi, takes API key and model name as arguments.
    def __init__(self, api_key: str, ai_model: str):

        # Configuring the Gemini API with the provided API key.
        gemini.configure(api_key=api_key)

        # Creating a GenerativeModel object with the specified model.
        self._model = gemini.GenerativeModel(ai_model)

        # Starting a chat session with the model.
        self._chat = self._model.start_chat()

    # Method to generate an answer from the AI model, takes input string as argument.
    def generateAnswer(self, input: str):

        # Generating content from the model with streaming enabled.
        response = self._model.generate_content(input, stream=True)

        return response  # Returning the streamed response.

    # Method to load a prompt from a file, takes file name as argument.
    def loadPrompt(self, file_name: str):

        with open(file_name) as file:  # Opening the file in read mode.

            prompt_enhance = file.read()  # Reading the content of the file.

        return prompt_enhance  # Returning the prompt content.


# Defining a class UI that inherits from QWidget to represent the main user interface.
class UI(QWidget):

    def __init__(self):  # Constructor for UI.

        # Calling the superclass constructor to initialize the QWidget.
        super().__init__()

        self.resize(1080, 720)  # Setting the initial size of the window.

        self.setWindowTitle('PyCxx IDE')  # Setting the title of the window.

        self.__folder = QPushButton('Folder')  # Creating a Folder button.

        # Setting the object name for styling purposes.
        self.__folder.setObjectName('btn')

        self.__newfile = QPushButton('New')  # Creating a New button.

        # Setting the object name for styling purposes.
        self.__newfile.setObjectName('btn')

        self.__openfile = QPushButton('Open')  # Creating an Open button.

        # Setting the object name for styling purposes.
        self.__openfile.setObjectName('btn')

        self.__savefile = QPushButton('Save')  # Creating a Save button.

        # Setting the object name for styling purposes.
        self.__savefile.setObjectName('btn')

        self.__runProg = QPushButton('Run')  # Creating a Run button.

        # Setting the object name for styling purposes.
        self.__runProg.setObjectName('btn')

        # Creating a horizontal layout for the menu bar.
        self.menu_bar_layout = QHBoxLayout()

        # Aligning the layout to center and top.
        self.menu_bar_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        # Adding the Folder button to the layout.
        self.menu_bar_layout.addWidget(self.__folder)

        # Adding the New button to the layout.
        self.menu_bar_layout.addWidget(self.__newfile)

        # Adding the Open button to the layout.
        self.menu_bar_layout.addWidget(self.__openfile)

        # Adding the Save button to the layout.
        self.menu_bar_layout.addWidget(self.__savefile)

        # Adding the Run button to the layout.
        self.menu_bar_layout.addWidget(self.__runProg)

        self.ide = Editor()  # Creating an instance of the Editor class.
        self.ide.setObjectName("ide-background")

        # Initializing GeminiAi object.
        self._ai = GeminiAi(
            "AIzaSyAjBYJJLqpIkWi7owhN_sdMDkd64GqeXoo", "gemini-1.5-flash")

        # Creating a combo box for selecting AI commands.
        self._prompt_command = QComboBox()

        self._prompt_command.addItem('None')  # Adding 'None' as an item.

        self._prompt_command.addItem('explain')  # Adding 'explain' as an item.

        self._prompt_command.addItem('fixt')  # Adding 'fixt' as an item.

        self._prompt_command.addItem('comment')  # Adding 'comment' as an item.

        self._prompt = QLineEdit()  # Creating a line edit for user input.

        # Setting the object name for styling purposes.
        self._prompt.setObjectName('prompt')

        self._send_button = QPushButton('Send')  # Creating a Send button.

        # Setting the object name for styling purposes.
        self._send_button.setObjectName('send')

        # Connecting the clicked signal to the runThread method.
        self._send_button.clicked.connect(self.runThread)

        # Creating a tree widget to display files.
        self._file_tree = QTreeWidget()

        # Setting the object name for styling purposes.
        self._file_tree.setObjectName('tree_view')

        # Hiding the header of the tree widget.
        self._file_tree.setHeaderHidden(True)

        # Connecting the itemClicked signal to the loadTreeFile method.
        self._file_tree.itemClicked.connect(self.ide.loadTreeFile)

        # Creating a vertical layout for the left side.
        self.left_side_layout = QVBoxLayout()

        # Setting the object name for styling purposes.
        self.left_side_layout.setObjectName('left_container')

        # Adding the menu bar layout to the left side layout.
        self.left_side_layout.addLayout(self.menu_bar_layout)

        # Adding the file tree widget to the left side layout.
        self.left_side_layout.addWidget(self._file_tree)

        # Creating a horizontal layout for the prompt area.
        self.prompt_layout = QHBoxLayout()

        # Adding the combo box to the prompt layout.
        self.prompt_layout.addWidget(self._prompt_command)

        # Adding the line edit to the prompt layout.
        self.prompt_layout.addWidget(self._prompt)

        # Adding the send button to the prompt layout.
        self.prompt_layout.addWidget(self._send_button)

        # Creating a vertical layout for the right side.
        self.right_side_layout = QVBoxLayout()

        # Adding the prompt layout to the right side layout.
        self.right_side_layout.addLayout(self.prompt_layout)

        # Adding the code editor to the right side layout.
        self.right_side_layout.addWidget(self.ide)

        # Creating a text edit for the chat area.
        self._chat_area = QTextEdit()

        # Setting the chat area to read-only.
        self._chat_area.setReadOnly(True)

        # Creating a dock widget for the chat area.
        self.dock_layout = QDockWidget()

        # Making the dock widget closable.
        self.dock_layout.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable)

        # Setting the chat area as the widget of the dock widget.
        self.dock_layout.setWidget(self._chat_area)

        self.dock_layout.hide()  # Hiding the dock widget initially.

        # Connecting the clicked signal of the Folder button to the showFiles method.
        self.__folder.clicked.connect(self.showFiles)

        # Connecting the clicked signal of the New button to the newFile method.
        self.__newfile.clicked.connect(self.ide.newFile)

        # Connecting the clicked signal of the Open button to the openAndShowFilesFolder method.
        self.__openfile.clicked.connect(self.openAndShowFilesFolder)

        # Connecting the clicked signal of the Save button to the saveFile method.
        self.__savefile.clicked.connect(self.ide.saveFile)

        # Connecting the clicked signal of the Run button to the run_program method.
        self.__runProg.clicked.connect(self.run_program)

        # Creating a horizontal layout for the main window.
        self.main_layout = QHBoxLayout()

        # Adding the left side layout to the main layout.
        self.main_layout.addLayout(self.left_side_layout)

        # Adding the right side layout to the main layout with a stretch factor of 80.
        self.main_layout.addLayout(self.right_side_layout, 80)

        # Adding the dock widget to the main layout with a stretch factor of 40.
        self.main_layout.addWidget(self.dock_layout, 40)

        # self.main_layout.addWidget(self.ide,75) #commented out: Redundant, IDE already added above.

        self.install_prompt = QWidget()
        self.install_prompt.setFixedSize(360, 80)
        self.install_text = QLabel()
        self.ok_btn = QPushButton("OK")
        self.cc_btn = QPushButton("Cancel")
        self.cc_btn.clicked.connect(self.install_prompt.close)
        self.install_layout = QVBoxLayout()
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.ok_btn)
        self.btn_layout.addWidget(self.cc_btn)
        self.install_layout.addWidget(self.install_text)
        self.install_layout.addLayout(self.btn_layout)
        self.install_prompt.setLayout(self.install_layout)

        # Setting the main layout for the window.
        self.setLayout(self.main_layout)

    # Method to open a file and populate the file tree.
    def openAndShowFilesFolder(self):

        # Opening a file using the openFile method of the Editor class.
        self.ide.openFile()

        # Populating the file tree with the files in the directory of the opened file.
        self.populateTree(os.path.dirname(self.ide.file_path))

    # Recursive method to add items to the file tree.
    def add_tree_items(self, parent_item, path):

        extension = ['.py', '.c', '.cpp', '.txt',  # List of supported file extensions.

                     '.md', '.html', '.css', '.js']

        # Iterating through the items in the given path.
        for item_name in os.listdir(path):

            # Creating the full path of the item.
            item_path = os.path.join(path, item_name)

            # Checking if the item is a directory.
            if os.path.isdir(item_path):

                # Creating a tree item for the directory.
                tree_item = QTreeWidgetItem(parent_item)

                # Setting the text of the tree item to the directory name.
                tree_item.setText(0, item_name)

                # Setting the data of the tree item to the directory path.
                tree_item.setData(0, Qt.UserRole, item_path)

                # Recursively calling the method for subdirectories.
                self.add_tree_items(tree_item, item_path)

                # Setting the directory to be initially collapsed.
                tree_item.setExpanded(False)

            else:  # If the item is not a directory.

                # Checking if the item has a supported extension.
                if any(item_name.endswith(ext) for ext in extension):

                    # Creating a tree item for the file.
                    tree_item = QTreeWidgetItem(parent_item)

                    # Setting the text of the tree item to the file name.
                    tree_item.setText(0, item_name)

                    # Setting the data of the tree item to the file path.
                    tree_item.setData(0, Qt.UserRole, item_path)

    def showFiles(self):  # Method to show a file dialog to select a folder.

        # Showing a file dialog to select a folder.
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')

        # Populating the file tree with the files in the selected folder.
        self.populateTree(folder)

    # Method to populate the file tree with the files in a given folder.
    def populateTree(self, folder):

        self._file_tree.clear()  # Clearing the file tree.

        if folder:  # Checking if a folder was selected.

            # Setting the directory path in the Editor class.
            self.ide.dir_path = folder

            # Creating a root item for the folder.
            root_item = QTreeWidgetItem(self._file_tree)

            # Setting the text of the root item to the folder name.
            root_item.setText(0, os.path.basename(folder))

            # Setting the data of the root item to the folder path.
            root_item.setData(0, Qt.UserRole, folder)

            # Setting the root item to be initially expanded.
            root_item.setExpanded(True)

            # Calling the add_tree_items method to add items to the tree.
            self.add_tree_items(root_item, folder)

    def collectInput(self):  # Method to collect user input for the AI.

        if self._prompt_command.currentIndex() == 0:  # none

            # Setting input_prompt to an empty string if 'None' is selected.
            input_prompt = ''

        elif self._prompt_command.currentIndex() == 1:  # explain

            # Loading the 'explain' prompt from a file.
            input_prompt = self._ai.loadPrompt('prompt_train/explain.txt')

            print('explain')  # Printing 'explain' to the console.

        elif self._prompt_command.currentIndex() == 2:  # fixt

            # Loading the 'fixt' prompt from a file.
            input_prompt = self._ai.loadPrompt('prompt_train/fixt.txt')

        elif self._prompt_command.currentIndex() == 3:  # comment

            input_prompt = self._ai.loadPrompt('prompt_train/comment.txt')

        # Getting the text from the prompt line edit.
        input_command = self._prompt.text()

        input_code = self.ide.text()  # Getting the code from the code editor.

        self._prompt.clear()  # Clearing the prompt line edit.

        # Combining the prompts, command, and code into a single string.
        final_input = input_prompt + input_command + '\n' + input_code

        return final_input  # Returning the combined input string.

    def runThread(self):  # Method to run the AI thread.

        self.dock_layout.show()  # Showing the dock widget.

        self.dock_layout.repaint()  # Repainting the dock widget.

        # Creating an instance of the GeminiThreat class.
        self.ai_work = GeminiThreat(self._chat_area, self.collectInput())

        # Connecting the progress signal to the updateChatArea method.
        self.ai_work.progress.connect(self.updateChatArea)

        self.ai_work.start()  # Starting the AI thread.

    # Method to update the chat area with the AI response.
    def updateChatArea(self, text: str):

        # Setting the markdown text in the chat area.
        self._chat_area.setMarkdown(text)

        self._chat_area.repaint()  # Repainting the chat area.

    def execute_cmd(self, cmd):
        if platform.system() == "Windows":
            subprocess.Popen(["powershell", "-NoExit", "-Command", cmd])
        else:
            for term in term_map:
                if shutil.which(term) is not None:
                    final = term_map[term].format(cmd)
                    subprocess.Popen(final, shell=True)
                    break

    def install(self, package):
        if not shutil.which(package):
            print(f"Package {package} is not installed")
        for pkg in pkg_map:
            if shutil.which(pkg) is not None:
                cmd = pkg_map[pkg].format(package)
                self.execute_cmd(cmd)

    def show_prompt(self, package):
        self.ok_btn.clicked.connect(lambda: self.install(
            package
        ) or self.install_prompt.close())
        self.install_prompt.setWindowTitle(f"Install {package}")
        self.install_text.setText(f"Do you want to install {package}?")
        self.install_prompt.show()

    def run_program(self):
        file_path = self.ide.file_path  # Getting the file path.

        file_path = file_path.replace("\\", "/")

        if file_path:  # Checking if the file path is not empty.

            # Opening the file in write mode.
            with open(file_path, 'w') as file:

                # print(self.text()) #commented out: Unnecessary print statement.

                # Getting the text from the editor.
                file_text = self.ide.text()

                # Removing trailing whitespace from the text.
                cleaned_text = file_text.rstrip()

                # Writing the cleaned text to the file.
                file.write(cleaned_text)

        # Get file extension

        # Getting the file extension.
        base_name, file_extension = os.path.splitext(file_path)

    # Determine action based on file type

        if file_extension == ".py":  # Checking if the file is a Python file.

            # Python file

            # Checking if Python is installed.
            if self.ide.is_executable_available("python"):

                # Printing a message to the console.
                print("Python interpreter found. Running the script...")

                # execute_command_in_terminal(f"python {file_path}") #commented out: Unnecessary function call.

                # subprocess.run(["python", file_path]) # Running the Python script.
                command = f'python "{os.path.join(self.ide.dir_path, self.ide.file_path)}"'
                print(command)
                self.execute_cmd(command)

            else:

                # Printing an error message to the console.
                print("Python interpreter not found.")
                self.show_prompt('python')

        # Checking if the file is a C or C++ file.
        elif file_extension in [".c", ".cpp"]:

            # C or C++ file

            # Setting the compiler based on the file extension.
            compiler = "gcc" if file_extension == ".c" else "g++"

            # Checking if the compiler is installed.
            if self.ide.is_executable_available(compiler):

                print(

                    # Printing a message to the console.
                    f"{compiler} compiler found. Compiling and running the program...")

            # Compile the program

                # Setting the output file name.
                output_file = (f"{base_name.split('/')[-1]}.exe" if platform.system() == "Windows" else f"{base_name.split('/')[-1]}.out")
                os.chdir(self.ide.dir_path)
                # Creating the compile command.
                compile_command = [compiler, file_path, "-o", output_file]

                # execute_command_in_terminal(compile_command) #commented out: Unnecessary function call.

                # Running the compile command.
                compile_process = subprocess.run(compile_command)

            # Check if compilation was successful

                # Checking if the compilation was successful.
                if compile_process.returncode == 0:

                    # Printing a message to the console.
                    print("Compilation successful. Running the program...")
                    if platform.system() == "Windows":
                        output_command = output_file.replace("\\","/").split('.')[0]
                        
                #    subprocess.run([output_file]) # Running the compiled program.
                    self.execute_cmd(f"./{output_command}")

                else:

                    # Printing an error message to the console.
                    print("Compilation failed.")

            else:

                # Printing an error message to the console.
                print(f"{compiler} compiler not found. Please install {compiler}.")
                self.show_prompt(compiler)

        else:

            # Printing an error message to the console.
            print("Unsupported file type. Please provide a '.py', '.c', or '.cpp' file.")


# Defining a class Editor that inherits from QsciScintilla for code editing.
class Editor(QsciScintilla):

    def __init__(self):  # Constructor for Editor.

        # Calling the superclass constructor to initialize the QsciScintilla.
        super().__init__()

        # Setting the margin type to number margin.
        self.setMarginType(0, QsciScintilla.NumberMargin)

        # for 0000 digit line of code # Setting the width of the margin.
        self.setMarginWidth(0, '00000')

        # Setting the color of the margin.
        self.setMarginsForegroundColor(QColor("#9da8af"))

        # Setting the wrap mode to wrap by word.
        self.setWrapMode(QsciScintilla.WrapWord)

        # Setting the visual flags for wrapping.
        self.setWrapVisualFlags(QsciScintilla.WrapFlagByText)

        # Setting the indent mode for wrapping.
        self.setWrapIndentMode(QsciScintilla.WrapIndentIndented)

        # Setting the folding style.
        self.setFolding(QsciScintilla.PlainFoldStyle)

        self.setCaretLineVisible(True)  # Making the caret line visible.

        # Setting the background color of the caret line.
        self.setCaretLineBackgroundColor(QColor('#e6ffe6'))

        self.setAutoIndent(True)  # Enabling auto-indent.

        # Enable all sources for auto completion (api + editor stream)
        self.setAutoCompletionSource(QsciScintilla.AcsAll)

        # threshold for the number of character the suggestion will show
        self.setAutoCompletionThreshold(1)

        self.file_path = ''  # Initializing the file path to an empty string.

        # Initializing the directory path to an empty string.
        self.dir_path = ''

    def loadFile(self, filepath):  # Method to load a file into the editor.

        if os.path.isfile(filepath):  # Checking if the file exists.

            # Opening the file in read mode.
            main_file_context = open(filepath, 'r')

            # Reading the content of the file.
            file_text = main_file_context.read()

            # Setting the text of the editor to the file content.
            self.setText(file_text)

            extension = filepath.split(".")[-1]  # Getting the file extension.

            match extension:  # Matching the extension to set the appropriate lexer.

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

            # Setting the lexer for syntax highlighting.
            self.setLexer(self.lexer)
            self.setup_autocomplete()

    def openFile(self):  # Method to open a file using a file dialog.

        # Showing a file dialog to open a file.
        filename, _ = QFileDialog().getOpenFileName()

        self.file_path = filename  # Setting the file path.

        # Setting the directory path.
        self.dir_path = os.path.dirname(filename)

        self.loadFile(filename)  # Loading the file into the editor.

    # Method to load a file from the file tree.
    def loadTreeFile(self, item, col):

        # Initializing an empty list to store the text of the tree items.
        texts = []

        # Iterating through the tree items until the root item is reached.
        while item is not None:

            # Inserting the text of the tree item at the beginning of the list.
            texts.insert(0, item.text(0))

            item = item.parent()  # Getting the parent item.

        # Joining the text of the tree items to create the file name.
        filename = "/".join(texts[1:])

        # Creating the full path of the file.
        filepath = os.path.join(self.dir_path, filename)

        self.file_path = filepath  # Setting the file path.

        self.loadFile(filepath)  # Loading the file into the editor.

    def newFile(self):  # Method to create a new file.

        fileName, _ = QFileDialog.getSaveFileName(self, 'Save File', os.getcwd(

            # Showing a file dialog to save a new file.
        ), 'Python Files (*.py);;C Files (*.c);;C++ Files (*.cpp)')

        if fileName:  # Checking if a file name was selected.

            # Checking if the file already exists.
            if not os.path.exists(fileName):

                with open(fileName, 'w') as file:  # Creating the file.

                    file.write('')  # Writing an empty string to the file.

    def saveFile(self):  # Method to save a file.

        filename = None  # Initializing the file name to None.

        if not self.file_path:  # Checking if the file path is empty.

            self.openFile()  # Opening a file using a file dialog.

        else:

            # Setting the file name to the file path.
            filename = self.file_path

        if filename:  # Checking if a file name was selected.

            # Opening the file in write mode.
            with open(filename, 'w') as file:

                file_text = self.text()  # Getting the text from the editor.

                # Removing trailing whitespace from the text.
                cleaned_text = file_text.rstrip()

                # Writing the cleaned text to the file.
                file.write(cleaned_text)

                # print(self.text()) #commented out: Unnecessary print statement.

        print("file saved")  # Printing "file saved" to the console.

    def openTerminalRunCommand(self, command):
        if platform.system() == 'Windows':
            # Ensure the command is passed as a list with explicit path
            subprocess.Popen(
                ["powershell", "-NoExit", "-Command", f"& {command}"])
        else:
            subprocess.Popen(["bash", "-c", f"{command}"])

    # Method to check if an executable is available on the system.
    def is_executable_available(self, executable_name):
        """Check if a given executable is available on the system."""

        # Returning True if the executable is found, False otherwise.
        return shutil.which(executable_name) is not None
    def setup_autocomplete(self):
        # Initialize API object for Python Lexer
        api = QsciAPIs(self.lexer)
        # Add built-in functions, keywords, and standard libraries
        self.add_builtin_functions(api)
        self.add_keywords(api)
        self.add_standard_libraries(api)

        # Add third-party modules using jedi
        self.add_third_party_modules(api)

        # Prepare the API for usage in auto-completion
        api.prepare()

    def add_builtin_functions(self, api):
        """Add built-in Python functions (like print(), len(), etc.) to the API"""
        for name, obj in builtins.__dict__.items():
            if callable(obj):
                api.add(name)

    def add_keywords(self, api):
        """Add Python keywords (like if, else, for, etc.) to the API"""
        for kw in keyword.kwlist:
            api.add(kw)

    def add_standard_libraries(self, api):
        """Add common Python standard libraries (like os, sys, math, etc.)"""
        try:
            import sys
            standard_libs = sys.builtin_module_names
            for lib in standard_libs:
                api.add(lib)
        except Exception as e:
            print("Error while adding standard libraries:", e)

        self.add_module_functions(api,'os')
        self.add_module_functions(api,'sys')
    def add_module_functions(self,api,module_name):
        try:
            module = __import__(module_name)
            for name , obj in inspect.getmembers(module):
                if callable(obj):
                    api.add(f"{module_name}.{name}")
        except ImportError:
            print(f"Moudle {module_name} could not imported.")

    def add_third_party_modules(self, api):
        """Add third-party modules installed via pip using jedi."""
        try:
        # Create a static list of currently loaded module names
            installed_modules = list(sys.modules.keys())
            for module_name in installed_modules:
                if module_name not in sys.builtin_module_names:
                    self.add_module_functions(api, module_name)
        except Exception as e:
            print(f"Error while adding third-party modules: {e}")

def load_stylesheet(file_name):  # Function to load a stylesheet from a file.

    with open(file_name, 'r') as file:  # Opening the file in read mode.

        return file.read()  # Returning the content of the file.


def main():  # Main function.

    app = QApplication([])  # Creating a QApplication instance.

    stylesheet = load_stylesheet("styles/style.qss")  # Loading the stylesheet.

    # Setting the stylesheet for the application.
    app.setStyleSheet(stylesheet)

    editor = UI()  # Creating an instance of the UI class.

    editor.show()  # Showing the main window.

    app.exec_()  # Starting the application event loop.


if __name__ == '__main__':  # Checking if the script is being run directly.

    main()  # Calling the main function.