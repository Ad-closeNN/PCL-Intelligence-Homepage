from google import genai
from google.genai import types
import os
import time
from flask import Flask, request, abort, send_file, render_template

app = Flask(__name__)

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
            'You are an AI assistant developed by PCL-Community, with responses generated based on the Google Gemini 2.5 Flash model. '
            '在中文和英文之间加入一个空格。'
        )
    )

    if searching:
        base_config.tools = [types.Tool(google_search=types.GoogleSearch())]
        app.logger.debug("联网搜索已开启。")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
        config=base_config
    )
    print(type(response.text))
    safe_text = response.text
    
    os.system(f"mkdir /tmp/HB")
    with open(f"/tmp/HB/response.md", "w", encoding="utf-8") as f:
        f.write(str(safe_text))
    content = """name: external
    fill:
    templates:
        - MarkdownCard
        - Raw
    """
    with open(f"/tmp/HB/__LIBRARY__.yml", "w", encoding="utf-8") as f:
        f.write(content)
    try:
        os.system('builder build --output-path "/tmp/HB/Custom.xaml"')
    except:
        os.system("cd HomepageBuilder-0.14.5")
        os.system("pip install .")
    os.system("cd HomepageBuilder-0.14.5/PCL-Intelligence")
    with open("/tmp/HB/Custom.xaml", "r", encoding="utf-8") as re:
        xaml = re.read()
    return xaml

@app.route("/Custom.xaml", methods=["GET"])
def trigger():
    
    # 给 default，避免 None
    q = request.args.get("q", "").strip()
    if not q:
        abort(400, description="缺少 q 参数。")

    searching_flag = request.args.get("searching", "false").lower() == "true"
    
    return generate_response(query=q, searching=searching_flag)

@app.route("/Custom.json")
def send():
    q = request.args.get("q", "").strip()
    with open("/tmp/Custom.json", "w", encoding="utf-8") as fa:
        fa.write('{"Title": "'+q+'","Description": "PCL Intelligence"}')
    return send_file("/tmp/Custom.json", as_attachment=True)

@app.route("/")
def main():
    os.system("cd HomepageBuilder-0.14.5 && sudo pip install .")
    return render_template('index.html')
