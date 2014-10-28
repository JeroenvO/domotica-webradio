(function($){'use strict';if($['zepto']&&!$.fn.removeData){throw new ReferenceError('Zepto is loaded without the data module.');}
$.fn['noUiSlider']=function(options,rebuild){var
doc=$(document),body=$('body'),namespace='.nui',$VAL=$.fn.val,clsList=['noUi-base','noUi-origin','noUi-handle','noUi-input','noUi-active','noUi-state-tap','noUi-target','-lower','-upper','noUi-connect','noUi-horizontal','noUi-vertical','noUi-background','noUi-stacking','noUi-block','noUi-state-blocked','noUi-ltr','noUi-rtl','noUi-dragable','noUi-extended','noUi-state-drag'],actions=window.navigator['pointerEnabled']?{start:'pointerdown',move:'pointermove',end:'pointerup'}:window.navigator['msPointerEnabled']?{start:'MSPointerDown',move:'MSPointerMove',end:'MSPointerUp'}:{start:'mousedown touchstart',move:'mousemove touchmove',end:'mouseup touchend'};function fromPercentage(range,value){return(value*100)/(range[1]-range[0]);}
function toPercentage(range,value){return fromPercentage(range,range[0]<0?value+Math.abs(range[0]):value-range[0]);}
function isPercentage(range,value){return((value*(range[1]-range[0]))/100)+range[0];}
function isInstance(a){return a instanceof $||($['zepto']&&$['zepto']['isZ'](a));}
function isNumeric(a){return!isNaN(parseFloat(a))&&isFinite(a);}
function call(functions,scope){if(!$.isArray(functions)){functions=[functions];}
$.each(functions,function(){if(typeof this==='function'){this.call(scope);}});}
function setN(target,number){return function(){var val=[null,null];val[number]=$(this).val();target.val(val,true);};}
function closest(value,to){return Math.round(value/to)*to;}
function format(value,options){value=value.toFixed(options['decimals']);if(parseFloat(value)===0){value=value.replace('-0','0');}
return value.replace('.',options['serialization']['mark']);}
function closestHandle(handles,location,style){if(handles.length===1){return handles[0];}
var total=handles[0].offset()[style]+
handles[1].offset()[style];return handles[location<total/2?0:1];}
function digits(value,round){return parseFloat(value.toFixed(round));}
function fixEvent(e){e.preventDefault();var touch=e.type.indexOf('touch')===0,mouse=e.type.indexOf('mouse')===0,pointer=e.type.indexOf('pointer')===0,x,y,event=e;if(e.type.indexOf('MSPointer')===0){pointer=true;}
if(e.originalEvent){e=e.originalEvent;}
if(touch){x=e.changedTouches[0].pageX;y=e.changedTouches[0].pageY;}
if(mouse||pointer){if(!pointer&&window.pageXOffset===undefined){window.pageXOffset=document.documentElement.scrollLeft;window.pageYOffset=document.documentElement.scrollTop;}
x=e.clientX+window.pageXOffset;y=e.clientY+window.pageYOffset;}
return $.extend(event,{'pointX':x,'pointY':y,cursor:mouse});}
function attach(events,element,callback,pass){var target=pass.target;events=events.replace(/\s/g,namespace+' ')+namespace;return element.on(events,function(e){var disabled=target.attr('disabled');disabled=!(disabled===undefined||disabled===null);if(target.hasClass('noUi-state-tap')||disabled){return false;}
callback(fixEvent(e),pass,target.data('base').data('options'));});}
function serialize(a){var target=this.target;if(a===undefined){return this.element.data('value');}
if(a===true){a=this.element.data('value');}else{this.element.data('value',a);}
if(a===undefined){return;}
$.each(this.elements,function(){if(typeof this==='function'){this.call(target,a);}else{this[0][this[1]](a);}});}
function storeElement(handle,item,number){if(isInstance(item)){var elements=[],target=handle.data('target');if(handle.data('options').direction){number=number?0:1;}
item.each(function(){$(this).on('change'+namespace,setN(target,number));elements.push([$(this),'val']);});return elements;}
if(typeof item==='string'){item=[$('<input type="hidden" name="'+item+'">').appendTo(handle).addClass(clsList[3]).change(function(e){e.stopPropagation();}),'val'];}
return[item];}
function store(handle,i,serialization){var elements=[];$.each(serialization['to'][i],function(index){elements=elements.concat(storeElement(handle,serialization['to'][i][index],i));});return{element:handle,elements:elements,target:handle.data('target'),'val':serialize};}
function block(base,stateless){var target=base.data('target');if(!target.hasClass(clsList[14])){if(!stateless){target.addClass(clsList[15]);setTimeout(function(){target.removeClass(clsList[15]);},450);}
target.addClass(clsList[14]);call(base.data('options').block,target);}}
function placeHandle(handle,to){var settings=handle.data('options');to=digits(to,7);handle.data('target').removeClass(clsList[14]);handle.css(settings['style'],to+'%').data('pct',to);if(handle.is(':first-child')){handle.toggleClass(clsList[13],to>50);}
if(settings['direction']){to=100-to;}
handle.data('store').val(format(isPercentage(settings['range'],to),settings));}
function setHandle(handle,to){var base=handle.data('base'),settings=base.data('options'),handles=base.data('handles'),lower=0,upper=100;if(!isNumeric(to)){return false;}
if(settings['step']){to=closest(to,settings['step']);}
if(handles.length>1){if(handle[0]!==handles[0][0]){lower=digits(handles[0].data('pct')+settings['margin'],7);}else{upper=digits(handles[1].data('pct')-settings['margin'],7);}}
to=Math.min(Math.max(to,lower),upper<0?100:upper);if(to===handle.data('pct')){return[!lower?false:lower,upper===100?false:upper];}
placeHandle(handle,to);return true;}
function jump(base,handle,to,callbacks){base.addClass(clsList[5]);setTimeout(function(){base.removeClass(clsList[5]);},300);setHandle(handle,to);call(callbacks,base.data('target'));base.data('target').change();}
function move(event,Dt,Op){var handles=Dt.handles,limits,proposal=event[Dt.point]-Dt.start[Dt.point];proposal=(proposal*100)/Dt.size;if(handles.length===1){limits=setHandle(handles[0],Dt.positions[0]+proposal);if(limits!==true){if($.inArray(handles[0].data('pct'),limits)>=0){block(Dt.base,!Op['margin']);}
return;}}else{var l1,u1,l2,u2;if(Op['step']){proposal=closest(proposal,Op['step']);}
l1=l2=Dt.positions[0]+proposal;u1=u2=Dt.positions[1]+proposal;if(l1<0){u1+=-1*l1;l1=0;}else if(u1>100){l1-=(u1-100);u1=100;}
if(l2<0&&!l1&&!handles[0].data('pct')){return;}
if(u1===100&&u2>100&&handles[1].data('pct')===100){return;}
placeHandle(handles[0],l1);placeHandle(handles[1],u1);}
call(Op['slide'],Dt.target);}
function end(event,Dt,Op){if(Dt.handles.length===1){Dt.handles[0].data('grab').removeClass(clsList[4]);}
if(event.cursor){body.css('cursor','').off(namespace);}
doc.off(namespace);Dt.target.removeClass(clsList[14]+' '+clsList[20]).change();call(Op['set'],Dt.target);}
function start(event,Dt,Op){if(Dt.handles.length===1){Dt.handles[0].data('grab').addClass(clsList[4]);}
event.stopPropagation();attach(actions.move,doc,move,{start:event,base:Dt.base,target:Dt.target,handles:Dt.handles,positions:[Dt.handles[0].data('pct'),Dt.handles[Dt.handles.length-1].data('pct')],point:Op['orientation']?'pointY':'pointX',size:Op['orientation']?Dt.base.height():Dt.base.width()});attach(actions.end,doc,end,{target:Dt.target,handles:Dt.handles});if(event.cursor){body.css('cursor',$(event.target).css('cursor'));if(Dt.handles.length>1){Dt.target.addClass(clsList[20]);}
body.on('selectstart'+namespace,function(){return false;});}}
function tap(event,Dt,Op){var base=Dt.base,handle,to,point,size;event.stopPropagation();if(Op['orientation']){point=event['pointY'];size=base.height();}else{point=event['pointX'];size=base.width();}
handle=closestHandle(base.data('handles'),point,Op['style']);to=((point-base.offset()[Op['style']])*100)/size;jump(base,handle,to,[Op['slide'],Op['set']]);}
function edge(event,Dt,Op){var handles=Dt.base.data('handles'),to,i;i=Op['orientation']?event['pointY']:event['pointX'];i=i<Dt.base.offset()[Op['style']];to=i?0:100;i=i?0:handles.length-1;jump(Dt.base,handles[i],to,[Op['slide'],Op['set']]);}
function test(input,sliders){function values(a){if(a.length!==2){return false;}
a=[parseFloat(a[0]),parseFloat(a[1])];if(!isNumeric(a[0])||!isNumeric(a[1])){return false;}
if(a[1]<a[0]){return false;}
return a;}
var serialization={resolution:function(q,o){switch(q){case 1:case 0.1:case 0.01:case 0.001:case 0.0001:case 0.00001:q=q.toString().split('.');o['decimals']=q[0]==='1'?0:q[1].length;break;case undefined:o['decimals']=2;break;default:return false;}
return true;},mark:function(q,o,w){if(!q){o[w]['mark']='.';return true;}
switch(q){case'.':case',':return true;default:return false;}},to:function(q,o,w){function ser(r){return isInstance(r)||typeof r==='string'||typeof r==='function'||r===false||(isInstance(r[0])&&typeof r[0][r[1]]==='function');}
function filter(value){var items=[[],[]];if(ser(value)){items[0].push(value);}else{$.each(value,function(i,val){if(i>1){return;}
if(ser(val)){items[i].push(val);}else{items[i]=items[i].concat(val);}});}
return items;}
if(!q){o[w]['to']=[[],[]];}else{var i,j;q=filter(q);if(o['direction']&&q[1].length){q.reverse();}
for(i=0;i<o['handles'];i++){for(j=0;j<q[i].length;j++){if(!ser(q[i][j])){return false;}
if(!q[i][j]){q[i].splice(j,1);}}}
o[w]['to']=q;}
return true;}},tests={'handles':{'r':true,'t':function(q){q=parseInt(q,10);return(q===1||q===2);}},'range':{'r':true,'t':function(q,o,w){o[w]=values(q);return o[w]&&o[w][0]!==o[w][1];}},'start':{'r':true,'t':function(q,o,w){if(o['handles']===1){if($.isArray(q)){q=q[0];}
q=parseFloat(q);o.start=[q];return isNumeric(q);}
o[w]=values(q);return!!o[w];}},'connect':{'r':true,'t':function(q,o,w){if(q==='lower'){o[w]=1;}else if(q==='upper'){o[w]=2;}else if(q===true){o[w]=3;}else if(q===false){o[w]=0;}else{return false;}
return true;}},'orientation':{'t':function(q,o,w){switch(q){case'horizontal':o[w]=0;break;case'vertical':o[w]=1;break;default:return false;}
return true;}},'margin':{'r':true,'t':function(q,o,w){q=parseFloat(q);o[w]=fromPercentage(o['range'],q);return isNumeric(q);}},'direction':{'r':true,'t':function(q,o,w){switch(q){case'ltr':o[w]=0;break;case'rtl':o[w]=1;o['connect']=[0,2,1,3][o['connect']];break;default:return false;}
return true;}},'behaviour':{'r':true,'t':function(q,o,w){o[w]={'tap':q!==(q=q.replace('tap','')),'extend':q!==(q=q.replace('extend','')),'drag':q!==(q=q.replace('drag','')),'fixed':q!==(q=q.replace('fixed',''))};return!q.replace('none','').replace(/\-/g,'');}},'serialization':{'r':true,'t':function(q,o,w){return serialization.to(q['to'],o,w)&&serialization.resolution(q['resolution'],o)&&serialization.mark(q['mark'],o,w);}},'slide':{'t':function(q){return $.isFunction(q);}},'set':{'t':function(q){return $.isFunction(q);}},'block':{'t':function(q){return $.isFunction(q);}},'step':{'t':function(q,o,w){q=parseFloat(q);o[w]=fromPercentage(o['range'],q);return isNumeric(q);}}};$.each(tests,function(name,test){var value=input[name],isSet=value!==undefined;if((test['r']&&!isSet)||(isSet&&!test['t'](value,input,name))){if(window.console&&console.log&&console.group){console.group('Invalid noUiSlider initialisation:');console.log('Option:\t',name);console.log('Value:\t',value);console.log('Slider(s):\t',sliders);console.groupEnd();}
throw new RangeError('noUiSlider');}});}
function create(options){this.data('options',$.extend(true,{},options));options=$.extend({'handles':2,'margin':0,'connect':false,'direction':'ltr','behaviour':'tap','orientation':'horizontal'},options);options['serialization']=options['serialization']||{};test(options,this);options['style']=options['orientation']?'top':'left';return this.each(function(){var target=$(this),i,dragable,handles=[],handle,base=$('<div/>').appendTo(target);if(target.data('base')){throw new Error('Slider was already initialized.');}
target.data('base',base).addClass([clsList[6],clsList[16+options['direction']],clsList[10+options['orientation']]].join(' '));for(i=0;i<options['handles'];i++){handle=$('<div><div/></div>').appendTo(base);handle.addClass(clsList[1]);handle.children().addClass([clsList[2],clsList[2]+clsList[7+options['direction']+
(options['direction']?-1*i:i)]].join(' '));handle.data({'base':base,'target':target,'options':options,'grab':handle.children(),'pct':-1}).attr('data-style',options['style']);handle.data({'store':store(handle,i,options['serialization'])});handles.push(handle);}
switch(options['connect']){case 1:target.addClass(clsList[9]);handles[0].addClass(clsList[12]);break;case 3:handles[1].addClass(clsList[12]);case 2:handles[0].addClass(clsList[9]);case 0:target.addClass(clsList[12]);break;}
base.addClass(clsList[0]).data({'target':target,'options':options,'handles':handles});target.val(options['start']);if(!options['behaviour']['fixed']){for(i=0;i<handles.length;i++){attach(actions.start,handles[i].children(),start,{base:base,target:target,handles:[handles[i]]});}}
if(options['behaviour']['tap']){attach(actions.start,base,tap,{base:base,target:target});}
if(options['behaviour']['extend']){target.addClass(clsList[19]);if(options['behaviour']['tap']){attach(actions.start,target,edge,{base:base,target:target});}}
if(options['behaviour']['drag']){dragable=base.find('.'+clsList[9]).addClass(clsList[18]);if(options['behaviour']['fixed']){dragable=dragable.add(base.children().not(dragable).data('grab'));}
attach(actions.start,dragable,start,{base:base,target:target,handles:handles});}});}
function getValue(){var base=$(this).data('base'),answer=[];$.each(base.data('handles'),function(){answer.push($(this).data('store').val());});if(answer.length===1){return answer[0];}
if(base.data('options').direction){return answer.reverse();}
return answer;}
function setValue(args,set){if(!$.isArray(args)){args=[args];}
return this.each(function(){var b=$(this).data('base'),to,i,handles=Array.prototype.slice.call(b.data('handles'),0),settings=b.data('options');if(handles.length>1){handles[2]=handles[0];}
if(settings['direction']){args.reverse();}
for(i=0;i<handles.length;i++){to=args[i%2];if(to===null||to===undefined){continue;}
if($.type(to)==='string'){to=to.replace(',','.');}
to=toPercentage(settings['range'],parseFloat(to));if(settings['direction']){to=100-to;}
if(setHandle(handles[i],to)!==true){handles[i].data('store').val(true);}
if(set===true){call(settings['set'],$(this));}}});}
function destroy(target){var elements=[[target,'']];$.each(target.data('base').data('handles'),function(){elements=elements.concat($(this).data('store').elements);});$.each(elements,function(){if(this.length>1){this[0].off(namespace);}});target.removeClass(clsList.join(' '));target.empty().removeData('base options');}
function build(options){return this.each(function(){var values=$(this).val()||false,current=$(this).data('options'),setup=$.extend({},current,options);if(values!==false){destroy($(this));}
if(!options){return;}
$(this)['noUiSlider'](setup);if(values!==false&&setup.start===current.start){$(this).val(values);}});}
$.fn.val=function(){if(this.hasClass(clsList[6])){return arguments.length?setValue.apply(this,arguments):getValue.apply(this);}
return $VAL.apply(this,arguments);};return(rebuild?build:create).call(this,options);};}(window['jQuery']||window['Zepto']));