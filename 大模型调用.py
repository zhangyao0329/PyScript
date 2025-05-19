import openai

api_key = "sk-9qCNNk6DcGAvi87U0d810f9d6c614f169aBf45E07b9a46C5"
base_url = "https://api.xty.app/v1"

openai.api_key = api_key
openai.api_base = base_url

msg = input("请输入你的消息：")  # 提示用户输入消息

response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": msg}
    ]
)

# 从响应中提取生成的消息内容
content = response['choices'][0]['message']['content']

print("生成的回复：", content)
