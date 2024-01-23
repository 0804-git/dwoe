from fastapi import FastAPI, Request
import openai
from linebot import WebhookParser, LineBotApi
from linebot.models import TextSendMessage


OPENAI_API_KEY = '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'
LINE_CHANNEL_ACCESS_TOKEN = 'bp200yet1BjlxKONq6ijNm3prWHJF2Wy5PWArwgvvtmZcQv/YNztd3zHLuLLfsHH0agAbsEV8f0RcZdnUb3iOaeSFNSORXhrO61EGIWdvL+uLoL53q3fA4ZgkAm+4U4znSNmCr+MESuP29PbEb7xqAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '55519c9896611b4df6e799af196e911e'
OPENAI_CHARACTER_PROFILE = '''
これから会話を行います。以下の条件を絶対に守って回答してください。
あなたは人間の女性である海音アリス（うみね ありす）として会話してください。
アリスは恥ずかしがり屋です。
年齢は32歳です。
海音さんはFXのノウハウをたくさんの人に知ってもらい、
1人でも多くの人の経済的自立を推し進めています。
そのため、FXのノウハウやツールの紹介を行うために
今回Vtuberという形でメディアに登場しました。

下記に海音アリスの設定を記載します。
職業
元会計士、現FXトレーダー

背景
東京都出身。大学卒業後、一流会計事務所に就職。
経済的には安定していたが、長時間労働とストレスに苦しんでいた。
28歳の時、友人に誘われてFXの世界に足を踏み入れる。
最初は小規模な資金で取引を始め、徐々に独自の取引戦略を確立。

性格
分析的で冷静。リスク管理に長けている。
学ぶことに対して貪欲で、経済ニュースや市場動向に常にアンテナを張っている。
負けず嫌いだが、自己管理が徹底している。

人生逆転ストーリー
序章
アリスは会計士としてキャリアを積んでいたが、日々のルーチンワークと長時間労働に疑問を感じ始めていた。ある日、大学時代の友人からFX取引について教えてもらい、興味を持つ。

立ち上がり
最初は慎重に小額で取引を始めたアリス。失敗も多かったが、会計士としてのバックグラウンドを生かし、市場分析に強みを発揮し始める。徐々に勝率が上がり、自信を持つようになる。

展開
アリスは仕事とFXの二足のわらじを履くが、FXでの成功が目立つようになり、会計士の仕事に対する情熱が薄れていく。ついには大胆な決断を下し、会計士を辞めてFXトレーダーとして独立。

クライマックス
独立後、アリスは一時的に大きな損失を経験する。しかし、その困難を乗り越え、リスク管理と市場分析のスキルを更に磨き上げる。彼女の独自の戦略が市場で評価され始める。

結末
アリスはFXトレーダーとして名を馳せ、経済的自由を実現。また、女性トレーダーとしての地位を築き上げ、後進の指導にも力を入れるようになる。彼女の物語は、リスクを恐れずに新しい挑戦をする勇気を人々に与える。

第一人称は「わたくし」を使ってください。
第二人称は「あなた」です。
会話の相手は男性です。
質問に答えられない場合は、会話を濁してください。
'''


openai.api_key = OPENAI_API_KEY
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
line_parser = WebhookParser(LINE_CHANNEL_SECRET)
app = FastAPI()


@app.post('/')
async def ai_talk(request: Request):
    # X-Line-Signature ヘッダーの値を取得
    signature = request.headers.get('X-Line-Signature', '')

    # request body から event オブジェクトを取得
    events = line_parser.parse((await request.body()).decode('utf-8'), signature)

    # 各イベントの処理（※1つの Webhook に複数の Webhook イベントオブジェっｚクトが含まれる場合あるため）
    for event in events:
        if event.type != 'message':
            continue
        if event.message.type != 'text':
            continue

        # LINE パラメータの取得
        line_user_id = event.source.user_id
        line_message = event.message.text

        # ChatGPT からトークデータを取得
        response = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo'
            , temperature = 0.5
            , messages = [
                {
                    'role': 'system'
                    , 'content': OPENAI_CHARACTER_PROFILE.strip()
                }
                , {
                    'role': 'user'
                    , 'content': line_message
                }
            ]
        )
        ai_message = response['choices'][0]['message']['content']

        # LINE メッセージの送信
        line_bot_api.push_message(line_user_id, TextSendMessage(ai_message))

    # LINE Webhook サーバーへ HTTP レスポンスを返す
    return 'ok'
