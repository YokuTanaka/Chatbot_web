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

# テキストファイルから情報を読み込む関数
def read_text_file(file_path):
    try:
        with open(file_path, 'rb') as file:  # 'rb'でバイナリモードで読み込み
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            data = raw_data.decode(encoding)
        return data
    except FileNotFoundError:
        return "指定されたファイルが見つかりません。"

# 全てのファイルの内容を読み込み、まとめる関数
def load_all_info():
    porthall_info = read_text_file('porthall_Basic Info.txt')
    portstudio_info = read_text_file('portstudio_Basic Info.txt')
    return porthall_info + "\n" + portstudio_info

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
        return response.choices[0]["message"]["content"]
    except openai.error.OpenAIError as e:
        return f"エラーが発生しました: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    context = load_all_info()
    if request.method == "POST":
        user_input = request.form["user_input"]
        bot_response = chatbot(user_input, context)
        response = render_template("index.html", user_input=user_input, bot_response=bot_response)
        return response, 200, {'Content-Type': 'text/html; charset=utf-8'}
    return render_template("index.html"), 200, {'Content-Type': 'text/html; charset=utf-8'}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
