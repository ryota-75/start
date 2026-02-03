"""
AIを使ってXのポストを生成するモジュール
Twitterアルゴリズム最適化版
複数のバックエンドに対応（Groq無料、Gemini、Anthropic、テンプレート）
"""

import os
import random
import requests
from typing import Optional


# ================== Twitterアルゴリズム最適化プロンプト ==================

ALGORITHM_OPTIMIZED_PROMPT = """あなたはX（Twitter）でAI×副業の情報を発信し、10万フォロワーを持つインフルエンサーです。
Twitterのアルゴリズムを熟知しており、エンゲージメントを最大化するポストを作成します。

【Twitterアルゴリズムの重要ポイント】
1. 最初の2行で興味を引く（スクロールを止めさせる）
2. リプライや引用RTを促す内容（会話を生む）
3. 具体的な数字・データで信頼性を高める
4. 保存したくなる実用的な価値を提供
5. 最後に行動を促すCTA（質問や意見募集）

【トピック】
{topic}

【参考情報】
{context}

【スタイル指示】
{style_instruction}

【生成ルール】
- 文字数: 400〜800文字程度（長文OK、読み応えのある内容に）
- 構成:
  ・冒頭: 強烈なフック（衝撃的な事実、問いかけ、意外な数字）
  ・本文: 具体的なノウハウ・事例・ステップ（箇条書き活用）
  ・結び: 読者への問いかけやCTA
- 改行を効果的に使い、読みやすく
- 絵文字は控えめに（1-3個程度）
- ハッシュタグは最後に2-3個

【出力形式】
ポスト本文のみを出力してください（説明や補足は不要）:"""

STYLE_INSTRUCTIONS = {
    "informative": """
情報提供型：専門家として信頼性の高い情報を提供
- 具体的なデータや数字を必ず含める
- 「〜によると」「実際に〜」など根拠を示す
- ステップバイステップで実践可能な内容に""",

    "provocative": """
問いかけ型：読者の常識を覆し、議論を促す
- 冒頭で意外な事実や逆説的な主張を展開
- 「実は〜」「〜は間違いだった」などの切り口
- 最後に「あなたはどう思いますか？」と問いかける""",

    "storytelling": """
ストーリー型：実体験ベースで共感を呼ぶ
- 「〜してみた結果」「〜で失敗した話」など体験談形式
- ビフォーアフターや学びを具体的に
- 読者が自分事として捉えられる内容に""",

    "casual": """
カジュアル型：親しみやすく、気軽に読める
- 友達に話すような口調
- 「マジで」「ぶっちゃけ」など砕けた表現OK
- でも中身は濃く、価値ある情報を"""
}

# ================== テンプレートベースの生成（API不要） ==================

RICH_TEMPLATES = {
    "informative": [
        """【{topic}で月収を増やす具体的な方法】

{fact}

これ、意外と知られてないんですが...

▼ 実践ステップ
①まず{tip}から始める
②小さな実績を作る（最初は無料でもOK）
③ポートフォリオを整えて単価UP

▼ 収益目安
・初月: 1-3万円
・3ヶ月目: 5-10万円
・半年後: 10-30万円も可能

大事なのは「完璧を目指さない」こと。
まず小さく始めて、走りながら改善していく。

これから{topic}始めようと思ってる人、
質問あればリプで教えてください👇

#AI副業 #副業""",

        """知らないと損する{topic}の話をします。

{fact}

正直、これを知ってるかどうかで
収入が月10万円変わると思ってます。

【具体的なやり方】
✅ {tip}
✅ 最初は時給換算で考えない
✅ 実績を見せられる形で残す

【注意点】
・最初から完璧を求めない
・1つのスキルに絞る
・継続が最重要

僕自身、{topic}を始めて3ヶ月で
副収入が本業の半分になりました。

始めるか迷ってる人、
何がハードルになってますか？

#AI副業 #副業 #AI活用"""
    ],

    "provocative": [
        """「{topic}は難しそう」

↑これ、完全に間違いです。

{fact}

むしろ今が一番チャンス。
なぜなら...

・参入者がまだ少ない
・ツールが急速に進化してる
・需要は爆発的に増えてる

実際、僕の周りでも
・プログラミング未経験の主婦
・本業が忙しい会社員
・50代からスタートした人

みんな成果出してます。

ポイントは{tip}

「自分には無理」と思ってる人ほど
意外とすんなりできたりします。

やらない理由、本当にそれで合ってますか？

#AI副業 #副業""",

        """【悲報】まだ{topic}やってない人、
かなり損してます。

{fact}

「え、そんなに稼げるの？」
って思いますよね。

でも実際、市場を見てみると...

・案件数: 前年比300%増
・単価: 平均20%上昇
・参入障壁: どんどん下がってる

つまり「今が最高のタイミング」

始め方は超シンプル
→{tip}

これだけ。

1年後に「あの時始めてれば...」
と後悔する前に。

どう思います？🤔

#AI副業 #AI活用"""
    ],

    "storytelling": [
        """{topic}を始めて半年。
正直に結果を報告します。

{fact}

最初は不安でした。

・本当に稼げるの？
・自分にできる？
・時間ある？

でも、思い切って始めてみたら...

【1ヶ月目】
手探りで月5,000円

【3ヶ月目】
コツを掴んで月3万円

【半年後】
今では月15万円を安定して稼げるように

一番の学びは
「{tip}」ということ。

完璧じゃなくていい。
まず始めることが大事。

同じように迷ってる人、
最初の一歩で躓いたこと教えてください。
一緒に解決策考えましょう💪

#AI副業 #副業 #体験談""",

        """ぶっちゃけます。

{topic}で「稼げない」と言ってる人、
たぶんこれができてない。

{fact}

僕も最初は全然ダメでした。

3ヶ月やっても月1万円...
「向いてないのかな」と思った時期も。

でも、{tip}を意識し始めてから
状況が一変。

今では安定して月10万円以上。

失敗から学んだこと👇
・最初から大きく狙わない
・1つのことを深掘りする
・成功者の真似から始める

結局、諦めなかった人が勝つ。

今苦戦してる人、
何に一番困ってますか？

#AI副業 #副業"""
    ],

    "casual": [
        """ちょっと聞いてほしいんだけど、

{topic}、マジで穴場かもしれない。

{fact}

いや、煽りじゃなくてガチで。

最近始めた友達がいるんだけど、
2週間で初収益出してた。

しかも{tip}だけで。

「難しそう」って思うじゃん？
僕も最初そう思ってた。

でもやってみたら意外と...
・専門知識いらない
・初期費用ほぼゼロ
・スキマ時間でOK

向き不向きはあると思うけど、
試してみる価値はあると思う。

興味ある人いたらリプください〜
始め方とか詳しく教えますよ👍

#AI副業 #副業"""
    ]
}


class TemplateGenerator:
    """テンプレートベースのポスト生成（API不要・高品質版）"""

    def generate_post(
        self,
        topic: str,
        context: str,
        style: str = "informative",
        hashtags: Optional[list[str]] = None,
    ) -> str:
        templates = RICH_TEMPLATES.get(style, RICH_TEMPLATES["informative"])
        template = random.choice(templates)

        lines = context.strip().split("\n")
        fact = lines[0] if lines else f"{topic}は今注目の副業で、月5-30万円の収入が狙える"
        tip = lines[1].replace("💡 ", "").replace("Tip: ", "") if len(lines) > 1 else "小さく始めて実績を積み重ねる"

        return template.format(topic=topic, fact=fact, tip=tip)

    def generate_thread(
        self,
        topic: str,
        context: str,
        num_posts: int = 5,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        lines = context.strip().split("\n")
        fact = lines[0] if lines else f"{topic}は今注目の副業"
        tip = lines[1].replace("💡 ", "").replace("Tip: ", "") if len(lines) > 1 else "継続が大事"

        thread = [
            f"🧵{topic}で副業を始めて月10万円稼ぐまでのロードマップ\n\n{fact}\n\n具体的な手順をスレッドで解説します👇",
            f"【STEP1: 準備期間】\n\nまず{tip}から始めましょう。\n\n必要なもの:\n・PC（スマホでも可）\n・1日30分の時間\n・学ぶ姿勢\n\n初期費用はほぼゼロでOK。",
            f"【STEP2: スキル習得】\n\n最初の1ヶ月は勉強期間。\n\n・YouTube/Udemyで基礎学習\n・実際に手を動かして練習\n・わからないことはAIに質問\n\n完璧を目指さず、60%の理解で次へ進む。",
            f"【STEP3: 実績作り】\n\n2ヶ月目から実践開始。\n\n・最初は安くてもOK\n・数をこなして経験を積む\n・良い仕事はポートフォリオに\n\nここが一番キツいけど、踏ん張りどころ。",
            f"【まとめ】\n\n{topic}は正しく継続すれば必ず成果が出ます。\n\n大事なのは:\n✅ 小さく始める\n✅ 毎日少しずつ\n✅ 諦めない\n\n質問あればリプで👇\n\n#AI副業 #副業",
        ]
        return thread[:num_posts]

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        styles = ["informative", "provocative", "storytelling", "casual"]
        return [
            self.generate_post(topic, context, style, hashtags)
            for style in styles[:num_variations]
        ]


# ================== Groq API（無料） ==================

class GroqGenerator:
    """Groq APIを使用したポスト生成（無料枠あり）"""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY が設定されていません")

    def _call_api(self, prompt: str, max_tokens: int = 1500) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.8,
        }
        try:
            response = requests.post(self.API_URL, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.HTTPError as e:
            error_msg = f"Groq API HTTP error: {e}"
            try:
                error_detail = e.response.json()
                if "error" in error_detail:
                    error_msg = f"Groq API: {error_detail['error'].get('message', str(e))}"
            except Exception:
                pass
            raise Exception(error_msg)
        except requests.exceptions.Timeout:
            raise Exception("Groq API: Request timeout")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Groq API connection error: {e}")

    def generate_post(
        self,
        topic: str,
        context: str,
        style: str = "informative",
        hashtags: Optional[list[str]] = None,
    ) -> str:
        style_instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["informative"])
        prompt = ALGORITHM_OPTIMIZED_PROMPT.format(
            topic=topic,
            context=context,
            style_instruction=style_instruction
        )
        return self._call_api(prompt, max_tokens=1500)

    def generate_thread(
        self,
        topic: str,
        context: str,
        num_posts: int = 5,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        prompt = f"""あなたはX（Twitter）で10万フォロワーを持つAI×副業インフルエンサーです。
バズるスレッドを作成してください。

【トピック】{topic}
【参考情報】{context}

【スレッド構成】（{num_posts}ポスト）
1つ目: 強烈なフック（「これ知らないと損」系）+ スレッドの予告
2〜{num_posts-1}つ目: 具体的なノウハウ・ステップ・事例
最後: まとめ + CTA（保存・フォロー促進）

【ルール】
- 各ポストは200-400文字程度
- 番号は「1/」「2/」形式
- 箇条書きを活用して読みやすく
- 最後のポストにハッシュタグを2-3個

{num_posts}つのポストを「---」で区切って出力してください:"""

        result = self._call_api(prompt, max_tokens=3000)
        posts = result.split("---")
        return [p.strip() for p in posts if p.strip()]

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        styles = ["informative", "provocative", "storytelling"][:num_variations]
        return [
            self.generate_post(topic, context, style, hashtags)
            for style in styles
        ]


# ================== Google Gemini API（無料枠あり） ==================

class GeminiGenerator:
    """Google Gemini APIを使用したポスト生成（無料枠あり）"""

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")

    def _call_api(self, prompt: str, max_tokens: int = 2000) -> str:
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": max_tokens,
            },
        }
        url = f"{self.API_URL}?key={self.api_key}"
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()

            if "candidates" not in result or not result["candidates"]:
                if "error" in result:
                    raise Exception(f"Gemini API error: {result['error'].get('message', 'Unknown error')}")
                raise Exception("Gemini API: No candidates in response")

            candidate = result["candidates"][0]
            if "content" not in candidate:
                finish_reason = candidate.get("finishReason", "UNKNOWN")
                if finish_reason == "SAFETY":
                    raise Exception("Gemini API: Content blocked by safety filter")
                raise Exception(f"Gemini API: No content (reason: {finish_reason})")

            return candidate["content"]["parts"][0]["text"].strip()
        except requests.exceptions.HTTPError as e:
            error_msg = f"Gemini API HTTP error: {e}"
            try:
                error_detail = e.response.json()
                if "error" in error_detail:
                    error_msg = f"Gemini API: {error_detail['error'].get('message', str(e))}"
            except Exception:
                pass
            raise Exception(error_msg)
        except requests.exceptions.Timeout:
            raise Exception("Gemini API: Request timeout")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Gemini API connection error: {e}")

    def generate_post(
        self,
        topic: str,
        context: str,
        style: str = "informative",
        hashtags: Optional[list[str]] = None,
    ) -> str:
        style_instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["informative"])
        prompt = ALGORITHM_OPTIMIZED_PROMPT.format(
            topic=topic,
            context=context,
            style_instruction=style_instruction
        )
        return self._call_api(prompt, max_tokens=2000)

    def generate_thread(
        self,
        topic: str,
        context: str,
        num_posts: int = 5,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        prompt = f"""あなたはX（Twitter）で10万フォロワーを持つAI×副業インフルエンサーです。
バズるスレッドを作成してください。

【トピック】{topic}
【参考情報】{context}

【スレッド構成】（{num_posts}ポスト）
1つ目: 強烈なフック + スレッドの予告
2〜{num_posts-1}つ目: 具体的なノウハウ・ステップ・事例
最後: まとめ + CTA

【ルール】
- 各ポストは200-400文字程度
- 番号は「1/」「2/」形式
- 箇条書きを活用
- 最後にハッシュタグ2-3個

{num_posts}つのポストを「---」で区切って出力:"""

        result = self._call_api(prompt, max_tokens=4000)
        posts = result.split("---")
        return [p.strip() for p in posts if p.strip()]

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        styles = ["informative", "provocative", "storytelling"][:num_variations]
        return [
            self.generate_post(topic, context, style, hashtags)
            for style in styles
        ]


# ================== Anthropic API ==================

class AnthropicGenerator:
    """Anthropic APIを使用したポスト生成"""

    def __init__(self, api_key: Optional[str] = None):
        from anthropic import Anthropic
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")
        self.client = Anthropic(api_key=self.api_key)

    def _call_api(self, prompt: str, max_tokens: int = 1500) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    def generate_post(
        self,
        topic: str,
        context: str,
        style: str = "informative",
        hashtags: Optional[list[str]] = None,
    ) -> str:
        style_instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["informative"])
        prompt = ALGORITHM_OPTIMIZED_PROMPT.format(
            topic=topic,
            context=context,
            style_instruction=style_instruction
        )
        return self._call_api(prompt, max_tokens=1500)

    def generate_thread(
        self,
        topic: str,
        context: str,
        num_posts: int = 5,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        prompt = f"""あなたはX（Twitter）で10万フォロワーを持つAI×副業インフルエンサーです。
バズるスレッドを作成してください。

【トピック】{topic}
【参考情報】{context}

【スレッド構成】（{num_posts}ポスト）
1つ目: 強烈なフック + スレッドの予告
2〜{num_posts-1}つ目: 具体的なノウハウ・ステップ・事例
最後: まとめ + CTA

【ルール】
- 各ポストは200-400文字
- 番号は「1/」「2/」形式
- 最後にハッシュタグ2-3個

{num_posts}つのポストを「---」で区切って出力:"""

        result = self._call_api(prompt, max_tokens=3000)
        posts = result.split("---")
        return [p.strip() for p in posts if p.strip()]

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        styles = ["informative", "provocative", "storytelling"][:num_variations]
        return [
            self.generate_post(topic, context, style, hashtags)
            for style in styles
        ]


# ================== 統合クラス ==================

class XPostGenerator:
    """
    X（Twitter）用のポストを生成するクラス
    Twitterアルゴリズム最適化版

    利用可能なバックエンド（優先順）:
    1. Groq API（無料・高速）
    2. Gemini API（無料枠あり）
    3. Anthropic API（有料・高品質）
    4. テンプレート（API不要）
    """

    def __init__(self, backend: Optional[str] = None):
        self.backend_name = backend or self._detect_backend()
        self.generator = self._create_generator()

    def _detect_backend(self) -> str:
        if os.getenv("GROQ_API_KEY"):
            return "groq"
        elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            return "gemini"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        else:
            return "template"

    def _create_generator(self):
        if self.backend_name == "groq":
            return GroqGenerator()
        elif self.backend_name == "gemini":
            return GeminiGenerator()
        elif self.backend_name == "anthropic":
            return AnthropicGenerator()
        else:
            return TemplateGenerator()

    def get_backend_info(self) -> dict:
        info = {
            "groq": {"name": "Groq API", "model": "llama-3.1-8b-instant", "free": True},
            "gemini": {"name": "Google Gemini API", "model": "gemini-2.0-flash", "free": True},
            "anthropic": {"name": "Anthropic API", "model": "claude-sonnet-4-20250514", "free": False},
            "template": {"name": "テンプレート", "model": "なし", "free": True},
        }
        return {"backend": self.backend_name, **info.get(self.backend_name, {})}

    def generate_post(
        self,
        topic: str,
        context: str,
        style: str = "informative",
        include_hashtags: bool = True,
        hashtags: Optional[list[str]] = None,
    ) -> str:
        return self.generator.generate_post(
            topic=topic,
            context=context,
            style=style,
            hashtags=hashtags if include_hashtags else None,
        )

    def generate_thread(
        self,
        topic: str,
        context: str,
        num_posts: int = 5,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        return self.generator.generate_thread(
            topic=topic,
            context=context,
            num_posts=num_posts,
            hashtags=hashtags,
        )

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        return self.generator.generate_variations(
            topic=topic,
            context=context,
            num_variations=num_variations,
            hashtags=hashtags,
        )


def calculate_post_length(text: str) -> dict:
    """ポストの文字数を計算（X用）"""
    return {
        "total_chars": len(text),
        "is_valid": len(text) <= 4000,  # X Premium の上限
    }
