import os
import logging
import csv
import json
from urllib.parse import urlparse
from typing import List, Set, Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

# --- STATE FILES ---
STATE_FILE = "cdx_resume_state.txt"
KNOWN_DOMAINS_FILE = "known_domains.txt"
CSV_FALLBACK_FILE = os.path.join(os.path.dirname(__file__), "my_uk_list.csv")

# Comprehensive Pool of Top UK Domains across key industries & sectors
FALLBACK_UK_DOMAINS = [
    # Media & News
    "bbc.co.uk", "theguardian.com", "telegraph.co.uk", "independent.co.uk",
    "sky.com", "dailymail.co.uk", "mirror.co.uk", "express.co.uk",
    "standard.co.uk", "manchestereveningnews.co.uk", "walesonline.co.uk",
    "birminghammail.co.uk", "scotsman.com", "heraldscotland.com", "chroniclelive.co.uk",
    # Government & Public Services
    "gov.uk", "nhs.uk", "police.uk", "ordnancesurvey.co.uk",
    # Higher Education
    "ox.ac.uk", "cam.ac.uk", "imperial.ac.uk", "ucl.ac.uk", "manchester.ac.uk",
    "kcl.ac.uk", "ed.ac.uk", "warwick.ac.uk", "bristol.ac.uk", "gla.ac.uk",
    # Retail & Consumer
    "boots.com", "argos.co.uk", "currys.co.uk", "superdrug.com",
    "sainsburys.co.uk", "tesco.com", "asda.com", "marksandspencer.com",
    "next.co.uk", "johnlewis.com", "halfords.com", "screwfix.com",
    "toolstation.com", "wickes.co.uk", "bmstores.co.uk", "homebase.co.uk",
    "dunelm.com", "dfshome.co.uk", "very.co.uk", "waterstones.com",
    # Real Estate & Vehicles
    "rightmove.co.uk", "zoopla.co.uk", "onthemarket.com", "autotrader.co.uk",
    "carwow.co.uk", "evanshalshaw.com", "lookers.co.uk", "arnoldclark.com",
    # Business Directories & Services
    "trustpilot.com", "yell.com", "thomsonlocal.com", "cylex-uk.co.uk",
    "freeindex.co.uk", "checkatrade.com", "trustatrader.com", "mybuilder.com",
    "ratedpeople.com", "bark.com", "reed.co.uk", "totaljobs.com",
    # Banking & Finance
    "monzo.com", "revolut.com", "starlingbank.com", "barclays.co.uk",
    "hsbc.co.uk", "natwest.com", "lloydsbank.com", "halifax.co.uk",
    "santander.co.uk", "nationwide.co.uk", "tsb.co.uk", "virginmoney.com",
    # Technology & Telecoms
    "bt.com", "ee.co.uk", "vodafone.co.uk", "o2.co.uk", "three.co.uk",
    "talktalk.co.uk", "plus.net", "virginmedia.com"
]


def _load_resume_index() -> int:
    """Reads the 'bookmark' so we know how many records to skip."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                content = f.read().strip()
                return int(content) if content else 0
        except Exception:
            return 0
    return 0


def _save_resume_index(index: int):
    """Saves our place in the Common Crawl database."""
    try:
        with open(STATE_FILE, 'w') as f:
            f.write(str(index))
    except Exception as e:
        logger.warning(f"Could not write state file {STATE_FILE}: {e}")


def _load_known_domains() -> Set[str]:
    """Loads all domains we have ever scraped so we never repeat them."""
    if os.path.exists(KNOWN_DOMAINS_FILE):
        try:
            with open(KNOWN_DOMAINS_FILE, 'r') as f:
                return set(filter(None, f.read().splitlines()))
        except Exception:
            return set()
    return set()


def _save_known_domains(domains: Set[str]):
    """Appends new domains to our permanent list."""
    if not domains:
        return
    try:
        with open(KNOWN_DOMAINS_FILE, 'a') as f:
            for domain in domains:
                f.write(domain + '\n')
    except Exception as e:
        logger.warning(f"Could not save known domains: {e}")


def _load_csv_fallback_domains() -> List[str]:
    """Loads fallback domains from local my_uk_list.csv if present."""
    domains = []
    if os.path.exists(CSV_FALLBACK_FILE):
        try:
            with open(CSV_FALLBACK_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0] and row[0].strip() != 'Domain Name':
                        d = row[0].strip()
                        if d.startswith('www.'):
                            d = d[4:]
                        if d:
                            domains.append(d)
        except Exception as e:
            logger.warning(f"Could not read CSV fallback file {CSV_FALLBACK_FILE}: {e}")
    return domains


import re

# Comprehensive Country Profiles with Top TLDs and Business Hubs
COUNTRY_CONFIGS: Dict[str, Dict[str, Any]] = {
    "UK": {
        "name": "United Kingdom",
        "tlds": [".co.uk", ".uk", ".org.uk"],
        "cdx_pattern": "*.co.uk/*",
        "cities": [
            'london', 'manchester', 'birmingham', 'leeds', 'glasgow', 'edinburgh',
            'bristol', 'liverpool', 'sheffield', 'newcastle', 'nottingham', 'cardiff',
            'belfast', 'southampton', 'oxford', 'cambridge', 'york', 'bath', 'norwich',
            'exeter', 'plymouth', 'derby', 'leicester', 'aberdeen', 'dundee', 'coventry',
            'reading', 'brighton', 'luton', 'miltonkeynes', 'northampton', 'portsmouth',
            'swindon', 'bournemouth', 'slough', 'chelmsford', 'gloucester', 'cheltenham',
            'ipswich', 'colchester', 'bolton', 'stockport', 'preston', 'sunderland',
            'doncaster', 'huddersfield', 'swansea', 'newport', 'wrexham', 'stirling',
            'inverness', 'perth', 'sthelens', 'blackpool', 'warrington', 'solihull'
        ]
    },
    "US": {
        "name": "United States",
        "tlds": [".com", ".org", ".us", ".net"],
        "cdx_pattern": "*.us/*",
        "cities": [
            'newyork', 'losangeles', 'chicago', 'houston', 'phoenix', 'philadelphia',
            'sanantonio', 'sandiego', 'dallas', 'austin', 'sanjose', 'fortworth',
            'columbus', 'charlotte', 'indianapolis', 'sanfrancisco', 'seattle',
            'denver', 'nashville', 'washington', 'boston', 'elpaso', 'detroit',
            'portland', 'lasvegas', 'memphis', 'louisville', 'baltimore', 'milwaukee',
            'albuquerque', 'tucson', 'fresno', 'sacramento', 'atlanta', 'kansascity',
            'omaha', 'raleigh', 'miami', 'longbeach', 'virginiabeach', 'oakland',
            'minneapolis', 'tampa', 'tulsa', 'arlington', 'neworleans', 'wichita'
        ]
    },
    "CA": {
        "name": "Canada",
        "tlds": [".ca", ".com"],
        "cdx_pattern": "*.ca/*",
        "cities": [
            'toronto', 'montreal', 'vancouver', 'calgary', 'edmonton', 'ottawa',
            'winnipeg', 'quebec', 'hamilton', 'kitchener', 'london', 'victoria',
            'halifax', 'oshawa', 'windsor', 'saskatoon', 'regina', 'barrie'
        ]
    },
    "AU": {
        "name": "Australia",
        "tlds": [".com.au", ".net.au", ".au"],
        "cdx_pattern": "*.com.au/*",
        "cities": [
            'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'goldcoast',
            'newcastle', 'canberra', 'sunshinecoast', 'wollongong', 'geelong',
            'hobart', 'townsville', 'cairns', 'darwin', 'toowoomba', 'ballarat'
        ]
    },
    "DE": {
        "name": "Germany",
        "tlds": [".de"],
        "cdx_pattern": "*.de/*",
        "cities": [
            'berlin', 'hamburg', 'munich', 'cologne', 'frankfurt', 'stuttgart',
            'dusseldorf', 'leipzig', 'dortmund', 'essen', 'bremen', 'dresden',
            'hanover', 'nuremberg', 'duisburg', 'bochum', 'wuppertal', 'bonn'
        ]
    },
    "FR": {
        "name": "France",
        "tlds": [".fr"],
        "cdx_pattern": "*.fr/*",
        "cities": [
            'paris', 'marseille', 'lyon', 'toulouse', 'nice', 'nantes',
            'montpellier', 'strasbourg', 'bordeaux', 'lille', 'rennes', 'reims',
            'saintetienne', 'toulon', 'lehavre', 'grenoble', 'dijon', 'angers'
        ]
    },
    "ALL": {
        "name": "Global / All",
        "tlds": [".com", ".co.uk", ".org", ".net", ".ca", ".com.au"],
        "cdx_pattern": "*.com/*",
        "cities": [
            'london', 'newyork', 'toronto', 'sydney', 'losangeles', 'chicago',
            'manchester', 'melbourne', 'vancouver', 'berlin', 'paris', 'birmingham'
        ]
    }
}

INDUSTRY_SERVICES = [
    'plumbing', 'roofing', 'electrical', 'accountants', 'solicitors', 'legal',
    'dental', 'clinic', 'estates', 'properties', 'construction', 'builders',
    'cleaning', 'logistics', 'transport', 'design', 'marketing', 'digital',
    'consulting', 'recruitment', 'caterers', 'auto', 'garage', 'security',
    'finance', 'vet', 'tech', 'solutions', 'services', 'group', 'direct',
    'media', 'studios', 'hvac', 'glazing', 'interiors', 'renovations',
    'scaffolding', 'surveyors', 'mortgages', 'printing', 'web', 'it',
    'fitness', 'events', 'weddings', 'photography', 'care', 'nursing',
    'taxis', 'removals', 'pestcontrol', 'doubleglazing', 'locksmith',
    'engineering', 'architecture', 'landscape', 'joinery', 'joiners',
    'plastering', 'groundworks', 'driveways', 'solar', 'energy'
]

INDUSTRY_MODIFIERS = ['', '-services', '-group', '-direct', '247', '-pro', '-hub']


def normalize_country_code(country: Optional[str]) -> str:
    """Normalizes country input strings to standard ISO 2-letter codes or ALL."""
    if not country:
        return "UK"
    raw = country.strip().upper()
    mapping = {
        "UNITED KINGDOM": "UK",
        "GB": "UK",
        "GREAT BRITAIN": "UK",
        "ENGLAND": "UK",
        "SCOTLAND": "UK",
        "WALES": "UK",
        "UNITED STATES": "US",
        "USA": "US",
        "AMERICA": "US",
        "CANADA": "CA",
        "AUSTRALIA": "AU",
        "GERMANY": "DE",
        "DEUTSCHLAND": "DE",
        "FRANCE": "FR",
        "GLOBAL": "ALL",
        "WORLD": "ALL",
        "ANY": "ALL",
        "ALL": "ALL",
    }
    return mapping.get(raw, raw if raw in COUNTRY_CONFIGS else "UK")


def _generate_geo_domains(country_code: str = "UK", location: Optional[str] = None) -> List[str]:
    """
    Generates high-yield domain patterns tailored for a country and optional specific place/city.
    When location is specified (e.g. 'Manchester', 'Miami', 'Bristol'), 100% of generated domains
    focus specifically on that place.
    """
    cfg = COUNTRY_CONFIGS.get(country_code, COUNTRY_CONFIGS["UK"])
    tlds = cfg["tlds"]

    generated = []

    if location and location.strip():
        # Clean place name for domain formation
        loc_raw = location.strip().lower()
        loc_clean = re.sub(r'[^a-zA-Z0-9]', '', loc_raw)
        loc_hyphen = re.sub(r'[^a-zA-Z0-9]+', '-', loc_raw).strip('-')

        places_to_use = [loc_hyphen]
        if loc_clean != loc_hyphen:
            places_to_use.append(loc_clean)

        for p in places_to_use:
            for s in INDUSTRY_SERVICES:
                for m in INDUSTRY_MODIFIERS:
                    for tld in tlds:
                        generated.append(f"{p}-{s}{m}{tld}")
                        generated.append(f"{p}{s}{m}{tld}")
                        generated.append(f"{s}-{p}{m}{tld}")
                        generated.append(f"{s}in{p}{m}{tld}")
    else:
        # Sample across country's major hubs
        cities = cfg["cities"]
        for c in cities:
            for s in INDUSTRY_SERVICES:
                for m in INDUSTRY_MODIFIERS[:3]:
                    for tld in tlds[:2]:
                        generated.append(f"{c}-{s}{m}{tld}")
                        generated.append(f"{c}{s}{m}{tld}")

    return generated


def _generate_synthetic_uk_domains() -> List[str]:
    """Backwards compatibility helper."""
    return _generate_geo_domains("UK", None)



import socket

def _is_domain_resolvable(domain: str) -> bool:
    """Pre-checks that a domain has an active DNS record before scraping."""
    try:
        # Quick socket check with 1.0s timeout
        socket.gethostbyname(domain)
        return True
    except Exception:
        return False

def filter_live_domains(candidates: List[str], max_needed: int) -> List[str]:
    """Parallel DNS resolution to ensure live domains, with graceful fallback if DNS is throttled or offline."""
    valid_domains = []
    seen = set()
    unique_candidates = [d for d in candidates if not (d in seen or seen.add(d))]

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        future_map = {pool.submit(_is_domain_resolvable, d): d for d in unique_candidates[:max_needed * 4]}
        for fut in concurrent.futures.as_completed(future_map):
            dom = future_map[fut]
            try:
                if fut.result():
                    valid_domains.append(dom)
                    if len(valid_domains) >= max_needed:
                        break
            except Exception:
                continue

    # Graceful fallback: If DNS resolution yielded fewer than needed (e.g. throttled network),
    # supply candidates directly so crawling can still proceed
    if len(valid_domains) < max_needed:
        for d in unique_candidates:
            if d not in valid_domains:
                valid_domains.append(d)
                if len(valid_domains) >= max_needed:
                    break

    return valid_domains

def _apply_cdx_patch():
    """Patches cdx_toolkit & requests to gracefully handle malformed JSON lines, non-200 responses, and enforce stable HTTP timeouts."""
    try:
        import cdx_toolkit
        import cdx_toolkit.myrequests
        import requests
        from cdx_toolkit import CaptureObject

        if getattr(cdx_toolkit, '_safe_patch_applied', False):
            return

        # 1. Enforce realistic 15s HTTP timeout on requests Sessions so CDX doesn't prematurely abort
        orig_session_send = requests.Session.send
        def safe_session_send(self, request, **kwargs):
            if kwargs.get('timeout') is None or kwargs.get('timeout') == (30.0, 30.0):
                kwargs['timeout'] = (5.0, 15.0)
            return orig_session_send(self, request, **kwargs)
        requests.Session.send = safe_session_send

        # 2. Fast Network Error Retry Patch
        orig_myrequests_get = cdx_toolkit.myrequests.myrequests_get
        def safe_myrequests_get(url, **kwargs):
            kwargs['raise_error_after_n_errors'] = 2
            kwargs['retry_max_sec'] = 3
            kwargs.pop('timeout', None)
            return orig_myrequests_get(url, **kwargs)

        cdx_toolkit.myrequests.myrequests_get = safe_myrequests_get
        if hasattr(cdx_toolkit, 'myrequests_get'):
            cdx_toolkit.myrequests_get = safe_myrequests_get

        # 3. JSON Stream Line & Non-200 Response Patch
        orig_cdx_to_captures = cdx_toolkit.cdx_to_captures
        def safe_cdx_to_captures(resp, wb=None, warc_download_prefix=None):
            if getattr(resp, 'status_code', 200) != 200:
                return []

            text = getattr(resp, 'text', '')
            if text.startswith('{'):
                lines = text.splitlines()
                ret = []
                for line in lines:
                    try:
                        ret.append(CaptureObject(json.loads(line), wb=wb, warc_download_prefix=warc_download_prefix))
                    except Exception:
                        continue
                return ret

            try:
                return orig_cdx_to_captures(resp, wb=wb, warc_download_prefix=warc_download_prefix)
            except Exception:
                return []

        cdx_toolkit.cdx_to_captures = safe_cdx_to_captures
        cdx_toolkit._safe_patch_applied = True
    except Exception as patch_err:
        logger.debug(f"Could not patch cdx_toolkit: {patch_err}")

# Apply safety patch on module import
_apply_cdx_patch()


import concurrent.futures

def _fetch_cdx_records(
    target_new_domains: int,
    records_to_skip: int,
    known_domains: Set[str],
    cdx_pattern: str = "*.co.uk/*",
    location_filter: Optional[str] = None
) -> tuple[Set[str], int]:
    """Helper to query CDX API safely inside a worker thread with optional pattern and location filtering."""
    _apply_cdx_patch()
    import cdx_toolkit

    cdx = cdx_toolkit.CDXFetcher(source='cc')
    results = cdx.iter(cdx_pattern, filter=['=status:200', '=mime:text/html'])
    results_iter = iter(results)

    lines_per_page = getattr(cdx_toolkit, 'lines_per_page', 3000)
    start_page = records_to_skip // lines_per_page
    current_record_index = 0

    if start_page > 0 and hasattr(results_iter, 'page'):
        results_iter.page = start_page - 1
        results_iter.captures = []
        current_record_index = start_page * lines_per_page

    discovered = set()
    consecutive_errors = 0
    max_consecutive_errors = 10
    loc_clean = re.sub(r'[^a-zA-Z0-9]', '', location_filter.lower()) if location_filter else None

    while len(discovered) < target_new_domains and consecutive_errors < max_consecutive_errors:
        current_record_index += 1
        try:
            obj = next(results_iter)
            consecutive_errors = 0
        except StopIteration:
            break
        except Exception as item_err:
            consecutive_errors += 1
            logger.debug(f"Skipping malformed CDX item ({consecutive_errors}/{max_consecutive_errors}): {item_err}")
            continue

        if current_record_index <= records_to_skip:
            continue

        try:
            url = obj.data.get('url') if hasattr(obj, 'data') and isinstance(obj.data, dict) else None
            if url:
                domain = urlparse(url).netloc
                if domain.startswith('www.'):
                    domain = domain[4:]

                if loc_clean and loc_clean not in domain.lower():
                    # If user requested a specific place, prioritize domains matching that location
                    continue

                if domain and domain not in known_domains and domain not in discovered:
                    discovered.add(domain)
                    print(f"  [+] Discovered new target from CDX: {domain}")
                    if len(discovered) >= target_new_domains:
                        break
        except Exception as item_parse_err:
            logger.debug(f"Skipping malformed CDX domain item: {item_parse_err}")
            continue

    return discovered, current_record_index


def discover_domains(
    target_new_domains: int = 20,
    country: Optional[str] = "UK",
    location: Optional[str] = None,
    known_domains: Optional[Set[str]] = None,
    records_to_skip: Optional[int] = None
) -> tuple[List[str], int]:
    """
    Discovers new business domains targeted by country and optional place/city.
    - If location is provided (e.g. 'Manchester', 'Miami', 'Bristol'), prioritizes businesses in that location.
    - If country is provided (e.g. 'UK', 'US', 'CA', 'AU', 'DE', 'FR', 'ALL'), targets appropriate TLDs and business pools.
    - Leverages CDX API, curated datasets, and active DNS resolution for high yield and real-time streaming.
    """
    if records_to_skip is None:
        records_to_skip = _load_resume_index()
    if known_domains is None:
        known_domains = _load_known_domains()

    country_code = normalize_country_code(country)
    cfg = COUNTRY_CONFIGS.get(country_code, COUNTRY_CONFIGS["UK"])
    cdx_pattern = cfg.get("cdx_pattern", "*.co.uk/*")

    new_domains = set()
    current_record_index = records_to_skip

    loc_desc = f" in {location}" if location else ""
    print(f"\n📚 Resuming discovery for {cfg['name']}{loc_desc}... Fast-forwarding past {records_to_skip} old records.")

    # 1. Attempt quick CDX API Discovery inside ThreadPoolExecutor with 4s timeout
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(
            _fetch_cdx_records,
            target_new_domains,
            records_to_skip,
            known_domains,
            cdx_pattern,
            location
        )
        cdx_discovered, cdx_last_index = future.result(timeout=4.0)
        for dom in cdx_discovered:
            if dom not in known_domains and dom not in new_domains:
                new_domains.add(dom)
                if len(new_domains) >= target_new_domains:
                    break
        if cdx_last_index > records_to_skip:
            current_record_index = cdx_last_index
    except Exception as e:
        logger.warning(f"CDX API Note ({e}). Proceeding to high-yield geo domain generator.")
        if records_to_skip > 50000:
            current_record_index = 0
    finally:
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass

    # 2. Location-specific or Country-specific targeted domain generation
    if len(new_domains) < target_new_domains:
        needed = target_new_domains - len(new_domains)
        candidates = _generate_geo_domains(country_code, location)
        untested_candidates = [d for d in candidates if d not in known_domains and d not in new_domains]

        if untested_candidates:
            # Validate via parallel DNS resolution
            live = filter_live_domains(untested_candidates, max_needed=needed)
            for dom in live:
                new_domains.add(dom)
                if len(new_domains) >= target_new_domains:
                    break

    # 3. For UK with no specific location, fallback to curated UK list
    if len(new_domains) < target_new_domains and country_code == "UK" and not location:
        csv_domains = _load_csv_fallback_domains()
        if csv_domains:
            for fallback in csv_domains:
                clean_dom = fallback[4:] if fallback.startswith('www.') else fallback
                if clean_dom and clean_dom not in known_domains and clean_dom not in new_domains:
                    new_domains.add(clean_dom)
                    if len(new_domains) >= target_new_domains:
                        break

        if len(new_domains) < target_new_domains:
            for fallback in FALLBACK_UK_DOMAINS:
                clean_dom = fallback[4:] if fallback.startswith('www.') else fallback
                if clean_dom and clean_dom not in known_domains and clean_dom not in new_domains:
                    new_domains.add(clean_dom)
                    if len(new_domains) >= target_new_domains:
                        break

    print(f"✅ Discovery complete: Yielded {len(new_domains)} domains for {country_code}{loc_desc} out of {target_new_domains} requested.")

    # Save local state fallback
    _save_resume_index(current_record_index)
    _save_known_domains(new_domains)

    return list(new_domains), current_record_index


def discover_uk_domains(
    target_new_domains: int = 20,
    known_domains: Optional[Set[str]] = None,
    records_to_skip: Optional[int] = None
) -> tuple[List[str], int]:
    """Backwards-compatible wrapper for discover_domains targeting UK."""
    return discover_domains(
        target_new_domains=target_new_domains,
        country="UK",
        location=None,
        known_domains=known_domains,
        records_to_skip=records_to_skip
    )