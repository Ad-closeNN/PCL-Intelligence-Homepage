from google import genai
from google.genai import types
import os
import sys
import shutil
import subprocess
import zipfile
import random
import uuid
from flask import Flask, abort, send_file, render_template
import flask

try:
    import requests
except ImportError:
    print("未安装 requests")

"""
if os.getenv("mode") is None:
    print("Mode 为空")
else:
    try:
        if os.getenv("mode").startswith("http"):
            import requests
    except ImportError:
        print("Requests 未安装：已启用多API模式，但未正确安装 requests 库。请检查 requirements.txt 或其他文件。")
        requests = None
"""

link = os.getenv("link")
if link is None:
    print("变量 link 为空，请检查后重试。再不注意你就 500 Internal Server Error 了。")

app = Flask(__name__)

def install_and_import():
        try:
            # 尝试直接导入
            import homepagebuilder
        except ImportError:
            # 如果导入失败，则安装到 /tmp 目录
            print("homepagebuilder 未安装。")
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
            import homepagebuilder

"""获取 API Key"""
def get_api_key_local(): # 本地获取 API Key：mode = local 时执行
        """本地返回随机 API"""
        try:
            with open("/var/task/config/api_key", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    random_api_key = random.choice(lines)
                    return random_api_key
                else:
                    print("API Key 文件为空，请检查后重试。")
                    abort(500, description="API Key 文件为空，请检查相关文件。")
        except Exception as e:
            e = str(e)
            print(e)
            abort(500, description="获取 API Key 时出错，请检查相关文件和后台日志。")       
def get_api_key_link(url): # 联网获取 API：mode 以 http 开头时执行
    if requests is None:
        abort(500, "已启用多API模式，但未正确安装 requests 库。请检查 requirements.txt 或其他文件。")
    request = requests.get(url)
    if request.status_code != 200:
        print(f"获取 API 失败，状态码：{request.status_code}")
        abort(500, description="获取 API Key 时出错：状态码非200，请检查相关文件和后台日志。")
    key = request.json()
    print("Key 类型："+str(type(key)))
    """服务器返回列表：['sk1', 'sk2', 'sk3', 'sk4']"""
    if isinstance(key, list) and key: # and key: key ≠ 空
        key = random.choice(key)
    else:
        print("获取 API Key 失败：服务器返回的内容不是列表或为空。")
        abort(500, description="获取 API Key 时出错：服务器返回的内容不是列表或为空，请检查相关文件和后台日志。")
    return key

def generate_response(query: str, searching: bool, uid: str):
    import homepagebuilder.main # 有用吗我不知道
    """优先选择 mode"""
    mode = os.getenv("mode")
    #api_key = "See 什么 See 我删了 (*^_^*)"
    
    """------单API Key/多API Key------
    单API：直接在 Vercel 后台设置变量 api_key
    多API：在 Vercel 后台设置变量 mode = multiple (单API Key无需设置mode)
    """
    if not mode: # 此时 api_key = None
        api_key = os.getenv("api_key")
        if not api_key: # mode = None, api_key = None
            abort(500, description="服务器未正确配置 API 密钥(api_key) 或 请求模式(mode)，请检查变量。")
    else:
        if mode == "local":
            api_key = get_api_key_local()
        elif mode.startswith("http"):
            api_key = get_api_key_link(url=mode)
        else:
            abort(500, description="服务器未正确配置 请求模式(mode)：mode被设置为了非 local/http 开头的内容，请检查变量。")

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
    
    """ TODO
    if response.s
        with open("/var/task/templates/toomany.xaml", "r", encoding="utf-8") as f:
            raw = f.read()
        return raw
    """
    
    safe_text = response.text
    """使用 HomepageBuilder 构建 Markdown -> XAML"""
    # 创建文件夹
    if not os.path.exists(f"/tmp/Homepage/{uid}"):
        os.makedirs(f"/tmp/Homepage/{uid}", exist_ok=True)
        shutil.copytree("/var/task/BaseProject", f"/tmp/Homepage/{uid}", dirs_exist_ok=True)
    # 把生成的内容放到 Custom.md
    try:
        with open(f"/tmp/Homepage/{uid}/libraries/Custom.md", "w", encoding="utf-8") as f:
            f.write(str(safe_text))
    except Exception as e:
        print(str(e))

    sys.argv = ['prog_name', 'build', '--project', f'/tmp/Homepage/{uid}/Project.yml' ,'--output-path', f'/tmp/Homepage/{uid}/Custom_base.xaml']
    homepagebuilder.main.main()
    with open(f"/tmp/Homepage/{uid}/Custom_base.xaml", "r", encoding="utf-8") as raw:
        xaml = raw.readlines()
        with open(f"/tmp/Homepage/{uid}/Custom.xaml", "w", encoding="utf-8") as f:
            for line in xaml: # 不管了能用就行炸了再说 反正 Builder 输出的是规则的 别乱改了 :)
                if line.startswith('<local:MyCard Title="'):
                    if searching:
                        f.write(f'<local:MyCard Title="（已联网）{query}"'+' CanSwap="False" IsSwaped="False" Style="{StaticResource Card}" >')
                    else:
                        f.write(f'<local:MyCard Title="（未联网）{query}"'+' CanSwap="False" IsSwaped="False" Style="{StaticResource Card}" >')
                else:
                    f.write(line)
    
    with open(f"/tmp/Homepage/{uid}/Custom.xaml", "r", encoding="utf-8") as raw:
        xaml = raw.read()
    with open("/var/task/templates/footer.xaml", "r", encoding="utf-8") as f:
        footer = f.read()
    return xaml+"\n\n"+footer

@app.route("/Custom.xaml", methods=["GET"])
def trigger():
    q = flask.request.args.get("q", "").strip()
    if not q or q == "":
        #abort(400, description="缺少 query(q) 参数。")
        with open("/var/task/templates/empty.xaml", "r", encoding="utf-8") as f:
            """
            Name: empty.xaml
            easter-egg
            return to homepage
            """
            content = f.read()
            content = content.replace("https://pclintelligence.19991230.xyz", link.rstrip("/"))
        return content
    search_flag = flask.request.args.get("search", "false").lower() == "true" # bool var
    install_and_import()
    uid = uuid.uuid4().hex
    try:
        return generate_response(query=q, searching=search_flag, uid=uid)
    finally: # 删库(libraries)跑路 :)
        shutil.rmtree(f"/tmp/Homepage/{uid}")

@app.route("/Custom.json")
def send():
    q = flask.request.args.get("q", "").strip()
    if not q or q == "":
        return '{"Title": "400 Bad Request","Description": "PCL Intelligence Homepage"}'
    else:
        return '{"Title": "'+q+'","Description": "PCL Intelligence Homepage"}'

@app.route("/")
def main():
    with open("/var/task/templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        content = content.replace("https://pclintelligence.19991230.xyz", link.rstrip("/"))
    return content # v1.4.0 此时的 templates 失去了它本该被用作 Flask 渲染预设网页的价值（

@app.route("/version")
def pcl_version_check():
    return "1.4.0"