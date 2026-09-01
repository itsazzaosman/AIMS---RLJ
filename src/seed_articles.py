import sys
import random
from django.utils import timezone

from journal.models import Journal, Issue
from submission.models import Article, Section, Keyword, KeywordArticle, STAGE_PUBLISHED
from core.models import Account

journal = Journal.objects.first()
if not journal:
    print("No journal found.")
    sys.exit(1)

owner = Account.objects.first()

section, _ = Section.objects.get_or_create(journal=journal, name="Articles")
issue, _ = Issue.objects.get_or_create(journal=journal, volume=1, issue=1, defaults={'date': timezone.now().date()})

articles_data = [
    {"title": "The Future of International Arbitration", "keywords": ["Arbitration", "International Law"], "abstract": "An exploration of international arbitration trends."},
    {"title": "Human Rights in the Digital Age", "keywords": ["Human Rights", "Digital Privacy", "Technology"], "abstract": "How technology impacts human rights globally."},
    {"title": "Intellectual Property and AI", "keywords": ["Intellectual Property", "Artificial Intelligence", "Copyright"], "abstract": "Analyzing copyright in AI-generated works."},
    {"title": "Climate Change and Corporate Law", "keywords": ["Corporate Law", "Environment", "Climate Change"], "abstract": "Corporate responsibility towards environmental issues."},
    {"title": "Data Protection Regulations in Africa", "keywords": ["Data Protection", "Privacy", "Africa"], "abstract": "A review of emerging data protection frameworks in Africa."},
    {"title": "The Evolution of Cyber Crime Laws", "keywords": ["Cyber Crime", "Technology", "Criminal Law"], "abstract": "Tracking the development of laws against cyber crime."},
    {"title": "Cross-Border Mergers and Acquisitions", "keywords": ["M&A", "Corporate Law", "Cross-Border"], "abstract": "Legal challenges in cross-border M&A transactions."},
    {"title": "Space Law: The Next Frontier", "keywords": ["Space Law", "International Law", "Technology"], "abstract": "An introduction to the legal frameworks governing outer space."},
    {"title": "The Role of the WTO in Modern Trade", "keywords": ["WTO", "Trade Law", "International Law"], "abstract": "Evaluating the WTO's effectiveness in current global trade disputes."},
    {"title": "Consumer Protection in E-Commerce", "keywords": ["Consumer Protection", "E-Commerce", "Digital Privacy"], "abstract": "Safeguarding consumer rights in online transactions."},
    {"title": "Blockchain and Smart Contracts", "keywords": ["Blockchain", "Smart Contracts", "Technology"], "abstract": "Legal enforceability of smart contracts on the blockchain."},
    {"title": "Feminist Legal Theory in Practice", "keywords": ["Feminist Legal Theory", "Human Rights", "Jurisprudence"], "abstract": "Applying feminist legal theory to contemporary case law."},
    {"title": "The Legality of Humanitarian Intervention", "keywords": ["Humanitarian Intervention", "International Law", "Human Rights"], "abstract": "Debating the legal basis for humanitarian intervention."},
    {"title": "Corporate Governance and Ethics", "keywords": ["Corporate Governance", "Ethics", "Corporate Law"], "abstract": "The intersection of legal duties and ethical practices in corporations."},
    {"title": "Refugee Law and Policy", "keywords": ["Refugee Law", "Human Rights", "International Law"], "abstract": "Analyzing current international refugee law and policies."},
]

print("Seeding articles...")
for data in articles_data:
    article = Article.objects.create(
        journal=journal,
        owner=owner,
        title=data["title"],
        abstract=data["abstract"],
        stage=STAGE_PUBLISHED,
        date_published=timezone.now(),
        section=section
    )
    issue.articles.add(article)
    for i, kw in enumerate(data["keywords"]):
        keyword_obj, _ = Keyword.objects.get_or_create(word=kw)
        KeywordArticle.objects.create(keyword=keyword_obj, article=article, order=i)
    
print(f"Successfully seeded {len(articles_data)} articles!")
