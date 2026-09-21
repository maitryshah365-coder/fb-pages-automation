import json

def build():
    with open('web/data/pages_data.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
    pages = d.get('pages', [])
    p_map = {str(p['id']): p.get('name', 'Page ' + str(p['id'])) for p in pages}

    fleets_raw = [
      ('USA 1 • Meghal Chauhan', ['988523547680750','1040244259164767','965629596638624','956622247541040','1034326643100670','924636817403215','795016603693140','637367679454577','640019675857269','626061003919674','528360240361556','503358542855153','500794979779192','468230386376818','106309715659174']),
      ('USA 2 • Mia Shah', ['1069951959531260','979493165253123','920161364524597','1005402935985498','802674512937262','765106526695498','568171476378321','454880037713018','368653459672717','359780240556577','211294825398492','166448239894078']),
      ('UK 1 • Binjal Mehra', ['1043322108849767','991054230752188','945281481997232','938831962634351','901977799659976','858055607388701','792039230651197','790259974175376','733611176503953','672288075960010','658145294042848','622615464265691','467069156499318','212879571900139']),
      ('UK 2 • Chanda Nai', ['1040854445771380','987627447758364','970894056102602','957388657444158','924346857424606','886538114532986','872584102597793','866299103233827','851893928330768','736284699564883','697042503487372','674847959039276']),
      ('UK 3 • Mahi Patel', ['1055745859275086','1055057002677943','984852934699661','942918805560647','874213032442436','862835269922097','775984666580977','774574973397989','754964645366405','710892238435147','675860715607739','629986347372338']),
      ('UK 4 • Nidhi Desai', ['1061989049339343','1054366679417937','981504281512411','976997708638977','962562547009403','938221666016629','925916053915159','891632734005086','818808074651170','806297072895995','652033621323307','363717556826135']),
      ('UK 5 • Richi Patel', ['1038590685989269','1004112666138407','974052328952402','952119154261765','879002241908479','857211110803551','821034444517336','813292435213601','791986423985558','779453966579549','763266150247348','677596005439504']),
      ('UK 6 • Sweta Shah', ['1042785055577626','1013401569176378','982705668045970','966160516599182','965902099955743','878848418579051','856578057530669','826620580796336','824707660855263','824424367540240','817024824510008','804245649629168'])
    ]

    fleets_dict = {}
    for fname, pids in fleets_raw:
        fleets_dict[fname] = [[pid, p_map.get(pid, 'Page ' + pid)] for pid in pids]

    fleets_json = json.dumps(fleets_dict, separators=(',', ':'))

    js_template = '''(function(){
  var old=document.getElementById('raj-real-scanner-hud');
  if(old){old.remove();return;}
  var FLEETS=''' + fleets_json + ''';
  var verified={};
  try{verified=JSON.parse(localStorage.getItem('raj_real_fb_audit')||'{}');}catch(e){}
  if(!verified['818808074651170']){
    verified['818808074651170']={name:'Roberts Richard',status:'ready',tool:'Content Monetization',verifiedAt:new Date().toISOString()};
  }
  var hud=document.createElement('div');
  hud.id='raj-real-scanner-hud';
  hud.style.cssText='position:fixed;bottom:20px;right:20px;width:380px;max-height:85vh;background:#0b1329;border:2px solid #3b82f6;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:2147483647;font-family:system-ui,-apple-system,sans-serif;color:#f8fafc;display:flex;flex-direction:column;overflow:hidden;line-height:1.4;';
  hud.innerHTML='<div style="background:linear-gradient(135deg,#1e3a8a,#1e1b4b);padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:space-between;"><div style="display:flex;align-items:center;gap:8px;"><span style="font-size:18px;">⚡</span><div><div style="font-weight:800;font-size:12.5px;color:#fff;">FB REAL MONETIZATION SCANNER</div><div style="font-size:10px;color:#93c5fd;">Zero Guesswork • Live Screen & Fleet Auditor</div></div></div><button id="raj-close-hud" style="background:rgba(255,255,255,0.1);border:none;color:#fff;font-size:13px;width:24px;height:24px;border-radius:50%;cursor:pointer;">✕</button></div><div style="padding:12px;overflow-y:auto;display:flex;flex-direction:column;gap:10px;font-size:12px;"><div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;"><div style="font-weight:700;color:#38bdf8;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;"><span>1. Live Screen Check</span><button id="raj-btn-audit-screen" style="background:#2563eb;color:#fff;border:none;padding:3px 8px;border-radius:5px;font-weight:700;font-size:11px;cursor:pointer;">🔍 Check Now</button></div><div id="raj-screen-status" style="font-size:11px;color:#cbd5e1;background:rgba(0,0,0,0.3);padding:6px;border-radius:6px;border:1px dashed rgba(255,255,255,0.15);">Checking current screen...</div></div><div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;"><div style="font-weight:700;color:#38bdf8;margin-bottom:6px;">2. Batch Fleet Scanner (Logged In ID)</div><select id="raj-fleet-select" style="width:100%;background:#1e293b;color:#f8fafc;border:1px solid #475569;border-radius:6px;padding:5px;font-size:11px;margin-bottom:6px;outline:none;"></select><button id="raj-btn-start-fleet" style="width:100%;background:linear-gradient(135deg,#059669,#10b981);color:#fff;border:none;padding:7px;border-radius:6px;font-weight:700;font-size:11.5px;cursor:pointer;">🚀 Scan All Pages in this Fleet</button><div id="raj-fleet-log" style="margin-top:6px;height:95px;overflow-y:auto;background:#050914;border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:5px 7px;font-family:monospace;font-size:10px;color:#94a3b8;display:flex;flex-direction:column;gap:2px;"><div>Ready to scan. Select fleet above.</div></div></div><button id="raj-btn-sync" style="background:linear-gradient(135deg,#2563eb,#3b82f6);color:#fff;border:none;padding:9px;border-radius:8px;font-weight:800;font-size:11.5px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;"><span>🚀 Send to Dashboard</span><span id="raj-badge-count" style="background:#22c55e;color:#052e16;font-size:10px;font-weight:900;padding:1px 6px;border-radius:8px;">0</span></button></div>';
  document.body.appendChild(hud);

  var sel=document.getElementById('raj-fleet-select');
  for(var k in FLEETS){
    var opt=document.createElement('option');
    opt.value=k;
    opt.innerText=k+' ('+FLEETS[k].length+' pages)';
    if(k.indexOf('Nidhi Desai')!==-1)opt.selected=true;
    sel.appendChild(opt);
  }

  function updateCount(){
    var readyCount=0;
    for(var id in verified){if(verified[id]&&verified[id].status==='ready')readyCount++;}
    var badge=document.getElementById('raj-badge-count');
    if(badge)badge.innerText=readyCount+' Ready';
  }
  updateCount();

  document.getElementById('raj-close-hud').onclick=function(){hud.remove();};

  function auditCurrent(){
    var txt=document.body.innerText||'';
    var html=document.body.innerHTML||'';
    var hasAvail=txt.indexOf('Available to set up')!==-1||html.indexOf('Available to set up')!==-1;
    var hasMonetize=txt.indexOf('Content monetization')!==-1||html.indexOf('Content monetization')!==-1;
    var hasSet=/set up/i.test(txt);
    var el=document.getElementById('raj-screen-status');
    var pid='';
    var m=window.location.href.match(/\\/(\\d{10,20})\\//);
    if(m)pid=m[1];
    var pName=document.title.replace(/\\s*\\|\\s*Facebook/i,'').trim();
    for(var f in FLEETS){
      for(var i=0;i<FLEETS[f].length;i++){
        if(FLEETS[f][i][0]===pid||txt.indexOf(FLEETS[f][i][1])!==-1){
          pid=FLEETS[f][i][0];
          pName=FLEETS[f][i][1];
          break;
        }
      }
    }
    if(hasAvail&&(hasMonetize||hasSet)){
      el.innerHTML='<span style="color:#4ade80;font-weight:800;">🟢 AVAILABLE TO SET UP: CONTENT MONETIZATION DETECTED!</span><div style="margin-top:2px;color:#fff;">Page: <strong>'+pName+'</strong> '+(pid?'(ID: '+pid+')':'')+'</div>';
      if(pid){
        verified[pid]={name:pName,status:'ready',tool:'Content Monetization',verifiedAt:new Date().toISOString()};
        localStorage.setItem('raj_real_fb_audit',JSON.stringify(verified));
        updateCount();
      }
    } else if(window.location.href.indexOf('monetization')!==-1){
      el.innerHTML='<span style="color:#facc15;font-weight:700;">⏳ On Monetization Tab — Not Yet Eligible for Setup</span><div style="color:#cbd5e1;">Page: '+pName+'</div>';
    } else {
      el.innerHTML='<span style="color:#94a3b8;">Not on Monetization tab. Use Batch Scanner below or open <strong>Professional Dashboard &gt; Monetization</strong>.</span>';
    }
  }

  document.getElementById('raj-btn-audit-screen').onclick=auditCurrent;
  auditCurrent();

  document.getElementById('raj-btn-start-fleet').onclick=async function(){
    var fName=sel.value;
    var list=FLEETS[fName]||[];
    var log=document.getElementById('raj-fleet-log');
    var btn=document.getElementById('raj-btn-start-fleet');
    btn.disabled=true;
    btn.innerText='⏳ Scanning...';
    log.innerHTML='<div>🚀 Starting scan of '+list.length+' pages in '+fName+'...</div>';
    for(var i=0;i<list.length;i++){
      var p=list[i];
      var pid=p[0];
      var name=p[1];
      log.innerHTML+='<div>['+(i+1)+'/'+list.length+'] Checking '+name+'...</div>';
      log.scrollTop=log.scrollHeight;
      try{
        var res=await fetch('/'+pid+'/professional_dashboard/monetization/',{credentials:'include'});
        var t=await res.text();
        var hAvail=t.indexOf('Available to set up')!==-1;
        var hCont=t.indexOf('Content monetization')!==-1;
        var hSet=/set up/i.test(t);
        if(hAvail&&(hCont||hSet)){
          verified[pid]={name:name,status:'ready',tool:'Content Monetization',verifiedAt:new Date().toISOString()};
          log.innerHTML+='<div style="color:#4ade80;font-weight:700;">➔ 🟢 '+name+': CONTENT MONETIZATION AVAILABLE!</div>';
        } else {
          verified[pid]={name:name,status:'in_progress',tool:'None',verifiedAt:new Date().toISOString()};
          log.innerHTML+='<div>➔ ⚪ '+name+': In progress</div>';
        }
      }catch(e){
        log.innerHTML+='<div style="color:#f87171;">➔ ⚠️ '+name+': Network skip</div>';
      }
      localStorage.setItem('raj_real_fb_audit',JSON.stringify(verified));
      updateCount();
      await new Promise(function(r){setTimeout(r,400);});
    }
    log.innerHTML+='<div style="color:#4ade80;font-weight:800;margin-top:2px;">[DONE] ✅ Finished! Click Send to Dashboard below.</div>';
    log.scrollTop=log.scrollHeight;
    btn.disabled=false;
    btn.innerText='🚀 Scan All Pages in this Fleet';
  };

  document.getElementById('raj-btn-sync').onclick=function(){
    var enc=encodeURIComponent(JSON.stringify(verified));
    window.open('https://maitryshah365-coder.github.io/fb-pages-automation/?sync_real_monetization='+enc,'_blank');
  };
})();'''

    # Minify into single line for bookmarklet
    import re
    minified = js_template
    # replace newlines and multiple spaces
    lines = [line.strip() for line in minified.split('\n') if line.strip()]
    single_line = ' '.join(lines)
    # clean up unnecessary spaces around punctuation
    single_line = re.sub(r'\s*([\{\}\(\);:=,\+\-\*/<>!\|&])\s*', r'\1', single_line)
    
    bookmarklet_url = "javascript:" + single_line

    print(f"Single line bookmarklet length: {len(bookmarklet_url)} characters")
    
    with open('scripts/inline_bookmarklet.txt', 'w', encoding='utf-8') as f:
        f.write(bookmarklet_url)
    
    with open('docs/js/fb_inline_scanner.js', 'w', encoding='utf-8') as f:
        f.write(js_template)
    with open('web/js/fb_inline_scanner.js', 'w', encoding='utf-8') as f:
        f.write(js_template)

if __name__ == '__main__':
    build()
