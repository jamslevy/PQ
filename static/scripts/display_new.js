if(typeof snaptalent=='undefined'){snaptalent={dom:'http://snaptalent.com',idom:'http://media.snaptalent.com',impression:{},exist:false,serve:true,overlay:true,open:false,delay:false,test:false,transitions:true,onSuccess:'',onFailure:'',kads:{},not_ie:true,d:function(uid,w,h){if(this.serve){var t=this;if(!t.exist){t.ac();}
t.cc(uid,w,h);if(t.delay){t.oc(uid);}else{t.gc(uid);}
t.cb();if(!t.exist){if(t.overlay&&t.not_ie){t.pi();t.uc();}
t.exist=true;}}},cb:function(){if(navigator.appName=='Microsoft Internet Explorer'){this.not_ie=false;}},ac:function(){var n='snaptalent';var ss=['#'+n+'_idiv { position:fixed;z-index:10000000}','#'+n+'_close { height:100%;left:0;position:fixed;top:0;width:100%; background-color:black; _background-color:transparent; opacity:0.2; filter=alpha(opacity=20) }','#'+n+'_ftl { background: transparent url('+this.idom+'/images/frame.png) no-repeat 0 -42px; height:25px; width:21px; float:left; }','#'+n+'_ftc { background: transparent url('+this.idom+'/images/frame.png) repeat-x 0 0; height:25px; float:left;}','#'+n+'_ftr { background: transparent url('+this.idom+'/images/frame.png) no-repeat -23px -42px; height:25px; width:27px; float:right; cursor:pointer }','#'+n+'_fbl { background: transparent url('+this.idom+'/images/frame.png) no-repeat 0 -68px; height:16px; width:21px; float:left; clear:left; }','#'+n+'_fbc { background: transparent url('+this.idom+'/images/frame.png) repeat-x 0 -25px; height:16px; float:left; }','#'+n+'_fbr { background: transparent url('+this.idom+'/images/frame.png) no-repeat -29px -68px; height:16px; width:21px; float:right; }','#'+n+'_fl { background: transparent url('+this.idom+'/images/loading.png) repeat-y 1px 0; height:470px; width:14px; float:left; clear:left; }','#'+n+'_fc { background: white url('+this.idom+'/images/loading.png) no-repeat -30px 0px; overflow:hidden; float:left; }','#'+n+'_fr { background: transparent url('+this.idom+'/images/loading.png) repeat-y -13px 0; height:470px; width:15px; float:right; }','#'+n+'_iframe { border:0; height:470px; overflow:hidden; width:698px;}','.'+n+'_container, .'+n+'_container *, .'+n+'_container * *, #'+n+'_idiv, #'+n+'_idiv *, #'+n+'_idiv * *, #'+n+'_dd, #'+n+'_close, #'+n+'_iframe { margin:0; padding:0; }'];if(false){var s=document.createElement('style');document.getElementsByTagName('head')[0].appendChild(s);var x=document.styleSheets;var r=x[x.length-1];for(var i=0;i<ss.length;i++){r.insertRule(ss[i],r.length);}}else{document.write('<style type="text/css" media="screen">'+ss.join(' ')+'</style>');}},pi:function(){var o='<div id="snaptalent_close"  style="display:none">&nbsp;</div>';o+='<div id="snaptalent_idiv" style="display:none">';o+='<div id="snaptalent_ftl">&nbsp;</div><div id="snaptalent_ftc">&nbsp;</div><div id="snaptalent_ftr" onclick="snaptalent.l()">&nbsp;</div>';o+='<div id="snaptalent_fl">&nbsp;</div>';o+='<div id="snaptalent_fc"><iframe id="snaptalent_iframe" scrolling=no src="">Loading ad content</iframe></div>';o+='<div id="snaptalent_fr">&nbsp;</div>';o+='<div id="snaptalent_fbl">&nbsp;</div><div id="snaptalent_fbc">&nbsp;</div><div id="snaptalent_fbr">&nbsp;</div>';o+='</div>';var d=document.createElement('div');d.id='snaptalent_dd';d.innerHTML=o;document.body.appendChild(d);},cc:function(uid,w,h){var o='<div style="width:'+w+'px;height:'+h+'px;" id="snaptalent_'+uid+'" class="snaptalent_container"></div>';o+='<div style="display:none">';var is=['loading','frame'];for(var i=0;i<is.length;i++){o+='<img src="'+this.idom+'/images/'+is[i]+'.png" alt="" />';}
o+='</div>';document.write(o);},gc:function(uid){


var url='/static/scripts/data.js';

demo_url = '/st_quiz/?proficiencies=["Building Webapps", "Startup Financing", "Clean Energy", "Collective Intelligence"]'; // Clean Energy

if(this.delay){var s=document.createElement('script');s.src=url;s.lang='javascript';this.$('snaptalent_'+uid).appendChild(s);}else{document.write('<script type="text/javascript" charset="utf-8" src='+url+'></script>');}},oc:function(uid){var fn=function(){snaptalent.oc(uid);};if(typeof window.addEventListener!='undefined'){window.addEventListener('load',fn,false)}
else if(typeof document.addEventListener!='undefined'){document.addEventListener('load',fn,false)}
else if(typeof window.attachEvent!='undefined'){window.attachEvent('onload',fn)}
else{var oldfn=window.onload;if(typeof window.onload!='function'){window.onload=fn;}else{window.onload=function(){oldfn();fn();}}}},uc:function(){var fn=function(){document.getElementById('snaptalent_iframe').src};if(typeof window.addEventListener!='undefined'){window.addEventListener('unload',fn,false)}
else if(typeof document.addEventListener!='undefined'){document.addEventListener('unload',fn,false)}
else if(typeof window.attachEvent!='undefined'){window.attachEvent('onunload',fn)}
else{var oldfn=window.onunload;if(typeof window.onunload!='function'){window.onunload=fn;}else{window.onunload=function(){oldfn();fn();}}}},c:function(uid,iid){this.si(uid,iid);var c=this.$('snaptalent_'+uid);c.innerHTML=this.j;},m:function(jid,uid){if(this.overlay&&this.not_ie){var f=this.$('snaptalent_iframe');var url=demo_url;if(f.src!=url){f.src=url;if(!this.open){this.boxObj=this.$('snaptalent_idiv');this.boxObj.style.display='block';this.$('snaptalent_close').style.display='block';if(this.transitions){var wh=this.wh();this.boxObj.style.height='0px';this.boxObj.style.width='0px';this.boxObj.style.opacity=1;this.boxObj.style.filter='alpha(opacity=100)';this.boxObj.style.left=parseInt(wh[0]/2)+'px';/*this.boxObj.style.top=parseInt((wh[1]-100)/2)+'px'; */this.boxObj.style.overflow='hidden';this.td=[true,true];this.boxID=setInterval("snaptalent.ts(true)",30);}
this.open=true; /* useful for ST? */ flash = document.getElementsByTagName('object'); flash.item(0).style.visibility = "hidden";  }}else{this.l();}
return false;}else if(!this.not_ie){/*location.href="http://snaptalent.com/ads/"+jid+"/k/";*/}else{return true;}},l:function(){if(this.transitions){this.boxID=setInterval("snaptalent.ts(false)",35);}else{this.ll();}
this.$('snaptalent_close').style.display='none'; flash.item(0).style.visibility = "visible";  this.open=false;},ll:function(){this.$('snaptalent_iframe').src;this.boxObj.style.display='none';},si:function(uid,iid){this.impression[uid]=iid;},wh:function(){var W=1000,H=500;if(typeof(window.innerWidth)=='number'){W=window.innerWidth;H=window.innerHeight;}else if(document.body&&(document.body.clientWidth||document.body.clientHeight)){W=document.body.clientWidth;H=document.body.clientHeight;}
return[W,H];},ts:function(eu){var s=this.boxObj.style;if(eu){var h=parseInt(s.height);var w=parseInt(s.width);var l=parseInt(s.left);var t=parseInt(s.top);if(!this.td[0]&&!this.td[1]){clearInterval(this.boxID);if(!eu){}}
var MW=726;var MH=512;if(w<MW&&this.td[0]){var a=parseInt(2+(MW-w)/8);this.boxObj.style.width=w+a+'px';this.$('snaptalent_fc').style.width=w+a-29+'px';this.$('snaptalent_ftc').style.width=w+a-48+'px';this.$('snaptalent_fbc').style.width=w+a-42+'px';this.boxObj.style.left=l-a/2+'px';}else{this.td[0]=false}
if(h<MH&&this.td[1]){var a=parseInt(1+(MH-h)/6);this.boxObj.style.height=h+a+'px';this.$('snaptalent_fc').style.height=h+a-42+'px';this.$('snaptalent_fr').style.height=h+a-42+'px';this.$('snaptalent_fl').style.height=h+a-42+'px';this.boxObj.style.top=t-a/2+'px';}else{this.td[1]=false}}
else{var o=parseFloat(s.opacity);if(o>0){this.boxObj.style.opacity=o-0.10;this.boxObj.style.filter='alpha(opacity='+parseInt(o*100)-10+')';}else{clearInterval(this.boxID);this.ll();}}},alert:function(m,t){if(this.test){if(typeof t=='undefined'){t='info'};try{eval('console.'+t+'(m)');}catch(e){alert(m);}}},$:function(name){return document.getElementById(name);}}}
