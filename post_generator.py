"""
AIを使ってXのポストを生成するモジュール
複数のバックエンドに対応（Groq無料、Anthropic、テンプレート）
"""

import os
import random
import requests
from typing import Optional


# ================== テンプレートベースの生成（API不要） ==================

POST_TEMPLATES = {
    "informative": [
        "【{topic}】\n{fact}\n\n具体的には{tip}\n\n{hashtags}",
        "意外と知られてない{topic}の話。\n\n{fact}\n\nポイントは「{tip}」\n\n{hashtags}",
        "{topic}で稼ぐコツ👇\n\n✅ {fact}\n✅ {tip}\n\n今日から始められます\n\n{hashtags}",
        "🔥 {topic}\n\n{fact}\n\n始め方：{tip}\n\n{hashtags}",
    ],
    "casual": [
        "{topic}、マジで穴場かも。\n\n{fact}\n\nやり方は{tip}だけ。\n\n{hashtags}",
        "最近{topic}始めたんだけど、{fact}って知ってた？\n\n{tip}がコツ💡\n\n{hashtags}",
        "え、まだ{topic}やってないの？\n\n{fact}\n\n{tip}から始めよう\n\n{hashtags}",
    ],
    "provocative": [
        "【悲報】まだ{topic}を知らない人、損してます\n\n{fact}\n\n{tip}\n\n{hashtags}",
        "99%の人が見落としてる{topic}の真実\n\n{fact}\n\n解決策→{tip}\n\n{hashtags}",
        "「{topic}は難しい」←これ、嘘です\n\n実は{fact}\n\n{tip}で誰でも始められる\n\n{hashtags}",
    ],
    "storytelling": [
        "{topic}を1ヶ月試した結果…\n\n{fact}ということがわかった\n\n学び：{tip}\n\n{hashtags}",
        "副業で{topic}を選んだ理由\n\n→{fact}\n\n成功のコツは{tip}\n\n{hashtags}",
        "最初は半信半疑だった{topic}\n\n実際やってみたら{fact}\n\nおすすめは{tip}\n\n{hashtags}",
    ],
}

THREAD_TEMPLATES = [
    "1/ {topic}で副業する方法を解説します🧵\n\n{fact}",
    "2/ まず知っておくべきこと\n\n→{tip}",
    "3/ 具体的な始め方\n\n①無料ツールで練習\n②小さく始める\n③実績を作る",
    "4/ 注意点\n\n・最初は時間がかかる\n・継続が大事\n・差別化を意識",
    "5/ まとめ\n\n{topic}は今が始めどき。\n\nこのスレッドが役立ったらフォロー&保存お願いします🙏\n\n{hashtags}",
]


class TemplateGenerator:
    """テンプレートベースのポスト生成（API不要）"""

    def generate_post(
        self,
        topic: str,
        context: str,
        style: str = "informative",
        hashtags: Optional[list[str]] = None,
    ) -> str:
        templates = POST_TEMPLATES.get(style, POST_TEMPLATES["informative"])
        template = random.choice(templates)

        # コンテキストから情報を抽出
        lines = context.strip().split("\n")
        fact = lines[0] if lines else f"{topic}は今注目の副業"
        tip = lines[1].replace("💡 ", "").replace("Tip: ", "") if len(lines) > 1 else "小さく始めて実績を作る"

        hashtag_str = " ".join([f"#{h}" for h in (hashtags or ["AI副業", "副業"])])

        return template.format(
            topic=topic,
            fact=fact,
            tip=tip,
            hashtags=hashtag_str,
        )

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
        hashtag_str = " ".join([f"#{h}" for h in (hashtags or ["AI副業", "副業"])])

        posts = []
        for i, tmpl in enumerate(THREAD_TEMPLATES[:num_posts]):
            post = tmpl.format(topic=topic, fact=fact, tip=tip, hashtags=hashtag_str)
            posts.append(post)
        return posts

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        styles = ["informative", "casual", "provocative"]
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

    def _call_api(self, prompt: str, max_tokens: int = 500) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "llama-3.1-8b-instant",  # 無料で高速
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        try:
            response = requests.post(self.API_URL, headers=headers, json=data, timeout=30)
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
        style_instructions = {
            "informative": "情報提供型で、具体的な数字やデータを含めて信頼性を高める",
            "casual": "親しみやすいカジュアルな口調で、絵文字を適度に使用",
            "provocative": "読者の興味を引く問いかけや意外な事実から始める",
            "storytelling": "短いストーリー形式で、共感を呼ぶ体験談風に",
        }
        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n使用するハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""あなたはX（Twitter）でAI×副業の情報を発信するインフルエンサーです。
以下の情報を基に、フォロワーを増やすための魅力的なポストを作成してください。

【トピック】{topic}
【参考情報】{context}
【スタイル】{style_instructions.get(style, style_instructions["informative"])}
{hashtag_text}

ルール:
- 140文字以内
- 具体的で実用的な情報を含める
- 冒頭で興味を引く

ポスト本文のみを出力:"""

        return self._call_api(prompt)

    def generate_thread(
        self,
        topic: str,
        context: str,
        num_posts: int = 5,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n最後のポストに使用するハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""X（Twitter）でAI×副業の情報を発信するインフルエンサーとして、{num_posts}ポストのスレッドを作成。

【トピック】{topic}
【参考情報】{context}
{hashtag_text}

ルール:
- 各ポストは140文字以内
- 各ポストは「1/」「2/」などの番号で始める
- 1つ目は強力なフック、最後はまとめ

{num_posts}つのポストを空行で区切って出力:"""

        result = self._call_api(prompt, max_tokens=1500)
        posts = result.split("\n\n")
        return [p.strip() for p in posts if p.strip()]

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n使用可能なハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""X（Twitter）でAI×副業の情報を発信するインフルエンサーとして、{num_variations}種類の異なるスタイルのポストを作成。

【トピック】{topic}
【参考情報】{context}
{hashtag_text}

スタイル: 1.情報提供型 2.問いかけ型 3.体験談型
各ポストは140文字以内。

{num_variations}つのポストを「---」で区切って出力:"""

        result = self._call_api(prompt, max_tokens=1200)
        posts = result.split("---")
        return [p.strip() for p in posts if p.strip()]


# ================== Google Gemini API（無料枠あり） ==================

class GeminiGenerator:
    """Google Gemini APIを使用したポスト生成（無料枠あり）"""

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")

    def _call_api(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000,
            },
        }
        url = f"{self.API_URL}?key={self.api_key}"
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            # レスポンス構造を確認
            if "candidates" not in result or not result["candidates"]:
                # ブロックされた場合やエラーの場合
                if "error" in result:
                    raise Exception(f"Gemini API error: {result['error'].get('message', 'Unknown error')}")
                raise Exception("Gemini API: No candidates in response")

            candidate = result["candidates"][0]
            if "content" not in candidate:
                # 安全フィルターでブロックされた場合
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
        style_instructions = {
            "informative": "情報提供型で、具体的な数字やデータを含めて信頼性を高める",
            "casual": "親しみやすいカジュアルな口調で、絵文字を適度に使用",
            "provocative": "読者の興味を引く問いかけや意外な事実から始める",
            "storytelling": "短いストーリー形式で、共感を呼ぶ体験談風に",
        }
        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n使用するハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""あなたはX（Twitter）でAI×副業の情報を発信するインフルエンサーです。
以下の情報を基に、フォロワーを増やすための魅力的なポストを作成してください。

【トピック】{topic}
【参考情報】{context}
【スタイル】{style_instructions.get(style, style_instructions["informative"])}
{hashtag_text}

ルール:
- 140文字以内
- 具体的で実用的な情報を含める
- 冒頭で興味を引く

ポスト本文のみを出力（説明不要）:"""

        return self._call_api(prompt)

    def generate_thread(
        self,
        topic: str,
        context: str,
        num_posts: int = 5,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n最後のポストに使用するハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""X（Twitter）でAI×副業の情報を発信するインフルエンサーとして、{num_posts}ポストのスレッドを作成。

【トピック】{topic}
【参考情報】{context}
{hashtag_text}

ルール:
- 各ポストは140文字以内
- 各ポストは「1/」「2/」などの番号で始める
- 1つ目は強力なフック、最後はまとめ

{num_posts}つのポストを空行で区切って出力:"""

        result = self._call_api(prompt)
        posts = result.split("\n\n")
        return [p.strip() for p in posts if p.strip()]

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n使用可能なハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""X（Twitter）でAI×副業の情報を発信するインフルエンサーとして、{num_variations}種類の異なるスタイルのポストを作成。

【トピック】{topic}
【参考情報】{context}
{hashtag_text}

スタイル: 1.情報提供型 2.問いかけ型 3.体験談型
各ポストは140文字以内。

{num_variations}つのポストを「---」で区切って出力:"""

        result = self._call_api(prompt)
        posts = result.split("---")
        return [p.strip() for p in posts if p.strip()]


# ================== Anthropic API ==================

class AnthropicGenerator:
    """Anthropic APIを使用したポスト生成"""

    def __init__(self, api_key: Optional[str] = None):
        from anthropic import Anthropic
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")
        self.client = Anthropic(api_key=self.api_key)

    def _call_api(self, prompt: str, max_tokens: int = 500) -> str:
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
        style_instructions = {
            "informative": "情報提供型で、具体的な数字やデータを含めて信頼性を高める",
            "casual": "親しみやすいカジュアルな口調で、絵文字を適度に使用",
            "provocative": "読者の興味を引く問いかけや意外な事実から始める",
            "storytelling": "短いストーリー形式で、共感を呼ぶ体験談風に",
        }
        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n使用するハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""あなたはX（Twitter）でAI×副業の情報を発信するインフルエンサーです。
以下の情報を基に、フォロワーを増やすための魅力的なポストを作成してください。

【トピック】{topic}
【参考情報】{context}
【スタイル】{style_instructions.get(style, style_instructions["informative"])}
{hashtag_text}

ルール:
- 140文字以内に収める
- 具体的で実用的な情報を含める
- 冒頭で興味を引く（フック）

ポスト本文のみを出力:"""

        return self._call_api(prompt)

    def generate_thread(
        self,
        topic: str,
        context: str,
        num_posts: int = 5,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n最後のポストに使用するハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""X（Twitter）でAI×副業の情報を発信するインフルエンサーとして、{num_posts}ポストのスレッドを作成。

【トピック】{topic}
【参考情報】{context}
{hashtag_text}

ルール:
- 各ポストは140文字以内
- 各ポストは「1/」「2/」などの番号で始める

{num_posts}つのポストを空行で区切って出力:"""

        result = self._call_api(prompt, max_tokens=1500)
        posts = result.split("\n\n")
        return [p.strip() for p in posts if p.strip()]

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n使用可能なハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""X（Twitter）でAI×副業の情報を発信するインフルエンサーとして、{num_variations}種類の異なるスタイルのポストを作成。

【トピック】{topic}
【参考情報】{context}
{hashtag_text}

スタイル: 1.情報提供型 2.問いかけ型 3.体験談型
各ポストは140文字以内。

{num_variations}つのポストを「---」で区切って出力:"""

        result = self._call_api(prompt, max_tokens=1200)
        posts = result.split("---")
        return [p.strip() for p in posts if p.strip()]


# ================== 統合クラス ==================

class XPostGenerator:
    """
    X（Twitter）用のポストを生成するクラス
    利用可能なバックエンドを自動選択:
    1. Groq API（無料）
    2. Gemini API（無料枠あり）
    3. Anthropic API
    4. テンプレート（API不要）
    """

    def __init__(self, backend: Optional[str] = None):
        """
        Args:
            backend: 使用するバックエンド ("groq", "gemini", "anthropic", "template", None=自動選択)
        """
        self.backend_name = backend or self._detect_backend()
        self.generator = self._create_generator()

    def _detect_backend(self) -> str:
        """利用可能なバックエンドを検出"""
        if os.getenv("GROQ_API_KEY"):
            return "groq"
        elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            return "gemini"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        else:
            return "template"

    def _create_generator(self):
        """バックエンドに応じたジェネレータを作成"""
        if self.backend_name == "groq":
            return GroqGenerator()
        elif self.backend_name == "gemini":
            return GeminiGenerator()
        elif self.backend_name == "anthropic":
            return AnthropicGenerator()
        else:
            return TemplateGenerator()

    def get_backend_info(self) -> dict:
        """使用中のバックエンド情報を取得"""
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
    japanese_chars = sum(1 for c in text if ord(c) > 127)
    ascii_chars = len(text) - japanese_chars

    return {
        "total_chars": len(text),
        "japanese_chars": japanese_chars,
        "ascii_chars": ascii_chars,
        "x_weight": japanese_chars + (ascii_chars * 0.5),
        "is_valid": len(text) <= 280,
    }
