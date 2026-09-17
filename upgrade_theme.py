import re
import os

html_file = 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace Fonts
new_fonts = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@500;700;800&family=Space+Grotesk:wght@500;700;800&display=swap" rel="stylesheet">'
content = re.sub(r'<link href="https://fonts\.googleapis\.com/css2[^"]+" rel="stylesheet">', new_fonts, content)

# 2. Complete CSS Replacement
new_style = """<style>
        :root {
            --bg-color: #030712;
            --glass-bg: rgba(17, 24, 39, 0.6);
            --glass-border: rgba(56, 189, 248, 0.15);
            --glass-highlight: rgba(56, 189, 248, 0.3);
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.6);
            --k8s-blue: #326ce5;
            --az-blue: #0078d4;
            --ai-purp: #a855f7;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
        }

        /* Ambient Cyber Grid Background */
        body {
            background-color: var(--bg-color);
            background-image: 
                linear-gradient(rgba(56, 189, 248, 0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(56, 189, 248, 0.04) 1px, transparent 1px),
                radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.15), transparent 40%),
                radial-gradient(circle at 10% 90%, rgba(139, 92, 246, 0.1), transparent 40%);
            background-size: 30px 30px, 30px 30px, 100% 100%, 100% 100%;
            background-attachment: fixed;
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 2.5rem 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
        }

        /* Subtle scanlines for terminal vibe */
        body::after {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.15) 50%);
            background-size: 100% 4px;
            z-index: 9999;
            pointer-events: none;
            opacity: 0.6;
        }

        .container { width: 100%; max-width: 1400px; position: relative; z-index: 10; }
        
        /* Modern Space Grotesk Typography */
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.5px; }
        
        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid var(--glass-border); padding-bottom: 1rem; margin-bottom: 3rem;
        }
        .time-display {
            font-family: 'JetBrains Mono', monospace; font-size: 1.25rem !important;
            background: linear-gradient(135deg, #38bdf8, #a855f7); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; font-weight: bold;
            text-shadow: 0 0 10px rgba(168, 85, 247, 0.4);
        }
        
        /* Cyber Neon Header */
        h1 {
            font-size: 3.8rem; font-weight: 800; text-align: center; margin: 0.5rem 0;
            background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 40%, #38bdf8 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-transform: uppercase;
            filter: drop-shadow(0 0 25px rgba(56, 189, 248, 0.4));
            animation: pulse-glow 3s ease-in-out infinite alternate;
        }
        
        @keyframes pulse-glow {
            0% { filter: drop-shadow(0 0 20px rgba(56,189,248,0.2)); }
            100% { filter: drop-shadow(0 0 35px rgba(56,189,248,0.6)); }
        }

        .quote-container {
            max-width: 800px; margin: 0 auto 3.5rem auto; text-align: center;
            font-style: italic; font-size: 1.15rem; color: #cbd5e1;
            background: rgba(10, 15, 30, 0.5); padding: 1.5rem 2rem;
            border-radius: 12px; border: 1px solid var(--glass-border); border-left: 4px solid var(--accent);
            backdrop-filter: blur(12px); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        }
        
        .controls {
            display: flex; justify-content: center; align-items: center; gap: 1.5rem;
            margin: 0 auto 3.5rem auto; background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(12px); padding: 0.85rem 2rem; border-radius: 50px;
            border: 1px solid rgba(56, 189, 248, 0.2); box-shadow: 0 0 25px rgba(56, 189, 248, 0.1);
        }
        
        .btn {
            background: rgba(255, 255, 255, 0.03); border: 1px solid var(--glass-border);
            color: var(--text-main); padding: 0.6rem 1.4rem; border-radius: 30px;
            cursor: pointer; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            text-transform: uppercase; font-weight: 600; letter-spacing: 1px;
        }
        
        .btn:hover {
            background: rgba(56, 189, 248, 0.15); border-color: var(--accent);
            transform: translateY(-3px) scale(1.05); box-shadow: 0 5px 20px var(--accent-glow);
            color: #fff;
        }
        
        .date-display { font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: var(--text-main); font-weight: bold; }
        
        .countdown-container { display: flex; gap: 2rem; margin-bottom: 3.5rem; width: 100%; justify-content: center; flex-wrap: wrap; }
        .countdown-card {
            background: linear-gradient(145deg, rgba(17, 24, 39, 0.8), rgba(3, 7, 18, 0.9));
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255,255,255,0.05);
            padding: 1.5rem 2.5rem; border-radius: 16px; text-align: center; min-width: 240px;
            position: relative; overflow: hidden;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5), 0 10px 30px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        /* Top Glowing Line for HUD effect */
        .countdown-card::before {
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px;
            background: var(--card-color, #38bdf8);
            box-shadow: 0 0 15px var(--card-color, #38bdf8);
        }
        .countdown-card:hover { transform: translateY(-5px); box-shadow: inset 0 0 20px rgba(0,0,0,0.6), 0 15px 40px rgba(0,0,0,0.4), 0 0 20px rgba(255,255,255,0.05); }
        .countdown-title { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.85rem; color: var(--text-dim); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 2px; }
        .countdown-timer { font-family: 'Space Grotesk', sans-serif; font-size: 2rem; color: var(--text-main); font-weight: 800; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
        
        /* ── HOLOGRAPHIC BENTO BOX ── */
        #content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem; align-items: start; max-width: 1400px;
        }
        
        .card:nth-child(5) { grid-column: 1 / -1; }
        @media (min-width: 1400px) {
            #content { grid-template-columns: repeat(3, 1fr); }
            .card:nth-child(4) { grid-column: span 1; }
            .card:nth-child(5) { grid-column: span 2; }
            .card:nth-child(6) { grid-column: span 1; }
        }
        
        .card {
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.7) 0%, rgba(3, 7, 18, 0.9) 100%);
            backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.04);
            border-top: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px; padding: 2rem; 
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.05);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            --accent: #38bdf8; --accent-glow: rgba(56, 189, 248, 0.3);
            
            /* Staggered Animation */
            opacity: 0; animation: fadeInUp 0.6s ease forwards;
        }
        
        .card::before {
            content: "";
            position: absolute; inset: 0; border-radius: 20px;
            padding: 2px; /* Border thickness */
            background: linear-gradient(135deg, transparent 40%, var(--accent) 100%);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor; mask-composite: exclude;
            opacity: 0; transition: opacity 0.4s ease;
            pointer-events: none;
        }
        
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
        
        .card:nth-child(1) { animation-delay: 0.05s; } .card:nth-child(2) { animation-delay: 0.1s; }
        .card:nth-child(3) { animation-delay: 0.15s; } .card:nth-child(4) { animation-delay: 0.2s; }
        .card:nth-child(5) { animation-delay: 0.25s; } .card:nth-child(6) { animation-delay: 0.3s; }
        .card:nth-child(7) { animation-delay: 0.35s; } .card:nth-child(8) { animation-delay: 0.4s; }
        
        .card:hover { 
            transform: translateY(-6px); 
            box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 40px var(--accent-glow);
        }
        .card:hover::before { opacity: 1; }

        .card h2 {
            margin-top: 0; font-size: 1.45rem; font-weight: 700; display: flex; justify-content: space-between;
            align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 1.25rem; margin-bottom: 1.25rem; line-height: 1.4;
            color: #f8fafc;
        }
        
        .course-link {
            font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #fff; text-decoration: none;
            background: rgba(255, 255, 255, 0.05); padding: 0.5rem 1rem; border-radius: 20px; transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1); white-space: nowrap; margin-left: 1rem; text-transform: uppercase; letter-spacing: 0.5px;
        }
        .course-link:hover { background: var(--accent); border-color: var(--accent); color: #000; box-shadow: 0 0 15px var(--accent-glow); transform: scale(1.05); }
        
        .task-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 1rem; }
        .task-item {
            background: rgba(0, 0, 0, 0.3); border-radius: 10px; padding: 1.25rem;
            border-left: 3px solid var(--accent); font-size: 0.95rem; line-height: 1.6; transition: all 0.2s;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.2);
        }
        .task-item:hover { background: rgba(0,0,0,0.5); transform: translateX(5px); }
        .task-meta { font-size: 0.8rem; color: #64748b; margin-top: 0.75rem; font-family: 'JetBrains Mono', monospace; display: flex; align-items: center; gap: 0.5rem; text-transform: uppercase; }
        .empty-state { color: var(--text-dim); font-style: italic; text-align: center; padding: 2rem; background: rgba(0,0,0,0.1); border-radius: 12px; }
        
        .loader { border: 3px solid rgba(255, 255, 255, 0.05); border-top: 3px solid var(--accent); border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 40px auto; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        
        /* ── Holographic Terminal Identity ── */
        .terminal-block {
            background: rgba(0,0,0,0.7) !important;
            padding: 1.75rem !important;
            border-radius: 12px !important;
            font-family: 'JetBrains Mono', monospace !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
            border-left: 4px solid #10b981 !important;
            color: #cbd5e1 !important;
            position: relative;
            overflow: hidden;
            box-shadow: inset 0 0 30px rgba(0,0,0,0.8), 0 5px 15px rgba(0,0,0,0.3) !important;
        }
        .terminal-block::before {
            content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(rgba(16, 185, 129, 0.05) 50%, transparent 50%);
            background-size: 100% 4px; pointer-events: none;
        }

        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        .cursor-blink { animation: blink 1s step-end infinite; }
    
        /* ── Backlog Cards ── */
        .backlog-card {
            --accent: #f97316; --accent-glow: rgba(249, 115, 22, 0.4); border-color: rgba(249, 115, 22, 0.3) !important;
            background: linear-gradient(180deg, rgba(249,115,22,0.1) 0%, rgba(30,41,59,0.8) 100%) !important;
        }
        .backlog-item { background: rgba(0, 0, 0, 0.4); border-radius: 10px; padding: 1.25rem; border-left: 3px solid #f97316; font-size: 0.95rem; line-height: 1.5; }
        .backlog-meta { font-size: 0.75rem; color: #fb923c; margin-top: 0.5rem; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }
        
        @media (max-width: 1024px) { #content { grid-template-columns: 1fr; } .card:nth-child(5) { grid-column: auto; } }
        @media (max-width: 640px) {
            body { padding: 1.5rem 0.5rem; } 
            h1 { font-size: 2.25rem !important; animation: none; filter: none; }
            .countdown-card { min-width: unset; flex: 1; padding: 1rem; }
            .card { padding: 1.5rem; border-radius: 16px; }
            .card h2 { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
            .course-link { margin-left: 0; width: 100%; text-align: center; }
            .top-bar { flex-direction: column !important; gap: 1rem; }
            .controls { flex-wrap: wrap; width: 100%; justify-content: center; }
            .btn { width: 45%; flex-grow: 1; text-align: center; }
            .date-display { width: 100%; text-align: center; margin: 0.5rem 0; }
        }
    </style>"""
content = re.sub(r'<style>.*?</style>', new_style, content, flags=re.DOTALL)

# 3. Add classes for dynamic colors on countdown cards
content = content.replace('style="border-bottom: 3px solid var(--k8s-blue);"', 'style="--card-color: var(--k8s-blue);"')
content = content.replace('style="border-bottom: 3px solid var(--az-blue);"', 'style="--card-color: var(--az-blue);"')

# 4. Modify the Terminal block to use the new "terminal-block" class
content = content.replace('style="background: rgba(0,0,0,0.5); padding: 1.5rem; border-radius: 12px; font-family: \'JetBrains Mono\', monospace; border-left: 3px solid #10b981; color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);"', 'class="terminal-block"')

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("success!")
