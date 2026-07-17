from pathlib import Path

INDEX_PATH = Path("index.html")
ADS_ID = "AW-18320037201"
FORM_LABEL = "a6M4CPLkp9EcENGq1p9E"

html = INDEX_PATH.read_text(encoding="utf-8")

required_items = [
    f"gtag('config', '{ADS_ID}');",
    f"gtag('event', 'conversion', {{'send_to': '{ADS_ID}/{FORM_LABEL}'}});",
]
missing = [item for item in required_items if item not in html]
if missing:
    raise SystemExit(f"Missing required Google Ads tracking code: {missing}")

phone_tracking = r'''
// Track every click-to-call link as a GA4/dataLayer event.
(function bindPhoneClickTracking(){
  document.querySelectorAll('a[href^="tel:"]').forEach(function(link){
    if(link.dataset.callTrackingBound === 'true') return;
    link.dataset.callTrackingBound = 'true';

    link.addEventListener('click', function(){
      var phoneNumber=(link.getAttribute('href')||'').replace(/^tel:/,'');
      var eventData={
        phone_number:phoneNumber,
        link_text:(link.textContent||'').trim(),
        page_location:window.location.href,
        transport_type:'beacon'
      };

      window.dataLayer=window.dataLayer||[];
      window.dataLayer.push(Object.assign({event:'phone_click'},eventData));

      if(typeof window.gtag === 'function'){
        window.gtag('event','phone_click',eventData);
      }
    });
  });
})();
'''

marker = "var contactForm=document.getElementById('contactForm');"
if "bindPhoneClickTracking" not in html:
    if marker not in html:
        raise SystemExit("Could not locate contact form script marker")
    html = html.replace(marker, phone_tracking + "\n" + marker, 1)

old_form_block = f"""      window.dataLayer=window.dataLayer||[];
      window.dataLayer.push({{event:'contact_form_submit',form_name:'Iznajmljivanje kontejnera Novi Sad'}});
      gtag('event', 'conversion', {{'send_to': '{ADS_ID}/{FORM_LABEL}'}});"""

new_form_block = f"""      window.dataLayer=window.dataLayer||[];
      window.dataLayer.push({{event:'contact_form_submit',form_name:'Iznajmljivanje kontejnera Novi Sad'}});

      // Fire lead events only after Web3Forms confirms success.
      if(typeof window.gtag === 'function'){{
        window.gtag('event','generate_lead',{{
          form_name:'Iznajmljivanje kontejnera Novi Sad',
          transport_type:'beacon'
        }});
        window.gtag('event','conversion',{{
          send_to:'{ADS_ID}/{FORM_LABEL}',
          transport_type:'beacon'
        }});
      }}"""

if old_form_block in html:
    html = html.replace(old_form_block, new_form_block, 1)
elif "window.gtag('event','generate_lead'" not in html:
    raise SystemExit("Could not locate the successful form conversion block")

INDEX_PATH.write_text(html, encoding="utf-8")
print("Google Ads form and phone-click tracking verified.")
