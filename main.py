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
    porthall_network = read_text_file('porthall_network.txt')
    porthall_power_panel = read_text_file('porthall_power_panel_Info.txt')
    porthall_internet = read_text_file('porthall_Internet_Info.txt')
    porthall_equipment_free = read_text_file('porthall_equipment_free_Info.txt')

    # デバッグ用に読み込んだ情報をログに記録
    print("All information loaded successfully.")

    return {
        "porthall_basic": porthall_basic,
        "porthall_technical": porthall_technical,
        "portstudio_basic": portstudio_basic,
        "portstudio_technical": portstudio_technical,
        "terms_of_use": terms_of_use,
        "porthall_network": porthall_network,
        "porthall_power_panel": porthall_power_panel,
        "porthall_internet": porthall_internet,
        "porthall_equipment_free": porthall_equipment_free
    }

# チャットボット機能
def chatbot(prompt, context):
    try:
        # OpenAIのモデルを使って意図解析と応答生成を行う
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You are a helpful assistant. When generating the response, "
                    "please ensure that the information is clearly separated by line breaks. "
                    "Use bullet points for lists, and insert line breaks after each point using '<<BR>>' as a placeholder."
                )},
                {"role": "system", "content": f"Context information: {context}"},
                {"role": "user", "content": prompt}
            ]
        )
        raw_response = response.choices[0].message["content"]
        print("Raw response from model:", raw_response)  # デバッグ用にモデルの応答を出力
        
        # プレースホルダーをHTMLの改行タグに置き換える
        formatted_response = format_response(raw_response)
        
        return formatted_response
    except openai.error.OpenAIError as e:
        return f"エラーが発生しました: {e}"

# 応答のフォーマット処理
def format_response(response):
    # '<<BR>>' プレースホルダーをHTML改行タグに置き換える
    response = response.replace("<<BR>>", "<br>")
    
    # 余分なスペースや改行を削除する
    response = response.replace("<br> <br>", "<br>")
    
    # 強調部分（**〜**）をHTMLの<strong>タグに変換
    response = response.replace("**", "<strong>").replace(" - ", "<br>- ")

    # セクションタイトルや「注意事項」などの強調部分に自動的に改行を追加
    # "〜:" の形式のセクションを検出して前後に改行を挿入
    response = response.replace(":", ":<br>")
    
    # 注意事項のように特定のセクションを明示的に太字にする
    response = response.replace("<strong>注意事項</strong>:", "<br><strong>注意事項</strong>:")
    
    # その他のセクションヘッダーのように**で囲まれている部分も同様に処理
    response = response.replace("<strong>照明機器の詳細</strong>:", "<br><strong>照明機器の詳細</strong>:")

    # デバッグ用にフォーマット後のテキストを出力
    print("Formatted response:", response)

    return response


@app.route("/", methods=["GET", "POST"])
def index():
    context = load_all_info()  # 事前にすべての情報を読み込む
    if request.method == "POST":
        user_input = request.form["user_input"]
        bot_response = chatbot(user_input, context)
        print("Sending response to client:", bot_response)  # デバッグ用にレスポンスを出力
        return bot_response  # HTMLではなく、チャットボットの応答のみを返す
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
