"""AI In PCL Flask"""
from google import genai
from google.genai import types
import os
import flask

app = flask.Flask(__name__)
@app.route("/query")
def get(query, searching:bool=False):
    api_key = os.getenv("api_key")
    if not api_key or api_key == "":
        print("没有找到 API Key。请检查后重试。")
    client = genai.Client(api_key=api_key)
    if searching:
        print("联网搜索已开启。\n")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0), # 深度思考关闭
                system_instruction='You are a helpful assistant. Your name is PAI. You must use Simplified Chinese to answer. You are an AI assistant developed by PCL-Community, with responses generated based on the Google Gemini 2.5 Flash model. 在中文和英文之间加入一个空格.', # 预设提示词
                tools=[types.Tool(google_search=types.GoogleSearch())] # 联网搜索 
            )
        )
    else:
        print("联网搜索已关闭。\n")
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0), # 深度思考关闭
            system_instruction='You are a helpful assistant. Your name is PAI. You must use Simplified Chinese to answer. You are an AI assistant developed by PCL-Community, with responses generated based on the Google Gemini 2.5 Flash model. 在中文和英文之间加入一个空格.', # 预设提示词            
        )
    )
    
    return "<TextBlock Text="+response.text+"/>"