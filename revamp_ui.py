import re

def revamp_html():
    target_path = r'c:\Job Tracker\index.html'
    
    with open(target_path, 'r', encoding='utf-8') as f:
        html_src = f.read()

    new_css = """<style>
        :root {
            --bg-color: #030712;
            --glass-bg: rgba(17, 24, 39, 0.6);
            --glass-border: rgba(255, 255, 255, 0.06);
            --glass-highlight: rgba(255, 255, 255, 0.1);
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.3);
            --k8s-blue: #326ce5;
            --az-blue: #0078d4;
            --ai-purp: #a855f7;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
        }
        body {
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.08), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.08), transparent 25%),
                radial-gradient(circle at 50% 90%, rgba(16, 185, 129, 0.05), transparent 30%);
            background-attachment: fixed;
            background-size: cover;
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 2.5rem 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container { width: 100%; max-width: 1400px; }
        h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif; }
        .top-bar {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid var(--glass-border); padding-bottom: 1rem; margin-bottom: 3rem;
        }
        .time-display {
            font-family: 'JetBrains Mono', monospace; font-size: 1.25rem !important;
            background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; font-weight: bold;
        }
        h1 {
            font-size: 3.8rem; font-weight: 800; text-align: center; margin: 0.5rem 0;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: -1.5px; filter: drop-shadow(0 4px 20px rgba(255,255,255,0.05));
        }
        .quote-container {
            max-width: 800px; margin: 0 auto 3.5rem auto; text-align: center;
            font-style: italic; font-size: 1.15rem; color: #cbd5e1;
            background: rgba(255, 255, 255, 0.015); padding: 1.5rem 2rem;
            border-radius: 16px; border: 1px solid var(--glass-border); border-left: 4px solid #818cf8;
            backdrop-filter: blur(8px); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .controls {
            display: inline-flex; justify-content: center; align-items: center; gap: 1.5rem;
            margin: 0 auto 3.5rem auto; background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(12px); padding: 0.75rem 1.5rem; border-radius: 50px;
            border: 1px solid var(--glass-border); box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            position: relative; left: 50%; transform: translateX(-50%);
        }
        .btn {
            background: rgba(255, 255, 255, 0.03); border: 1px solid var(--glass-border);
            color: var(--text-main); padding: 0.6rem 1.25rem; border-radius: 30px;
            cursor: pointer; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .btn:hover {
            background: rgba(255, 255, 255, 0.08); border-color: rgba(255,255,255,0.2);
            transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .date-display { font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: var(--text-main); font-weight: bold; }
        .countdown-container { display: flex; gap: 1.5rem; margin-bottom: 3.5rem; width: 100%; justify-content: center; flex-wrap: wrap; }
        .countdown-card {
            background: rgba(17, 24, 39, 0.4); backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border); border-top: 1px solid var(--glass-highlight);
            padding: 1.25rem 2rem; border-radius: 16px; text-align: center; min-width: 220px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .countdown-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .countdown-title { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 0.9rem; color: var(--text-dim); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px; }
        .countdown-timer { font-family: 'JetBrains Mono', monospace; font-size: 1.75rem; color: var(--text-main); font-weight: bold; }
        
        /* ── BENTO BOX GRID ── */
        #content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
            gap: 1.75rem; align-items: start; max-width: 1400px;
        }
        
        /* Special Spans */
        .card:nth-child(5) { grid-column: 1 / -1; } /* Cold Email Template */
        @media (min-width: 1400px) {
            #content { grid-template-columns: repeat(3, 1fr); }
            .card:nth-child(4) { grid-column: span 1; }
            .card:nth-child(5) { grid-column: span 2; }
            .card:nth-child(6) { grid-column: span 1; }
        }
        
        .card {
            background: var(--glass-bg); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--glass-border); border-top: 1px solid rgba(255,255,255,0.12);
            border-radius: 24px; padding: 2rem; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2), inset 0 0 0 1px rgba(255,255,255,0.02);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            --accent: #38bdf8; --accent-glow: rgba(56, 189, 248, 0.3);
            
            /* Staggered Animation */
            opacity: 0; animation: fadeInUp 0.6s ease forwards;
        }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        
        .card:nth-child(1) { animation-delay: 0.05s; } .card:nth-child(2) { animation-delay: 0.1s; }
        .card:nth-child(3) { animation-delay: 0.15s; } .card:nth-child(4) { animation-delay: 0.2s; }
        .card:nth-child(5) { animation-delay: 0.25s; } .card:nth-child(6) { animation-delay: 0.3s; }
        .card:nth-child(7) { animation-delay: 0.35s; } .card:nth-child(8) { animation-delay: 0.4s; }
        
        .card:hover { border-color: var(--accent); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px var(--accent-glow); transform: translateY(-4px); }
        .card h2 {
            margin-top: 0; font-size: 1.45rem; font-weight: 700; display: flex; justify-content: space-between;
            align-items: center; border-bottom: 1px solid var(--glass-border); padding-bottom: 1.25rem; margin-bottom: 1.25rem; line-height: 1.4;
        }
        .course-link {
            font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--accent); text-decoration: none;
            background: rgba(255, 255, 255, 0.05); padding: 0.4rem 0.8rem; border-radius: 20px; transition: all 0.2s;
            border: 1px solid transparent; white-space: nowrap; margin-left: 1rem;
        }
        .course-link:hover { background: var(--accent-glow); border-color: var(--accent); color: #fff; transform: translateY(-1px); }
        
        .task-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.8rem; }
        .task-item {
            background: rgba(0, 0, 0, 0.3); border-radius: 14px; padding: 1.25rem;
            border-left: 3px solid var(--accent); font-size: 0.95rem; line-height: 1.6; transition: background 0.2s;
        }
        .task-item:hover { background: rgba(0,0,0,0.4); }
        .task-meta { font-size: 0.8rem; color: var(--text-dim); margin-top: 0.75rem; font-family: 'JetBrains Mono', monospace; display: flex; align-items: center; gap: 0.5rem; }
        .empty-state { color: var(--text-dim); font-style: italic; text-align: center; padding: 2rem; background: rgba(0,0,0,0.1); border-radius: 12px; }
        
        .loader { border: 3px solid rgba(255, 255, 255, 0.05); border-top: 3px solid #38bdf8; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 40px auto; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        
        /* ── Backlog Cards ── */
        .backlog-card {
            --accent: #f97316; --accent-glow: rgba(249, 115, 22, 0.2); border-color: rgba(249, 115, 22, 0.3) !important;
            background: linear-gradient(180deg, rgba(249,115,22,0.08) 0%, rgba(30,41,59,0.7) 100%) !important;
        }
        .backlog-item { background: rgba(0, 0, 0, 0.3); border-radius: 12px; padding: 1.25rem; border-left: 3px solid #f97316; font-size: 0.95rem; line-height: 1.5; }
        .backlog-meta { font-size: 0.8rem; color: #fb923c; margin-top: 0.5rem; font-family: 'JetBrains Mono', monospace; }
        
        @media (max-width: 1024px) { #content { grid-template-columns: 1fr; } .card:nth-child(5) { grid-column: auto; } }
        @media (max-width: 640px) {
            body { padding: 1.5rem 0.75rem; } h1 { font-size: 2.25rem; }
            .countdown-card { min-width: unset; flex: 1; padding: 1rem; }
            .card { padding: 1.5rem; border-radius: 20px; }
            .card h2 { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
            .course-link { margin-left: 0; width: 100%; text-align: center; }
        }
    </style>"""

    # Replace <style> block
    html_src = re.sub(r'<style>.*?</style>', new_css, html_src, flags=re.DOTALL)
    
    # Replace Fonts
    old_fonts = r'<link\s+href="https://fonts.googleapis.com/css2\?family=Inter:wght@400;600;800&family=JetBrains\+Mono:wght@400;700&display=swap"\s+rel="stylesheet">'
    new_fonts = r'<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">'
    html_src = re.sub(old_fonts, new_fonts, html_src, flags=re.DOTALL)
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(html_src)
        
    print("UI Successfully Revamped.")

if __name__ == "__main__":
    revamp_html()
