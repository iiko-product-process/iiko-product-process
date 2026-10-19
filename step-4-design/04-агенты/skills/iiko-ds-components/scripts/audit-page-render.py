#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Three objective render detectors over the iiko DS recommendation pages.

Finds what a downscaled contact sheet hides:
  PLATE     element with own text whose background-color equals its color
            (Figma autogen put the text fill into the background) -> solid slab
  CONTRAST  text with contrast ratio below the threshold against its effective
            background (walks up until a non-transparent background) -> invisible text
  OVERFLOW  element whose rect sticks out of its .panel (ancestors with
            overflow != visible are skipped, otherwise scrollers give false hits)

Why a wrapper page: --dump-dom does not execute our JS on the target page, and
iframes need same-origin access to contentDocument, so all pages are loaded
through the local server (python serve.py 8899 in the DS root).

Usage (server must be up):
  python audit-page-render.py                 # all three detectors, all pages
  python audit-page-render.py --only plates
  python audit-page-render.py --contrast-threshold 2.5
  python audit-page-render.py --pages dialog,list,menu
Exit code 1 when anything is found.
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

DS = r"C:\Users\asukharev\GitHub\DS"
OUT = os.path.join(DS, "iiko-ds-mobile", "prototypes", "recommendations")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = "http://127.0.0.1:8899/iiko-ds-mobile/prototypes/recommendations/"

JS_TMPL = r"""<!doctype html><meta charset="utf-8"><body><pre id="out"></pre><script>
const PAGES = %(pages)s, THRESH = %(thresh)s, OUT = []; let i = 0;
function lum(c){const m=c.match(/[\d.]+/g); if(!m) return null;
  const v=m.slice(0,3).map(Number).map(x=>{x/=255; return x<=0.03928? x/12.92 : Math.pow((x+0.055)/1.055,2.4);});
  return 0.2126*v[0]+0.7152*v[1]+0.0722*v[2];}
function effBg(el, win){let a=el; while(a && a!==win.document.documentElement){
  const c=win.getComputedStyle(a);
  if(c.backgroundColor && c.backgroundColor!=='rgba(0, 0, 0, 0)' && c.opacity!=='0') return c.backgroundColor;
  a=a.parentElement;} return 'rgb(255,255,255)';}
function ratio(a,b){const l1=lum(a), l2=lum(b); if(l1==null||l2==null) return null;
  const hi=Math.max(l1,l2), lo=Math.min(l1,l2); return (hi+0.05)/(lo+0.05);}
function clipped(el, win){let a=el.parentElement;
  while(a && !a.classList.contains('panel')){
    if(win.getComputedStyle(a).overflow!=='visible') return true; a=a.parentElement;} return false;}
function ownText(el){return [...el.childNodes].some(n=>n.nodeType===3 && n.textContent.trim());}
function scan(doc, win, page){
  doc.querySelectorAll('.panel').forEach(pan=>{
    const mode=pan.dataset.mode||'desktop', pr=pan.getBoundingClientRect();
    pan.querySelectorAll('*').forEach(el=>{
      const c=win.getComputedStyle(el);
      if(c.display==='none'||c.visibility==='hidden'||c.opacity==='0') return;
      const cls=((el.className||el.tagName)+'').slice(0,44);
      if(ownText(el)){
        const bg=c.backgroundColor, txt=el.textContent.trim().slice(0,30);
        if(bg!=='rgba(0, 0, 0, 0)' && bg!=='transparent' && bg===c.color)
          OUT.push('PLATE | '+page+' ['+mode+'] '+cls+' | '+txt);
        const r=ratio(c.color, effBg(el, win));
        if(r!=null && r<THRESH)
          OUT.push('CONTRAST | '+page+' ['+mode+'] '+cls+' | '+r.toFixed(2)+' | '+txt);
      }
      if(clipped(el, win)) return;
      const b=el.getBoundingClientRect(); if(!b.width && !b.height) return;
      const dL=pr.left-b.left, dR=b.right-pr.right;
      if(dL>5 || dR>5)
        OUT.push('OVERFLOW | '+page+' ['+mode+'] '+cls+' | left+'+Math.round(dL)+' right+'+Math.round(dR)+' | '+el.textContent.trim().slice(0,24));
    });
  });
}
function next(){ if(i>=PAGES.length){document.getElementById('out').textContent=OUT.join('\n'); return;}
  const page=PAGES[i++]; const f=document.createElement('iframe');
  f.style.cssText='width:1600px;height:1400px;border:0';
  f.src='/iiko-ds-mobile/prototypes/recommendations/'+page+'.html';
  f.onload=()=>setTimeout(()=>{scan(f.contentDocument, f.contentWindow, page); f.remove(); next();},320);
  document.body.appendChild(f);}
next();
</script></body>"""


def pages_on_disk():
    return sorted(
        os.path.basename(p)[:-5]
        for p in glob.glob(os.path.join(OUT, "*.html"))
        if not os.path.basename(p).startswith(("index", "_"))
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["plates", "contrast", "overflow"], default=None)
    ap.add_argument("--contrast-threshold", type=float, default=2.0)
    ap.add_argument("--pages", default=None, help="comma separated slugs")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()

    pages = args.pages.split(",") if args.pages else pages_on_disk()
    if not pages:
        print("no pages found in", OUT)
        return 2
    wrapper = os.path.join(OUT, "_detectors.html")
    prof = os.path.join(tempfile.gettempdir(), "udd_detectors")
    shutil.rmtree(prof, ignore_errors=True)  # fresh profile: never measure cached CSS
    with open(wrapper, "w", encoding="utf-8", newline="\n") as f:
        f.write(JS_TMPL % {"pages": repr(pages).replace("'", '"'), "thresh": repr(args.contrast_threshold)})
    try:
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--virtual-time-budget=" + str(args.timeout * 1000),
               "--user-data-dir=" + prof, "--dump-dom", BASE + "_detectors.html"]
        dom = subprocess.run(cmd, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=args.timeout).stdout
    finally:
        os.remove(wrapper)

    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    lines = []
    if m:
        raw = (m.group(1).replace("&lt;", "<").replace("&gt;", ">")
               .replace("&quot;", '"').replace("&amp;", "&"))
        lines = [l for l in raw.splitlines() if l.strip()]

    kinds = {"plates": "PLATE", "contrast": "CONTRAST", "overflow": "OVERFLOW"}
    wanted = [kinds[args.only]] if args.only else ["PLATE", "CONTRAST", "OVERFLOW"]
    total = 0
    for kind in wanted:
        found = [l for l in lines if l.startswith(kind + " |")]
        total += len(found)
        label = {v: k for k, v in kinds.items()}[kind]
        print("-- %s: %d" % (label, len(found)))
        for l in found:
            print("     ", l)
    if not lines:
        print("WARNING: no output parsed -- is the server on 8899 up?")
        return 2
    print("\npages scanned: %d   findings: %d" % (len(pages), total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
