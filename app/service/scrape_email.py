import asyncio
import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, Dict, List, Optional, Any

# --- CONFIGURATION ---
MAX_PAGES_PER_DOMAIN = 4
HIGH_VALUE_PATHS = ['contact', 'about', 'team', 'support', 'reach', 'hello']

from app.service.website_classifier import classify_website

class AdvancedDomainScraper:
    def __init__(self, base_url: str, preferred_category: Optional[str] = None):
        self.base_url = base_url if base_url.startswith('http') else f"http://{base_url}"
        # We clean the base netloc immediately to handle the 'www.' trap
        self.domain_netloc = self._clean_netloc(urlparse(self.base_url).netloc)
        self.preferred_category = preferred_category
        self.visited_urls = set()
        self.found_emails = set()
        self.crawled_html = []
        self.category = "GENERAL"
        self.subcategory = None
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

    def _clean_netloc(self, netloc: str) -> str:
        """Removes 'www.' so we don't fail when comparing subdomains."""
        return netloc[4:] if netloc.startswith('www.') else netloc

    def _is_internal_link(self, url: str) -> bool:
        """Safely checks if a URL belongs to the same core domain."""
        link_netloc = self._clean_netloc(urlparse(url).netloc)
        return link_netloc == self.domain_netloc

    def _prioritize_links(self, links: Set[str]) -> List[str]:
        """Sorts links so /contact and /about are crawled first."""
        def score_link(link: str) -> int:
            link_lower = link.lower()
            return sum(1 for keyword in HIGH_VALUE_PATHS if keyword in link_lower)
        return sorted(list(links), key=score_link, reverse=True)

    async def _extract_data(self, html_text: str, base_url_for_links: str) -> Set[str]:
        """Extracts emails and internal links from a single page, collecting page text for classification."""
        if len(self.crawled_html) < 3:
            self.crawled_html.append(html_text)

        soup = BeautifulSoup(html_text, 'html.parser')

        # 1. Extract Emails via Regex
        page_text = soup.get_text(separator=' ')
        for candidate in self.email_pattern.findall(page_text):
            cand_clean = candidate.strip().rstrip('.,;:!?')
            cand_lower = cand_clean.lower()
            if not any(cand_lower.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.css', '.js')):
                self.found_emails.add(cand_clean)

        # 2. Extract Emails via mailto: links
        for link in soup.select('a[href^="mailto:"]'):
            href = link.get('href')
            if href:
                email = href.replace('mailto:', '').split('?')[0].strip().rstrip('.,;:!?')
                if email and '@' in email:
                    email_lower = email.lower()
                    if not any(email_lower.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.css', '.js')):
                        self.found_emails.add(email)

        # 3. Extract Internal Links safely using the final resolved URL
        internal_links = set()
        for link in soup.find_all('a', href=True):
            href = link.get('href').strip()
            if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                continue

            # Stitch the link together using the actual resolved URL
            full_url = urljoin(base_url_for_links, href).split('#')[0]

            if self._is_internal_link(full_url) and full_url not in self.visited_urls:
                internal_links.add(full_url)

        return internal_links

    async def run(self) -> Set[str]:
        """Executes the targeted deep crawl for the domain and classifies its industry."""
        pages_to_visit = [self.base_url]
        pages_crawled = 0
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
            while pages_to_visit and pages_crawled < MAX_PAGES_PER_DOMAIN:
                current_url = pages_to_visit.pop(0)

                if current_url in self.visited_urls:
                    continue

                self.visited_urls.add(current_url)
                pages_crawled += 1

                try:
                    response = await client.get(current_url)
                    response.raise_for_status()

                    if 'text/html' not in response.headers.get('Content-Type', ''):
                        continue

                    # Pass str(response.url) instead of current_url so relative links don't break after a redirect
                    new_links = await self._extract_data(response.text, str(response.url))

                    pages_to_visit.extend(new_links)
                    pages_to_visit = self._prioritize_links(set(pages_to_visit))

                except Exception as e:
                    print(f"  [!] Skipped {current_url} | Error: {type(e).__name__}")

        # Classify website based on crawled content
        try:
            combined_html = " ".join(self.crawled_html)
            cat, subcat = classify_website(
                html_text=combined_html,
                domain_url=self.domain_netloc,
                preferred_category=self.preferred_category
            )
            self.category = cat
            self.subcategory = subcat
        except Exception as class_err:
            print(f"  [!] Classification error for {self.domain_netloc}: {class_err}")
            self.category = "GENERAL"
            self.subcategory = None

        return self.found_emails

# --- ORCHESTRATOR ---
async def process_domain_task(domain: str, semaphore: asyncio.Semaphore, preferred_category: Optional[str] = None) -> Dict:
    async with semaphore:
        scraper = AdvancedDomainScraper(domain, preferred_category=preferred_category)
        emails = await scraper.run()

        return {
            "domain": str(domain),
            "emails": list(emails),
            "category": scraper.category,
            "subcategory": scraper.subcategory,
            "pages_scanned": len(scraper.visited_urls),
            "status": "success" if emails else "no_emails_found"
        }


async def scrape_email(request) -> Dict:
    """
    Main scrape email function that handles requests from API

    Args:
        request: Request object with urls to scrape

    Returns:
        Dictionary with scraping results
    """
    try:
        if hasattr(request, 'urls'):
            # Handle BulkScrapeRequest
            domains = [str(url) for url in request.urls]
        else:
            # Handle single URL if passed differently
            domains = [str(request)]

        # Scrape each domain with concurrency control
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent scrapes
        tasks = [process_domain_task(domain, semaphore) for domain in domains]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if r['status'] == 'success')

        return {
            "total_processed": len(results),
            "successful_leads": successful,
            "results": results
        }
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return {
            "total_processed": 0,
            "successful_leads": 0,
            "results": [],
            "error": str(e)
        }


async def scrape_email_to_db(
    email_limit: int,
    domain_limit: int,
    category: str,
    db = None
) -> Dict:
    """
    Fetch UK domains, scrape emails from them, and save to database with email limit

    Args:
        email_limit: Maximum number of emails to collect before stopping
        domain_limit: Maximum number of domains to scrape (1-10000)
        category: Category for saved emails (WEB, MARKETING, GENERAL)
        db: Database session

    Returns:
        Dictionary with scraping and saving results
    """
    from app.service.email_service import save_extracted_emails
    from app.model.emails import Category as EmailCategory
    from app.service.uk_domain_service import discover_uk_domains

    try:
        # Convert category string to enum
        try:
            category_enum = EmailCategory[category.lower()]
        except KeyError:
            category_enum = EmailCategory.web

        # Validate domain_limit
        domain_limit = max(1, min(domain_limit, 10000))

        results = []
        total_emails_found = 0
        total_emails_saved = 0
        duplicates_skipped = 0
        errors = 0
        domains_scraped = 0

        print(f"🔍 Fetching up to {domain_limit} UK domains from CDX...")
        uk_domains = discover_uk_domains(target_new_domains=domain_limit)

        if not uk_domains:
            return {
                "total_processed": 0,
                "successful_leads": 0,
                "total_emails_found": 0,
                "total_emails_saved": 0,
                "duplicates_skipped": 0,
                "errors": 1,
                "results": [],
                "error": "No UK domains found from CDX API"
            }

        print(f"✅ Found {len(uk_domains)} UK domains to scrape")

        # Scrape each domain with limit check
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent scrapes

        preferred_cat = category.upper() if category and category.upper() not in ("AUTO", "ALL", "WEB", "GENERAL") else None

        for domain_url in uk_domains:
            # Check if we've reached the email limit
            if total_emails_found >= email_limit:
                print(f"Reached email limit of {email_limit}. Stopping scraping.")
                break

            try:
                async with semaphore:
                    # Scrape and categorize the domain
                    scraper = AdvancedDomainScraper(domain_url, preferred_category=preferred_cat)
                    emails = await scraper.run()
                    domains_scraped += 1

                    # Check if scraping this domain would exceed limit
                    emails_from_domain = len(emails)
                    total_emails_found += emails_from_domain

                    # If emails exceed limit, trim them
                    if total_emails_found > email_limit:
                        excess = total_emails_found - email_limit
                        emails = list(emails)[:-excess] if excess < len(emails) else set()
                        total_emails_found = email_limit

                    cat_to_save = preferred_cat if preferred_cat else scraper.category

                    # Save emails to database with category, subcategory and domain
                    if emails:
                        save_result = await save_extracted_emails(
                            emails=emails,
                            category=cat_to_save,
                            db=db,
                            subcategory=scraper.subcategory,
                            domain=scraper.domain_netloc
                        )
                        total_emails_saved += save_result['saved']
                        duplicates_skipped += save_result['duplicates']
                        errors += save_result['failed']

                    # Add to results with rich classification metadata
                    results.append({
                        "domain": str(domain_url),
                        "emails": list(emails),
                        "category": cat_to_save,
                        "subcategory": scraper.subcategory,
                        "pages_scanned": len(scraper.visited_urls),
                        "status": "success" if emails else "no_emails_found"
                    })

            except Exception as e:
                errors += 1
                results.append({
                    "domain": str(domain_url),
                    "emails": [],
                    "pages_scanned": 0,
                    "status": "error",
                    "error": str(e)
                })

        return {
            "total_processed": domains_scraped,
            "successful_leads": sum(1 for r in results if r['status'] == 'success'),
            "total_emails_found": total_emails_found,
            "total_emails_saved": total_emails_saved,
            "duplicates_skipped": duplicates_skipped,
            "errors": errors,
            "results": results
        }

    except Exception as e:
        print(f"Error during scrape to DB: {str(e)}")
        return {
            "total_processed": 0,
            "successful_leads": 0,
            "total_emails_found": 0,
            "total_emails_saved": 0,
            "duplicates_skipped": 0,
            "errors": 1,
            "results": [],
            "error": str(e)
        }
