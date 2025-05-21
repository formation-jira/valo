from fastapi import FastAPI, Depends, Query
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import httpx
from bs4 import BeautifulSoup
from typing import Optional, List

from groq import Groq
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialiser le client Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)
# ----- CONFIG BDD -----
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:hama@localhost/etudiant_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ----- MODELE -----
class RecommendedBook(Base):
    __tablename__ = "recommended_books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    availability = Column(String(100), nullable=False)

# ----- APP FASTAPI -----
app = FastAPI()

# ----- DEPENDENCY -----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- SCRAPING -----
async def scrape_books():
    url = "https://books.toscrape.com/catalogue/page-1.html"  
    books = []

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # Lève une erreur si statut != 2xx
        except httpx.HTTPStatusError as e:
            raise Exception(f"Erreur serveur : {e}")
        except httpx.RequestError as e:
            raise Exception(f"Erreur réseau : {e}")

        soup = BeautifulSoup(response.text, "html.parser")

        # Récupérer la catégorie via breadcrumb
        breadcrumb = soup.find("ul", class_="breadcrumb")
        if breadcrumb:
            breadcrumb_items = breadcrumb.find_all("li")
            category = breadcrumb_items[2].text.strip() if len(breadcrumb_items) > 2 else "Unknown"
        else:
            category = "Unknown"

        articles = soup.find_all("article", class_="product_pod")
        print(f"📚 {len(articles)} livres trouvés")  # ✅ Log utile

        for article in articles:
            title = article.h3.a["title"]
            price_text = article.find("p", class_="price_color").text.strip()
            price = float(price_text.lstrip("£"))
            availability = article.find("p", class_="instock availability").text.strip()

            books.append({
                "title": title,
                "price": price,
                "category": category,
                "availability": availability,
            })

    return books

# ----- ROUTE POUR SCRAPER ET STOCKER -----
@app.api_route("/scrape_books", methods=["GET", "POST"])
async def scrape_and_store_books(db: Session = Depends(get_db)):
    try:
        books = await scrape_books()

        if not books:
            return {"error": "Aucun livre trouvé. Aucune modification apportée à la base."}

        # Supprime anciens livres uniquement s'il y a des nouveautés
        db.query(RecommendedBook).delete()
        db.commit()

        # Insère les nouveaux livres
        for book in books:
            book_db = RecommendedBook(**book)
            db.add(book_db)
        db.commit()

        return {"message": f"{len(books)} livres insérés dans la base."}

    except Exception as e:
        return {"error": str(e)}

# ----- ROUTE POUR AFFICHER LES RECOMMANDATIONS -----
@app.get("/recommendations", response_model=List[dict])
def get_recommendations(
    category: Optional[str] = None,
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(RecommendedBook)

    if category:
        query = query.filter(RecommendedBook.category == category)
    if price_min is not None:
        query = query.filter(RecommendedBook.price >= price_min)
    if price_max is not None:
        query = query.filter(RecommendedBook.price <= price_max)

    results = query.all()

    return [{
        "id": book.id,
        "title": book.title,
        "price": book.price,
        "category": book.category,
        "availability": book.availability
    } for book in results]


from fastapi import Query

@app.get("/books/summary")
async def generate_book_summary(title: str = Query(..., description="Titre du livre")):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Génère un court résumé captivant du livre intitulé '{title}'."
                }
            ],
            model="llama-3.3-70b-versatile",  # Modèle actuel supporté par Groq
            temperature=0.7,
            max_tokens=150,
        )

        summary = chat_completion.choices[0].message.content.strip()
        return {"title": title, "summary": summary}

    except Exception as e:
        return {"error": str(e)}

# ----- MIDDLEWARE CORS -----
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- CREATION DES TABLES -----
Base.metadata.create_all(bind=engine)

print("✅ Backend main1.py lancé avec succès")
