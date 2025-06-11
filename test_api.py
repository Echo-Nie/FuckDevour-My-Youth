from openai import OpenAI

url = 'https://api.siliconflow.cn/v1/'
api_key = 'NTSoftware-Devour-My-Youth'

client = OpenAI(
    base_url=url,
    api_key=api_key
)

content = ""
reasoning_content=""
messages = [
    {"role": "user", "content": "你是谁？"}
]
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1",
    messages=messages,
    stream=True,
    max_tokens=4096
)

is_first_reasoning = True
is_content_start = True

for chunk in response:
    if chunk.choices[0].delta.content:
        if not is_first_reasoning and is_content_start:
            print("</think>")
            is_content_start = False
        content += chunk.choices[0].delta.content
        print(chunk.choices[0].delta.content, end='')

    if chunk.choices[0].delta.reasoning_content:
        if is_first_reasoning:
            print("</think>", end='')
            is_first_reasoning = False
        reasoning_content += chunk.choices[0].delta.reasoning_content
        print(chunk.choices[0].delta.reasoning_content, end='')