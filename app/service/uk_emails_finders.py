import asyncio

from app.service.uk_domain_service import discover_uk_domains
from app.service.scrape_email import process_domain_task
from asyncio import Semaphore

async def get_uk_email():
    emails = []
    scraped_domains = discover_uk_domains()
    for domain in scraped_domains:
        emails.append(await process_domain_task(domain, semaphore=Semaphore(100)))

    print(emails)

if __name__ == '__main__':
    asyncio.run(get_uk_email())

