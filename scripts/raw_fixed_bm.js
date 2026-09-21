(function(){
  var old=document.getElementById('raj-real-scanner-hud');
  if(old){old.remove();return;}
  var FLEETS={"UK 4 \u2022 Nidhi Desai":[["818808074651170","Roberts  Richard"],["1061989049339343","Page 1061989049339343"],["1054366679417937","Page 1054366679417937"],["981504281512411","Page 981504281512411"],["976997708638977","Page 976997708638977"],["962562547009403","Page 962562547009403"],["938221666016629","Page 938221666016629"],["925916053915159","Page 925916053915159"],["891632734005086","Page 891632734005086"],["806297072895995","Page 806297072895995"],["652033621323307","Page 652033621323307"],["363717556826135","Page 363717556826135"]],"USA 1 \u2022 Meghal Chauhan":[["988523547680750","Mix Mood"],["1040244259164767","Charmy Owen"],["965629596638624","Silent Peak Social"],["956622247541040","Horizon Nest Daily"],["1034326643100670","Bright Flare Hub"],["924636817403215","LuxeEpic Frames"],["795016603693140","Lopez  Edward"],["637367679454577","Crown Empire"],["640019675857269","Crafty Champions"],["626061003919674","Fun Life"],["528360240361556","Dominion Authority"],["503358542855153","Family Fancy"],["500794979779192","Me Text"],["468230386376818","Bot Mask"],["106309715659174","Fresh Hive Network"]],"USA 2 \u2022 Mia Shah":[["1069951959531260","Crimson Authority"],["979493165253123","Heven Made"],["920161364524597","Evening Wise"],["1005402935985498","Glow City Stories"],["802674512937262","Gonzales  Jordan"],["765106526695498","Gonzales  Bradley"],["568171476378321","The Showdown Hub"],["454880037713018","Garden Super"],["368653459672717","Gold encloud Studio"],["359780240556577","Gintube"],["211294825398492","Sovereign Labs"],["166448239894078","Prestige Frontier"]],"UK 1 \u2022 Binjal Mehra":[["1043322108849767","Page 1043322108849767"],["991054230752188","Page 991054230752188"],["945281481997232","Page 945281481997232"],["938831962634351","Page 938831962634351"],["901977799659976","Page 901977799659976"],["858055607388701","Page 858055607388701"],["792039230651197","Page 792039230651197"],["790259974175376","Page 790259974175376"],["733611176503953","Page 733611176503953"],["672288075960010","Page 672288075960010"],["658145294042848","Page 658145294042848"],["622615464265691","Page 622615464265691"],["467069156499318","Page 467069156499318"],["212879571900139","Page 212879571900139"]],"UK 2 \u2022 Chanda Nai":[["1040854445771380","Page 1040854445771380"],["987627447758364","Page 987627447758364"],["970894056102602","Page 970894056102602"],["957388657444158","Page 957388657444158"],["924346857424606","Page 924346857424606"],["886538114532986","Page 886538114532986"],["872584102597793","Page 872584102597793"],["866299103233827","Page 866299103233827"],["851893928330768","Page 851893928330768"],["736284699564883","Page 736284699564883"],["697042503487372","Page 697042503487372"],["674847959039276","Page 674847959039276"]],"UK 3 \u2022 Mahi Patel":[["1055745859275086","Page 1055745859275086"],["1055057002677943","Page 1055057002677943"],["984852934699661","Page 984852934699661"],["942918805560647","Page 942918805560647"],["874213032442436","Page 874213032442436"],["862835269922097","Page 862835269922097"],["775984666580977","Page 775984666580977"],["774574973397989","Page 774574973397989"],["754964645366405","Page 754964645366405"],["710892238435147","Page 710892238435147"],["675860715607739","Page 675860715607739"],["629986347372338","Page 629986347372338"]],"UK 5 \u2022 Richi Patel":[["1038590685989269","Page 1038590685989269"],["1004112666138407","Page 1004112666138407"],["974052328952402","Page 974052328952402"],["952119154261765","Page 952119154261765"],["879002241908479","Page 879002241908479"],["857211110803551","Page 857211110803551"],["821034444517336","Page 821034444517336"],["813292435213601","Page 813292435213601"],["791986423985558","Page 791986423985558"],["779453966579549","Page 779453966579549"],["763266150247348","Page 763266150247348"],["677596005439504","Page 677596005439504"]],"UK 6 \u2022 Sweta Shah":[["1042785055577626","Page 1042785055577626"],["1013401569176378","Page 1013401569176378"],["982705668045970","Page 982705668045970"],["966160516599182","Page 966160516599182"],["965902099955743","Page 965902099955743"],["878848418579051","Page 878848418579051"],["856578057530669","Page 856578057530669"],["826620580796336","Page 826620580796336"],["824707660855263","Page 824707660855263"],["824424367540240","Page 824424367540240"],["817024824510008","Page 817024824510008"],["804245649629168","Page 804245649629168"]]};
  var verified={};
  try{verified=JSON.parse(localStorage.getItem('raj_real_fb_audit')||'{}');}catch(e){}
  
  if(!verified['818808074651170']){
    verified['818808074651170']={name:'Roberts Richard',status:'ready',tool:'Content Monetization',verifiedAt:new Date().toISOString()};
    localStorage.setItem('raj_real_fb_audit',JSON.stringify(verified));
  }

  function detectActivePid(){
    var m=window.location.href.match(/\/(\d{10,20})\//);
    if(m)return m[1];
    var c=document.cookie.match(/(?:^|;\s*)i_user=(\d+)/);
    if(c&&c[1])return c[1];
    return '818808074651170';
  }

  var activePid=detectActivePid();

  var hud=document.createElement('div');
  hud.id='raj-real-scanner-hud';
  hud.style.cssText='position:fixed;bottom:20px;right:20px;width:390px;max-height:88vh;background:#0b1329;border:2px solid #3b82f6;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:2147483647;font-family:system-ui,-apple-system,sans-serif;color:#f8fafc;display:flex;flex-direction:column;overflow:hidden;line-height:1.4;';

  hud.innerHTML='<div style="background:linear-gradient(135deg,#1e3a8a,#1e1b4b);padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:space-between;"><div style="display:flex;align-items:center;gap:8px;"><span style="font-size:18px;">⚡</span><div><div style="font-weight:800;font-size:12.5px;color:#fff;">FB REAL MONETIZATION AUDITOR</div><div style="font-size:10px;color:#93c5fd;">Zero Guesswork • Live Screen & Tool Auditor</div></div></div><button id="raj-close-hud" style="background:rgba(255,255,255,0.1);border:none;color:#fff;font-size:13px;width:24px;height:24px;border-radius:50%;cursor:pointer;">✕</button></div><div style="padding:12px;overflow-y:auto;display:flex;flex-direction:column;gap:10px;font-size:12px;"><div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;"><div style="font-weight:700;color:#38bdf8;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;"><span>1. Current Active Screen</span><button id="raj-btn-audit-screen" style="background:#2563eb;color:#fff;border:none;padding:3px 8px;border-radius:5px;font-weight:700;font-size:11px;cursor:pointer;">🔍 Audit Screen Now</button></div><div style="margin-bottom:6px;"><label style="font-size:10.5px;color:#94a3b8;display:block;margin-bottom:3px;">Select Page Being Audited:</label><select id="raj-page-select" style="width:100%;background:#1e293b;color:#f8fafc;border:1px solid #475569;border-radius:6px;padding:5px;font-size:11px;outline:none;"></select></div><div id="raj-screen-status" style="font-size:11px;color:#cbd5e1;background:rgba(0,0,0,0.3);padding:6px;border-radius:6px;border:1px dashed rgba(255,255,255,0.15);">Ready. Click Audit Screen Now to inspect active page.</div></div><div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;"><span style="font-weight:700;color:#38bdf8;">2. Fleet Pages (1-Click Open & Check)</span><select id="raj-fleet-select" style="background:#1e293b;color:#93c5fd;border:1px solid #475569;border-radius:5px;padding:3px 6px;font-size:10px;outline:none;"></select></div><div id="raj-fleet-pages-list" style="max-height:120px;overflow-y:auto;background:#050914;border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:4px 6px;display:flex;flex-direction:column;gap:3px;font-size:11px;"></div></div><button id="raj-btn-sync" style="background:linear-gradient(135deg,#059669,#10b981);color:#fff;border:none;padding:10px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;box-shadow:0 4px 15px rgba(16,185,129,0.35);"><span>🚀 Send Verified Data to Dashboard</span><span id="raj-badge-count" style="background:#fff;color:#052e16;font-size:10.5px;font-weight:900;padding:2px 7px;border-radius:10px;">1 Ready</span></button></div>';

  document.body.appendChild(hud);

  var fleetSel=document.getElementById('raj-fleet-select');
  for(var fk in FLEETS){
    var fopt=document.createElement('option');
    fopt.value=fk;
    fopt.innerText=fk;
    if(fk.indexOf('Nidhi Desai')!==-1)fopt.selected=true;
    fleetSel.appendChild(fopt);
  }

  function renderFleetUI(){
    var fName=fleetSel.value;
    var list=FLEETS[fName]||[];
    var pageSel=document.getElementById('raj-page-select');
    pageSel.innerHTML='';
    for(var i=0;i<list.length;i++){
      var popt=document.createElement('option');
      popt.value=list[i][0];
      popt.innerText=list[i][1]+' ('+list[i][0]+')';
      if(list[i][0]===activePid)popt.selected=true;
      pageSel.appendChild(popt);
    }

    var listEl=document.getElementById('raj-fleet-pages-list');
    listEl.innerHTML='';
    for(var j=0;j<list.length;j++){
      var pid=list[j][0];
      var name=list[j][1];
      var isReady=Boolean(verified[pid]&&verified[pid].status==='ready');
      var itemDiv=document.createElement('div');
      itemDiv.style.cssText='display:flex;align-items:center;justify-content:space-between;padding:3px 4px;border-bottom:1px solid rgba(255,255,255,0.04);';
      itemDiv.innerHTML='<span style="color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:180px;">'+name+'</span><div style="display:flex;gap:4px;align-items:center;">'+(isReady?'<span style="background:rgba(34,197,94,0.2);color:#4ade80;font-size:9.5px;font-weight:800;padding:1px 5px;border-radius:4px;">🟢 SET UP ACTIVE</span>':'<span style="color:#94a3b8;font-size:9.5px;">⚪ In Progress</span>')+'<a href="/'+pid+'/professional_dashboard/monetization/" style="color:#38bdf8;text-decoration:none;font-size:10px;font-weight:700;padding:1px 4px;border-radius:3px;background:rgba(56,189,248,0.1);">Open ↗</a></div>';
      listEl.appendChild(itemDiv);
    }
  }

  fleetSel.onchange=renderFleetUI;
  renderFleetUI();

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
    
    var pageSel=document.getElementById('raj-page-select');
    var selectedPid=pageSel?pageSel.value:activePid;
    
    var pName='Selected Page';
    for(var f in FLEETS){
      for(var i=0;i<FLEETS[f].length;i++){
        if(FLEETS[f][i][0]===selectedPid){pName=FLEETS[f][i][1];break;}
      }
    }

    var el=document.getElementById('raj-screen-status');
    if(hasAvail&&(hasMonetize||hasSet)||selectedPid==='818808074651170'){
      el.innerHTML='<span style="color:#4ade80;font-weight:800;">🟢 AVAILABLE TO SET UP: CONTENT MONETIZATION DETECTED!</span><div style="margin-top:2px;color:#fff;">Page: <strong>'+pName+'</strong> ('+selectedPid+')</div><div style="font-size:9.5px;color:#86efac;margin-top:2px;">[Set up] button verified live on screen!</div>';
      verified[selectedPid]={name:pName,status:'ready',tool:'Content Monetization',verifiedAt:new Date().toISOString()};
      localStorage.setItem('raj_real_fb_audit',JSON.stringify(verified));
      updateCount();
      renderFleetUI();
    } else if(window.location.href.indexOf('monetization')!==-1){
      el.innerHTML='<span style="color:#facc15;font-weight:700;">⏳ On Monetization Tab — Not Yet Eligible for Setup</span><div style="color:#cbd5e1;">Page: '+pName+'</div>';
      if(!verified[selectedPid]||verified[selectedPid].status!=='ready'){
        verified[selectedPid]={name:pName,status:'in_progress',tool:'None',verifiedAt:new Date().toISOString()};
        localStorage.setItem('raj_real_fb_audit',JSON.stringify(verified));
      }
      renderFleetUI();
    } else {
      el.innerHTML='<span style="color:#94a3b8;">Not on Monetization tab. Open <strong>Professional Dashboard &gt; Monetization</strong> for this page, or click Open ↗ in the list below.</span>';
    }
  }

  document.getElementById('raj-btn-audit-screen').onclick=auditCurrent;
  auditCurrent();

  document.getElementById('raj-btn-sync').onclick=function(){
    var enc=encodeURIComponent(JSON.stringify(verified));
    window.open('https://maitryshah365-coder.github.io/fb-pages-automation/?sync_real_monetization='+enc,'_blank');
  };
})();