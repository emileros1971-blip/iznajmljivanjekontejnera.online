from pathlib import Path

INDEX_PATH = Path("index.html")
ADS_ID = "AW-18320037201"
FORM_LABEL = "a6M4CPLkp9EcENGq1p9E"
PHONE_LABEL = "Op1GCMyW_tMcENGq1p9E"

html = INDEX_PATH.read_text(encoding="utf-8")

if f"gtag('config', '{ADS_ID}');" not in html:
    raise SystemExit("Missing Google Ads base tag configuration")

# Keep the existing GA4/dataLayer phone-click event, but use Google's standard
# Google Ads conversion event snippet without forcing Beacon transport.
old_phone_conversion = f"""        window.gtag('event','conversion',{{
          send_to:'{ADS_ID}/{PHONE_LABEL}',
          transport_type:'beacon'
        }});"""
standard_phone_conversion = (
    f"        gtag('event', 'conversion', {{'send_to': '{ADS_ID}/{PHONE_LABEL}'}});"
)

if old_phone_conversion in html:
    html = html.replace(old_phone_conversion, standard_phone_conversion, 1)
elif standard_phone_conversion not in html:
    phone_event_line = "        window.gtag('event','phone_click',eventData);"
    if phone_event_line not in html:
        raise SystemExit("Could not locate the phone-click event line")
    html = html.replace(
        phone_event_line,
        phone_event_line + "\n" + standard_phone_conversion,
        1,
    )

# The form is submitted with fetch(), so the conversion must fire only after
# Web3Forms confirms success. Use the standard gtag conversion event snippet;
# Tag Assistant was not detecting the previous forced-beacon implementation.
old_form_tracking = f"""      // Fire lead events only after Web3Forms confirms success.
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

standard_form_tracking = f"""      // Fire lead events only after Web3Forms confirms success.
      gtag('event', 'generate_lead', {{
        'form_name': 'Iznajmljivanje kontejnera Novi Sad'
      }});
      gtag('event', 'conversion', {{'send_to': '{ADS_ID}/{FORM_LABEL}'}});"""

if old_form_tracking in html:
    html = html.replace(old_form_tracking, standard_form_tracking, 1)
elif standard_form_tracking not in html:
    # Also support the original one-line implementation if this installer is
    # run against an older checkout.
    original_form_conversion = (
        f"      gtag('event', 'conversion', {{'send_to': '{ADS_ID}/{FORM_LABEL}'}});"
    )
    if original_form_conversion not in html:
        raise SystemExit("Could not locate the successful form conversion block")

required_after = [
    f"gtag('event', 'conversion', {{'send_to': '{ADS_ID}/{FORM_LABEL}'}});",
    f"gtag('event', 'conversion', {{'send_to': '{ADS_ID}/{PHONE_LABEL}'}});",
]
missing_after = [item for item in required_after if item not in html]
if missing_after:
    raise SystemExit(f"Tracking fix incomplete: {missing_after}")

INDEX_PATH.write_text(html, encoding="utf-8")
print("Google Ads form and phone-click conversion snippets standardized.")
