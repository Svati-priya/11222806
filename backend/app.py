from flask import Flask, request, jsonify, redirect
from datetime import datetime, timedelta
import re, string, random, platform

app = Flask(__name__)

# 🧠 Memory-based sparkle storage (like a magic diary 💫)
pink_links = {}

# 💌 Custom fancy logger
@app.before_request
def log_request():
    log = {
        "time": datetime.utcnow().isoformat(),
        "method": request.method,
        "requested_url": request.url,
        "from_IP": request.remote_addr,
        "body": request.get_data(as_text=True)
    }
    with open("💖_pink_logs.txt", "a") as diary:
        diary.write(str(log) + "\n")

# ✨ Short & sweet code generator
def sprinkle_code(length=6, prefix="glam"):
    vibes = string.ascii_letters + string.digits
    return f"{prefix}_{''.join(random.choices(vibes, k=length))}"

# 🔍 Pretty URL checker
def is_pretty_url(url):
    pattern = re.compile(
        r'^(https?:\/\/)'  # http or https
        r'(([\w\-]+\.)+[\w]{2,})'  # domain
        r'([\w\-\.\/~%]*)*$',  # path
        re.IGNORECASE
    )
    return re.match(pattern, url) is not None

# 💗 Create a sparkly short URL
@app.route('/shorturls', methods=['POST'])
def create_sparkly_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"💔 oops": "Missing the URL field, hun!"}), 400

    original = data['url']
    if not is_pretty_url(original):
        return jsonify({"🚫 nope": "Hmm... That doesn't look like a valid URL!"}), 400

    life_minutes = int(data.get('validity', 30))
    code = data.get('shortcode')

    if code:
        if not re.match(r'^[a-zA-Z0-9]{1,20}$', code):
            return jsonify({"⚠️ uh-oh": "Shortcode must be cute, alphanumeric, and max 20 chars!"}), 400
        if code in pink_links:
            return jsonify({"😿": "That shortcode is already taken. Try another glam one!"}), 409
    else:
        code = sprinkle_code()

    expires_at = datetime.utcnow() + timedelta(minutes=life_minutes)

    pink_links[code] = {
        "original": original,
        "expires": expires_at,
        "created": datetime.utcnow(),
        "visits": 0,
        "vibes": []
    }

    return jsonify({
        "✨Your PinkLink✨": f"http://localhost:5000/{code}",
        "⏳Expires on": expires_at.isoformat() + 'Z',
        "🧭Time left (sec)": int((expires_at - datetime.utcnow()).total_seconds())
    }), 201

# 🌈 Redirect to original link
@app.route('/<code>', methods=['GET'])
def open_magic_link(code):
    sparkle = pink_links.get(code)
    if not sparkle:
        return jsonify({"😢": "No sparkle found for that code."}), 404

    if datetime.utcnow() > sparkle['expires']:
        return jsonify({"⌛": "Oops! This PinkLink has faded away."}), 410

    sparkle['visits'] += 1
    sparkle['vibes'].append({
        "🌟 when": datetime.utcnow().isoformat() + 'Z',
        "📱 from": request.headers.get('User-Agent', 'unknown'),
        "💻 platform": platform.system(),
        "📍 IP": request.remote_addr
    })

    return redirect(sparkle['original'], code=302)

# 📊 Show click stats
@app.route('/shorturls/<code>', methods=['GET'])
def sparkle_stats(code):
    sparkle = pink_links.get(code)
    if not sparkle:
        return jsonify({"😵": "No record found for that sparkly code."}), 404

    return jsonify({
        "🔗 Original": sparkle['original'],
        "🗓️ Expires": sparkle['expires'].isoformat() + 'Z',
        "👀 Visits": sparkle['visits'],
        "📍 Visitors": sparkle['vibes']
    }), 200

# 🧾 Show all pink links
@app.route('/shorturls', methods=['GET'])
def show_all_pinklinks():
    return jsonify([
        {
            "💫 code": alias,
            "🔗 link": data['original'],
            "📅 expires": data['expires'].isoformat() + 'Z',
            "👣 clicks": data['visits']
        }
        for alias, data in pink_links.items()
    ]), 200

# 💖 Run the magic
if __name__ == '__main__':
    app.run(debug=True)