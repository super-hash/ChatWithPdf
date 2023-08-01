import openai
""""填入你的openai key"""
openai.api_key = 'sk-'
completion = openai.ChatCompletion.create(
   model="gpt-3.5-turbo",
    messages=[
     {"role": "user", "content": "你好，你是Openai吗"}
   ]
 )
print(completion.choices[0].message['content'])
