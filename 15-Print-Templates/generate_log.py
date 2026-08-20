import datetime

start_date = datetime.date(2026, 7, 31)
end_date = datetime.date(2026, 12, 31)
delta = datetime.timedelta(days=1)

html_out = []
html_out.append('    <!-- DAILY HOURS LOG BOOK -->')
html_out.append('    <div class="page page-break">')
html_out.append('        <h2>STUDY & LAB HOURS LOG BOOK</h2>')
html_out.append('        <p><strong>Your 154-Day Sprint:</strong> Log your daily focused hours leading up to December 31st.</p>')
html_out.append('        <table>')
html_out.append('            <tr><th>Day</th><th>Date</th><th>Topic Focus</th><th>Theory (hrs)</th><th>Lab (hrs)</th><th>Total</th></tr>')

current_date = start_date
day_count = 1
while current_date <= end_date:
    date_str = current_date.strftime('%b %d, %Y')
    html_out.append(f'            <tr><td>Day {day_count}</td><td>{date_str}</td><td></td><td></td><td></td><td></td></tr>')
    current_date += delta
    day_count += 1
    
    # Optional page break if it gets too long, but normal CSS will handle table breaks.
    
html_out.append('        </table>')
html_out.append('        <div class="page-footer">')
html_out.append('            <span>DevOps Master Workbook 2027</span>')
html_out.append('            <span>Log Book</span>')
html_out.append('        </div>')
html_out.append('    </div>')

with open("log_markup.txt", "w") as f:
    f.write("\n".join(html_out))
