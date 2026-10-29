// Headless local artifact QA. Does not attach to the user's browser.
const {chromium}=require('C:/Users/jonma/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('path'),fs=require('fs');
(async()=>{let browser;try{
 browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1280,height:900},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const response=await page.goto('http://127.0.0.1:8787/designs/eye-camera-ov9281/architecture/three-board-r01/index.html');
 if(response.status()!==200)throw Error('Review HTTP '+response.status());
 await page.waitForLoadState('networkidle');
 const dir=path.resolve(__dirname,'../../../../generated/three-board-a01');
 await page.screenshot({path:path.join(dir,'review-desktop.png'),fullPage:true});
 for(const label of ['Back','With base station','Steel alternative','Front']){
   await page.getByRole('button',{name:label,exact:true}).click();
   await page.waitForFunction(()=>{const i=document.getElementById('cad-view');return i.complete&&i.naturalWidth>0});
 }
 await page.locator('summary').click();
 const images=await page.locator('img').evaluateAll(imgs=>imgs.map(i=>({src:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0})));
 if(images.some(i=>!i.ok)||errors.length)throw Error(JSON.stringify({images,errors}));
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(dir,'review-mobile.png'),fullPage:true});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 if(overflow)throw Error('Mobile viewport overflow');
 fs.writeFileSync(path.join(dir,'html-validation.json'),JSON.stringify({http_status:200,script_errors:errors,images,view_switches:4,mobile_overflow:overflow,status:'pass'},null,2));
 console.log('HTML_QA_OK');
}finally{if(browser)await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
