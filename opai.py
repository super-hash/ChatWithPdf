import openai
openai.api_key = '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'
completion = openai.ChatCompletion.create(
   model="gpt-3.5-turbo",
    messages=[
     {"role": "user", "content": "你好，你是Openai吗"}
   ]
 )
print(completion.choices[0].message['content'])