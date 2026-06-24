from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from groq import Groq
import openai
import urllib.parse
import urllib.request
import re

app = Flask(__name__)

# System Memory States (In-Memory Configuration for Demo)
CONFIG = {
    "saved_ai": "Groq (Llama 3 - FREE)",
    "saved_key": "",  # अपनी API Key यहाँ डालें या UI से पास करें
    "master_training": "मेरा नाम गौरव है। मैं एक डेवलपर हूँ।",
    "twin_mood": "Chill 😎",
    "user_sentiment": "Neutral 🧘",
    "pinned_summary": "चैट रूम एक्टिवेटेड।"
}

def live_web_search(query):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')
            results = [a.get_text().strip() for a in soup.find_all('a', class_='result__snippet')[:2]]
            return "\n".join(results) if results else "No direct data."
    except:
        return "Web Grid Offline."

def query_brain_matrix(user_message, live_search):
    web_context = live_web_search(user_message) if live_search else ""
    
    master_prompt = (
        f"You are Gaurav's advanced digital twin. Context: {CONFIG['master_training']}. "
        f"Mood: {CONFIG['twin_mood']}. Live Web Data: {web_context}. Respond naturally and briefly. "
        f"Strict Rule: Append [SENTIMENT: mood_word] and [SUMMARY: short_line] at the very end of your response."
    )
    
    bot_reply = "System Core Error."
    if not CONFIG['saved_key']:
        return "⚠️ कृपया पहले अपनी API Key सेटअप करें!", CONFIG['user_sentiment'], CONFIG['pinned_summary']
        
    try:
        if "Gemini" in CONFIG['saved_ai']:
            genai.configure(api_key=CONFIG['saved_key'])
            model = genai.GenerativeModel('gemini-2.5-flash')
            bot_reply = model.generate_content(f"{master_prompt}\nUser: {user_message}").text
        elif "Groq" in CONFIG['saved_ai']:
            client = Groq(api_key=CONFIG['saved_key'])
            bot_reply = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": f"{master_prompt}\nUser: {user_message}"}]
            ).choices[0].message.content
        elif "OpenAI" in CONFIG['saved_ai']:
            client = openai.OpenAI(api_key=CONFIG['saved_key'])
            bot_reply = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"{master_prompt}\nUser: {user_message}"}]
            ).choices[0].message.content
    except Exception as e:
        bot_reply = f"Matrix Error: {str(e)}"

    # Parse Sentiment and Summary Tags
    sentiment = CONFIG['user_sentiment']
    summary = CONFIG['pinned_summary']
    if "[SENTIMENT:" in bot_reply:
        sentiment = bot_reply.split("[SENTIMENT:")[1].split("]")[0].strip()
        bot_reply = bot_reply.split("[SENTIMENT:")[0]
    if "[SUMMARY:" in bot_reply:
        summary = bot_reply.split("[SUMMARY:")[1].split("]")[0].strip()
        bot_reply = bot_reply.split("[SUMMARY:")[0]
        
    CONFIG['user_sentiment'] = sentiment
    CONFIG['pinned_summary'] = summary
    return bot_reply.strip(), sentiment, summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/configure', methods=['POST'])
def configure_system():
    data = request.json
    CONFIG['saved_ai'] = data.get('ai_engine', CONFIG['saved_ai'])
    CONFIG['saved_key'] = data.get('api_key', CONFIG['saved_key'])
    CONFIG['master_training'] = data.get('training_text', CONFIG['master_training'])
    CONFIG['twin_mood'] = data.get('mood', CONFIG['twin_mood'])
    return jsonify({"success": True, "status": "Core Updated Successfully"})

@app.route('/api/process_command', methods=['POST'])
def process_command():
    data = request.json
    command = data.get('command', '')
    live_search = data.get('live_search', False)
    
    if not command:
        return jsonify({"success": False, "response": "No input received."})
        
    # Check for Special Trigger: Mummy Call Protocol
    if "mummy ko call lagao" in command.lower():
        return jsonify({
            "success": True,
            "response": "📡 MUMMY CALL INTERFACE ACTIVATED. Synced Profile: Gaurav_Voice_v3.2.bin.",
            "mummy_protocol": True,
            "sentiment": CONFIG['user_sentiment'],
            "summary": CONFIG['pinned_summary']
        })
        
    reply, sentiment, summary = query_brain_matrix(command, live_search)
    return jsonify({
        "success": True,
        "response": reply,
        "sentiment": sentiment,
        "summary": summary,
        "mummy_protocol": False
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    
