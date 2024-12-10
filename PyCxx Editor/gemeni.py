

    

import pathlib

import textwrap



import google.generativeai as gemini





gemini.configure(api_key='AIzaSyAjBYJJLqpIkWi7owhN_sdMDkd64GqeXoo') # Configures the Gemini API client with an API key.  Consider using environment variables for better security.



"""

for m in gemini.list_models():

    print(m.name)

"""

# This block is commented out. It would list the available Gemini models.



model = gemini.GenerativeModel("gemini-1.5-flash") # Creates a GenerativeModel object, specifying the "gemini-1.5-flash" model.

chat = model.start_chat() # Starts a new chat session with the specified model.

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

# This block is commented out. It would allow for a conversational interaction with the model until the user types "exit".  The response is streamed and printed chunk by chunk.



try:

    text  = input("$#$#$#$") # Prompts the user for input, using a somewhat unusual prompt.

    response = model.generate_content(text,stream=True) # Generates content from the user's input, streaming the response.

    for chunk in response:

        print(chunk.text) # Prints each chunk of the streamed response.

    # print(response.text) #This line is commented out; it would print the complete response text.

    print(response.prompt_feedback) # Prints feedback related to the prompt. This might include information about the model's processing.

except Exception as e:

    print(e) # Catches and prints any exceptions that occur during the content generation process.