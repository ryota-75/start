"""
AI×副業に関する最新情報・トレンドをリサーチするモジュール
"""

import requests
from typing import Optional
from datetime import datetime


class AIBusinessResearcher:
    """AI×副業に関する情報をリサーチするクラス"""

    RESEARCH_TOPICS = [
        "AI 副業 最新トレンド 2025",
        "ChatGPT 副業 稼ぎ方",
        "AIツール 収益化 方法",
        "AI画像生成 副業",
        "AIライティング 副収入",
        "プロンプトエンジニアリング 仕事",
        "AI自動化 ビジネス",
        "AIコンテンツ作成 収益",
        "Midjourney Stable Diffusion 副業",
        "AI音声合成 ビジネス活用",
        "ノーコード AI ツール",
        "AI翻訳 副業",
        "AIチャットボット 開発 副業",
        "Claude API ビジネス活用",
        "AI動画編集 収益化",
    ]

    NICHE_TOPICS = [
        "AIエージェント 自動化 収益",
        "RAG システム 構築 副業",
        "ファインチューニング 受託開発",
        "AIアバター 制作 副業",
        "AI音楽生成 ロイヤリティフリー",
        "AIデータ分析 フリーランス",
        "LLM 活用 コンサルティング",
        "AI教育コンテンツ 制作",
        "プロンプト販売 マーケットプレイス",
        "AIキャラクター 開発 収益化",
    ]

    def __init__(self):
        self.collected_info = []

    def get_research_prompts(self, category: str = "all") -> list[str]:
        """リサーチ用のプロンプトを取得"""
        if category == "niche":
            return self.NICHE_TOPICS
        elif category == "trending":
            return self.RESEARCH_TOPICS
        else:
            return self.RESEARCH_TOPICS + self.NICHE_TOPICS

    def format_research_context(self, topic: str, search_results: str) -> str:
        """検索結果をリサーチコンテキストとしてフォーマット"""
        return f"""
【リサーチトピック】
{topic}

【収集した情報】
{search_results}

【収集日時】
{datetime.now().strftime("%Y年%m月%d日 %H:%M")}
"""

    def get_post_categories(self) -> dict:
        """投稿カテゴリとその説明を取得"""
        return {
            "tips": {
                "name": "実践的なTips",
                "description": "今すぐ使えるAI×副業のノウハウ",
                "hashtags": ["AI副業", "副業Tips", "AI活用術"],
            },
            "tools": {
                "name": "ツール紹介",
                "description": "知られざるAIツールの紹介",
                "hashtags": ["AIツール", "便利ツール", "生産性向上"],
            },
            "trends": {
                "name": "トレンド情報",
                "description": "AI×副業の最新動向",
                "hashtags": ["AIトレンド", "最新情報", "テック速報"],
            },
            "income": {
                "name": "収益化戦略",
                "description": "AIを使った具体的な稼ぎ方",
                "hashtags": ["AI収益化", "マネタイズ", "稼ぐ力"],
            },
            "beginner": {
                "name": "初心者向け",
                "description": "AI副業の始め方・入門情報",
                "hashtags": ["AI副業入門", "初心者歓迎", "始め方"],
            },
            "case_study": {
                "name": "事例紹介",
                "description": "成功事例・失敗事例の分析",
                "hashtags": ["成功事例", "AI活用事例", "学び"],
            },
        }


# 知られていないが有益な情報のテンプレート
HIDDEN_GEM_TEMPLATES = [
    {
        "topic": "プロンプトマーケットプレイス",
        "info": "PromptBaseやPromptHeroでプロンプトを販売可能。良質なプロンプトは1つ$2-$10で売れる",
        "tip": "ニッチな業界特化プロンプトが高値で売れやすい",
    },
    {
        "topic": "AI音声クローン副業",
        "info": "ElevenLabsやRVCを使ったナレーション制作。1件5000円〜が相場",
        "tip": "多言語対応できると単価が2-3倍に",
    },
    {
        "topic": "AIデータラベリング",
        "info": "RLHFのための人間フィードバック提供。Remotasksなどで時給$10-20",
        "tip": "専門知識があると高単価案件にアクセス可能",
    },
    {
        "topic": "LoRA作成代行",
        "info": "Stable Diffusion用のカスタムLoRA作成。1モデル1-3万円が相場",
        "tip": "企業のブランドキャラクター用LoRAは高単価",
    },
    {
        "topic": "AIチャットボット構築",
        "info": "Dify、Flowise、LangChainでノーコード/ローコード構築。1件10-50万円",
        "tip": "業界特化の知識ベース構築がキモ",
    },
    {
        "topic": "AI活用コンサルティング",
        "info": "中小企業向けAI導入支援。時給1-3万円が可能",
        "tip": "業務フロー分析とROI試算ができると信頼度UP",
    },
    {
        "topic": "プロンプトエンジニアリング講師",
        "info": "Udemy、ストアカでAI講座開講。月10-50万円の不労所得化可能",
        "tip": "実績をXで発信すると集客に直結",
    },
    {
        "topic": "AI翻訳×専門分野",
        "info": "DeepL+専門知識で高品質翻訳。医療・法律分野は文字単価3-5円",
        "tip": "AIの出力を専門家として校正する形が効率的",
    },
    {
        "topic": "AIアート NFT",
        "info": "Midjourney/DALL-E作品のNFT化。OpenSeaで0.01-0.1ETHで販売",
        "tip": "シリーズ化とストーリー性が重要",
    },
    {
        "topic": "RAGシステム構築",
        "info": "企業の社内文書検索AI構築。1案件30-100万円",
        "tip": "セキュリティとプライバシー対応がセールスポイント",
    },
]


def get_hidden_gems() -> list[dict]:
    """あまり知られていない有益な情報を取得"""
    return HIDDEN_GEM_TEMPLATES
