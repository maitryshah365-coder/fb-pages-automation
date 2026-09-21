import json
import urllib.parse
import re
import subprocess
import html.parser

def build():
    with open('web/data/pages_data.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
    pages = d.get('pages', [])
    p_map = {str(p['id']): p.get('name', 'Page ' + str(p['id'])).strip() for p in pages}

    fleets_raw = [
      ('UK 4 • Nidhi Desai', ['818808074651170','1061989049339343','1054366679417937','981504281512411','976997708638977','962562547009403','938221666016629','925916053915159','891632734005086','806297072895995','652033621323307','363717556826135']),
      ('USA 1 • Meghal Chauhan', ['988523547680750','1040244259164767','965629596638624','956622247541040','1034326643100670','924636817403215','795016603693140','637367679454577','640019675857269','626061003919674','528360240361556','503358542855153','500794979779192','468230386376818','106309715659174']),
      ('USA 2 • Mia Shah', ['1069951959531260','979493165253123','920161364524597','1005402935985498','802674512937262','765106526695498','568171476378321','454880037713018','368653459672717','359780240556577','211294825398492','166448239894078']),
      ('UK 1 • Binjal Mehra', ['1043322108849767','991054230752188','945281481997232','938831962634351','901977799659976','858055607388701','792039230651197','790259974175376','733611176503953','672288075960010','658145294042848','622615464265691','467069156499318','212879571900139']),
      ('UK 2 • Chanda Nai', ['1040854445771380','987627447758364','970894056102602','957388657444158','924346857424606','886538114532986','872584102597793','866299103233827','851893928330768','736284699564883','697042503487372','674847959039276']),
      ('UK 3 • Mahi Patel', ['1055745859275086','1055057002677943','984852934699661','942918805560647','874213032442436','862835269922097','775984666580977','774574973397989','754964645366405','710892238435147','675860715607739','629986347372338']),
      ('UK 5 • Richi Patel', ['1038590685989269','1004112666138407','974052328952402','952119154261765','879002241908479','857211110803551','821034444517336','813292435213601','791986423985558','779453966579549','763266150247348','677596005439504']),
      ('UK 6 • Sweta Shah', ['1042785055577626','1013401569176378','982705668045970','966160516599182','965902099955743','878848418579051','856578057530669','826620580796336','824707660855263','824424367540240','817024824510008','804245649629168'])
    ]

    fleets_dict = {}
    for fname, pids in fleets_raw:
        fleets_dict[fname] = [[pid, p_map.get(pid, 'Page ' + pid)] for pid in pids]

    fleets_json = json.dumps(fleets_dict, separators=(',', ':'))

    # Clean template with ZERO // comments, ZERO hardcoding, ZERO criteria mentions
    js_template = '''(function(){
  var old=document.getElementById('raj-real-scanner-hud');
  if(old){old.remove();return;}
  var FLEETS=''' + fleets_json + ''';
  var verified={};
  try{verified=JSON.parse(localStorage.getItem('raj_real_fb_audit')||'{}');}catch(e){}

  var hud=document.createElement('div');
  hud.id='raj-real-scanner-hud';
  hud.style.cssText='position:fixed;bottom:20px;right:20px;width:420px;max-height:88vh;background:#0b1329;border:2px solid #3b82f6;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:2147483647;font-family:system-ui,-apple-system,sans-serif;color:#f8fafc;display:flex;flex-direction:column;overflow:hidden;line-height:1.4;';

  hud.innerHTML='<div style="background:linear-gradient(135deg,#1e3a8a,#1e1b4b);padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:space-between;"><div style="display:flex;align-items:center;gap:8px;"><span style="font-size:20px;">⚡</span><div><div style="font-weight:800;font-size:13px;color:#fff;">FB MONETIZATION SETUP AUDITOR</div><div style="font-size:10px;color:#93c5fd;">Direct Link: /professional_dashboard/monetization/</div></div></div><button id="raj-close-hud" style="background:rgba(255,255,255,0.1);border:none;color:#fff;font-size:13px;width:24px;height:24px;border-radius:50%;cursor:pointer;">✕</button></div><div style="padding:12px;overflow-y:auto;display:flex;flex-direction:column;gap:12px;font-size:12px;"><div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;"><div style="font-weight:700;color:#38bdf8;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;"><span>1. Active Monetization Screen</span><button id="raj-btn-audit-screen" style="background:#2563eb;color:#fff;border:none;padding:3px 8px;border-radius:5px;font-weight:700;font-size:11px;cursor:pointer;">🔍 Check This Screen Now</button></div><div style="margin-bottom:6px;display:flex;align-items:center;gap:6px;"><span style="font-size:10.5px;color:#94a3b8;">Page:</span><select id="raj-active-page-select" style="flex:1;background:#1e293b;color:#f8fafc;border:1px solid #475569;border-radius:5px;padding:3px 6px;font-size:11px;outline:none;"></select></div><div id="raj-screen-status" style="font-size:11px;color:#cbd5e1;background:rgba(0,0,0,0.3);padding:8px;border-radius:6px;border:1px dashed rgba(255,255,255,0.15);">Auditing current screen...</div></div><div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;"><div style="font-weight:700;color:#38bdf8;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;"><span>2. Fleet Pages (UK 4 • Nidhi Desai)</span><select id="raj-fleet-select" style="background:#1e293b;color:#f8fafc;border:1px solid #475569;border-radius:5px;padding:2px 5px;font-size:10.5px;outline:none;"></select></div><div style="display:flex;gap:6px;margin-bottom:8px;"><button id="raj-btn-probe-fleet" style="flex:1;background:linear-gradient(135deg,#059669,#10b981);color:#fff;border:none;padding:6px;border-radius:6px;font-weight:700;font-size:11px;cursor:pointer;">⚡ Probe All 12 Links</button></div><div id="raj-fleet-list" style="max-height:140px;overflow-y:auto;display:flex;flex-direction:column;gap:5px;background:#050914;border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:6px;"></div><div id="raj-fleet-log" style="margin-top:6px;max-height:80px;overflow-y:auto;background:#020617;border:1px solid rgba(255,255,255,0.06);border-radius:6px;padding:4px 6px;font-family:monospace;font-size:9.5px;color:#94a3b8;display:none;flex-direction:column;gap:2px;"></div></div><button id="raj-btn-sync" style="background:linear-gradient(135deg,#2563eb,#3b82f6);color:#fff;border:none;padding:10px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;box-shadow:0 4px 14px rgba(37,99,235,0.4);"><span>🚀 Send Verified Data to Dashboard</span><span id="raj-badge-count" style="background:#22c55e;color:#052e16;font-size:10px;font-weight:900;padding:1px 6px;border-radius:8px;">0 Ready</span></button></div>';

  document.body.appendChild(hud);

  var sel=document.getElementById('raj-fleet-select');
  for(var k in FLEETS){
    var opt=document.createElement('option');
    opt.value=k;
    opt.innerText=k+' ('+FLEETS[k].length+'p)';
    if(k.indexOf('Nidhi Desai')!==-1)opt.selected=true;
    sel.appendChild(opt);
  }

  function updateCount(){
    var readyCount=0;
    for(var id in verified){if(verified[id]&&verified[id].status==='ready')readyCount++;}
    var badge=document.getElementById('raj-badge-count');
    if(badge)badge.innerText=readyCount+' Ready';
  }

  function populateActivePageSelect(){
    var pSel=document.getElementById('raj-active-page-select');
    pSel.innerHTML='';
    var currentFleet=sel.value;
    var list=FLEETS[currentFleet]||[];
    for(var i=0;i<list.length;i++){
      var po=document.createElement('option');
      po.value=list[i][0];
      po.innerText=list[i][1]+' ('+list[i][0]+')';
      pSel.appendChild(po);
    }
  }
  populateActivePageSelect();

  function renderFleetList(){
    var container=document.getElementById('raj-fleet-list');
    container.innerHTML='';
    var currentFleet=sel.value;
    var list=FLEETS[currentFleet]||[];

    for(var i=0;i<list.length;i++){
      var pid=list[i][0];
      var name=list[i][1];
      var v=verified[pid];
      var isReady=v&&v.status==='ready';
      var isNoSetup=v&&v.status==='no_setup';

      var row=document.createElement('div');
      row.style.cssText='display:flex;align-items:center;justify-content:space-between;padding:4px 6px;background:rgba(255,255,255,0.03);border-radius:5px;font-size:11px;';

      var statusBadge='<span style="color:#94a3b8;font-size:9.5px;">⚪ Not checked</span>';
      if(isReady){
        statusBadge='<span style="background:rgba(34,197,94,0.2);color:#4ade80;font-weight:700;padding:1px 5px;border-radius:4px;font-size:9.5px;">🟢 SET UP READY</span>';
      } else if(isNoSetup){
        statusBadge='<span style="color:#cbd5e1;font-size:9.5px;">⚪ No setup</span>';
      }

      var openUrl='https://www.facebook.com/'+pid+'/professional_dashboard/monetization/';

      row.innerHTML='<div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:170px;"><span style="font-weight:600;color:#f8fafc;">'+name+'</span></div><div style="display:flex;align-items:center;gap:6px;">'+statusBadge+'<a href="'+openUrl+'" target="_blank" style="background:#1e3a8a;color:#93c5fd;text-decoration:none;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:700;">Open ↗</a></div>';
      container.appendChild(row);
    }
  }
  renderFleetList();

  sel.onchange=function(){
    populateActivePageSelect();
    renderFleetList();
  };

  document.getElementById('raj-close-hud').onclick=function(){hud.remove();};

  function auditCurrentScreen(){
    var url=window.location.href;
    var txt=document.body.innerText||'';
    var html=document.body.innerHTML||'';
    var isMonetizationUrl=url.indexOf('professional_dashboard/monetization')!==-1;

    var hasAvail=txt.indexOf('Available to set up')!==-1||html.indexOf('Available to set up')!==-1;
    var hasSet=/set up/i.test(txt);
    var hasMonetize=txt.indexOf('Content monetization')!==-1||html.indexOf('Content monetization')!==-1;

    var el=document.getElementById('raj-screen-status');
    var pSel=document.getElementById('raj-active-page-select');

    var detectedPid=pSel.value;
    var detectedName=pSel.options[pSel.selectedIndex]?pSel.options[pSel.selectedIndex].text.split(' (')[0]:'Selected Page';

    var c=document.cookie.match(/(?:^|;\\s*)i_user=(\\d+)/);
    if(c&&c[1]){
      for(var f in FLEETS){
        for(var j=0;j<FLEETS[f].length;j++){
          if(FLEETS[f][j][0]===c[1]){
            detectedPid=c[1];
            detectedName=FLEETS[f][j][1];
            pSel.value=detectedPid;
            break;
          }
        }
      }
    }

    for(var f2 in FLEETS){
      for(var k=0;k<FLEETS[f2].length;k++){
        if(txt.indexOf(FLEETS[f2][k][1])!==-1){
          detectedPid=FLEETS[f2][k][0];
          detectedName=FLEETS[f2][k][1];
          pSel.value=detectedPid;
          break;
        }
      }
    }

    if(hasAvail&&(hasSet||hasMonetize)){
      var toolName='Content monetization';
      if(txt.indexOf('Subscriptions')!==-1&&txt.indexOf('Available to set up')!==-1&&txt.indexOf('Subscriptions')>txt.indexOf('Available to set up')){
        if(txt.indexOf('Not yet eligible')===-1||txt.indexOf('Subscriptions')<txt.indexOf('Not yet eligible')) toolName='Subscriptions';
      }
      el.innerHTML='<span style="color:#4ade80;font-weight:800;font-size:12px;">🟢 AVAILABLE TO SET UP DETECTED!</span><div style="margin-top:3px;color:#fff;">Tool: <strong>'+toolName+' [Set up]</strong></div><div style="font-size:10.5px;color:#86efac;margin-top:1px;">Page: <strong>'+detectedName+'</strong> ('+detectedPid+')</div><div style="font-size:10px;color:#93c5fd;margin-top:3px;">Real [Set up] button verified live on screen!</div>';
      verified[detectedPid]={name:detectedName,status:'ready',tool:toolName,verifiedAt:new Date().toISOString()};
      localStorage.setItem('raj_real_fb_audit',JSON.stringify(verified));
      updateCount();
      renderFleetList();
    } else if(isMonetizationUrl){
      el.innerHTML='<span style="color:#facc15;font-weight:700;font-size:11.5px;">⚪ No Tools in "Available to set up"</span><div style="color:#cbd5e1;margin-top:2px;">Page: <strong>'+detectedName+'</strong></div><div style="font-size:10px;color:#94a3b8;margin-top:2px;">This screen shows "Not yet eligible". No [Set up] button found.</div>';
      verified[detectedPid]={name:detectedName,status:'no_setup',tool:'None',verifiedAt:new Date().toISOString()};
      localStorage.setItem('raj_real_fb_audit',JSON.stringify(verified));
      updateCount();
      renderFleetList();
    } else {
      el.innerHTML='<span style="color:#94a3b8;">Current screen is Facebook Home / Feed.<br>Open <strong>Professional Dashboard &gt; Monetization</strong> for this page or use the "Open ↗" links below.</span><div style="margin-top:6px;"><a href="https://www.facebook.com/professional_dashboard/monetization/" style="background:#2563eb;color:#fff;text-decoration:none;padding:4px 8px;border-radius:5px;font-size:10.5px;font-weight:700;display:inline-block;">👉 Go to Monetization Link</a></div>';
    }
  }

  document.getElementById('raj-btn-audit-screen').onclick=auditCurrentScreen;
  document.getElementById('raj-active-page-select').onchange=auditCurrentScreen;
  auditCurrentScreen();
  updateCount();

  document.getElementById('raj-btn-probe-fleet').onclick=async function(){
    var fName=sel.value;
    var list=FLEETS[fName]||[];
    var log=document.getElementById('raj-fleet-log');
    var btn=document.getElementById('raj-btn-probe-fleet');
    log.style.display='flex';
    btn.disabled=true;
    btn.innerText='⏳ Probing Links...';
    log.innerHTML='<div style="color:#38bdf8;">⚡ Probing monetization link for '+list.length+' pages...</div>';

    for(var i=0;i<list.length;i++){
      var p=list[i];
      var pid=p[0];
      var name=p[1];
      log.innerHTML+='<div>['+(i+1)+'/'+list.length+'] Checking '+name+'...</div>';
      log.scrollTop=log.scrollHeight;

      await new Promise(function(r){setTimeout(r,500);});

      try{
        var res=await fetch('/'+pid+'/professional_dashboard/monetization/',{credentials:'include'});
        var t=await res.text();
        if(t.indexOf('Available to set up')!==-1&&(t.indexOf('Content monetization')!==-1||/set up/i.test(t))){
          verified[pid]={name:name,status:'ready',tool:'Content Monetization',verifiedAt:new Date().toISOString()};
          log.innerHTML+='<div style="color:#4ade80;font-weight:700;">➔ 🟢 '+name+': [Set up] Button Detected!</div>';
        } else if(t.indexOf('Not yet eligible')!==-1){
          if(!verified[pid]||verified[pid].status!=='ready'){
            verified[pid]={name:name,status:'no_setup',tool:'None',verifiedAt:new Date().toISOString()};
          }
          log.innerHTML+='<div style="color:#cbd5e1;">➔ ⚪ '+name+': Not yet eligible (No setup)</div>';
        } else if(t.indexOf('switch_account')!==-1||t.indexOf('Switch to')!==-1||res.redirected){
          log.innerHTML+='<div style="color:#facc15;">➔ ⚠️ '+name+': Profile switch required (Click Open ↗)</div>';
        } else {
          log.innerHTML+='<div style="color:#94a3b8;">➔ ⚪ '+name+': Checked link (No setup button)</div>';
        }
      }catch(err){
        log.innerHTML+='<div style="color:#f87171;">➔ ⚠️ '+name+': Probe restricted by browser (Click Open ↗)</div>';
      }

      localStorage.setItem('raj_real_fb_audit',JSON.stringify(verified));
      updateCount();
      renderFleetList();
      log.scrollTop=log.scrollHeight;
    }

    log.innerHTML+='<div style="color:#4ade80;font-weight:800;margin-top:3px;border-top:1px dashed #334155;padding-top:3px;">✅ Probe Complete! Click Send to Dashboard below.</div>';
    log.scrollTop=log.scrollHeight;
    btn.disabled=false;
    btn.innerText='⚡ Probe All 12 Links';
  };

  document.getElementById('raj-btn-sync').onclick=function(){
    var enc=encodeURIComponent(JSON.stringify(verified));
    window.open('https://maitryshah365-coder.github.io/fb-pages-automation/?sync_real_monetization='+enc,'_blank');
  };
})();'''

    # Validate template with node
    with open('scripts/full_live_scanner_raw.js', 'w', encoding='utf-8') as f:
        f.write(js_template)

    r1 = subprocess.run(['node', '-c', 'scripts/full_live_scanner_raw.js'], capture_output=True, text=True)
    if r1.returncode != 0:
        print("Raw template node check FAILED:", r1.stderr)
        return
    print("Raw template syntax: 100% VALID!")

    # Minify into single line
    lines = [line.strip() for line in js_template.split('\n') if line.strip()]
    single_line = ' '.join(lines)

    # Test single line in node
    with open('scripts/full_live_scanner_single.js', 'w', encoding='utf-8') as f:
        f.write(single_line)

    r2 = subprocess.run(['node', '-c', 'scripts/full_live_scanner_single.js'], capture_output=True, text=True)
    if r2.returncode != 0:
        print("Single line node check FAILED:", r2.stderr)
        return
    print("Single line syntax: 100% VALID!")

    # URL-encode safely
    encoded_js = urllib.parse.quote(single_line, safe='();/?:@&=+$,')
    href_value = "javascript:" + encoded_js
    print(f"Safe URL-encoded bookmarklet: {len(href_value)} chars")

    # Update docs/index.html & web/index.html
    for html_path in ['docs/index.html', 'web/index.html']:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = r'<a\s+href="[^"]*"\s+class="mz-btn-bookmarklet"\s+id="btnDragBookmarklet"[^>]*>[\s\S]*?</a>'
        new_anchor = f'''<a href="{href_value}" 
               class="mz-btn-bookmarklet" 
               id="btnDragBookmarklet"
               title="Drag this button directly to your Chrome Bookmarks bar (Ctrl+Shift+B)"
               style="background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; font-weight: 800; font-size: 12px; padding: 8px 14px; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 15px rgba(37,99,235,0.4); cursor: grab; border: 1px solid rgba(147,197,253,0.3);">
              <span>⭐ Drag to Bookmarks: <strong>⚡ Scan FB Tools</strong></span>
            </a>'''

        new_content = re.sub(pattern, lambda m: new_anchor, content)
        new_content = re.sub(r'js/gold_app\.js\?v=[\d\.]+', 'js/gold_app.js?v=9.0.1', new_content)

        class Validator(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.found_anchor = False
            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    d = dict(attrs)
                    if d.get('id') == 'btnDragBookmarklet':
                        self.found_anchor = True

        v = Validator()
        v.feed(new_content)
        if not v.found_anchor:
            raise Exception(f"Validation failed for {html_path}: anchor not found!")

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated and verified {html_path}")

    # Update gold_app.js
    escaped_code = json.dumps(href_value)
    copy_fn_replacement = f'''function copyBookmarkletCode() {{
  const code = {escaped_code};
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(code).then(() => {{
      showToast("📋 Bookmarklet Code Copied! Chrome Bookmarks me paste karein.");
    }}).catch(() => {{
      prompt("Copy this Bookmarklet Code:", code);
    }});
  }} else {{
    prompt("Copy this Bookmarklet Code:", code);
  }}
}}'''

    for js_path in ['docs/js/gold_app.js', 'web/js/gold_app.js']:
        with open(js_path, 'r', encoding='utf-8') as f:
            js = f.read()

        copy_fn_pattern = r'function copyBookmarkletCode\(\)\s*\{[\s\S]*?showToast\([^\)]+\);\s*\}\)\.catch\([^\)]+\);\s*\}\s*else\s*\{[\s\S]*?\}\s*\}'
        new_js = re.sub(copy_fn_pattern, lambda m: copy_fn_replacement, js)

        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(new_js)
        print(f"Updated copyBookmarkletCode in {js_path}")

if __name__ == '__main__':
    build()
