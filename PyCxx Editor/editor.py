from PyQt5.QtCore import (

    Qt, 

    pyqtSlot,

    QObject,

    QThread,

    pyqtSignal

) # Importing necessary modules from PyQt5.QtCore for Qt functionalities, signals and threads.



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

) # Importing various PyQt5.QtWidgets modules for creating GUI elements like windows, layouts, buttons, text editors, etc.



from PyQt5.QtGui import QColor # Importing QColor from PyQt5.QtGui for color settings.

from PyQt5.Qsci import (

    QsciScintilla,

    QsciLexerPython,

    QsciLexerCPP,

    QsciLexerHTML,

    QsciLexerCSS,

    QsciLexerJavaScript

) # Importing QsciScintilla and various lexer modules from PyQt5.Qsci for advanced code editor functionalities.



import google.generativeai as gemini # Importing the Google Gemini AI library.



import os # Importing the os module for operating system functionalities.
import platform #Importing the platform module for system functionalities.

import subprocess # Importing the subprocess module for running external commands.

import shutil # Importing the shutil module for high-level file operations.

import sys # Importing the sys module for system-specific parameters and functions.

from install import prompt_pkg

class GeminiThreat(QThread): # Defining a class GeminiThreat that inherits from QThread for handling AI operations in a separate thread.

    progress = pyqtSignal(str) # Defining a pyqtSignal to emit progress updates as strings.

    def __init__(self,chat_area:QTextEdit,input:str): # Constructor for GeminiThreat, takes chat area and input string as arguments.

        super(QThread,self).__init__() # Calling the superclass constructor to initialize the QThread.

        self.chat_area = chat_area # Assigning the chat area widget to the instance.

        self.input_text = input # Assigning the input text to the instance.

        # self.finished = pyqtSignal() #commented out: Unnecessary signal, QThread already has finished signal.

        self.ai = GeminiAi("AIzaSyAjBYJJLqpIkWi7owhN_sdMDkd64GqeXoo", "gemini-1.5-flash") # Initializing GeminiAi object with API key and model.

    def run(self): # Defining the run method, which is executed when the thread starts.

        markdown = '' # Initializing an empty string to store the markdown response.

        for chunk in self.ai.generateAnswer(self.input_text): # Iterating through the chunks of the AI response.

            # self._chat_area.insertPlainText(chunk.text) #commented out:  Replaced by accumulating markdown

            # self._chat_area.repaint() #commented out: Repaint handled by progress signal

            markdown += chunk.text # Appending the text of each chunk to the markdown string.

            self.progress.emit(markdown) # Emitting the updated markdown as a progress signal.

            



class GeminiAi: # Defining a class GeminiAi for interacting with the Google Gemini AI.

    def __init__(self, api_key:str, ai_model:str): # Constructor for GeminiAi, takes API key and model name as arguments.

        gemini.configure(api_key=api_key) # Configuring the Gemini API with the provided API key.

        self._model = gemini.GenerativeModel(ai_model) # Creating a GenerativeModel object with the specified model.

        self._chat = self._model.start_chat() # Starting a chat session with the model.

    

    def generateAnswer(self,input:str): # Method to generate an answer from the AI model, takes input string as argument.

        response = self._model.generate_content(input,stream=True) # Generating content from the model with streaming enabled.

        return response # Returning the streamed response.

    def loadPrompt(self,file_name:str): # Method to load a prompt from a file, takes file name as argument.

        with open(file_name) as file: # Opening the file in read mode.

            prompt_enhance = file.read() # Reading the content of the file.

        return prompt_enhance # Returning the prompt content.





class UI(QWidget): # Defining a class UI that inherits from QWidget to represent the main user interface.

    def __init__(self): # Constructor for UI.

        super().__init__() # Calling the superclass constructor to initialize the QWidget.

        self.resize(1080, 720) # Setting the initial size of the window.

        self.setWindowTitle('PyCxx IDE') # Setting the title of the window.

        self.__folder = QPushButton('Folder') # Creating a Folder button.

        self.__folder.setObjectName('btn') # Setting the object name for styling purposes.

        self.__newfile = QPushButton('New') # Creating a New button.

        self.__newfile.setObjectName('btn') # Setting the object name for styling purposes.

        self.__openfile = QPushButton('Open') # Creating an Open button.

        self.__openfile.setObjectName('btn') # Setting the object name for styling purposes.

        self.__savefile = QPushButton('Save') # Creating a Save button.

        self.__savefile.setObjectName('btn') # Setting the object name for styling purposes.

        self.__runProg = QPushButton('Run') # Creating a Run button.

        self.__runProg.setObjectName('btn') # Setting the object name for styling purposes.



        self.menu_bar_layout = QHBoxLayout() # Creating a horizontal layout for the menu bar.

        self.menu_bar_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop) # Aligning the layout to center and top.

        self.menu_bar_layout.addWidget(self.__folder) # Adding the Folder button to the layout.

        self.menu_bar_layout.addWidget(self.__newfile) # Adding the New button to the layout.

        self.menu_bar_layout.addWidget(self.__openfile) # Adding the Open button to the layout.

        self.menu_bar_layout.addWidget(self.__savefile) # Adding the Save button to the layout.

        self.menu_bar_layout.addWidget(self.__runProg) # Adding the Run button to the layout.



        self.ide = Editor() # Creating an instance of the Editor class.

        self._ai = GeminiAi("AIzaSyAjBYJJLqpIkWi7owhN_sdMDkd64GqeXoo", "gemini-1.5-flash") # Initializing GeminiAi object.

        

        self._prompt_command = QComboBox() # Creating a combo box for selecting AI commands.

        self._prompt_command.addItem('None') # Adding 'None' as an item.

        self._prompt_command.addItem('explain') # Adding 'explain' as an item.

        self._prompt_command.addItem('fixt') # Adding 'fixt' as an item.

        self._prompt_command.addItem('comment') # Adding 'comment' as an item.

        self._prompt = QLineEdit() # Creating a line edit for user input.

        self._prompt.setObjectName('prompt') # Setting the object name for styling purposes.

        self._send_button = QPushButton('Send') # Creating a Send button.

        self._send_button.setObjectName('send') # Setting the object name for styling purposes.

        self._send_button.clicked.connect(self.runThread) # Connecting the clicked signal to the runThread method.





        self._file_tree = QTreeWidget() # Creating a tree widget to display files.

        self._file_tree.setObjectName('tree_view') # Setting the object name for styling purposes.

        self._file_tree.setHeaderHidden(True) # Hiding the header of the tree widget.

        self._file_tree.itemClicked.connect(self.ide.loadTreeFile) # Connecting the itemClicked signal to the loadTreeFile method.



        self.left_side_layout = QVBoxLayout() # Creating a vertical layout for the left side.

        self.left_side_layout.setObjectName('left_container') # Setting the object name for styling purposes.

        self.left_side_layout.addLayout(self.menu_bar_layout) # Adding the menu bar layout to the left side layout.

        self.left_side_layout.addWidget(self._file_tree) # Adding the file tree widget to the left side layout.



        self.prompt_layout = QHBoxLayout() # Creating a horizontal layout for the prompt area.

        self.prompt_layout.addWidget(self._prompt_command) # Adding the combo box to the prompt layout.

        self.prompt_layout.addWidget(self._prompt) # Adding the line edit to the prompt layout.

        self.prompt_layout.addWidget(self._send_button) # Adding the send button to the prompt layout.



        self.right_side_layout = QVBoxLayout() # Creating a vertical layout for the right side.

        self.right_side_layout.addLayout(self.prompt_layout) # Adding the prompt layout to the right side layout.

        self.right_side_layout.addWidget(self.ide) # Adding the code editor to the right side layout.



        self._chat_area = QTextEdit() # Creating a text edit for the chat area.

        self._chat_area.setReadOnly(True) # Setting the chat area to read-only.

        self.dock_layout = QDockWidget() # Creating a dock widget for the chat area.

        self.dock_layout.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable) # Making the dock widget closable.

        self.dock_layout.setWidget(self._chat_area) # Setting the chat area as the widget of the dock widget.

        self.dock_layout.hide() # Hiding the dock widget initially.



        self.__folder.clicked.connect(self.showFiles) # Connecting the clicked signal of the Folder button to the showFiles method.

        self.__newfile.clicked.connect(self.ide.newFile) # Connecting the clicked signal of the New button to the newFile method.

        self.__openfile.clicked.connect(self.openAndShowFilesFolder) # Connecting the clicked signal of the Open button to the openAndShowFilesFolder method.

        self.__savefile.clicked.connect(self.ide.saveFile) # Connecting the clicked signal of the Save button to the saveFile method.

        self.__runProg.clicked.connect(self.ide.run_program) # Connecting the clicked signal of the Run button to the run_program method.



        self.main_layout = QHBoxLayout() # Creating a horizontal layout for the main window.

        self.main_layout.addLayout(self.left_side_layout) # Adding the left side layout to the main layout.

        self.main_layout.addLayout(self.right_side_layout, 80) # Adding the right side layout to the main layout with a stretch factor of 80.

        self.main_layout.addWidget(self.dock_layout, 40) # Adding the dock widget to the main layout with a stretch factor of 40.

        # self.main_layout.addWidget(self.ide,75) #commented out: Redundant, IDE already added above.



        self.setLayout(self.main_layout) # Setting the main layout for the window.



    def openAndShowFilesFolder(self): # Method to open a file and populate the file tree.

        self.ide.openFile() # Opening a file using the openFile method of the Editor class.

        self.populateTree(os.path.dirname(self.ide.file_path)) # Populating the file tree with the files in the directory of the opened file.



    def add_tree_items(self, parent_item, path): # Recursive method to add items to the file tree.

        extension = ['.py', '.c', '.cpp', '.txt', # List of supported file extensions.

                    '.md', '.html', '.css', '.js']

        for item_name in os.listdir(path): # Iterating through the items in the given path.

            item_path = os.path.join(path, item_name) # Creating the full path of the item.



            if os.path.isdir(item_path): # Checking if the item is a directory.

                tree_item = QTreeWidgetItem(parent_item) # Creating a tree item for the directory.

                tree_item.setText(0, item_name) # Setting the text of the tree item to the directory name.

                tree_item.setData(0, Qt.UserRole, item_path) # Setting the data of the tree item to the directory path.

                self.add_tree_items(tree_item, item_path) # Recursively calling the method for subdirectories.

                tree_item.setExpanded(False) # Setting the directory to be initially collapsed.

            else: # If the item is not a directory.

                if any(item_name.endswith(ext) for ext in extension): # Checking if the item has a supported extension.

                   tree_item = QTreeWidgetItem(parent_item) # Creating a tree item for the file.

                   tree_item.setText(0, item_name) # Setting the text of the tree item to the file name.

                   tree_item.setData(0, Qt.UserRole, item_path) # Setting the data of the tree item to the file path.



    def showFiles(self): # Method to show a file dialog to select a folder.

        folder = QFileDialog.getExistingDirectory(self, 'Select Folder') # Showing a file dialog to select a folder.

        self.populateTree(folder) # Populating the file tree with the files in the selected folder.



    def populateTree(self, folder): # Method to populate the file tree with the files in a given folder.

        self._file_tree.clear() # Clearing the file tree.

        if folder: # Checking if a folder was selected.

            self.ide.dir_path = folder # Setting the directory path in the Editor class.

            root_item = QTreeWidgetItem(self._file_tree) # Creating a root item for the folder.

            root_item.setText(0, os.path.basename(folder)) # Setting the text of the root item to the folder name.

            root_item.setData(0, Qt.UserRole, folder) # Setting the data of the root item to the folder path.

            root_item.setExpanded(True) # Setting the root item to be initially expanded.

            self.add_tree_items(root_item, folder) # Calling the add_tree_items method to add items to the tree.

    

    def collectInput(self): # Method to collect user input for the AI.

        if self._prompt_command.currentIndex() == 0: #none

            input_prompt = '' # Setting input_prompt to an empty string if 'None' is selected.

        elif self._prompt_command.currentIndex() == 1: #explain

            input_prompt = self._ai.loadPrompt('prompt_train/explain.txt') # Loading the 'explain' prompt from a file.

            print('explain') # Printing 'explain' to the console.

        elif self._prompt_command.currentIndex() == 2: #fixt

            input_prompt = self._ai.loadPrompt('prompt_train/fixt.txt') # Loading the 'fixt' prompt from a file.

        elif self._prompt_command.currentIndex() == 3: #comment

            input_prompt = self._ai.loadPrompt('prompt_train/comment.txt')



        input_command = self._prompt.text() # Getting the text from the prompt line edit.

        input_code = self.ide.text() # Getting the code from the code editor.

        self._prompt.clear() # Clearing the prompt line edit.

        final_input = input_prompt + input_command + '\n' + input_code # Combining the prompts, command, and code into a single string.



        return final_input # Returning the combined input string.



    def runThread(self): # Method to run the AI thread.

        self.dock_layout.show() # Showing the dock widget.

        self.dock_layout.repaint() # Repainting the dock widget.

        

        self.ai_work = GeminiThreat(self._chat_area,self.collectInput()) # Creating an instance of the GeminiThreat class.

        self.ai_work.progress.connect(self.updateChatArea) # Connecting the progress signal to the updateChatArea method.

        self.ai_work.start() # Starting the AI thread.



    def updateChatArea(self, text: str): # Method to update the chat area with the AI response.

        self._chat_area.setMarkdown(text) # Setting the markdown text in the chat area.

        self._chat_area.repaint() # Repainting the chat area. 



class Editor(QsciScintilla): # Defining a class Editor that inherits from QsciScintilla for code editing.

    def __init__(self): # Constructor for Editor.

        super().__init__() # Calling the superclass constructor to initialize the QsciScintilla.

        self.setMarginType(0, QsciScintilla.NumberMargin) # Setting the margin type to number margin.

        self.setMarginWidth(0, '00000')  # for 0000 digit line of code # Setting the width of the margin.

        self.setMarginsForegroundColor(QColor("#9da8af")) # Setting the color of the margin.

        self.setWrapMode(QsciScintilla.WrapWord) # Setting the wrap mode to wrap by word.

        self.setWrapVisualFlags(QsciScintilla.WrapFlagByText) # Setting the visual flags for wrapping.

        self.setWrapIndentMode(QsciScintilla.WrapIndentIndented) # Setting the indent mode for wrapping.

        self.setFolding(QsciScintilla.PlainFoldStyle) # Setting the folding style.

        self.setCaretLineVisible(True) # Making the caret line visible.

        self.setCaretLineBackgroundColor(QColor('#e6ffe6')) # Setting the background color of the caret line.

        self.setAutoIndent(True) # Enabling auto-indent.

        self.setAutoCompletionSource(QsciScintilla.AcsAll)  # Enable all sources for auto completion (api + editor stream)

        self.setAutoCompletionThreshold(1) #threshold for the number of character the suggestion will show




        self.file_path = '' # Initializing the file path to an empty string.

        self.dir_path = '' # Initializing the directory path to an empty string.



    def loadFile(self, filepath): # Method to load a file into the editor.

        if os.path.isfile(filepath): # Checking if the file exists.

            main_file_context = open(filepath, 'r') # Opening the file in read mode.

            file_text = main_file_context.read() # Reading the content of the file.

            self.setText(file_text) # Setting the text of the editor to the file content.

            extension = filepath.split(".")[-1] # Getting the file extension.

            match extension: # Matching the extension to set the appropriate lexer.

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

            self.setLexer(self.lexer) # Setting the lexer for syntax highlighting.



    def openFile(self): # Method to open a file using a file dialog.

        filename, _ = QFileDialog().getOpenFileName() # Showing a file dialog to open a file.

        self.file_path = filename # Setting the file path.

        self.dir_path = os.path.dirname(filename) # Setting the directory path.

        self.loadFile(filename) # Loading the file into the editor.



    def loadTreeFile(self, item, col): # Method to load a file from the file tree.

        texts = [] # Initializing an empty list to store the text of the tree items.

        while item is not None: # Iterating through the tree items until the root item is reached.

            texts.insert(0, item.text(0)) # Inserting the text of the tree item at the beginning of the list.

            item = item.parent() # Getting the parent item.

        filename = "/".join(texts[1:]) # Joining the text of the tree items to create the file name.

        filepath = os.path.join(self.dir_path, filename) # Creating the full path of the file.

        self.file_path = filepath # Setting the file path.

        self.loadFile(filepath) # Loading the file into the editor.



    def newFile(self): # Method to create a new file.

        fileName, _ = QFileDialog.getSaveFileName(self, 'Save File', os.getcwd(

        ), 'Python Files (*.py);;C Files (*.c);;C++ Files (*.cpp)') # Showing a file dialog to save a new file.

        if fileName: # Checking if a file name was selected.

            if not os.path.exists(fileName): # Checking if the file already exists.

                with open(fileName, 'w') as file: # Creating the file.

                   file.write('') # Writing an empty string to the file.



    def saveFile(self): # Method to save a file.

        filename = None # Initializing the file name to None.

        if not self.file_path: # Checking if the file path is empty.

            self.openFile() # Opening a file using a file dialog.

        else:

            filename = self.file_path # Setting the file name to the file path.



        if filename: # Checking if a file name was selected.

            with open(filename, 'w') as file: # Opening the file in write mode.

                file_text = self.text() # Getting the text from the editor.

                cleaned_text = file_text.rstrip() # Removing trailing whitespace from the text.

                file.write(cleaned_text) # Writing the cleaned text to the file.

                # print(self.text()) #commented out: Unnecessary print statement.



        print("file saved") # Printing "file saved" to the console.


    def openTerminalRunCommand(self, command):
        if platform.system() == 'Windows':
            # Ensure the command is passed as a list with explicit path
            subprocess.Popen(["powershell", "-NoExit", "-Command", f"& {command}"])
        else:
            subprocess.Popen(["bash", "-c", f"{command}"])


    def is_executable_available(self, executable_name): # Method to check if an executable is available on the system.

        """Check if a given executable is available on the system."""

        return shutil.which(executable_name) is not None # Returning True if the executable is found, False otherwise.



    def run_program(self, file_path):
        """Run the program based on its file type."""
        file_path = self.file_path
        
        file_path = file_path.replace("\\", "/")
    
        # Write to file
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    # cleaned_text = self.text().rstrip()  # Assuming self.text() exists
                    file.write(self.text())
            except Exception as e:
                print(f"Error writing to file: {e}")
                return
    
        # Get file extension
        base_name, file_extension = os.path.splitext(file_path)
        print("base_name:  ",base_name)
        print("dir path: ",self.dir_path)
        print("file path: " , file_path)
        # Determine action based on file type
        if file_extension == ".py":
            # Python file
            if self.is_executable_available("python"):
                command = f"python '{file_path}'"
                self.openTerminalRunCommand(command)
            else:
                print("Python interpreter not found.")
                prompt_pkg('python')
    
        elif file_extension in [".c", ".cpp"]:
            compiler = "gcc" if file_extension == ".c" else "g++"
            os.chdir(self.dir_path)
            if self.is_executable_available(compiler):
                output_file = (f"{base_name.split('/')[-1]}.exe" if platform.system() == "Windows" else f"{base_name.split('/')[-1]}.out")
                compile_command = [compiler, file_path, "-o", output_file]
                try:
                    compile_process = subprocess.run(compile_command, check=True)
                    print("Compilation successful. Running the program...")
                    # Run the program with the correct path
                    output_command = output_file.replace("\\","/").split('.')[0]
                    self.openTerminalRunCommand(f"./{output_command}")
                except subprocess.CalledProcessError:
                    print("Compilation failed.")
            else:
                print(f"{compiler} compiler not found.")
                prompt_pkg(compiler)

        else:
            print("Unsupported file type. Please provide a '.py', '.c', or '.cpp' file.")






def load_stylesheet(file_name): # Function to load a stylesheet from a file.

    with open(file_name, 'r') as file: # Opening the file in read mode.

        return file.read() # Returning the content of the file.





def main(): # Main function.

    app = QApplication([]) # Creating a QApplication instance.

    stylesheet = load_stylesheet("styles/style.qss") # Loading the stylesheet.

    app.setStyleSheet(stylesheet) # Setting the stylesheet for the application.

    editor = UI() # Creating an instance of the UI class.

    editor.show() # Showing the main window.

    app.exec_() # Starting the application event loop.





if __name__ == '__main__': # Checking if the script is being run directly.

    main() # Calling the main function.