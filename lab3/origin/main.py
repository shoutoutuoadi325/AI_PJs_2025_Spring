# 这是一个 DMXAPI 调用 API 的 Python 例子
import requests
import json

# ------------------------------------------------------------------------------------
#         3秒步接入 DMXAPI ：  修改 Key 和 Base url (https://www.dmxapi.com)
# ------------------------------------------------------------------------------------
url = "https://api.gptsapi.net/v1/chat/completions"   # 这里不要用 openai base url，需要改成DMXAPI的中转 https://www.dmxapi.com ，下面是已经改好的。

payload = json.dumps({
   "model": "gpt-4o",  # 这里是你需要访问的模型，改成上面你需要测试的模型名称就可以了。
   "messages": [
      {
         "role": "system",
         "content": "You are a helpful assistant."
      },
      {
         "role": "user",
         "content": "xxxxx"
      }
   ]
})
headers = {
   'Accept': 'application/json',
   'Authorization': 'sk-xxxxxxxxxxxxxxxx', # 这里放你的 DMXapi key
   'User-Agent': 'DMXAPI/1.0.0 (https://www.dmxapi.com)',  # 这里也改成 DMXAPI 的中转URL https://www.dmxapi.com，已经改好
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
# print(response.text)  # 这里是你需要的返回结果

# 将response转为json格式
response_json = json.loads(response.text)
print(response_json['choices'][0]['message']['content'])  # 这里是你需要的返回结果

