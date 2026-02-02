import React, { useState } from 'react';

// AI×副業の隠れた有益情報
const HIDDEN_GEMS = [
  {
    topic: "プロンプトマーケットプレイス",
    info: "PromptBaseやPromptHeroでプロンプトを販売可能。良質なプロンプトは1つ$2-$10で売れる",
    tip: "ニッチな業界特化プロンプトが高値で売れやすい",
  },
  {
    topic: "AI音声クローン副業",
    info: "ElevenLabsやRVCを使ったナレーション制作。1件5000円〜が相場",
    tip: "多言語対応できると単価が2-3倍に",
  },
  {
    topic: "LoRA作成代行",
    info: "Stable Diffusion用のカスタムLoRA作成。1モデル1-3万円が相場",
    tip: "企業のブランドキャラクター用LoRAは高単価",
  },
  {
    topic: "AIチャットボット構築",
    info: "Dify、Flowise、LangChainでノーコード/ローコード構築。1件10-50万円",
    tip: "業界特化の知識ベース構築がキモ",
  },
  {
    topic: "RAGシステム構築",
    info: "企業の社内文書検索AI構築。1案件30-100万円",
    tip: "セキュリティとプライバシー対応がセールスポイント",
  },
  {
    topic: "AI活用コンサルティング",
    info: "中小企業向けAI導入支援。時給1-3万円が可能",
    tip: "業務フロー分析とROI試算ができると信頼度UP",
  },
  {
    topic: "プロンプトエンジニアリング講師",
    info: "Udemy、ストアカでAI講座開講。月10-50万円の不労所得化可能",
    tip: "実績をXで発信すると集客に直結",
  },
  {
    topic: "AIデータラベリング",
    info: "RLHFのための人間フィードバック提供。Remotasksなどで時給$10-20",
    tip: "専門知識があると高単価案件にアクセス可能",
  },
];

const POST_TEMPLATES = {
  informative: [
    "【{topic}】\n{fact}\n\n具体的には{tip}\n\n#AI副業 #副業",
    "意外と知られてない{topic}の話。\n\n{fact}\n\nポイントは「{tip}」\n\n#AI副業 #副業Tips",
    "{topic}で稼ぐコツ👇\n\n✅ {fact}\n✅ {tip}\n\n今日から始められます\n\n#AI副業 #AI活用術",
  ],
  provocative: [
    "【悲報】まだ{topic}を知らない人、損してます\n\n{fact}\n\n{tip}\n\n#AI副業 #知らないと損",
    "99%の人が見落としてる{topic}の真実\n\n{fact}\n\n解決策→{tip}\n\n#AI副業",
    "「{topic}は難しい」←これ、嘘です\n\n実は{fact}\n\n{tip}で誰でも始められる\n\n#AI副業",
  ],
  casual: [
    "{topic}、マジで穴場かも。\n\n{fact}\n\nやり方は{tip}だけ。\n\n#AI副業 #副業",
    "最近{topic}始めたんだけど、{fact}って知ってた？\n\n{tip}がコツ💡\n\n#AI副業",
  ],
};

export default function AIPostGenerator() {
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [customTopic, setCustomTopic] = useState('');
  const [generatedPosts, setGeneratedPosts] = useState([]);
  const [copied, setCopied] = useState(null);

  const generatePosts = () => {
    let topic, fact, tip;

    if (customTopic) {
      topic = customTopic;
      fact = `${customTopic}は今注目のAI副業分野`;
      tip = "小さく始めて実績を作ることが大切";
    } else if (selectedTopic) {
      const gem = HIDDEN_GEMS.find(g => g.topic === selectedTopic);
      topic = gem.topic;
      fact = gem.info;
      tip = gem.tip;
    } else {
      const gem = HIDDEN_GEMS[Math.floor(Math.random() * HIDDEN_GEMS.length)];
      topic = gem.topic;
      fact = gem.info;
      tip = gem.tip;
    }

    const posts = [];
    const styles = ['informative', 'provocative', 'casual'];

    styles.forEach(style => {
      const templates = POST_TEMPLATES[style];
      const template = templates[Math.floor(Math.random() * templates.length)];
      const post = template
        .replace(/{topic}/g, topic)
        .replace(/{fact}/g, fact)
        .replace(/{tip}/g, tip);
      posts.push({ style, post, topic });
    });

    setGeneratedPosts(posts);
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopied(index);
    setTimeout(() => setCopied(null), 2000);
  };

  const styleLabels = {
    informative: '📊 情報提供型',
    provocative: '🔥 問いかけ型',
    casual: '💬 カジュアル型',
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #fef3f2 0%, #fef9f8 50%, #f0f9ff 100%)',
      padding: '24px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: 'bold',
            color: '#1f2937',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px'
          }}>
            🐦 AI×副業 Xポストジェネレーター
          </h1>
          <p style={{ color: '#6b7280', marginTop: '8px' }}>
            トピックを選んで、バズるポストを自動生成！
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          {/* Left Panel - Input */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              💎 トピックを選択
            </h2>

            {/* Topic Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '8px',
              marginBottom: '16px'
            }}>
              {HIDDEN_GEMS.map((gem) => (
                <button
                  key={gem.topic}
                  onClick={() => {
                    setSelectedTopic(gem.topic);
                    setCustomTopic('');
                  }}
                  style={{
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: selectedTopic === gem.topic ? '2px solid #f97316' : '1px solid #e5e7eb',
                    background: selectedTopic === gem.topic ? '#fff7ed' : 'white',
                    cursor: 'pointer',
                    fontSize: '13px',
                    textAlign: 'left',
                    transition: 'all 0.2s',
                  }}
                >
                  {gem.topic}
                </button>
              ))}
            </div>

            {/* Custom Input */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '14px', color: '#6b7280', display: 'block', marginBottom: '6px' }}>
                または、カスタムトピックを入力：
              </label>
              <input
                type="text"
                value={customTopic}
                onChange={(e) => {
                  setCustomTopic(e.target.value);
                  setSelectedTopic(null);
                }}
                placeholder="例: AI動画編集、GPTs販売..."
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #e5e7eb',
                  fontSize: '14px',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            {/* Generate Button */}
            <button
              onClick={generatePosts}
              style={{
                width: '100%',
                padding: '14px',
                background: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
            >
              ✨ ポストを生成する
            </button>

            {/* Selected Topic Info */}
            {selectedTopic && (
              <div style={{
                marginTop: '16px',
                padding: '12px',
                background: '#fef3c7',
                borderRadius: '8px',
                fontSize: '13px',
              }}>
                <strong>💡 {selectedTopic}</strong>
                <p style={{ marginTop: '4px', color: '#92400e' }}>
                  {HIDDEN_GEMS.find(g => g.topic === selectedTopic)?.info}
                </p>
              </div>
            )}
          </div>

          {/* Right Panel - Output */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              📝 生成されたポスト
            </h2>

            {generatedPosts.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '40px 20px',
                color: '#9ca3af',
              }}>
                <div style={{ fontSize: '48px', marginBottom: '12px' }}>🐦</div>
                <p>ここに生成されたポストが表示されます</p>
                <p style={{ fontSize: '13px' }}>左側でトピックを選んで生成ボタンを押してください</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {generatedPosts.map((item, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '16px',
                      background: '#f9fafb',
                      borderRadius: '12px',
                      border: '1px solid #e5e7eb',
                    }}
                  >
                    <div style={{
                      fontSize: '12px',
                      color: '#f97316',
                      fontWeight: '600',
                      marginBottom: '8px',
                    }}>
                      {styleLabels[item.style]}
                    </div>
                    <p style={{
                      fontSize: '14px',
                      lineHeight: '1.6',
                      whiteSpace: 'pre-wrap',
                      color: '#1f2937',
                    }}>
                      {item.post}
                    </p>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginTop: '12px',
                    }}>
                      <span style={{ fontSize: '12px', color: '#9ca3af' }}>
                        {item.post.length}文字
                      </span>
                      <button
                        onClick={() => copyToClipboard(item.post, index)}
                        style={{
                          padding: '6px 12px',
                          background: copied === index ? '#22c55e' : '#3b82f6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '12px',
                          cursor: 'pointer',
                        }}
                      >
                        {copied === index ? '✅ コピー完了' : '📋 コピー'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Features */}
        <div style={{
          marginTop: '32px',
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '16px',
        }}>
          {[
            { icon: '💎', title: '穴場トピック', desc: 'あまり知られていない高収益AI副業情報' },
            { icon: '🎯', title: '3スタイル生成', desc: '情報提供・問いかけ・カジュアルの3パターン' },
            { icon: '📊', title: '具体的な数字', desc: '相場や収益目安を含む説得力のある内容' },
          ].map((feature, i) => (
            <div
              key={i}
              style={{
                background: 'white',
                borderRadius: '12px',
                padding: '16px',
                textAlign: 'center',
                boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
              }}
            >
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>{feature.icon}</div>
              <div style={{ fontWeight: '600', fontSize: '14px', marginBottom: '4px' }}>{feature.title}</div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>{feature.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
