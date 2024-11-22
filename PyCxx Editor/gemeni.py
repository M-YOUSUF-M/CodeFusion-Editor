import pathlib
import textwrap

import google.generativeai as gemini


gemini.configure(api_key='AIzaSyAjBYJJLqpIkWi7owhN_sdMDkd64GqeXoo')

"""
for m in gemini.list_models():
    print(m.name)
"""
model = gemini.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat()
question = ' '
"""
while(question != "exit"):
    question = input("text: ")
    response = chat.send_message(question,stream=True)

    for chunk in response:
        print(chunk.text)
        print('_'* 80)
print(chat.history)
"""
try:
    text  = input("$#$#$#$")
    response = model.generate_content(text,stream=True)
    for chunk in response:
        print(chunk.text)
    # print(response.text)
    print(response.prompt_feedback)
except Exception as e:
    print(e)



