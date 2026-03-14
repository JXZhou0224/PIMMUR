prepend_prompt = """
You are in a virtual chatroom. Below is a description of yourself.
{profile}

----

You and others are discussing the following topic:
{topic}

----
Never mix up yourself with others.
Here are the history of past conversations:
{memory}

----


"""

chat_prompt = prepend_prompt + """
Now, it is your turn to speak.
Please express your opinion and output what you will send to others.
"""

query_prompt = prepend_prompt + """
You have exited the group discussion.
Now, please answer the following question, please be concise. At the last line, output the answer with no explanation:
{query}
"""