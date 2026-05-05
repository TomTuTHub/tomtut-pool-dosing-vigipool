/*!
 * orpheo-vp-card.js — Lovelace custom card fuer die HA Integration orpheo_vp
 *
 * Fork von tomtut-pool-dosing-card (https://github.com/TomTuTHub/tomtut-pool-dosing-card)
 * Angepasst: Entity-Suffixe fuer orpheo_vp, Background-Image /local/orpheo_vp/dosieranlage.png
 *
 * Entity-Prefix-Konvention: sensor.<slug> wobei <slug> = Device-Name in HA slug-ifiziert
 * Erwartete Entities (relativ zum Prefix):
 *   sensor.<prefix>_ph                       (Lesen)
 *   sensor.<prefix>_orp_redox                (Lesen)
 *   sensor.<prefix>_ph_firmware              (Lesen)
 *   binary_sensor.<prefix>_durchfluss        (Lesen)
 *   binary_sensor.<prefix>_ph_dosierpumpe    (Lesen)
 *   binary_sensor.<prefix>_chlor_dosierpumpe (Lesen)
 */
function t(t,e,i,s){var o,r=arguments.length,n=r<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)n=Reflect.decorate(t,e,i,s);else for(var a=t.length-1;a>=0;a--)(o=t[a])&&(n=(r<3?o(n):r>3?o(e,i,n):o(e,i))||n);return r>3&&n&&Object.defineProperty(e,i,n),n}"function"==typeof SuppressedError&&SuppressedError;
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const e=globalThis,i=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),o=new WeakMap;let r=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(i&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=o.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&o.set(e,t))}return t}toString(){return this.cssText}};const n=(t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new r(i,t,s)},a=i?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new r("string"==typeof t?t:t+"",void 0,s))(e)})(t):t,{is:l,defineProperty:c,getOwnPropertyDescriptor:h,getOwnPropertyNames:p,getOwnPropertySymbols:d,getPrototypeOf:u}=Object,_=globalThis,g=_.trustedTypes,f=g?g.emptyScript:"",$=_.reactiveElementPolyfillSupport,m=(t,e)=>t,v={toAttribute(t,e){switch(e){case Boolean:t=t?f:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},y=(t,e)=>!l(t,e),w={attribute:!0,type:String,converter:v,reflect:!1,useDefault:!1,hasChanged:y};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */Symbol.metadata??=Symbol("metadata"),_.litPropertyMetadata??=new WeakMap;let b=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=w){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&c(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:o}=h(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:s,set(e){const r=s?.call(this);o?.call(this,e),this.requestUpdate(t,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??w}static _$Ei(){if(this.hasOwnProperty(m("elementProperties")))return;const t=u(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(m("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(m("properties"))){const t=this.properties,e=[...p(t),...d(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(a(t))}else void 0!==t&&e.push(a(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,s)=>{if(i)t.adoptedStyleSheets=s.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of s){const s=document.createElement("style"),o=e.litNonce;void 0!==o&&s.setAttribute("nonce",o),s.textContent=i.cssText,t.appendChild(s)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const o=(void 0!==i.converter?.toAttribute?i.converter:v).toAttribute(e,i.type);this._$Em=t,null==o?this.removeAttribute(s):this.setAttribute(s,o),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),o="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:v;this._$Em=s;const r=o.fromAttribute(e,t.type);this[s]=r??this._$Ej?.get(s)??r,this._$Em=null}}requestUpdate(t,e,i,s=!1,o){if(void 0!==t){const r=this.constructor;if(!1===s&&(o=this[t]),i??=r.getPropertyOptions(t),!((i.hasChanged??y)(o,e)||i.useDefault&&i.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:o},r){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),!0!==o||void 0!==r)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===s&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,s=this[e];!0!==t||this._$AL.has(e)||void 0===s||this.C(e,void 0,i,s)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};b.elementStyles=[],b.shadowRootOptions={mode:"open"},b[m("elementProperties")]=new Map,b[m("finalized")]=new Map,$?.({ReactiveElement:b}),(_.reactiveElementVersions??=[]).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const x=globalThis,A=t=>t,E=x.trustedTypes,S=E?E.createPolicy("lit-html",{createHTML:t=>t}):void 0,k="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,P="?"+C,Q=`<${P}>`,M=document,z=()=>M.createComment(""),O=t=>null===t||"object"!=typeof t&&"function"!=typeof t,T=Array.isArray,U="[ \t\n\f\r]",H=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,R=/-->/g,N=/>/g,D=RegExp(`>|${U}(?:([^\\s"'>=/]+)(${U}*=${U}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),B=/'/g,j=/"/g,L=/^(?:script|style|textarea|title)$/i,V=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),W=Symbol.for("lit-noChange"),I=Symbol.for("lit-nothing"),F=new WeakMap,q=M.createTreeWalker(M,129);function X(t,e){if(!T(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==S?S.createHTML(e):e}const G=(t,e)=>{const i=t.length-1,s=[];let o,r=2===e?"<svg>":3===e?"<math>":"",n=H;for(let e=0;e<i;e++){const i=t[e];let a,l,c=-1,h=0;for(;h<i.length&&(n.lastIndex=h,l=n.exec(i),null!==l);)h=n.lastIndex,n===H?"!--"===l[1]?n=R:void 0!==l[1]?n=N:void 0!==l[2]?(L.test(l[2])&&(o=RegExp("</"+l[2],"g")),n=D):void 0!==l[3]&&(n=D):n===D?">"===l[0]?(n=o??H,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?D:'"'===l[3]?j:B):n===j||n===B?n=D:n===R||n===N?n=H:(n=D,o=void 0);const p=n===D&&t[e+1].startsWith("/>")?" ":"";r+=n===H?i+Q:c>=0?(s.push(a),i.slice(0,c)+k+i.slice(c)+C+p):i+C+(-2===c?e:p)}return[X(t,r+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),s]};class Z{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let o=0,r=0;const n=t.length-1,a=this.parts,[l,c]=G(t,e);if(this.el=Z.createElement(l,i),q.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(s=q.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes())for(const t of s.getAttributeNames())if(t.endsWith(k)){const e=c[r++],i=s.getAttribute(t).split(C),n=/([.?@])?(.*)/.exec(e);a.push({type:1,index:o,name:n[2],strings:i,ctor:"."===n[1]?et:"?"===n[1]?it:"@"===n[1]?st:tt}),s.removeAttribute(t)}else t.startsWith(C)&&(a.push({type:6,index:o}),s.removeAttribute(t));if(L.test(s.tagName)){const t=s.textContent.split(C),e=t.length-1;if(e>0){s.textContent=E?E.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],z()),q.nextNode(),a.push({type:2,index:++o});s.append(t[e],z())}}}else if(8===s.nodeType)if(s.data===P)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=s.data.indexOf(C,t+1));)a.push({type:7,index:o}),t+=C.length-1}o++}}static createElement(t,e){const i=M.createElement("template");return i.innerHTML=t,i}}function J(t,e,i=t,s){if(e===W)return e;let o=void 0!==s?i._$Co?.[s]:i._$Cl;const r=O(e)?void 0:e._$litDirective$;return o?.constructor!==r&&(o?._$AO?.(!1),void 0===r?o=void 0:(o=new r(t),o._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=o:i._$Cl=o),void 0!==o&&(e=J(t,o._$AS(t,e.values),o,s)),e}class K{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??M).importNode(e,!0);q.currentNode=s;let o=q.nextNode(),r=0,n=0,a=i[0];for(;void 0!==a;){if(r===a.index){let e;2===a.type?e=new Y(o,o.nextSibling,this,t):1===a.type?e=new a.ctor(o,a.name,a.strings,this,t):6===a.type&&(e=new ot(o,this,t)),this._$AV.push(e),a=i[++n]}r!==a?.index&&(o=q.nextNode(),r++)}return q.currentNode=M,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class Y{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=I,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=J(this,t,e),O(t)?t===I||null==t||""===t?(this._$AH!==I&&this._$AR(),this._$AH=I):t!==this._$AH&&t!==W&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>T(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==I&&O(this._$AH)?this._$AA.nextSibling.data=t:this.T(M.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=Z.createElement(X(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new K(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=F.get(t.strings);return void 0===e&&F.set(t.strings,e=new Z(t)),e}k(t){T(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const o of t)s===e.length?e.push(i=new Y(this.O(z()),this.O(z()),this,this.options)):i=e[s],i._$AI(o),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=A(t).nextSibling;A(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class tt{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,o){this.type=1,this._$AH=I,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=I}_$AI(t,e=this,i,s){const o=this.strings;let r=!1;if(void 0===o)t=J(this,t,e,0),r=!O(t)||t!==this._$AH&&t!==W,r&&(this._$AH=t);else{const s=t;let n,a;for(t=o[0],n=0;n<o.length-1;n++)a=J(this,s[i+n],e,n),a===W&&(a=this._$AH[n]),r||=!O(a)||a!==this._$AH[n],a===I?t=I:t!==I&&(t+=(a??"")+o[n+1]),this._$AH[n]=a}r&&!s&&this.j(t)}j(t){t===I?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class et extends tt{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===I?void 0:t}}class it extends tt{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==I)}}class st extends tt{constructor(t,e,i,s,o){super(t,e,i,s,o),this.type=5}_$AI(t,e=this){if((t=J(this,t,e,0)??I)===W)return;const i=this._$AH,s=t===I&&i!==I||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==I&&(i===I||s);s&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class ot{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){J(this,t)}}const rt=x.litHtmlPolyfillSupport;rt?.(Z,Y),(x.litHtmlVersions??=[]).push("3.3.2");const nt=globalThis;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */class at extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const s=i?.renderBefore??e;let o=s._$litPart$;if(void 0===o){const t=i?.renderBefore??null;s._$litPart$=o=new Y(e.insertBefore(z(),t),t,void 0,i??{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return W}}at._$litElement$=!0,at.finalized=!0,nt.litElementHydrateSupport?.({LitElement:at});const lt=nt.litElementPolyfillSupport;lt?.({LitElement:at}),(nt.litElementVersions??=[]).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const ct=t=>(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},ht={attribute:!0,type:String,converter:v,reflect:!1,hasChanged:y},pt=(t=ht,e,i)=>{const{kind:s,metadata:o}=i;let r=globalThis.litPropertyMetadata.get(o);if(void 0===r&&globalThis.litPropertyMetadata.set(o,r=new Map),"setter"===s&&((t=Object.create(t)).wrapped=!0),r.set(i.name,t),"accessor"===s){const{name:s}=i;return{set(i){const o=e.get.call(this);e.set.call(this,i),this.requestUpdate(s,o,t,!0,i)},init(e){return void 0!==e&&this.C(s,void 0,t,e),e}}}if("setter"===s){const{name:s}=i;return function(i){const o=this[s];e.call(this,i),this.requestUpdate(s,o,t,!0,i)}}throw Error("Unsupported decorator location: "+s)};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function dt(t){return(e,i)=>"object"==typeof i?pt(t,e,i):((t,e,i)=>{const s=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),s?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function ut(t){return dt({...t,state:!0,attribute:!1})}const _t={water_top:53,water_height:10,water_width:94,water_center:50,water_speed:100,pump_left_top:7,pump_right_top:7,pump_left_x:21,pump_right_x:15,pump_left_size:9,pump_right_size:9,pump_speed:100,value_bottom:4,value_ph_x:35,value_rx_x:30,value_scale:100,firmware_top:18,firmware_left:50,plug_ph_top:12,plug_ph_left:3,plug_rx_top:12,plug_rx_right:3},xt={type1:{water_top:79,water_height:14,water_width:100,water_center:50,water_speed:16,water_direction:"right",water_inactive:"gray",pump_left_size:9,pump_style:"fan",pump_left_x:34.5,pump_left_top:25,pump_right_size:9,pump_right_x:33.5,pump_right_top:24.5,pump_speed:30,firmware_top:7,firmware_box:true,firmware_color:"white",firmware_left:51,firmware_scale:95,plug_ph_top:28,plug_ph_left:15,plug_rx_top:28,plug_rx_right:15,value_box:true,value_labels:true,value_color:"white",value_scale:85,value_rx_x:32,value_ph_x:33,value_bottom:23}},gt={type1:{light:"/local/orpheo_vp/dosieranlage.png",dark:"/local/orpheo_vp/dosieranlage.png"}},ft={arrow:'<path d="M20,6 A14,14 0 1,1 8,14" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/><polygon points="5,8 11,14 3,16" fill="currentColor"/>',fan:'<circle cx="20" cy="20" r="3" fill="currentColor"/><path d="M20,17 Q20,6 12,6 Q4,6 6,14 Q8,17 20,17 Z" fill="currentColor" opacity="0.85"/><path d="M23,20 Q34,20 34,12 Q34,4 26,6 Q23,8 23,20 Z" fill="currentColor" opacity="0.85"/><path d="M20,23 Q20,34 28,34 Q36,34 34,26 Q32,23 20,23 Z" fill="currentColor" opacity="0.85"/><path d="M17,20 Q6,20 6,28 Q6,36 14,34 Q17,32 17,20 Z" fill="currentColor" opacity="0.85"/>',dots:'<circle cx="20" cy="8" r="3.5" fill="currentColor"/><circle cx="31" cy="14" r="3.5" fill="currentColor"/><circle cx="31" cy="26" r="3.5" fill="currentColor"/><circle cx="20" cy="32" r="3.5" fill="currentColor"/><circle cx="9" cy="26" r="3.5" fill="currentColor"/><circle cx="9" cy="14" r="3.5" fill="currentColor"/><circle cx="20" cy="20" r="4" fill="currentColor"/>'};let $t=class extends at{setConfig(t){const c={...t};if(c.device_name&&!c.entity_prefix){c.entity_prefix="sensor."+c.device_name.toLowerCase().replace(/\s+/g,"_")}if(!c.entity_prefix)throw new Error("device_name or entity_prefix is required");this._config={model:"type1",image_variant:"dark",...c}}getCardSize(){return 6}_entity(t){return this.hass?.states[`${this._config.entity_prefix}${t}`]}_state(t){const s=this._entity(t)?.state;return s&&"unavailable"!==s&&"unknown"!==s?s:"—"}_binaryEntity(t){return this.hass?.states[`${this._config.entity_prefix.replace(/^sensor\./,"binary_sensor.")}${t}`]}_isOn(t){return"on"===this._binaryEntity(t)?.state}get _imagePath(){const t=this._config.model??"type1",e=this._config.image_variant??"dark";return gt[t]?.[e]??gt.type1.dark}get _flowActive(){return this._isOn("_durchfluss")}_v(t){return this._config[t]??(xt[this._config.model??'type1']??{})[t]??_t[t]}_togglePlug(e){const t=e?.currentTarget?.dataset?.entity||this._config.plug_entity_rx||this._config.plug_entity;t&&this.hass&&this.hass.callWS({type:"call_service",domain:t.split(".")[0],service:"toggle",target:{entity_id:t}})}_numId(s){return this._config.entity_prefix.replace(/^sensor\./,"number.")+s}_swId(s){return this._config.entity_prefix.replace(/^sensor\./,"switch.")+s}_biId(s){return this._config.entity_prefix.replace(/^sensor\./,"binary_sensor.")+s}_openSettings(e){e?.stopPropagation();this._settingsOpen=true;this.requestUpdate()}_closeSettings(e){e?.stopPropagation();this._settingsOpen=false;this.requestUpdate()}_stopProp(e){e.stopPropagation()}_setNumber(e){const t=e.currentTarget,id=t.dataset.entity,v=parseFloat(t.value);if(!isNaN(v))this.hass.callService("number","set_value",{entity_id:id,value:v})}_toggleSw(e){const t=e.currentTarget,id=t.dataset.entity,on=t.checked;this.hass.callService("switch",on?"turn_on":"turn_off",{entity_id:id})}_numberRow(label,suffix,icon){const id=this._numId(suffix),ent=this.hass.states[id];if(!ent)return V`<div class="settings-row missing"><span><ha-icon icon="${icon||"mdi:alert"}"></ha-icon>${label}</span><em>fehlt: ${id}</em></div>`;const a=ent.attributes||{},mn=a.min??0,mx=a.max??100,st=a.step??0.01,un=a.unit_of_measurement||"";return V`<div class="settings-row"><span class="settings-label"><ha-icon icon="${icon||"mdi:tune"}"></ha-icon>${label}</span><div class="settings-num"><input type="range" min="${mn}" max="${mx}" step="${st}" .value="${ent.state}" data-entity="${id}" @change="${this._setNumber}" @input="${this._setNumber}" /><input type="number" min="${mn}" max="${mx}" step="${st}" .value="${ent.state}" data-entity="${id}" @change="${this._setNumber}" /><span class="settings-unit">${un}</span></div></div>`}_switchRow(label,suffix,icon){const id=this._swId(suffix),ent=this.hass.states[id];if(!ent)return V`<div class="settings-row missing"><span><ha-icon icon="${icon||"mdi:alert"}"></ha-icon>${label}</span><em>fehlt: ${id}</em></div>`;const on=ent.state==="on";return V`<div class="settings-row"><span class="settings-label"><ha-icon icon="${icon||"mdi:toggle-switch-outline"}"></ha-icon>${label}</span><label class="settings-toggle"><input type="checkbox" .checked="${on}" data-entity="${id}" @change="${this._toggleSw}" /><span class="slider-track"></span></label></div>`}render(){if(!this._config||!this.hass)return I;const t=this._state("_ph"),e="—"!==t?parseFloat(t).toFixed(1).replace(".",","):"—",i=this._state("_orp_redox"),s="—"!==i?Math.round(parseFloat(i)).toString():"—",o=this._state("_ph_firmware"),r=this._isOn("_ph_dosierpumpe"),n=this._isOn("_chlor_dosierpumpe"),a=this._flowActive,l=ft[this._v("pump_style")??"arrow"],cPh=this._config.plug_entity_ph,hPh=!!cPh&&"on"===this.hass.states[cPh]?.state,cRx=this._config.plug_entity_rx||this._config.plug_entity,hRx=!!cRx&&"on"===this.hass.states[cRx]?.state,p=this._v("water_speed")??100,d=this._v("pump_speed")??100,u=Math.max(.01,p/100),_=1.8/u,g=2.4/u,f=1.4/u,$=0===p||!a?"paused":"running",m=1/Math.max(.01,d/100),v="left"===(this._v("water_direction")??"right"),y=this._v("value_color")??"white",w=!1!==(this._v("value_box")??!0),b=!1!==(this._v("value_labels")??!0),showCloud=!1!==(this._config.show_cloud??!0),showSettings=!1!==(this._config.show_settings??!0),cloudEnt=this.hass.states[this._biId("_cloud_verbindung")],cloudOn=cloudEnt?.state==="on",settingsOpen=!!this._settingsOpen;return V`
      <ha-card>
        <div class="card-wrap">
          <img class="bg" src="${this._imagePath}" alt="Dosieranlage" />

          <!-- Firmware -->
          <div class="firmware-badge ${!1!==(this._v("firmware_box")??!0)?"":"no-bg"}"
               style="top:${this._v("firmware_top")}%; left:${this._v("firmware_left")}%; transform:translateX(-50%) scale(${(this._v("firmware_scale")??100)/100}); color:${this._v("firmware_color")??"white"};">
            ${this._config.firmware_text||o}
          </div>

          <!-- Water -->
          <div class="water-zone ${a?"active":"gray"===(this._v("water_inactive")??"hidden")?"inactive-gray":""}"
               style="top:${this._v("water_top")}%; height:${this._v("water_height")}%; left:${(this._v("water_center")??50)-this._v("water_width")/2}%; right:${100-((this._v("water_center")??50)+this._v("water_width")/2)}%;">
            <svg class="water-svg" viewBox="0 0 600 50" preserveAspectRatio="none">
              <path class="wave wave1" style="animation-duration:${_}s; animation-direction:${v?"normal":"reverse"}; animation-play-state:${$};"
                d="M0,25 Q25,5 50,25 Q75,45 100,25 Q125,5 150,25 Q175,45 200,25 Q225,5 250,25 Q275,45 300,25 Q325,5 350,25 Q375,45 400,25 Q425,5 450,25 Q475,45 500,25 Q525,5 550,25 Q575,45 600,25 Q625,5 650,25 Q675,45 700,25 Q725,5 750,25 Q775,45 800,25" />
              <path class="wave wave2" style="animation-duration:${g}s; animation-direction:${v?"normal":"reverse"}; animation-play-state:${$};"
                d="M0,25 Q25,10 50,25 Q75,40 100,25 Q125,10 150,25 Q175,40 200,25 Q225,10 250,25 Q275,40 300,25 Q325,10 350,25 Q375,40 400,25 Q425,10 450,25 Q475,40 500,25 Q525,10 550,25 Q575,40 600,25 Q625,10 650,25 Q675,40 700,25 Q725,10 750,25 Q775,40 800,25" />
              <path class="wave wave3" style="animation-duration:${f}s; animation-direction:${v?"normal":"reverse"}; animation-play-state:${$};"
                d="M0,25 Q25,8 50,25 Q75,42 100,25 Q125,8 150,25 Q175,42 200,25 Q225,8 250,25 Q275,42 300,25 Q325,8 350,25 Q375,42 400,25 Q425,8 450,25 Q475,42 500,25 Q525,8 550,25 Q575,42 600,25 Q625,8 650,25 Q675,42 700,25 Q725,8 750,25 Q775,42 800,25" />
            </svg>
          </div>

          <!-- Pumps -->
          <div class="pump-arrow ${r?"spinning":""}"
               style="top:${this._v("pump_left_top")}%; left:${this._v("pump_left_x")}%; width:${this._v("pump_left_size")}%; --pump-dur:${m}s;">
            <svg viewBox="0 0 40 40" .innerHTML="${l}"></svg>
          </div>
          <div class="pump-arrow ${n?"spinning":""}"
               style="top:${this._v("pump_right_top")}%; right:${this._v("pump_right_x")}%; width:${this._v("pump_right_size")}%; --pump-dur:${m}s;">
            <svg viewBox="0 0 40 40" .innerHTML="${l}"></svg>
          </div>

          <!-- Plug pH (links) -->
          ${cPh?V`
            <div class="plug-badge ${hPh?"on":"off"}"
                 style="top:${this._v("plug_ph_top")}%; left:${this._v("plug_ph_left")}%;"
                 data-entity="${cPh}"
                 @click="${this._togglePlug}">
              <ha-icon icon="mdi:power-plug${hPh?"":"-off-outline"}"></ha-icon>
            </div>
          `:I}
          <!-- Plug Redox (rechts) -->
          ${cRx?V`
            <div class="plug-badge ${hRx?"on":"off"}"
                 style="top:${this._v("plug_rx_top")}%; right:${this._v("plug_rx_right")}%;"
                 data-entity="${cRx}"
                 @click="${this._togglePlug}">
              <ha-icon icon="mdi:power-plug${hRx?"":"-off-outline"}"></ha-icon>
            </div>
          `:I}

          <!-- Values -->
          <div class="value-box ${w?"":"no-bg"}"
               style="bottom:${this._v("value_bottom")}%; left:${this._v("value_ph_x")}%; transform:translateX(-50%) scale(${this._v("value_scale")/100}); --val-color:${y};">
            <span class="val">${e}</span>
            ${b?V`<span class="unit">pH</span>`:I}
          </div>
          <div class="value-box ${w?"":"no-bg"}"
               style="bottom:${this._v("value_bottom")}%; right:${this._v("value_rx_x")}%; transform:translateX(50%) scale(${this._v("value_scale")/100}); --val-color:${y};">
            <span class="val">${s}</span>
            ${b?V`<span class="unit">RX</span>`:I}
          </div>

          <!-- Cloud-Status oben links -->
          ${showCloud&&cloudEnt?V`
            <div class="cloud-badge ${cloudOn?"on":"off"}" title="Cloud-Verbindung: ${cloudOn?"verbunden":"getrennt"}">
              <ha-icon icon="${cloudOn?"mdi:cloud":"mdi:cloud-off-outline"}"></ha-icon>
            </div>
          `:I}

          <!-- Einstellungs-Zahnrad oben rechts -->
          ${showSettings?V`
            <div class="gear-badge" @click="${this._openSettings}" title="Einstellungen">
              <ha-icon icon="mdi:cog"></ha-icon>
            </div>
          `:I}

          <!-- Settings-Overlay (Sollwerte, Behaelter, Modi) -->
          ${settingsOpen?V`
            <div class="settings-overlay" @click="${this._closeSettings}">
              <div class="settings-panel" @click="${this._stopProp}">
                <div class="settings-header">
                  <h3><ha-icon icon="mdi:cog"></ha-icon> Einstellungen</h3>
                  <button class="settings-close" @click="${this._closeSettings}" title="Schliessen">
                    <ha-icon icon="mdi:close"></ha-icon>
                  </button>
                </div>

                <div class="settings-group">
                  <h4>Sollwerte</h4>
                  ${this._numberRow("pH Sollwert","_ph_sollwert","mdi:ph")}
                  ${this._numberRow("Redox Sollwert","_orp_sollwert","mdi:water-check")}
                </div>

                <div class="settings-group">
                  <h4>Behaelter &amp; Dosierung</h4>
                  ${this._numberRow("pH-Senker Behaelter","_ph_behaeltergroesse","mdi:barrel")}
                  ${this._numberRow("Chlor Behaelter","_chlor_behaeltergroesse","mdi:barrel")}
                  ${this._numberRow("pH Max / Tag","_ph_maximaldosis_tag","mdi:speedometer")}
                  ${this._numberRow("Chlor Max / Tag","_chlor_maximaldosis_tag","mdi:speedometer")}
                </div>

                <div class="settings-group">
                  <h4>Restmenge (manuell setzen beim Nachfuellen)</h4>
                  ${this._numberRow("pH-Senker Rest","_ph_restmenge","mdi:water-percent")}
                  ${this._numberRow("Chlor Rest","_chlor_restmenge","mdi:water-percent")}
                </div>

                <div class="settings-group">
                  <h4>Betriebsmodus</h4>
                  ${this._switchRow("Spa-Modus","_spa_modus","mdi:hot-tub")}
                  ${this._switchRow("Winter-Modus","_winter_modus","mdi:snowflake")}
                </div>
              </div>
            </div>
          `:I}
        </div>
      </ha-card>
    `}static getConfigElement(){return document.createElement("orpheo-vp-card-editor")}static getStubConfig(){return{device_name:"Orpheo VP Pool Dosieranlage",model:"type1",image_variant:"dark"}}};$t.styles=n`
    :host { display: block; }
    ha-card { overflow: hidden; padding: 0; background: transparent; }
    .card-wrap { position: relative; width: 100%; line-height: 0; }
    .bg { width: 100%; height: auto; display: block; }

    /* Firmware */
    .firmware-badge {
      position: absolute; padding: 2px 8px;
      background: rgba(0,0,0,0.6); border-radius: 4px;
      font-size: 0.75em; font-weight: 700; color: #fff;
      letter-spacing: 1px; font-family: monospace;
      line-height: 1.3; pointer-events: none; white-space: nowrap;
    }
    .firmware-badge.no-bg { background: none; }

    /* Water */
    .water-zone { position: absolute; overflow: hidden; transition: opacity 0.5s, filter 0.5s; pointer-events: none; }
    .water-zone.active { opacity: 1; }
    .water-svg { width: 200%; height: 100%; position: absolute; top: 0; left: 0; }
    .wave { fill: none; stroke-linecap: round; animation-name: waveScroll; animation-timing-function: linear; animation-iteration-count: infinite; }
    .wave1 { stroke: rgba(0,180,255,0.7); stroke-width: 3.5; }
    .wave2 { stroke: rgba(0,140,230,0.5); stroke-width: 2.5; animation-delay: -0.5s; }
    .wave3 { stroke: rgba(100,200,255,0.4); stroke-width: 2; animation-delay: -1s; }
    .water-zone:not(.active):not(.inactive-gray) { opacity: 0; }
    .water-zone:not(.active).inactive-gray { opacity: 0.5; filter: grayscale(1); }
    .water-zone:not(.active) .wave { animation-play-state: paused; }
    @keyframes waveScroll { to { transform: translateX(-50%); } }

    /* Pumps */
    .pump-arrow { position: absolute; aspect-ratio: 1; pointer-events: none; color: rgba(0,0,0,0.25); transition: color 0.3s; }
    .pump-arrow svg { width: 100%; height: 100%; overflow: visible; }
    .pump-arrow.spinning { color: rgba(0,0,0,0.9); filter: drop-shadow(0 0 3px rgba(0,0,0,0.2)); }
    .pump-arrow.spinning svg { animation: pumpSpin var(--pump-dur, 1s) linear infinite; }
    @keyframes pumpSpin { to { transform: rotate(360deg); } }

    /* Plug */
    .plug-badge {
      position: absolute; cursor: pointer; padding: 4px;
      border-radius: 50%; --mdc-icon-size: 24px;
      transition: all 0.3s; line-height: 0; background: rgba(0,0,0,0.4);
    }
    .plug-badge.on { color: #4caf50; box-shadow: 0 0 10px rgba(76,175,80,0.5); }
    .plug-badge.off { color: #f44336; opacity: 0.7; }
    .plug-badge:hover { transform: scale(1.15); }

    /* Values */
    .value-box {
      position: absolute; display: flex; flex-direction: column; align-items: center;
      justify-content: center; background: rgba(0,0,0,0.75);
      border: 1px solid rgba(255,255,255,0.15); border-radius: 10px;
      padding: 6px 16px; min-width: 75px; line-height: 1.2; backdrop-filter: blur(4px);
    }
    .value-box.no-bg { background: none; border: none; backdrop-filter: none; padding: 2px 6px; }
    .val { font-size: 1.5em; font-weight: 700; color: var(--val-color, #fff); }
    .unit { font-size: 0.85em; font-weight: 600; color: var(--val-color, #fff); opacity: 0.7; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }

    /* Cloud Badge */
    .cloud-badge {
      position: absolute; top: 6px; left: 6px;
      padding: 4px; border-radius: 50%;
      background: rgba(0,0,0,0.45); --mdc-icon-size: 20px;
      line-height: 0; pointer-events: none;
      transition: all 0.3s;
    }
    .cloud-badge.on { color: #8bd3ff; }
    .cloud-badge.off { color: #ff6b6b; opacity: 0.85; }

    /* Gear Badge */
    .gear-badge {
      position: absolute; top: 6px; right: 6px;
      padding: 6px; border-radius: 50%;
      background: rgba(0,0,0,0.45); color: #fff;
      --mdc-icon-size: 20px; line-height: 0;
      cursor: pointer; transition: all 0.2s;
      z-index: 5;
    }
    .gear-badge:hover { background: rgba(0,0,0,0.75); transform: rotate(45deg); }

    /* Settings Overlay */
    .settings-overlay {
      position: absolute; inset: 0;
      background: rgba(0,0,0,0.55);
      backdrop-filter: blur(4px);
      display: flex; align-items: center; justify-content: center;
      z-index: 20; line-height: normal;
      animation: fadeIn 0.2s ease-out;
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    .settings-panel {
      background: var(--card-background-color, #1e1e1e);
      color: var(--primary-text-color, #fff);
      border-radius: 16px;
      box-shadow: 0 16px 48px rgba(0,0,0,0.6);
      padding: 20px 24px;
      width: min(92%, 480px);
      max-height: 88%;
      overflow-y: auto;
      border: 1px solid rgba(255,255,255,0.08);
    }

    .settings-header {
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 12px;
      padding-bottom: 10px;
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .settings-header h3 {
      margin: 0; font-size: 1.15em; font-weight: 600;
      display: flex; align-items: center; gap: 8px;
      --mdc-icon-size: 22px;
    }
    .settings-close {
      background: transparent; border: none; cursor: pointer;
      color: var(--primary-text-color, #fff);
      padding: 4px; border-radius: 50%;
      --mdc-icon-size: 20px; line-height: 0;
      transition: background 0.2s;
    }
    .settings-close:hover { background: rgba(255,255,255,0.12); }

    .settings-group { margin-top: 16px; }
    .settings-group h4 {
      margin: 0 0 8px 0;
      font-size: 0.85em; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.8px;
      color: var(--secondary-text-color, #bbb);
    }

    .settings-row {
      display: flex; align-items: center; justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      gap: 12px;
    }
    .settings-row:last-child { border-bottom: none; }
    .settings-row.missing em { color: #ff6b6b; font-size: 0.75em; font-family: monospace; }

    .settings-label {
      display: flex; align-items: center; gap: 8px;
      font-size: 0.92em; font-weight: 500;
      --mdc-icon-size: 20px;
      flex-shrink: 0;
      color: var(--primary-text-color, #fff);
    }

    .settings-num {
      display: flex; align-items: center; gap: 8px;
      flex: 1; justify-content: flex-end;
    }
    .settings-num input[type="range"] {
      flex: 1; min-width: 0; max-width: 140px;
      accent-color: var(--primary-color, #03a9f4);
    }
    .settings-num input[type="number"] {
      width: 64px;
      padding: 4px 6px;
      background: rgba(255,255,255,0.08);
      color: var(--primary-text-color, #fff);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 4px;
      font-size: 0.9em;
      text-align: right;
      font-family: inherit;
    }
    .settings-num input[type="number"]:focus {
      outline: none; border-color: var(--primary-color, #03a9f4);
    }
    .settings-unit {
      font-size: 0.8em; color: var(--secondary-text-color, #bbb);
      min-width: 26px;
    }

    .settings-toggle {
      position: relative; display: inline-block;
      width: 44px; height: 24px; cursor: pointer;
    }
    .settings-toggle input { display: none; }
    .slider-track {
      position: absolute; inset: 0;
      background: rgba(255,255,255,0.18);
      border-radius: 12px; transition: background 0.2s;
    }
    .slider-track:before {
      content: ""; position: absolute;
      top: 2px; left: 2px;
      width: 20px; height: 20px;
      background: #fff; border-radius: 50%;
      transition: transform 0.2s;
    }
    .settings-toggle input:checked + .slider-track {
      background: var(--primary-color, #03a9f4);
    }
    .settings-toggle input:checked + .slider-track:before {
      transform: translateX(20px);
    }
  `,t([dt({attribute:!1})],$t.prototype,"hass",void 0),t([ut()],$t.prototype,"_config",void 0),$t=t([ct("orpheo-vp-card")],$t);let mt=class extends at{setConfig(t){this._config={...t};if(!this._config.device_name&&this._config.entity_prefix){this._config.device_name=this._config.entity_prefix.replace(/^sensor\./,"").replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase())}}_ev(t){const p=xt[this._config.model??'type1']??{};return this._config[t]??p[t]??_t[t]}_changed(t){const e=t.target,i=e.dataset.key;let s;if(s="range"===e.type?parseFloat(e.value):"checkbox"===e.type?e.checked:e.value,"device_name"===i){this._config={...this._config,device_name:s,entity_prefix:"sensor."+s.toLowerCase().replace(/\s+/g,"_")},this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:this._config}}));return}if("model"===i){const p=xt[s]??{},keep={type:this._config.type,device_name:this._config.device_name,entity_prefix:this._config.entity_prefix,model:s,image_variant:this._config.image_variant,plug_entity_ph:this._config.plug_entity_ph,plug_entity_rx:this._config.plug_entity_rx,plug_entity:this._config.plug_entity,firmware_text:this._config.firmware_text};this._config={...keep,...p},this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:this._config}}));return}this._config={...this._config,[i]:s},this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:this._config}}))}_slider(t,e,i,s,o="%",r=1){const n=this._ev(e)??100;return V`
      <div class="slider-row">
        <span class="slider-label">${t}</span>
        <input type="range" min="${i}" max="${s}" step="${r}"
               .value="${String(n)}" data-key="${e}" @input="${this._changed}" />
        <span class="slider-val">${n}${o}</span>
      </div>
    `}_toggle(t,e,i){const s=this._ev(e)??i;return V`
      <div class="toggle-row">
        <span class="slider-label">${t}</span>
        <input type="checkbox" ?checked="${s}" data-key="${e}" @change="${this._changed}" />
      </div>
    `}_section(t,e){return V`
      <details class="section">
        <summary>${t}</summary>
        <div class="section-body">${e}</div>
      </details>
    `}render(){return this._config?V`
      <div class="editor">
        <label>Name der Dosieranlage
          <input type="text" .value="${this._config.device_name||""}" data-key="device_name" @input="${this._changed}" placeholder="Orpheo VP Pool Dosieranlage" />
          <small>Gib hier den <b>Namen</b> deiner Dosieranlage ein — genau so wie du ihn bei der Integration vergeben hast. Beispiel: <b>Orpheo VP Pool Dosieranlage</b></small>
        </label>
        <label>Steckdose pH (optional)
          <input type="text" .value="${this._config.plug_entity_ph||""}" data-key="plug_entity_ph" @input="${this._changed}" placeholder="z.B. switch.dosierpumpe_ph" />
          <small>Entity-ID Schalter fuer pH-Pumpen-Netzteil — leer = kein Icon</small>
        </label>
        <label>Steckdose Redox (optional)
          <input type="text" .value="${this._config.plug_entity_rx||this._config.plug_entity||""}" data-key="plug_entity_rx" @input="${this._changed}" placeholder="z.B. switch.dosierpumpe_rx" />
          <small>Entity-ID Schalter fuer Redox-Pumpen-Netzteil — leer = kein Icon</small>
        </label>
        <label>Anlagentyp
          <select data-key="model" @change="${this._changed}">
            <option value="type1" ?selected="${"type1"===this._config.model}">Typ 1</option>
          </select>
        </label>
        <label>Bildvariante
          <select data-key="image_variant" @change="${this._changed}">
            <option value="dark" ?selected="${"dark"===this._config.image_variant}">Transparent</option>
            <option value="light" ?selected="${"light"===this._config.image_variant}">Weiß</option>
          </select>
        </label>
        <label>Pumpen-Symbol
          <select data-key="pump_style" @change="${this._changed}">
            <option value="arrow" ?selected="${"arrow"===(this._ev("pump_style")??"arrow")}">↻ Pfeil (Standard)</option>
            <option value="fan" ?selected="${"fan"===this._ev("pump_style")}">✦ Ventilator</option>
            <option value="dots" ?selected="${"dots"===this._ev("pump_style")}">● Punkte-Rad</option>
          </select>
        </label>

        ${this._section("Badges anzeigen",V`
          ${this._toggle("☁ Cloud-Status oben links","show_cloud",!0)}
          ${this._toggle("⚙ Einstellungs-Zahnrad oben rechts","show_settings",!0)}
        `)}

        ${this._section("Wasserfluss",V`
          ${this._slider("Geschwindigkeit (0=still)","water_speed",0,100)}
        `)}

        ${this._section("Pumpen — Drehgeschwindigkeit",V`
          ${this._slider("Drehgeschwindigkeit","pump_speed",10,100)}
        `)}

        ${this._section("Freitextfeld (Firmware-Anzeige)",V`
          <label>Eigener Text (leer = Firmware)
            <input type="text" .value="${this._config.firmware_text||""}" data-key="firmware_text" @input="${this._changed}" placeholder="z.B. Meine Dosieranlage" />
          </label>
          ${this._toggle("Box anzeigen","firmware_box",!0)}
          <div class="slider-row">
            <span class="slider-label">Schriftfarbe</span>
            <select data-key="firmware_color" @change="${this._changed}">
              <option value="white" ?selected="${"white"===(this._ev("firmware_color")??"white")}">Weiß</option>
              <option value="black" ?selected="${"black"===this._ev("firmware_color")}">Schwarz</option>
            </select>
          </div>
          ${this._slider("Größe","firmware_scale",50,200)}
        `)}

        <!-- Erweiterte Einstellungen -->
        <details class="section advanced">
          <summary>Erweiterte Einstellungen</summary>
          <div class="section-body advanced-body">

            ${this._section("Wasserfluss — Erweitert",V`
              <div class="slider-row">
                <span class="slider-label">Fließrichtung</span>
                <select data-key="water_direction" @change="${this._changed}">
                  <option value="right" ?selected="${"right"===(this._ev("water_direction")??"right")}">→ Nach rechts</option>
                  <option value="left" ?selected="${"left"===this._ev("water_direction")}">← Nach links</option>
                </select>
              </div>
              <div class="slider-row">
                <span class="slider-label">Bei Stillstand</span>
                <select data-key="water_inactive" @change="${this._changed}">
                  <option value="hidden" ?selected="${"hidden"===(this._ev("water_inactive")??"hidden")}">Ausblenden</option>
                  <option value="gray" ?selected="${"gray"===this._ev("water_inactive")}">Grau + stehend</option>
                </select>
              </div>
              ${this._slider("Von oben","water_top",0,100)}
              ${this._slider("Höhe","water_height",4,20)}
              ${this._slider("Breite","water_width",40,100)}
              ${this._slider("Mittelpunkt","water_center",30,70)}
            `)}

            ${this._section("Pumpe links (pH)",V`
              ${this._slider("Von oben","pump_left_top",0,30,"%",.5)}
              ${this._slider("Von links","pump_left_x",0,80,"%",.5)}
              ${this._slider("Größe","pump_left_size",4,16,"%",.5)}
            `)}

            ${this._section("Pumpe rechts (RX)",V`
              ${this._slider("Von oben","pump_right_top",0,30,"%",.5)}
              ${this._slider("Von rechts","pump_right_x",0,80,"%",.5)}
              ${this._slider("Größe","pump_right_size",4,16,"%",.5)}
            `)}

            ${this._section("Freitextfeld — Position",V`
              ${this._slider("Von oben","firmware_top",5,50)}
              ${this._slider("Von links","firmware_left",20,80)}
            `)}

            ${this._section("Steckdose pH — Position",V`
              ${this._slider("Von oben","plug_ph_top",0,100)}
              ${this._slider("Von links","plug_ph_left",0,100)}
            `)}
            ${this._section("Steckdose Redox — Position",V`
              ${this._slider("Von oben","plug_rx_top",0,100)}
              ${this._slider("Von rechts","plug_rx_right",0,100)}
            `)}

            ${this._section("pH- und RX Darstellung",V`
              ${this._slider("Von unten","value_bottom",0,30)}
              ${this._slider("pH — von links","value_ph_x",15,50)}
              ${this._slider("RX — von rechts","value_rx_x",15,50)}
              ${this._slider("Größe (beide)","value_scale",50,150)}
              <div class="slider-row">
                <span class="slider-label">Schriftfarbe</span>
                <select data-key="value_color" @change="${this._changed}">
                  <option value="white" ?selected="${"white"===(this._ev("value_color")??"white")}">Weiß</option>
                  <option value="black" ?selected="${"black"===this._ev("value_color")}">Schwarz</option>
                </select>
              </div>
              ${this._toggle("Box anzeigen","value_box",!0)}
              ${this._toggle("pH / RX Label anzeigen","value_labels",!0)}
            `)}

          </div>
        </details>
      </div>
    `:I}};mt.styles=n`
    .editor { display: flex; flex-direction: column; gap: 12px; padding: 16px; }
    label { display: flex; flex-direction: column; font-weight: 500; gap: 4px; }
    input[type="text"], select { padding: 8px; border: 1px solid var(--divider-color, #ccc); border-radius: 4px; font-size: 14px; }
    small { color: var(--secondary-text-color, #888); font-weight: 400; }

    /* Collapsible sections */
    .section { border: 1px solid var(--divider-color, #ccc); border-radius: 8px; overflow: hidden; }
    .section summary {
      padding: 10px 14px; font-size: 14px; font-weight: 600; cursor: pointer;
      color: var(--primary-text-color); background: var(--card-background-color, rgba(0,0,0,0.05));
      list-style: none; display: flex; align-items: center; gap: 8px;
      user-select: none;
    }
    .section summary::-webkit-details-marker { display: none; }
    .section summary::before { content: "▶"; font-size: 10px; transition: transform 0.2s; }
    .section[open] summary::before { transform: rotate(90deg); }
    .section-body { display: flex; flex-direction: column; gap: 10px; padding: 12px 14px; }
    .section.advanced { border-color: var(--warning-color, #ff9800); }
    .section.advanced > summary { font-size: 13px; color: var(--warning-color, #ff9800); background: rgba(255,152,0,0.08); }
    .advanced-body { gap: 8px; }

    .slider-row, .toggle-row { display: flex; align-items: center; gap: 8px; }
    .slider-label { flex: 1; font-size: 13px; color: var(--primary-text-color); }
    .slider-row input[type="range"] { flex: 2; }
    .slider-row select { flex: 2; padding: 6px; border: 1px solid var(--divider-color, #ccc); border-radius: 4px; font-size: 13px; }
    .slider-val { width: 40px; text-align: right; font-size: 13px; font-weight: 600; color: var(--primary-color); }
    .toggle-row input[type="checkbox"] { width: 18px; height: 18px; }
  `,t([dt({attribute:!1})],mt.prototype,"hass",void 0),t([ut()],mt.prototype,"_config",void 0),mt=t([ct("orpheo-vp-card-editor")],mt),window.customCards=window.customCards||[],window.customCards.push({type:"orpheo-vp-card",name:"TomTuT Pool Dosing",description:"Visualisierung der Beniferro Gen2 Dosieranlage mit animierten Pumpen und Wasserfluss",preview:!0,documentationURL:"https://github.com/TomTuTHub/orpheo-vp-card"});export{$t as TomtutPoolDosingCard,mt as TomtutPoolDosingCardEditor};
