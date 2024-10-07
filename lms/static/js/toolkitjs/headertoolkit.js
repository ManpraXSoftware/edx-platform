window.onload = onPageLoad();
function onPageLoad() {

  d=document;
  jf=d.createElement('script');
  jf.src= document.getElementById("external_js").getAttribute('lms_base_url')+"static/js/toolkitjs/vebarl.js" //'https://cdn.jsdelivr.net/gh/suprgyabhushan/js-files@master/vebar1.js';
  jf.type='text/javascript';
  jf.id='ToolBar';
  jf.setAttribute("lms_base_url", document.getElementById("external_js").getAttribute('lms_base_url'))

  d.getElementsByTagName('head')[0].appendChild(jf);
}

