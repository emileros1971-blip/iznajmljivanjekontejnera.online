from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

old = """      if(typeof window.gtag === 'function'){
        window.gtag('event','phone_click',eventData);
      }
"""

new = """      if(typeof window.gtag === 'function'){
        window.gtag('event','phone_click',eventData);
        window.gtag('event','conversion',{
          send_to:'AW-18320037201/Op1GCMyW_tMcENGq1p9E',
          transport_type:'beacon'
        });
      }
"""

if "AW-18320037201/Op1GCMyW_tMcENGq1p9E" in text:
    print("Phone conversion tracking already installed.")
elif old not in text:
    raise SystemExit("Expected phone_click tracking block was not found; no changes made.")
else:
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("Installed Google Ads website phone-click conversion tracking.")
