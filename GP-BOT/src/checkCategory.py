import openai
import ast
import os
from dotenv import load_dotenv

def checkCatos(Catos, word):
  load_dotenv()
  openai.api_key = os.getenv('API_KEY')
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "Some people play scattergories, you're here to check if the word given correspond to the category, for instance apple is a fruit but table is not, so in first case you answer true and in second example you answer false."},
      {"role": "user", "name":"exqmple_user", "content": "Category: capital, Word: paris"},
      {"role": "system", "name":"example_assistant", "content": "True"},
      {"role": "user", "name":"exqmple_user", "content": "Category: animal, Word: sky"},
      {"role": "system", "name":"example_assistant", "content": "False"},
      {"role": "user", "content": f"Category: {Catos}, Word: {word}"}
    ]
  )
  
  res = completion.choices[0].message.content
  res = ast.literal_eval(res)
  
  if res is True:
      return True
  elif res is False:
      return False
  else :
     raise


print(checkCatos("capital", 'Canada'))