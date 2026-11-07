() => {
  const parse = color => {
    const values = color.match(/[\d.]+/g)?.map(Number) || [0,0,0,0];
    return [...values.slice(0,3),values[3]??1];
  };
  const blend = (fg,bg) => fg.slice(0,3).map((c,i)=>c*fg[3]+bg[i]*(1-fg[3]));
  const background = node => {
    const chain=[];
    for(let e=node;e;e=e.parentElement) chain.unshift(parse(getComputedStyle(e).backgroundColor));
    return chain.reduce((bg,fg)=>blend(fg,bg),[255,255,255]);
  };
  const luminance = c => c.slice(0,3).map(x=>x/255).map(x=>x<=0.04045?x/12.92:((x+0.055)/1.055)**2.4)
    .reduce((sum,x,i)=>sum+x*[0.2126,0.7152,0.0722][i],0);
  const contrast = (a,b) => {const x=luminance(a),y=luminance(b);return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05);};
  const hex = c => '#'+c.slice(0,3).map(x=>Math.round(x).toString(16).padStart(2,'0')).join('');
  const selectors=['.page-heading h1','.page-heading p','.eyebrow','th','.app-footer','.info-note','.section-number','input[readonly]',
    '.stepper li:not(.reached)','.stepper li:not(.reached)>span','.tabs button:not(.active)',
    '.badge-closed','.badge-achieved','.badge-not_achieved','.badge-not_evaluable','.badge-cancelled','.badge-pending',
    '.badge-suspension_threshold','.success-notice','.form-error','.error-state','.diagnosis-grid h3','.result-note',
    '.metric-tags span','.back-link','.stat-warning strong','.button.primary','.button.secondary','.button.dark',
    '.field small','.check-label','.field label','.field label span','.picker-options button','.icon-button','.sidebar nav a'];
  const text=[];
  for(const selector of selectors) for(const e of [...document.querySelectorAll(selector)].slice(0,4)) {
    if(!e.getClientRects().length || e.matches(':disabled') || e.closest('[inert]')) continue;
    const s=getComputedStyle(e),bg=background(e),fg=blend(parse(s.color),bg);
    const large=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=18.6667&&Number(s.fontWeight)>=700);
    const icon=!e.textContent.trim();
    text.push({selector,text:e.textContent.trim().slice(0,70),kind:icon?'icon':'text',fg:hex(fg),bg:hex(bg),ratio:contrast(fg,bg),minimum:large||icon?3:4.5});
  }
  const placeholders=[];
  for(const e of document.querySelectorAll('input[placeholder],textarea[placeholder]')) {
    if(!e.getClientRects().length || e.value || e.closest('[inert]'))continue;
    const bg=background(e),style=getComputedStyle(e,'::placeholder'),color=parse(style.color);
    color[3]*=Number(style.opacity);
    const fg=blend(color,bg);
    placeholders.push({text:e.placeholder,fg:hex(fg),bg:hex(bg),ratio:contrast(fg,bg),minimum:4.5});
  }
  const boundaries=[];
  for(const e of document.querySelectorAll('input:not([type=checkbox]):not([type=hidden]),select,textarea,.search-box')) {
    if(!e.getClientRects().length || e.matches(':disabled') || e.closest('[inert]')) continue;
    const s=getComputedStyle(e);
    if(parseFloat(s.borderTopWidth)===0)continue;
    const inside=background(e),outside=background(e.parentElement),fg=parse(s.borderTopColor);
    boundaries.push({selector:e.tagName+'.'+e.className,color:s.borderTopColor,inside:hex(inside),outside:hex(outside),
      ratio:Math.min(contrast(blend(fg,inside),inside),contrast(blend(fg,outside),outside)),minimum:3});
  }
  const e=document.activeElement,style=getComputedStyle(e),bg=background(e);
  const ring=parse(style.outlineColor),outside=background(e.parentElement||e);
  const focus={element:e.tagName,outline:style.outline,color:hex(ring),inside:hex(bg),outside:hex(outside),
    ratio:contrast(blend(ring,parseFloat(style.outlineOffset)<0?bg:outside),parseFloat(style.outlineOffset)<0?bg:outside),minimum:3};
  return {text,placeholders,boundaries,focus,viewport:{width:innerWidth,height:innerHeight}};
}
