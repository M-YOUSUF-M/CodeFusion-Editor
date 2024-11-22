from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication , QWidget,
    QLabel,QTextEdit,QPushButton,QLineEdit,
    QVBoxLayout,QHBoxLayout 
)
from PyQt5.QtGui import (
    QColor
)

from editor import Editor

import google.generativeai as gemini

class UI(QWidget):
    def __init__(self,api_key:str,model:str):
        super().__init__()
        self.resize(720,720)
        self.setWindowTitle('Ai Assistant')

        self._prompt = QLineEdit()
        self._prompt.setPlaceholderText('enter your command')
        self._send_button = QPushButton('send')
        self._send_button.clicked.connect(self.printOutput)

        self.prompt_layout = QHBoxLayout()
        self.prompt_layout.addWidget(self._prompt)
        self.prompt_layout.addWidget(self._send_button)

        self._editor_area = Editor()
        self._chat_area = QTextEdit()
        self._chat_area.setReadOnly(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.prompt_layout)
        self.main_layout.addWidget(self._editor_area)
        self.main_layout.addWidget(self._chat_area)

        self.setLayout(self.main_layout)

        self._ai = GeminiAi(api_key , model)

    def collectInput(self):
        input_command = self._prompt.text()
        input_code = self._editor_area.text()
        self._prompt.clear()
        final_input = input_command + '\n' + input_code
        return final_input
    def printOutput(self):
        for chunk in self._ai.generateAnswer(self.collectInput()):
            self._chat_area.insertPlainText(chunk.text)
        self._chat_area.append('\n')

        
class GeminiAi:
    def __init__(self,api_key:str,ai_model:str):
        gemini.configure(api_key=api_key)
        self._model = gemini.GenerativeModel(ai_model)
        self._chat = self._model.start_chat() 
    
    def generateAnswer(self,input:str):
        response = self._model.generate_content(input,stream=True)
        return response

        

if __name__ == '__main__':
    api_key = 'AIzaSyAjBYJJLqpIkWi7owhN_sdMDkd64GqeXoo'  #I'm very consious about security :)
    ai_model = 'gemini-1.5-flash'
    app = QApplication([])
    context = UI(api_key,ai_model)
    context.show()
    app.exec_()
    


