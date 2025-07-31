from google import genai
from google.genai import types
import os
import sys
import shutil
import subprocess
import zipfile
from flask import Flask, request, abort, send_file, render_template


app = Flask(__name__)

def install_and_import(package):
        try:
            # 尝试直接导入
            __import__(package)
        except ImportError:
            # 如果导入失败，则安装到 /tmp 目录
            print(f"'{package}' 未安装。")
            # 使用 subprocess 调用 pip 命令
            try:
                #os.makedirs("/tmp/HomepageBuilder-a", exist_ok=True)

                with zipfile.ZipFile("/var/task/HomepageBuilder-0.14.8.zip", 'r') as zip_ref:
                    zip_ref.extractall("/tmp/")
            except FileExistsError as e:
                print("文件存在：\n"+str(e))
            shutil.copy2("/var/task/ProjectInfo.yml", "/tmp/HomepageBuilder-0.14.8/src/homepagebuilder/resources/configs/ProjectInfo.yml")
            shutil.copy2("/var/task/setup.py", "/tmp/HomepageBuilder-0.14.8/setup.py")

            subprocess.check_call([sys.executable, "-m", "pip", "install", "/tmp/HomepageBuilder-0.14.8/.", "--target", "/tmp/"])
            
            # 将 /tmp 添加到 sys.path
            if '/tmp/' not in sys.path:
                sys.path.insert(0, '/tmp/')
            
            # 再次尝试导入
            __import__("homepagebuilder")

def generate_response(query: str, searching: bool):
    import homepagebuilder.main # 有用吗我不知道
    api_key = os.getenv("api_key")
    #api_key = "See 什么 See 我删了 (*^_^*)"
    if not api_key:
        abort(500, description="服务器未配置 API Key，请检查环境变量 api_key。")

    client = genai.Client(api_key=api_key)

    base_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),  # 关闭深度思考
        system_instruction=(
            'You must speak Simplified Chinese.'
            'You are an AI assistant, with responses generated based on the Google Gemini 2.5 Flash model.'
            '在中文和英文之间加入一个空格。'
            'Use measurement units common in Mainland China (meters, kilograms, degrees Celsius, etc.).'
            'Use China’s official currency (Renminbi, “yuan”).'
            'Consider Mainland China’s holidays, customs, geography, and cuisine.'
            'When giving advice, reference Mainland China’s policies, regulations, city transportation, and climate.'
            'Express time in Beijing Time (UTC+8) and dates in the format “YYYY 年 MM 月 DD 日”.'
            'Maintain a written, formal tone in Simplified Chinese, adhering to Mainland China’s online and publishing standards without using Traditional Chinese or minority scripts.'
        )
    )
    
    if searching:
        base_config.tools = [types.Tool(google_search=types.GoogleSearch())]
        print("联网搜索已开启。")
    
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", # 自行调整
        contents=query,
        config=base_config
    )
    
    safe_text = response.text
    """使用 HomepageBuilder 构建 Markdown -> XAML"""
    # 创建文件夹
    if not os.path.exists("/tmp/Homepage"):
        os.makedirs("/tmp/Homepage", exist_ok=True)
        shutil.copytree("/var/task/BaseProject", "/tmp/Homepage", dirs_exist_ok=True)
    # 把生成的内容放到 Custom.md
    try:
        with open(f"/tmp/Homepage/libraries/Custom.md", "w", encoding="utf-8") as f:
            f.write(str(safe_text))
    except Exception as e:
        print(str(e))

    os.chdir("/tmp/Homepage")
    sys.argv = ['prog_name', 'build', '--output-path', 'Custom_base.xaml']
    homepagebuilder.main.main()
    with open("/tmp/Homepage/Custom_base.xaml", "r", encoding="utf-8") as raw:
        xaml = raw.readlines()
        with open("/tmp/Homepage/Custom.xaml", "w", encoding="utf-8") as f:
            for line in xaml:
                if line.startswith('<local:MyCard Title="'):
                    f.write(f'<local:MyCard Title="{query}"'+' CanSwap="False" IsSwaped="False" Style="{StaticResource Card}" >')
                else:
                    f.write(line)
    
    with open("/tmp/Homepage/Custom.xaml", "r", encoding="utf-8") as raw:
        xaml = raw.read()
    return xaml

@app.route("/Custom.xaml", methods=["GET"])
def trigger():
    q = request.args.get("q", "").strip()
    if not q or q == "":
        #abort(400, description="缺少 query(q) 参数。")
        with open("/var/task/templates/empty.html", "r", encoding="utf-8") as f:
            content = f.read()
        return content
    search_flag = request.args.get("search", "false").lower() == "true" # bool var
    install_and_import("homepagebuilder")
    return generate_response(query=q, searching=search_flag)

@app.route("/Custom.json")
def send():
    q = request.args.get("q", "").strip()
    if not q or q == "":
    #with open("/tmp/Custom.json", "w", encoding="utf-8") as f:
        return '{"Title": "400 Bad Request","Description": "PCL Intelligence Homepage"}'
    #f.write('{"Title": "'+q+'","Description": "PCL Intelligence Homepage"}')
    #return send_file("/tmp/Custom.json", as_attachment=True)
    else:
        return '{"Title": "'+q+'","Description": "PCL Intelligence Homepage"}'


@app.route("/")
def main():
    return render_template("index.html")

@app.route("/version")
def pcl_version_check():
    return "1.2.0"