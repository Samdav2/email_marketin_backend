import os
import cdx_toolkit
from urllib.parse import urlparse
from typing import List

# --- STATE FILES ---
# These files will be automatically created in your project folder
STATE_FILE = "cdx_resume_state.txt"
KNOWN_DOMAINS_FILE = "known_domains.txt"


def _load_resume_index() -> int:
    """Reads the 'bookmark' so we know how many records to skip."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return int(f.read().strip())
    return 0


def _save_resume_index(index: int):
    """Saves our place in the Common Crawl database."""
    with open(STATE_FILE, 'w') as f:
        f.write(str(index))


def _load_known_domains() -> set:
    """Loads all domains we have ever scraped so we never repeat them."""
    if os.path.exists(KNOWN_DOMAINS_FILE):
        with open(KNOWN_DOMAINS_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()


def _save_known_domains(domains: set):
    """Appends new domains to our permanent list."""
    with open(KNOWN_DOMAINS_FILE, 'a') as f:
        for domain in domains:
            f.write(domain + '\n')


def discover_uk_domains(target_new_domains: int = 20) -> List[str]:
    """
    Resumes from the last known position and fetches N entirely new domains.
    """
    cdx = cdx_toolkit.CDXFetcher(source='cc')

    records_to_skip = _load_resume_index()
    known_domains = _load_known_domains()
    new_domains = set()

    print(f"\n📚 Resuming discovery... Fast-forwarding past {records_to_skip} old records.")

    # Notice we removed the `limit` here because we manage it manually now
    results = cdx.iter("*.uk/*", filter=['=status:200', '=mime:text/html'])

    current_record_index = 0

    try:
        for obj in results:
            current_record_index += 1

            # 1. FAST FORWARD: Skip records we've processed in previous runs
            if current_record_index <= records_to_skip:
                continue

            url = obj.data.get('url')
            if url:
                domain = urlparse(url).netloc
                if domain.startswith('www.'):
                    domain = domain[4:]

                # 2. CHECK DUPLICATES: Make sure we've never scraped it before
                if domain not in known_domains and domain not in new_domains:
                    new_domains.add(domain)
                    print(f"  [+] Discovered new target: {domain}")

                    # 3. STOP CONDITION: Once we find enough NEW domains, stop
                    if len(new_domains) >= target_new_domains:
                        break

    except Exception as e:
        print(f"CDX API Error: {e}")

    finally:
        # 4. SAVE STATE: Always save our place so we don't start over next time!
        total_records_processed = records_to_skip + (current_record_index - records_to_skip)
        _save_resume_index(total_records_processed)
        _save_known_domains(new_domains)

    return list(new_domains)