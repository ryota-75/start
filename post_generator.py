"""
AIを使ってXのポストを生成するモジュール
"""

import os
from anthropic import Anthropic
from typing import Optional


class XPostGenerator:
    """X（Twitter）用のポストを生成するクラス"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")
        self.client = Anthropic(api_key=self.api_key)

    def generate_post(
        self,
        topic: str,
        context: str,
        style: str = "informative",
        include_hashtags: bool = True,
        hashtags: Optional[list[str]] = None,
    ) -> str:
        """
        トピックとコンテキストからXポストを生成

        Args:
            topic: ポストのトピック
            context: リサーチで収集した情報
            style: ポストのスタイル (informative, casual, provocative, storytelling)
            include_hashtags: ハッシュタグを含めるか
            hashtags: 使用するハッシュタグのリスト
        """

        style_instructions = {
            "informative": "情報提供型で、具体的な数字やデータを含めて信頼性を高める",
            "casual": "親しみやすいカジュアルな口調で、絵文字を適度に使用",
            "provocative": "読者の興味を引く問いかけや意外な事実から始める",
            "storytelling": "短いストーリー形式で、共感を呼ぶ体験談風に",
        }

        hashtag_text = ""
        if include_hashtags and hashtags:
            hashtag_text = f"\n使用するハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""あなたはX（Twitter）でAI×副業の情報を発信するインフルエンサーです。
以下の情報を基に、フォロワーを増やすための魅力的なポストを作成してください。

【トピック】
{topic}

【参考情報】
{context}

【スタイル指示】
{style_instructions.get(style, style_instructions["informative"])}
{hashtag_text}

【ポスト作成のルール】
1. 280文字以内（日本語は140文字が目安）に収める
2. 具体的で実用的な情報を含める
3. 読者がすぐに行動できるTipsを入れる
4. あまり知られていない情報や独自の視点を入れる
5. 「続きはスレッドで」などの誘導は使わない（単体で完結させる）
6. 数字や具体例を入れて信頼性を高める
7. 冒頭で興味を引く（フック）

ポスト本文のみを出力してください（説明は不要）:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    def generate_thread(
        self,
        topic: str,
        context: str,
        num_posts: int = 5,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        """
        スレッド形式の連続ポストを生成

        Args:
            topic: スレッドのトピック
            context: リサーチで収集した情報
            num_posts: スレッドのポスト数
            hashtags: 使用するハッシュタグのリスト
        """

        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n最後のポストに使用するハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""あなたはX（Twitter）でAI×副業の情報を発信するインフルエンサーです。
以下の情報を基に、{num_posts}ポストのスレッドを作成してください。

【トピック】
{topic}

【参考情報】
{context}
{hashtag_text}

【スレッド構成】
1. 1つ目: 強力なフックで興味を引く（問題提起や意外な事実）
2. 2-{num_posts-1}つ目: 具体的な情報・ノウハウ・ステップを展開
3. 最後: まとめとCTA（フォロー・保存の促し）

【ルール】
- 各ポストは140文字以内
- 各ポストは「1/」「2/」などの番号で始める
- 具体的な数字や事例を含める
- 各ポストが独立しても価値がある内容にする

{num_posts}つのポストを改行で区切って出力してください:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        posts = response.content[0].text.strip().split("\n\n")
        return [p.strip() for p in posts if p.strip()]

    def generate_variations(
        self,
        topic: str,
        context: str,
        num_variations: int = 3,
        hashtags: Optional[list[str]] = None,
    ) -> list[str]:
        """
        同じトピックで異なるスタイルのポストを複数生成

        Args:
            topic: ポストのトピック
            context: リサーチで収集した情報
            num_variations: 生成するバリエーション数
            hashtags: 使用するハッシュタグのリスト
        """

        hashtag_text = ""
        if hashtags:
            hashtag_text = f"\n使用可能なハッシュタグ: {', '.join(['#' + h for h in hashtags])}"

        prompt = f"""あなたはX（Twitter）でAI×副業の情報を発信するインフルエンサーです。
以下の情報を基に、{num_variations}種類の異なるスタイルのポストを作成してください。

【トピック】
{topic}

【参考情報】
{context}
{hashtag_text}

【作成するスタイル】
1. 情報提供型: 具体的なTipsやデータを提示
2. 問いかけ型: 読者に考えさせる質問から始める
3. 体験談型: 「〜してみた」「〜がわかった」形式

【ルール】
- 各ポストは140文字以内
- 具体的で実用的な情報を含める
- それぞれ全く異なるアプローチで書く

{num_variations}つのポストを「---」で区切って出力してください:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        posts = response.content[0].text.strip().split("---")
        return [p.strip() for p in posts if p.strip()]

    def improve_post(self, original_post: str, feedback: str) -> str:
        """
        既存のポストをフィードバックに基づいて改善

        Args:
            original_post: 元のポスト
            feedback: 改善のためのフィードバック
        """

        prompt = f"""以下のXポストを、フィードバックに基づいて改善してください。

【元のポスト】
{original_post}

【フィードバック】
{feedback}

【ルール】
- 140文字以内に収める
- 元の意図は維持しつつ、より魅力的に
- 具体性を高める

改善したポストのみを出力してください:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()


def calculate_post_length(text: str) -> dict:
    """ポストの文字数を計算（X用）"""
    # 日本語は1文字、英数字は0.5文字としてカウント（X準拠）
    japanese_chars = sum(1 for c in text if ord(c) > 127)
    ascii_chars = len(text) - japanese_chars

    return {
        "total_chars": len(text),
        "japanese_chars": japanese_chars,
        "ascii_chars": ascii_chars,
        "x_weight": japanese_chars + (ascii_chars * 0.5),
        "is_valid": len(text) <= 280,
    }
