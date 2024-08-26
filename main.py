import openai
from flask import Flask, request, render_template
import sys
import chardet
from dotenv import load_dotenv
import os

app = Flask(__name__)

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキーを設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pythonの標準出力と標準入力をUTF-8に設定
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

# テキストファイルから情報を読み込む関数（デバッグログ付き）
def read_text_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            print(f"Detected encoding for {file_path}: {encoding}")
            data = raw_data.decode(encoding)
            print(f"File {file_path} read successfully.")
        return data
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return "指定されたファイルが見つかりません。"
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return "ファイルの読み込み中にエラーが発生しました。"

# 全てのファイルの内容を読み込み、まとめる関数
def load_all_info():
    porthall_basic = read_text_file('porthall_Basic_Info.txt')
    porthall_technical = read_text_file('porthall_technical_Info.txt')
    portstudio_basic = read_text_file('portstudio_Basic_Info.txt')
    portstudio_technical = read_text_file('portstudio_technical_Info.txt')
    terms_of_use = read_text_file('Terms_of_use.txt')
    
    return {
        "porthall_basic": porthall_basic,
        "porthall_technical": porthall_technical,
        "portstudio_basic": portstudio_basic,
        "portstudio_technical": portstudio_technical,
        "terms_of_use": terms_of_use
    }

# チャットボット機能
def chatbot(prompt, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "system", "content": f"Here is some information about the venue: {context}"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]
    except openai.error.OpenAIError as e:
        return f"エラーが発生しました: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    context = load_all_info()
    if request.method == "POST":
        user_input = request.form["user_input"]
        bot_response = chatbot(user_input, context)
        return bot_response  # HTMLではなく、チャットボットの応答のみを返す
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
