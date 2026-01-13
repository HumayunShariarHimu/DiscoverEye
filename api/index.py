from flask import Flask, render_template, request
import urllib.parse
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='../templates')

def get_live_snippets(query):
    # কিছু প্ল্যাটফর্ম থেকে সরাসরি টেক্সট স্ক্র্যাপ করার চেষ্টা (যেমন: Google/Telegram)
    snippets = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # Telegram Scraper (পাবলিক চ্যানেল থেকে তথ্য আনা তুলনামূলক সহজ)
    try:
        t_url = f"https://t.me/s/all?q={query}"
        res = requests.get(t_url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        msgs = soup.find_all('div', class_='tgme_widget_message_text')
        for m in msbs[:2]:
            snippets.append({"source": "Telegram Live", "content": m.get_text()[:200]})
    except:
        pass
    return snippets

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if not query: return "Please enter a query"
    
    encoded = urllib.parse.quote(query)
    
    # সরাসরি সার্চ লিংকসমূহ
    platforms = [
        {"name": "Google", "url": f"https://www.google.com/search?q={encoded}", "color": "#4285F4"},
        {"name": "YouTube", "url": f"https://www.youtube.com/results?search_query={encoded}", "color": "#FF0000"},
        {"name": "Facebook", "url": f"https://www.facebook.com/search/top/?q={encoded}", "color": "#1877F2"},
        {"name": "WhatsApp", "url": f"https://wa.me/?text=Searching%20for:%20{encoded}", "color": "#25D366"},
        {"name": "Instagram", "url": f"https://www.instagram.com/explore/tags/{query.replace(' ', '')}/", "color": "#E4405F"},
        {"name": "Telegram", "url": f"https://t.me/s/all?q={encoded}", "color": "#0088cc"}
    ]
    
    live_data = get_live_snippets(query)
    return render_template('index.html', platforms=platforms, live_data=live_data, query=query)
