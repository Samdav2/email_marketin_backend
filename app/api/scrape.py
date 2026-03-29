from fastapi import APIRouter, Depends, HTTPException, status
from app.service.scrape_email import scrape_email, scrape_email_to_db
from app.schema.scrape import BulkScrapeRequest, ScrapeToDBRequest, ScrapeToDBResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["scrape_email"], prefix="/scrape")

@router.post("/scrape")
async def scrape(request: BulkScrapeRequest):
    response = await scrape_email(request)
    return response


@router.post("/scrape-to-db", response_model=ScrapeToDBResponse)
async def scrape_to_db(
    request: ScrapeToDBRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Automatically fetch UK domains, scrape emails from them, and save to database

    Args:
        request: ScrapeToDBRequest with email_limit, domain_limit, and category
        db: Database session

    Returns:
        ScrapeToDBResponse with scraping and saving statistics
    """
    try:
        if request.email_limit < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email limit must be at least 1"
            )

        if request.domain_limit < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain limit must be at least 1"
            )

        if request.domain_limit > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain limit cannot exceed 10000"
            )

        # Scrape UK domains and save emails to database
        result = await scrape_email_to_db(
            email_limit=request.email_limit,
            domain_limit=request.domain_limit,
            category=request.category,
            db=db
        )

        logger.info(
            f"Scrape to DB completed: {result['total_emails_saved']} emails saved, "
            f"{result['duplicates_skipped']} duplicates skipped"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during scrape to DB: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during scraping: {str(e)}"
        )
