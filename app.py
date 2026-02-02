"""
AI×副業 Xポスト作成アプリ - Web API
FastAPIによるWebサーバー
"""

import os
import random
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from researcher import AIBusinessResearcher, get_hidden_gems
from post_generator import XPostGenerator, calculate_post_length

load_dotenv()

app = FastAPI(
    title="AI×副業 Xポスト作成API",
    description="AI×副業に関する情報をリサーチしてXのポストを自動生成するAPI",
    version="1.0.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    topic: Optional[str] = None
    category: Optional[str] = None
    style: Optional[str] = "informative"
    include_hashtags: bool = True


class ThreadRequest(BaseModel):
    topic: Optional[str] = None
    num_posts: int = 5


class VariationsRequest(BaseModel):
    topic: Optional[str] = None
    num_variations: int = 3


# HTMLテンプレート
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI×副業 Xポスト作成アプリ</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            color: rgba(255,255,255,0.8);
            text-align: center;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .form-group {
            margin-bottom: 16px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            color: #333;
        }
        select, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.2s;
        }
        select:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .result {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        .result.show { display: block; }
        .post-text {
            font-size: 18px;
            line-height: 1.6;
            color: #333;
            white-space: pre-wrap;
        }
        .char-count {
            text-align: right;
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }
        .copy-btn {
            margin-top: 12px;
            padding: 10px 20px;
            background: #1da1f2;
            width: auto;
        }
        .gems-list {
            display: grid;
            gap: 12px;
        }
        .gem-item {
            background: #f0f4ff;
            padding: 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .gem-item:hover {
            background: #e0e8ff;
        }
        .gem-title {
            font-weight: 600;
            color: #667eea;
        }
        .gem-info {
            font-size: 14px;
            color: #666;
            margin-top: 4px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .loading.show { display: block; }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            flex: 1;
            padding: 12px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        }
        .tab.active {
            background: white;
            color: #667eea;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI×副業 Xポスト作成</h1>
        <p class="subtitle">フォロワーを増やす魅力的なコンテンツを自動生成</p>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('generate')">ポスト生成</button>
            <button class="tab" onclick="switchTab('gems')">💎 隠れ情報</button>
            <button class="tab" onclick="switchTab('thread')">スレッド</button>
        </div>

        <div id="generate-tab" class="tab-content active">
            <div class="card">
                <div class="form-group">
                    <label>トピック（空欄でランダム）</label>
                    <input type="text" id="topic" placeholder="例: プロンプト販売、LoRA作成代行">
                </div>
                <div class="form-group">
                    <label>カテゴリ</label>
                    <select id="category">
                        <option value="">選択してください</option>
                        <option value="tips">実践的なTips</option>
                        <option value="tools">ツール紹介</option>
                        <option value="trends">トレンド情報</option>
                        <option value="income">収益化戦略</option>
                        <option value="beginner">初心者向け</option>
                        <option value="case_study">事例紹介</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>スタイル</label>
                    <select id="style">
                        <option value="informative">情報提供型</option>
                        <option value="casual">カジュアル</option>
                        <option value="provocative">問いかけ型</option>
                        <option value="storytelling">ストーリー型</option>
                    </select>
                </div>
                <button class="btn" onclick="generatePost()">✨ ポストを生成</button>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p style="margin-top:10px;color:#666;">生成中...</p>
                </div>

                <div class="result" id="result">
                    <div class="post-text" id="post-text"></div>
                    <div class="char-count" id="char-count"></div>
                    <button class="btn copy-btn" onclick="copyPost()">📋 コピー</button>
                </div>
            </div>
        </div>

        <div id="gems-tab" class="tab-content">
            <div class="card">
                <h3 style="margin-bottom:16px;">💎 あまり知られていない有益情報</h3>
                <p style="color:#666;margin-bottom:16px;">クリックするとその情報でポストを生成します</p>
                <div class="gems-list" id="gems-list"></div>
            </div>
        </div>

        <div id="thread-tab" class="tab-content">
            <div class="card">
                <div class="form-group">
                    <label>トピック（空欄でランダム）</label>
                    <input type="text" id="thread-topic" placeholder="例: AI副業の始め方">
                </div>
                <div class="form-group">
                    <label>ポスト数</label>
                    <select id="thread-count">
                        <option value="3">3ポスト</option>
                        <option value="5" selected>5ポスト</option>
                        <option value="7">7ポスト</option>
                    </select>
                </div>
                <button class="btn" onclick="generateThread()">📝 スレッドを生成</button>

                <div class="loading" id="thread-loading">
                    <div class="spinner"></div>
                    <p style="margin-top:10px;color:#666;">生成中...</p>
                </div>

                <div class="result" id="thread-result"></div>
            </div>
        </div>
    </div>

    <script>
        let currentPost = '';

        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
        }

        async function generatePost(topic = null) {
            const topicValue = topic || document.getElementById('topic').value;
            const category = document.getElementById('category').value;
            const style = document.getElementById('style').value;

            document.getElementById('loading').classList.add('show');
            document.getElementById('result').classList.remove('show');

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        topic: topicValue || null,
                        category: category || null,
                        style: style
                    })
                });
                const data = await response.json();

                if (data.error) {
                    alert('エラー: ' + data.error);
                    return;
                }

                currentPost = data.post;
                document.getElementById('post-text').textContent = data.post;
                document.getElementById('char-count').textContent =
                    data.length.total_chars + '文字 / 280';
                document.getElementById('result').classList.add('show');
            } catch (e) {
                alert('エラーが発生しました: ' + e.message);
            } finally {
                document.getElementById('loading').classList.remove('show');
            }
        }

        async function generateThread() {
            const topic = document.getElementById('thread-topic').value;
            const count = document.getElementById('thread-count').value;

            document.getElementById('thread-loading').classList.add('show');
            document.getElementById('thread-result').classList.remove('show');

            try {
                const response = await fetch('/api/thread', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        topic: topic || null,
                        num_posts: parseInt(count)
                    })
                });
                const data = await response.json();

                if (data.error) {
                    alert('エラー: ' + data.error);
                    return;
                }

                let html = '';
                data.posts.forEach((post, i) => {
                    html += `<div style="background:#f0f4ff;padding:16px;border-radius:8px;margin-bottom:12px;">
                        <div style="font-size:16px;line-height:1.5;">${post}</div>
                        <div style="text-align:right;color:#666;font-size:12px;margin-top:8px;">
                            ${post.length}文字
                        </div>
                    </div>`;
                });
                document.getElementById('thread-result').innerHTML = html;
                document.getElementById('thread-result').classList.add('show');
            } catch (e) {
                alert('エラーが発生しました: ' + e.message);
            } finally {
                document.getElementById('thread-loading').classList.remove('show');
            }
        }

        function copyPost() {
            navigator.clipboard.writeText(currentPost);
            event.target.textContent = '✅ コピーしました！';
            setTimeout(() => {
                event.target.textContent = '📋 コピー';
            }, 2000);
        }

        async function loadGems() {
            const response = await fetch('/api/gems');
            const data = await response.json();

            let html = '';
            data.gems.forEach(gem => {
                html += `<div class="gem-item" onclick="generateFromGem('${gem.topic.replace(/'/g, "\\'")}')">
                    <div class="gem-title">💎 ${gem.topic}</div>
                    <div class="gem-info">${gem.info}</div>
                </div>`;
            });
            document.getElementById('gems-list').innerHTML = html;
        }

        function generateFromGem(topic) {
            switchTab('generate');
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.querySelectorAll('.tab')[1].classList.remove('active');
            document.getElementById('topic').value = topic;
            generatePost(topic);
        }

        // 初期化
        loadGems();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    """メインページ"""
    return HTML_TEMPLATE


@app.get("/api/health")
async def health():
    """ヘルスチェック"""
    generator = XPostGenerator()
    return {
        "status": "ok",
        "app": "AI×副業 Xポスト作成API",
        "backend": generator.get_backend_info(),
    }


@app.get("/api/backend")
async def get_backend():
    """使用中のバックエンド情報を取得"""
    generator = XPostGenerator()
    return generator.get_backend_info()


@app.get("/api/topics")
async def get_topics():
    """利用可能なトピックを取得"""
    researcher = AIBusinessResearcher()
    return {
        "trending": researcher.RESEARCH_TOPICS,
        "niche": researcher.NICHE_TOPICS,
    }


@app.get("/api/categories")
async def get_categories():
    """投稿カテゴリを取得"""
    researcher = AIBusinessResearcher()
    return researcher.get_post_categories()


@app.get("/api/gems")
async def get_gems_list():
    """隠れた有益情報を取得"""
    return {"gems": get_hidden_gems()}


@app.post("/api/generate")
async def generate_post(request: GenerateRequest):
    """ポストを生成"""
    generator = XPostGenerator()
    researcher = AIBusinessResearcher()
    categories = researcher.get_post_categories()

    # トピック選択
    if request.topic:
        topic = request.topic
        gems = get_hidden_gems()
        matching = [g for g in gems if request.topic.lower() in g["topic"].lower()]
        if matching:
            context_info = f"{matching[0]['info']}\n💡 {matching[0]['tip']}"
        else:
            context_info = f"AI×副業における「{request.topic}」に関する実践的な情報"
    else:
        gems = get_hidden_gems()
        gem = random.choice(gems)
        topic = gem["topic"]
        context_info = f"{gem['info']}\n💡 {gem['tip']}"

    # ハッシュタグ
    hashtags = ["AI副業", "副業", "AI活用"]
    if request.category and request.category in categories:
        hashtags = categories[request.category]["hashtags"]

    post = generator.generate_post(
        topic=topic,
        context=context_info,
        style=request.style or "informative",
        include_hashtags=request.include_hashtags,
        hashtags=hashtags,
    )

    length_info = calculate_post_length(post)

    return {
        "post": post,
        "topic": topic,
        "length": length_info,
        "backend": generator.get_backend_info(),
    }


@app.post("/api/thread")
async def generate_thread(request: ThreadRequest):
    """スレッドを生成"""
    generator = XPostGenerator()

    # トピック選択
    if request.topic:
        topic = request.topic
        context_info = f"AI×副業における「{request.topic}」に関する実践的な情報"
    else:
        gems = get_hidden_gems()
        gem = random.choice(gems)
        topic = gem["topic"]
        context_info = f"{gem['info']}\n💡 {gem['tip']}"

    posts = generator.generate_thread(
        topic=topic,
        context=context_info,
        num_posts=request.num_posts,
        hashtags=["AI副業", "副業"],
    )

    return {
        "posts": posts,
        "topic": topic,
    }


@app.post("/api/variations")
async def generate_variations(request: VariationsRequest):
    """バリエーションを生成"""
    generator = XPostGenerator()

    # トピック選択
    if request.topic:
        topic = request.topic
        context_info = f"AI×副業における「{request.topic}」に関する実践的な情報"
    else:
        gems = get_hidden_gems()
        gem = random.choice(gems)
        topic = gem["topic"]
        context_info = f"{gem['info']}\n💡 {gem['tip']}"

    posts = generator.generate_variations(
        topic=topic,
        context=context_info,
        num_variations=request.num_variations,
        hashtags=["AI副業", "副業"],
    )

    return {
        "posts": posts,
        "topic": topic,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
