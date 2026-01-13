from flask import Flask, render_template_string, request
import requests
from bs4 import BeautifulSoup
import concurrent.futures

app = Flask(__name__)

# UI ডিজাইন (Cyberpunk/Terminal Style)
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DiscoverEye PRO - OSINT Engine</title>
    <style>
        :root{ --neon-green: #00ff41; --bg-black: #0a0a0a; --panel-bg: #111; --border: #003b1a; }
        body { background: var(--bg-black); color: #b6ffcc; font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; border: 1px solid var(--border); padding: 20px; box-shadow: 0 0 20px rgba(0,255,65,0.1); }
        h1 { color: var(--neon-green); text-align: center; text-transform: uppercase; letter-spacing: 5px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        input, button { width: 100%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid var(--border); color: var(--neon-green); font-weight: bold; }
        button { background: var(--neon-green); color: #000; cursor: pointer; transition: 0.3s; }
        button:hover { background: #00cc33; box-shadow: 0 0 15px var(--neon-green); }
        .result-box { margin-top: 20px; }
        .source-card { background: var(--panel-bg); border-left: 4px solid var(--neon-green); padding: 15px; margin-bottom: 15px; }
        .platform { color: var(--neon-green); font-size: 12px; text-decoration: underline; }
        .data-content { margin-top: 8px; font-size: 14px; color: #fff; line-height: 1.5; }
        .link { font-size: 11px; color: #555; display: block; margin-top: 5px; }
        .loader { text-align: center; color: yellow; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DiscoverEye PRO</h1>
        <form method="POST">
            <input type="text" name="target" placeholder="NAME / PHONE / USERNAME" required value="{{ target }}">
            <input type="text" name="location" placeholder="LOCATION (Optional)" value="{{ location }}">
            <button type="submit">EXECUTE DEEP SCAN</button>
        </form>

        {% if results %}
        <div class="result-box">
            <h3>[ SCAN_LOGS_FOUND ]</h3>
            {% for item in results %}
            <div class="source-card">
                <span class="platform">SOURCE: {{ item.platform }}</span>
                <div class="data-content">{{ item.data }}</div>
                <a href="{{ item.link }}" class="link" target="_blank">{{ item.link }}</a>
            </div>
            {% endfor %}
        </div>
        {% elif searched %}
        <p style="color: red; text-align: center;">No direct data found in public records.</p>
        {% endif %}
    </div>
</body>
</html>
"""

def scrape_engine(platform_name, site, query):
    """গুগল ইনডেক্স থেকে রিয়েল ডাটা টেনে আনার ইঞ্জিন"""
    search_url = f"https://www.google.com/search?q=site:{site} {query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    try:
        r = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        findings = []
        
        # গুগল রেজাল্টের মেইন অংশগুলো থেকে ডাটা নেয়া
        for g in soup.find_all('div', class_='tF2Cxc')[:3]:
            title = g.find('h3').text if g.find('h3') else platform_name
            snippet = g.find('div', class_='VwiC3b').text if g.find('div', class_='VwiC3b') else "No public snippet available."
            link = g.find('a')['href']
            findings.append({'platform': f"{platform_name} ({title})", 'data': snippet, 'link': link})
        return findings
    except:
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    target = ""
    location = ""
    searched = False

    if request.method == 'POST':
        target = request.form.get('target')
        location = request.form.get('location', '')
        search_query = f"{target} {location}".strip()
        searched = True

        # এই প্ল্যাটফর্মগুলো থেকে ডাটা একযোগে কালেক্ট হবে
        sources = [
            ('FACEBOOK', 'facebook.com'),
            ('LINKEDIN', 'linkedin.com'),
            ('TELEGRAM', 't.me'),
            ('WHATSAPP', 'wa.me'),
            ('TWITTER', 'twitter.com'),
            ('GITHUB', 'github.com'),
            ('INSTAGRAM', 'instagram.com')
        ]

        # মাল্টি-থ্রেডিং ব্যবহার করা হয়েছে যাতে দ্রুত ডাটা আসে
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_source = {executor.submit(scrape_engine, name, site, search_query): name for name, site in sources}
            for future in concurrent.futures.as_completed(future_to_source):
                results.extend(future.result())

    return render_template_string(HTML_LAYOUT, results=results, target=target, location=location, searched=searched)

# For Vercel
app.debug = False
