import re

html_file = 'index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()


css_to_add = """
        .progress-container {
            width: 100%; max-width: 650px; margin: 1.5rem auto 0 auto;
            background: rgba(0, 0, 0, 0.4); border-radius: 20px;
            border: 1px solid rgba(56, 189, 248, 0.2);
            padding: 5px; box-shadow: inset 0 2px 10px rgba(0,0,0,0.6);
            display: flex; align-items: center; position: relative;
        }
        .progress-bar-fill {
            height: 16px; border-radius: 12px;
            background: linear-gradient(90deg, #a855f7, #38bdf8);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
            transition: width 1.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            width: 0%;
        }
        .progress-text {
            position: absolute; width: 100%; text-align: center;
            font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
            color: #fff; font-weight: 700; text-shadow: 0 1px 4px rgba(0,0,0,0.9);
            pointer-events: none; letter-spacing: 0.5px;
        }
"""
content = content.replace('    </style>', css_to_add + '\n    </style>')

html_to_add = """
            <div class="progress-container" title="Overall Roadmap Completion">
                <div class="progress-bar-fill" id="overall-progress-bar"></div>
                <div class="progress-text" id="overall-progress-text">Computing Progress...</div>
            </div>
        </header>"""
content = content.replace('        </header>', html_to_add)

# JS State Variables
content = content.replace("""            let backlogCkaHtml = '';
            let backlogAzHtml = '';

            const lines = currentRawMarkdown.split('\\n');""", """            let backlogCkaHtml = '';
            let backlogAzHtml = '';
            let totalTasks = 0;
            let completedTasks = 0;

            const lines = currentRawMarkdown.split('\\n');""")

# JS Logic additions for tasks
content = content.replace("""                    const duration = cols[4];
                    const isDone = cols[5] && (cols[5].includes('✅') || cols[5].includes('☑'));""", """                    const duration = cols[4];
                    const isDone = cols[5] && (cols[5].includes('✅') || cols[5].includes('☑'));
                    totalTasks++;
                    if (isDone) completedTasks++;""")

content = content.replace("""                    const duration = cols[4];
                    const isDone = cols[5].includes('✅') || cols[5].includes('☑');""", """                    const duration = cols[4];
                    const isDone = cols[5].includes('✅') || cols[5].includes('☑');
                    totalTasks++;
                    if (isDone) completedTasks++;""")

content = content.replace("""                    const isDone = cols[4].includes('✅') || cols[4].includes('☑');""", """                    const isDone = cols[4].includes('✅') || cols[4].includes('☑');
                    totalTasks++;
                    if (isDone) completedTasks++;""")

js_update_ui = """
            if(totalTasks > 0) {
                const pct = Math.round((completedTasks / totalTasks) * 100);
                document.getElementById('overall-progress-bar').style.width = pct + '%';
                document.getElementById('overall-progress-text').innerText = `Roadmap Progress: ${pct}% (${completedTasks}/${totalTasks} Tasks)`;
                if(pct === 100) document.getElementById('overall-progress-bar').style.background = 'linear-gradient(90deg, #10b981, #34d399)';
            }

            document.getElementById('video-tasks').innerHTML = videoHtml;"""

content = content.replace("            document.getElementById('video-tasks').innerHTML = videoHtml;", js_update_ui)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("success!")
