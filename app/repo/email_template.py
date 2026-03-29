from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.model.email_template import EmailTemplate, TemplateType
from typing import List, Optional


async def get_all_templates(db: AsyncSession) -> List[EmailTemplate]:
    """Get all email templates"""
    statement = select(EmailTemplate)
    result = await db.exec(statement)
    return result.all()


async def get_template_by_id(template_id: str, db: AsyncSession) -> Optional[EmailTemplate]:
    """Get email template by ID"""
    statement = select(EmailTemplate).where(EmailTemplate.id == template_id)
    result = await db.exec(statement)
    return result.first()


async def create_template(
    name: str,
    template_type: TemplateType,
    subject: str,
    body: str,
    description: Optional[str],
    db: AsyncSession
) -> EmailTemplate:
    """Create new email template"""
    template = EmailTemplate(
        name=name,
        template_type=template_type,
        subject=subject,
        body=body,
        description=description
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def update_template(
    template_id: str,
    db: AsyncSession,
    **kwargs
) -> Optional[EmailTemplate]:
    """Update email template"""
    template = await get_template_by_id(template_id, db)
    if not template:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(template, key, value)

    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def delete_template(template_id: str, db: AsyncSession) -> bool:
    """Delete email template"""
    template = await get_template_by_id(template_id, db)
    if not template:
        return False

    await db.delete(template)
    await db.commit()
    return True
