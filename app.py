from google import genai
from google.genai import types
import os
from flask import Flask, request, abort

app = Flask(__name__)

# 建议把 get 函数改名为 generate_response，更语义化
def generate_response(query: str, searching: bool = False) -> str:
    api_key = os.getenv("api_key")
    if not api_key:
        abort(500, description="服务器未配置 API Key，请检查环境变量 GOOGLE_API_KEY。")

    client = genai.Client(api_key=api_key)

    # 公共的 config
    base_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),  # 关闭深度思考
        system_instruction=(
            'You are a helpful assistant. Your name is PAI. '
            'You must use Simplified Chinese to answer. '
            'You are an AI assistant developed by PCL-Community. '
            '在中文和英文之间加入一个空格。'
        )
    )

    if searching:
        # 如果需要联网搜索，就给工具列表添加 GoogleSearch
        base_config.tools = [types.Tool(google_search=types.GoogleSearch())]
        app.logger.debug("联网搜索已开启。")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
        config=base_config
    )

    # 用双引号包裹 response.text，防止标签语法错误
    safe_text = response.text.replace('"', '\\"')
    return f'<TextBlock Text="{safe_text}" />'

@app.route("/query", methods=["GET"])
def trigger():
    # 给 default，避免 None
    q = request.args.get("q", "").strip()
    if not q:
        abort(400, description="缺少 q 参数。")

    searching_flag = request.args.get("searching", "false").lower() == "true"
    return generate_response(query=q, searching=searching_flag)
