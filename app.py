from google import genai
from google.genai import types
import os
import sys
import shutil
import subprocess
from flask import Flask, request, abort, send_file, render_template


app = Flask(__name__)

def install_and_import(package):
        try:
            # 尝试直接导入
            __import__(package)
        except ImportError:
            # 如果导入失败，则安装到 /tmp 目录
            print(f"'{package}' not found. Installing to /tmp...")
            # 使用 subprocess 调用 pip 命令
            try:
                shutil.copytree("./HomepageBuilder-a", "/tmp/HomepageBuilder-a")
            except FileExistsError as e:
                print("What a OneYear? FileExists?\n"+str(e))
                
            subprocess.check_call([sys.executable, "-m", "pip", "install", "/tmp/HomepageBuilder-a/.", "--target", "/tmp"])
            
            # 将 /tmp 添加到 sys.path
            if '/tmp' not in sys.path:
                sys.path.insert(0, '/tmp')
            
            # 再次尝试导入
            __import__("homepagebuilder")

def generate_response(query: str) -> str:
    import homepagebuilder.main
    api_key = os.getenv("api_key")
    #api_key = "See 什么 See 我删了 (*^_^*)"
    if not api_key:
        abort(500, description="服务器未配置 API Key，请检查环境变量 api_key。")

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
    """ TODO
    if searching:
        base_config.tools = [types.Tool(google_search=types.GoogleSearch())]
        app.logger.debug("联网搜索已开启。")
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
        config=base_config
    )
    print(type(response.text))
    safe_text = response.text
    
    # 创建文件夹
    if not os.path.exists("/tmp/Homepage"):
        os.makedirs("/tmp/Homepage", exist_ok=True)
        shutil.copytree("/var/task/BaseProject", "/tmp/Homepage", dirs_exist_ok=True)
    # 把生成的内容放到 Custom.md
    try:
        with open(f"/tmp/Homepage/libraries/Custom.md", "w", encoding="utf-8") as f:
            f.write(str(safe_text)) # Holy shit sometimes it does not work!(Maybe)
    except Exception as e:
        print(str(e))

    os.chdir("/tmp/Homepage")
    sys.argv = ['prog_name', 'build', '--output-path', 'Custom.xaml']
    homepagebuilder.main.main()
    with open("/tmp/Homepage/Custom.xaml", "r", encoding="utf-8") as raw:
        xaml = raw.read()
    return xaml

@app.route("/Custom.xaml", methods=["GET"])
def trigger():
    
    # 给 default，避免 None
    q = request.args.get("q", "").strip()
    if not q:
        abort(400, description="缺少 q 参数。")

    #searching_flag = request.args.get("searching", "false").lower() == "true"
    install_and_import("homepagebuilder")
    #return generate_response(query=q, searching=searching_flag)
    return generate_response(query=q)

@app.route("/Custom.json")
def send():
    q = request.args.get("q", "").strip()
    with open("/tmp/Custom.json", "w", encoding="utf-8") as fa:
        fa.write('{"Title": "'+q+'","Description": "PCL Intelligence Homepage"}')
    return send_file("/tmp/Custom.json", as_attachment=True)

@app.route("/")
def main():
    return render_template('index.html')