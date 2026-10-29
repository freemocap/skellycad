// Isolated headless artifact QA; does not control the user's browser.
const {chromium}=require('C:/Users/jonma/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('path'),fs=require('fs');
(async()=>{let browser;try{
 browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1280,height:900},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const response=await page.goto('http://127.0.0.1:8787/designs/eye-camera-ov9281/electronics/three-board-e01/index.html');
 if(response.status()!==200)throw Error('HTTP '+response.status());
 await page.waitForLoadState('networkidle');
 const dir=path.resolve(__dirname,'../../../../generated/three-board-e01');
 await page.screenshot({path:path.join(dir,'review-desktop.png'),fullPage:true});
 for(const label of ['Base station','Complete view','Complete top','Head assembly']){
  await page.getByRole('button',{name:label,exact:true}).click();
  await page.waitForFunction(()=>{const i=document.getElementById('cad-view');return i.complete&&i.naturalWidth>0});
 }
 const images=await page.locator('img').evaluateAll(imgs=>imgs.map(i=>({src:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0})));
 if(images.some(i=>!i.ok)||errors.length)throw Error(JSON.stringify({images,errors}));
 await page.locator('summary').click();
 const bomRows=await page.locator('details tbody tr').count();if(bomRows!==196)throw Error('BOM count '+bomRows);
 await page.locator('summary').click();
 await page.setViewportSize({width:390,height:844});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);if(overflow)throw Error('Mobile overflow');
 await page.screenshot({path:path.join(dir,'review-mobile.png'),fullPage:true});
 const statuses=await page.locator('.checks li').evaluateAll(nodes=>nodes.map(n=>n.className));
 fs.writeFileSync(path.join(dir,'html-validation.json'),JSON.stringify({status:'pass',http_status:200,images,script_errors:errors,view_switches:4,bom_rows:bomRows,mobile_overflow:overflow,checklist_states:statuses},null,2));
 console.log('E01_HTML_QA_PASS');
}finally{if(browser)await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
