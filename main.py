#!/usr/bin/env python3
"""
AI×副業 Xポスト作成アプリ
- 最新トレンドのリサーチ
- あまり知られていない情報の提供
- AIによるポスト自動生成
"""

import argparse
import sys
import random
from dotenv import load_dotenv

from researcher import AIBusinessResearcher, get_hidden_gems
from post_generator import XPostGenerator, calculate_post_length


def print_header():
    """アプリのヘッダーを表示"""
    print("\n" + "=" * 60)
    print("  AI×副業 Xポスト作成アプリ")
    print("  〜フォロワーを増やす魅力的なコンテンツを自動生成〜")
    print("=" * 60 + "\n")


def cmd_topics(args):
    """利用可能なトピックを表示"""
    researcher = AIBusinessResearcher()

    print("\n📌 【トレンドトピック】")
    for i, topic in enumerate(researcher.RESEARCH_TOPICS, 1):
        print(f"  {i}. {topic}")

    print("\n💎 【ニッチトピック（穴場）】")
    for i, topic in enumerate(researcher.NICHE_TOPICS, 1):
        print(f"  {i}. {topic}")

    print("\n🔥 【あまり知られていない有益情報】")
    for gem in get_hidden_gems():
        print(f"\n  ▶ {gem['topic']}")
        print(f"    {gem['info']}")
        print(f"    💡 Tip: {gem['tip']}")


def cmd_categories(args):
    """投稿カテゴリを表示"""
    researcher = AIBusinessResearcher()
    categories = researcher.get_post_categories()

    print("\n📂 【投稿カテゴリ】\n")
    for key, cat in categories.items():
        hashtags = " ".join(["#" + h for h in cat["hashtags"]])
        print(f"  [{key}] {cat['name']}")
        print(f"      {cat['description']}")
        print(f"      {hashtags}\n")


def cmd_generate(args):
    """ポストを生成"""
    try:
        generator = XPostGenerator()
    except ValueError as e:
        print(f"\n❌ エラー: {e}")
        print("   環境変数 ANTHROPIC_API_KEY を設定してください")
        print("   例: export ANTHROPIC_API_KEY='your-api-key'")
        return

    researcher = AIBusinessResearcher()
    categories = researcher.get_post_categories()

    # トピック選択
    if args.topic:
        topic = args.topic
    else:
        gems = get_hidden_gems()
        gem = random.choice(gems)
        topic = gem["topic"]
        context_info = f"{gem['info']}\n💡 {gem['tip']}"
        print(f"\n🎲 ランダムトピック選択: {topic}")

    # カテゴリからハッシュタグ取得
    hashtags = []
    if args.category and args.category in categories:
        hashtags = categories[args.category]["hashtags"]
    else:
        hashtags = ["AI副業", "副業", "AI活用"]

    # コンテキスト情報
    if args.topic:
        gems = get_hidden_gems()
        matching = [g for g in gems if args.topic.lower() in g["topic"].lower()]
        if matching:
            context_info = f"{matching[0]['info']}\n💡 {matching[0]['tip']}"
        else:
            context_info = f"トピック「{args.topic}」に関するAI×副業の実践的な情報"
    # context_info is already set in random selection case

    print(f"\n⏳ ポストを生成中...")

    if args.variations:
        # 複数バリエーション生成
        posts = generator.generate_variations(
            topic=topic,
            context=context_info,
            num_variations=args.variations,
            hashtags=hashtags,
        )
        print(f"\n✨ {len(posts)}種類のポストを生成しました:\n")
        for i, post in enumerate(posts, 1):
            length_info = calculate_post_length(post)
            print(f"【パターン{i}】({length_info['total_chars']}文字)")
            print("-" * 40)
            print(post)
            print()
    elif args.thread:
        # スレッド生成
        posts = generator.generate_thread(
            topic=topic,
            context=context_info,
            num_posts=args.thread,
            hashtags=hashtags,
        )
        print(f"\n✨ {len(posts)}ポストのスレッドを生成しました:\n")
        for post in posts:
            length_info = calculate_post_length(post)
            print(f"({length_info['total_chars']}文字)")
            print(post)
            print()
    else:
        # 単一ポスト生成
        post = generator.generate_post(
            topic=topic,
            context=context_info,
            style=args.style or "informative",
            include_hashtags=not args.no_hashtags,
            hashtags=hashtags,
        )
        length_info = calculate_post_length(post)

        print(f"\n✨ ポストを生成しました ({length_info['total_chars']}文字):\n")
        print("-" * 40)
        print(post)
        print("-" * 40)

        if not length_info["is_valid"]:
            print(f"\n⚠️  警告: 文字数が280を超えています")


def cmd_gems(args):
    """隠れた有益情報からランダムにポストを生成"""
    try:
        generator = XPostGenerator()
    except ValueError as e:
        print(f"\n❌ エラー: {e}")
        print("   環境変数 ANTHROPIC_API_KEY を設定してください")
        return

    gems = get_hidden_gems()

    if args.all:
        selected_gems = gems
    else:
        num = min(args.num or 1, len(gems))
        selected_gems = random.sample(gems, num)

    print(f"\n💎 隠れた有益情報からポストを生成中...\n")

    for gem in selected_gems:
        context = f"{gem['info']}\n💡 Tip: {gem['tip']}"

        post = generator.generate_post(
            topic=gem["topic"],
            context=context,
            style="provocative",
            hashtags=["AI副業", "知らないと損", "副業Tips"],
        )

        length_info = calculate_post_length(post)
        print(f"📌 {gem['topic']} ({length_info['total_chars']}文字)")
        print("-" * 40)
        print(post)
        print("-" * 40 + "\n")


def cmd_interactive(args):
    """インタラクティブモード"""
    try:
        generator = XPostGenerator()
    except ValueError as e:
        print(f"\n❌ エラー: {e}")
        return

    researcher = AIBusinessResearcher()

    print_header()
    print("インタラクティブモードへようこそ！")
    print("コマンド: topics, categories, generate, gems, quit\n")

    while True:
        try:
            cmd = input("🤖 > ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 終了します")
            break

        if cmd in ["quit", "exit", "q"]:
            print("\n👋 終了します")
            break
        elif cmd == "topics":
            cmd_topics(None)
        elif cmd == "categories":
            cmd_categories(None)
        elif cmd == "gems":
            gems = get_hidden_gems()
            gem = random.choice(gems)
            context = f"{gem['info']}\n💡 {gem['tip']}"

            print(f"\n💎 トピック: {gem['topic']}")
            print("⏳ 生成中...")

            post = generator.generate_post(
                topic=gem["topic"],
                context=context,
                style="provocative",
                hashtags=["AI副業", "知らないと損"],
            )
            print(f"\n{post}\n")
        elif cmd == "generate" or cmd == "g":
            topic = input("トピックを入力 (空欄でランダム): ").strip()
            if not topic:
                gems = get_hidden_gems()
                gem = random.choice(gems)
                topic = gem["topic"]
                context = f"{gem['info']}\n💡 {gem['tip']}"
            else:
                context = f"AI×副業における「{topic}」に関する実践的な情報"

            print(f"\n📌 トピック: {topic}")
            print("⏳ 生成中...")

            post = generator.generate_post(
                topic=topic,
                context=context,
                style="informative",
                hashtags=["AI副業", "副業"],
            )
            print(f"\n{post}\n")
        elif cmd == "help" or cmd == "h":
            print("\n📖 コマンド一覧:")
            print("  topics     - 利用可能なトピックを表示")
            print("  categories - 投稿カテゴリを表示")
            print("  generate   - ポストを生成")
            print("  gems       - 隠れた有益情報からポスト生成")
            print("  quit       - 終了\n")
        elif cmd:
            print(f"❓ 不明なコマンド: {cmd}")
            print("   'help' でコマンド一覧を表示\n")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="AI×副業 Xポスト作成アプリ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py topics                    # トピック一覧を表示
  python main.py generate                  # ランダムなトピックでポスト生成
  python main.py generate -t "プロンプト販売"  # 指定トピックでポスト生成
  python main.py generate --variations 3   # 3種類のバリエーションを生成
  python main.py generate --thread 5       # 5ポストのスレッドを生成
  python main.py gems                      # 隠れた有益情報からポスト生成
  python main.py interactive               # インタラクティブモード
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="利用可能なコマンド")

    # topics コマンド
    subparsers.add_parser("topics", help="利用可能なトピックを表示")

    # categories コマンド
    subparsers.add_parser("categories", help="投稿カテゴリを表示")

    # generate コマンド
    gen_parser = subparsers.add_parser("generate", help="ポストを生成")
    gen_parser.add_argument("-t", "--topic", help="ポストのトピック")
    gen_parser.add_argument(
        "-c",
        "--category",
        choices=["tips", "tools", "trends", "income", "beginner", "case_study"],
        help="投稿カテゴリ",
    )
    gen_parser.add_argument(
        "-s",
        "--style",
        choices=["informative", "casual", "provocative", "storytelling"],
        help="ポストのスタイル",
    )
    gen_parser.add_argument(
        "--variations", type=int, help="生成するバリエーション数"
    )
    gen_parser.add_argument(
        "--thread", type=int, help="スレッドのポスト数"
    )
    gen_parser.add_argument(
        "--no-hashtags", action="store_true", help="ハッシュタグを含めない"
    )

    # gems コマンド
    gems_parser = subparsers.add_parser(
        "gems", help="隠れた有益情報からポストを生成"
    )
    gems_parser.add_argument(
        "-n", "--num", type=int, default=1, help="生成するポスト数"
    )
    gems_parser.add_argument(
        "--all", action="store_true", help="全ての情報からポストを生成"
    )

    # interactive コマンド
    subparsers.add_parser("interactive", help="インタラクティブモード")

    args = parser.parse_args()

    print_header()

    if args.command == "topics":
        cmd_topics(args)
    elif args.command == "categories":
        cmd_categories(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "gems":
        cmd_gems(args)
    elif args.command == "interactive":
        cmd_interactive(args)
    else:
        parser.print_help()
        print("\n💡 ヒント: 'python main.py interactive' でインタラクティブモードを起動")


if __name__ == "__main__":
    main()
