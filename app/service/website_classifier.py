"""
Website Classifier Service
Analyzes scraped website content (HTML, title, meta description, headings, domain name, text)
and accurately categorizes it into targeted business categories and subcategories.
"""

import re
from typing import Tuple, Optional, Dict, List
from bs4 import BeautifulSoup


# Category Taxonomy & Subcategory Keywords
CATEGORY_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "LOCAL_SERVICES": {
        "Barbershops": [
            "barbershop", "barber shop", "barber", "haircut", "beard trim", "fade",
            "shave", "hot towel", "mens grooming", "gentlemans barber"
        ],
        "Hair salons": [
            "hair salon", "hairdresser", "hairdressing", "hair stylist", "balayage",
            "hair extensions", "blowdry", "hair colouring", "highlights", "hair cuts"
        ],
        "Nail technicians": [
            "nail salon", "nail tech", "manicure", "pedicure", "acrylic nails",
            "gel nails", "nail art", "shellac", "biab nails", "nail bar"
        ],
        "Makeup artists": [
            "makeup artist", "mua", "bridal makeup", "make up artist", "glam makeup",
            "wedding makeup", "occasion makeup", "cosmetics artist"
        ],
        "Tattoo studios": [
            "tattoo studio", "tattoo artist", "tattoo parlour", "ink studio",
            "body piercing", "custom tattoo", "tattooing", "body art"
        ],
        "Massage therapists": [
            "massage therapist", "massage therapy", "deep tissue massage", "sports massage",
            "swedish massage", "holistic massage", "masseuse", "masseur", "body massage"
        ],
        "Skincare clinics": [
            "skincare clinic", "skin clinic", "facial aesthetics", "dermatology",
            "botox", "chemical peel", "microdermabrasion", "laser clinic", "anti-aging", "facials"
        ],
        "Mobile beauticians": [
            "mobile beautician", "mobile beauty", "beauty therapist", "lash extensions",
            "waxing", "eyebrow threading", "mobile lashes", "beauty treatments"
        ],
        "Private tutors": [
            "private tutor", "tuition centre", "maths tutor", "english tutor",
            "gcse tutor", "a-level tutor", "tutoring services", "home tuition", "11 plus"
        ],
        "Driving instructors": [
            "driving instructor", "driving school", "driving lessons", "pass plus",
            "automatic driving lessons", "manual driving", "adi instructor", "learn to drive"
        ],
        "Cleaning companies": [
            "commercial cleaning", "office cleaning", "cleaning company", "cleaning services",
            "contract cleaners", "deep cleaning", "end of tenancy cleaning", "commercial cleaners"
        ],
        "Domestic cleaners": [
            "domestic cleaning", "house cleaner", "home cleaning", "residential cleaners",
            "maid service", "domestic cleaner", "carpet cleaning"
        ],
        "Car wash services": [
            "car wash", "hand car wash", "valeting", "valet service", "car valet", "auto wash"
        ],
        "Mobile car detailers": [
            "car detailing", "mobile detailing", "ceramic coating", "paint correction",
            "auto detailer", "car polish", "vehicle detailing"
        ],
        "Auto repair garages": [
            "car repair", "auto repair", "mot test", "vehicle service", "brake repair",
            "clutch replacement", "mechanic", "garage services", "auto centre", "car diagnostics"
        ],
        "Tyre shops": [
            "tyre shop", "tyres", "mobile tyre fitting", "wheel alignment",
            "puncture repair", "part worn tyres", "tyre replacement", "new tyres"
        ],
        "Electricians": [
            "electrician", "electrical services", "rewiring", "fuse box",
            "electrical installation", "emergency electrician", "lighting installation", "napit", "niceic"
        ],
        "Plumbers": [
            "plumber", "plumbing services", "boiler repair", "emergency plumber",
            "blocked drains", "central heating", "gas safe", "leak repair", "bathroom plumbing"
        ],
        "Painters and decorators": [
            "painter and decorator", "painting and decorating", "interior painter",
            "exterior painting", "wallpapering", "commercial painting", "decorating services"
        ],
        "Handymen": [
            "handyman", "handyman services", "home repairs", "flat pack assembly",
            "odd jobs", "property maintenance", "general repairs"
        ],
        "Builders": [
            "builder", "building contractors", "home extension", "loft conversion",
            "bricklayer", "renovation contractor", "construction services", "house builders"
        ],
        "Tilers": [
            "tiler", "tiling services", "wall tiling", "floor tiling",
            "bathroom tiler", "kitchen tiler", "ceramic tiling", "porcelain tiles"
        ],
        "Kitchen fitters": [
            "kitchen fitter", "kitchen installation", "fitted kitchens",
            "kitchen renovation", "worktop installation", "bespoke kitchens"
        ],
        "Locksmiths": [
            "locksmith", "emergency locksmith", "lock replacement", "upvc door locks",
            "24 hour locksmith", "lock out", "key cutting", "master locksmith"
        ],
        "Pest control services": [
            "pest control", "rodent control", "wasp nest removal", "bed bug treatment",
            "fumigation", "pest eradication", "rat exterminator", "pest management"
        ],
        "Gardeners": [
            "gardener", "gardening services", "lawn mowing", "hedge trimming",
            "garden maintenance", "pruning", "lawn care", "garden clearance"
        ],
        "Landscaping services": [
            "landscaping", "landscape gardener", "paving", "patio installation",
            "decking", "turfing", "artificial grass", "driveways", "fencing"
        ],
        "Waste removal companies": [
            "waste removal", "rubbish clearance", "house clearance", "junk removal",
            "waste disposal", "skip hire", "man and van clearance", "waste management"
        ],
    },
    "HEALTH_CARE": {
        "Care agencies": [
            "care agency", "care recruitment", "nursing agency", "healthcare staffing",
            "cqc registered", "care workers", "healthcare assistants", "carers recruitment"
        ],
        "Supported living providers": [
            "supported living", "supported accommodation", "learning disabilities support",
            "mental health support living", "assisted living", "semi-independent living"
        ],
        "Domiciliary care startups": [
            "domiciliary care", "home care", "homecare services", "visiting care",
            "live-in care", "elderly home care", "care in your home", "personal care at home"
        ],
        "Childcare services": [
            "childcare services", "childminder", "after school care", "babysitting agency",
            "nanny agency", "creche", "child care provider"
        ],
        "Private day nurseries": [
            "day nursery", "private nursery", "early years education", "preschool",
            "kindergarten", "nursery school", "ofsted registered nursery", "toddler care"
        ],
        "Therapy services": [
            "therapy services", "psychotherapy", "cbt therapy", "occupational therapy",
            "speech and language therapy", "mental health clinic", "clinical psychology"
        ],
        "Counsellors": [
            "counsellor", "counselling", "relationship counselling", "bereavement counselling",
            "psychotherapist", "bacp registered", "talking therapies", "family counselling"
        ],
        "Home physio services": [
            "home physiotherapy", "physiotherapist", "mobile physio", "stroke rehabilitation",
            "mobility physio", "rehab at home", "physiotherapy clinic", "musculoskeletal"
        ],
        "Private support workers": [
            "private support worker", "personal assistant care", "support worker",
            "respite care", "carer services", "autism support", "disability care"
        ],
    },
    "FOOD_HOSPITALITY": {
        "Takeaway restaurants": [
            "takeaway", "fast food", "order online", "delivery takeaway", "pizza takeaway",
            "fish and chips", "chinese takeaway", "indian takeaway", "kebab shop", "burger takeaway"
        ],
        "African food vendors": [
            "african food", "nigerian cuisine", "jollof rice", "african kitchen",
            "ghanaian food", "african grocery", "suya", "african restaurant", "afro-caribbean"
        ],
        "Catering businesses": [
            "catering", "caterers", "wedding catering", "corporate catering",
            "buffet catering", "event catering", "party food catering", "outside catering"
        ],
        "Food trucks": [
            "food truck", "street food", "mobile catering unit", "food trailer",
            "pop up food", "street food vendor"
        ],
        "Home based bakers": [
            "home baker", "custom cakes", "birthday cakes", "wedding cakes",
            "cupcakes", "baked goods", "artisan baker", "cake decorator", "patisserie"
        ],
        "Event cooks": [
            "event cook", "private chef", "personal chef", "dinner party chef",
            "hire a chef", "bespoke dining", "in-home dining"
        ],
        "Small cafés": [
            "cafe", "café", "coffee shop", "espresso bar", "tea room",
            "breakfast cafe", "brunch spot", "artisan coffee", "speciality coffee"
        ],
        "Local lounges": [
            "lounge bar", "cocktail lounge", "shisha lounge", "wine bar",
            "tapas lounge", "social lounge", "cocktail bar"
        ],
        "Meal prep businesses": [
            "meal prep", "healthy meals delivery", "prep kitchen", "diet meal delivery",
            "weekly meal plans", "fitness meals", "macro meals"
        ],
    },
    "PROFESSIONAL_SERVICES": {
        "Travel agents": [
            "travel agent", "travel agency", "holiday booking", "luxury travel",
            "flight booking", "package holidays", "abta", "atol", "honeymoon travel"
        ],
        "Property sourcing agents": [
            "property sourcing", "property deal packaging", "property investor",
            "bmv property", "property deal sourcer", "property consultant", "buy to let deals"
        ],
        "Accountancy": [
            "chartered accountant", "bookkeeping", "payroll services", "tax return",
            "vat return", "accounting firm", "accountants", "auditing"
        ],
        "Legal & Solicitors": [
            "solicitor", "solicitors", "law firm", "legal services", "conveyancing",
            "probate", "family law", "commercial law", "lawyers"
        ],
        "Estate & Lettings": [
            "estate agent", "letting agent", "property management", "houses for sale",
            "flats to rent", "commercial property agent", "lettings"
        ],
        "Consulting & Business": [
            "business consultant", "management consultancy", "recruitment agency",
            "staffing agency", "financial advisor", "wealth management", "insurance broker"
        ],
    }
}


def classify_website(
    html_text: str = "",
    domain_url: str = "",
    soup: Optional[BeautifulSoup] = None,
    preferred_category: Optional[str] = None
) -> Tuple[str, Optional[str]]:
    """
    Classifies a website based on its content, metadata, and domain name into
    one of the target categories and detects its specific subcategory.

    Args:
        html_text: Raw HTML string of crawled page(s)
        domain_url: Domain URL or host
        soup: Optional pre-parsed BeautifulSoup instance
        preferred_category: Optional category passed in request (e.g. "HEALTH_CARE").
                           If provided and valid, bias towards finding best subcategory within it.

    Returns:
        Tuple[str, Optional[str]]: (category, subcategory)
        e.g. ("HEALTH_CARE", "Care agencies")
    """
    if soup is None and html_text:
        try:
            soup = BeautifulSoup(html_text[:50000], 'html.parser')
        except Exception:
            soup = None

    # 1. Extract high-signal textual components
    title_text = ""
    meta_desc = ""
    meta_keywords = ""
    headings_text = ""
    body_sample = ""

    if soup:
        # Title tag
        if soup.title and soup.title.string:
            title_text = soup.title.string.strip()

        # Meta tags
        meta_desc_tag = soup.find('meta', attrs={'name': re.compile(r'description', re.I)}) or \
                        soup.find('meta', attrs={'property': re.compile(r'og:description', re.I)})
        if meta_desc_tag and meta_desc_tag.get('content'):
            meta_desc = str(meta_desc_tag.get('content')).strip()

        meta_key_tag = soup.find('meta', attrs={'name': re.compile(r'keywords', re.I)})
        if meta_key_tag and meta_key_tag.get('content'):
            meta_keywords = str(meta_key_tag.get('content')).strip()

        # Headings (H1, H2)
        headings = [h.get_text(separator=' ', strip=True) for h in soup.find_all(['h1', 'h2'])[:8]]
        headings_text = " ".join(headings)

        # Body text sample
        body_sample = soup.get_text(separator=' ', strip=True)[:5000]
    elif html_text:
        body_sample = html_text[:5000]

    # Clean domain string
    clean_domain = domain_url.lower()
    for prefix in ("http://", "https://", "www."):
        if clean_domain.startswith(prefix):
            clean_domain = clean_domain[len(prefix):]
    clean_domain = clean_domain.split('/')[0]

    # Combined text for analysis (with weighted components)
    text_corpus_lower = f"{clean_domain} {title_text} {title_text} {meta_desc} {meta_keywords} {headings_text} {body_sample}".lower()

    # 2. Score across categories and subcategories
    category_scores: Dict[str, float] = {cat: 0.0 for cat in CATEGORY_TAXONOMY}
    subcategory_scores: Dict[str, Dict[str, float]] = {cat: {} for cat in CATEGORY_TAXONOMY}

    for cat_name, subcats in CATEGORY_TAXONOMY.items():
        for subcat_name, kw_list in subcats.items():
            subcat_score = 0.0
            for kw in kw_list:
                kw_lower = kw.lower()
                clean_kw = kw_lower.replace(' ', '')
                if clean_kw in clean_domain:
                    subcat_score += 5.0
                elif any(word in clean_domain for word in kw_lower.split() if len(word) > 3):
                    subcat_score += 2.0

                if kw_lower in title_text.lower():
                    subcat_score += 4.0

                if kw_lower in meta_desc.lower() or kw_lower in meta_keywords.lower():
                    subcat_score += 3.0

                if kw_lower in headings_text.lower():
                    subcat_score += 2.5

                occurrences = text_corpus_lower.count(kw_lower)
                if occurrences > 0:
                    subcat_score += min(occurrences * 1.0, 5.0)

            if subcat_score > 0:
                subcategory_scores[cat_name][subcat_name] = subcat_score
                category_scores[cat_name] += subcat_score

    # 3. If a specific preferred category was explicitly requested by the user
    norm_preferred = (preferred_category or "").upper()
    if norm_preferred in CATEGORY_TAXONOMY:
        cat_subcats = subcategory_scores.get(norm_preferred, {})
        if cat_subcats:
            best_subcat = max(cat_subcats.items(), key=lambda x: x[1])[0]
            return norm_preferred, best_subcat
        return norm_preferred, list(CATEGORY_TAXONOMY[norm_preferred].keys())[0]

    # 4. Find the category with the highest score
    best_cat = None
    best_cat_score = 0.0

    for cat_name, score in category_scores.items():
        if score > best_cat_score:
            best_cat_score = score
            best_cat = cat_name

    # Threshold for confident categorization
    if best_cat and best_cat_score >= 2.0:
        subcats = subcategory_scores[best_cat]
        if subcats:
            best_subcat = max(subcats.items(), key=lambda x: x[1])[0]
        else:
            best_subcat = None
        return best_cat, best_subcat

    # Fallback to GENERAL if no category scores enough
    return "GENERAL", None
