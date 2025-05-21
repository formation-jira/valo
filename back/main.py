# Importation des modules nécessaires de FastAPI et autres bibliothèques
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr  # Pour la validation des données d'entrée
from sqlalchemy import create_engine, Column, Integer, String  # Pour définir le modèle de la BDD
from sqlalchemy.orm import sessionmaker, declarative_base  # Pour gérer les sessions et modèles ORM
from fastapi.middleware.cors import CORSMiddleware  # Pour gérer les autorisations CORS
from passlib.context import CryptContext  # Pour hacher les mots de passe
from sqlalchemy.orm import Session  # Pour typer la session BDD dans les endpoints
from jose import JWTError, jwt  # Pour la gestion du JWT
from datetime import datetime, timedelta  # Pour gérer les expirations de token
from fastapi.security import OAuth2PasswordBearer  # Pour sécuriser les routes avec token

# ---------------------------- CONFIGURATION BASE DE DONNÉES ----------------------------

# Connexion à la base MySQL avec les identifiants
DATABASE_URL = "mysql+mysqlconnector://root:hama@localhost/etudiant_db"
engine = create_engine(DATABASE_URL)  # Création de l’engine SQLAlchemy
SessionLocal = sessionmaker(bind=engine)  # Création d’une session locale pour les requêtes
Base = declarative_base()  # Base de données déclarative pour les modèles ORM

# ---------------------------- GESTION MOT DE PASSE ----------------------------

# Création du gestionnaire de hachage de mot de passe (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------- DÉFINITION DU MODÈLE ÉTUDIANT ----------------------------

# Modèle SQLAlchemy qui représente la table "etudiants" dans la base
class Etudiant(Base):
    __tablename__ = "etudiants"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255))
    age = Column(Integer)
    classe = Column(String(255))
    departement = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))  # Le mot de passe sera stocké sous forme hachée

# Création des tables si elles n'existent pas déjà
Base.metadata.create_all(bind=engine)

# ---------------------------- SCHEMAS Pydantic POUR LES REQUÊTES ----------------------------

# Schéma pour les données d'inscription (signup)
class EtudiantCreate(BaseModel):
    nom: str
    age: int
    classe: str
    departement: str
    email: EmailStr
    password: str

# Schéma pour les données de connexion (login)
class EtudiantLogin(BaseModel):
    email: EmailStr
    password: str

# Schéma pour afficher les informations du profil étudiant
class EtudiantProfile(BaseModel):
    nom: str
    age: int
    classe: str
    departement: str

# ---------------------------- CONFIGURATION DU JWT ----------------------------

# Clé secrète pour signer le JWT
SECRET_KEY = "c5d478dcdb5c4f8a847d0008de971c1f7e15f4bb08949c8f83db16a7a4044ab5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Durée de validité du token

# Fonction pour hacher un mot de passe
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Fonction pour vérifier un mot de passe par rapport à son hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Fonction pour créer un token JWT à partir des données utilisateur
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()  # Copie des données
    expire = datetime.utcnow() + expires_delta  # Calcul de la date d'expiration
    to_encode.update({"exp": expire})  # Ajout de l'expiration dans le payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encodage du JWT
    return encoded_jwt

# ---------------------------- AUTHENTIFICATION UTILISATEUR ----------------------------

# Utilisé pour extraire le token depuis l’en-tête Authorization: Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Fonction qui vérifie le token JWT et retourne l'email de l'utilisateur
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Décodage du token
        email: str = payload.get("sub")  # Extraction de l’email (champ "sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception

# ---------------------------- INITIALISATION FASTAPI ----------------------------

app = FastAPI()  # Création de l'instance FastAPI

# Page d’accueil simple
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API!"}

# ---------------------------- CONFIGURATION CORS ----------------------------

# Autoriser les requêtes CORS depuis le frontend (localhost:3000 = Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------- UTILITAIRE POUR ACCÈS À LA BASE ----------------------------

# Fonction utilitaire pour ouvrir une session BDD proprement
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------- ENDPOINT POUR INSCRIPTION ----------------------------

@app.post("/api/signup")
def signup(etudiant: EtudiantCreate, db: Session = Depends(get_db)):
    # Vérifier si l'email existe déjà
    db_etudiant = db.query(Etudiant).filter(Etudiant.email == etudiant.email).first()
    if db_etudiant:
        raise HTTPException(status_code=400, detail="Email déjà utilisé.")
    
    # Hacher le mot de passe
    hashed_password = hash_password(etudiant.password)

    # Créer un objet Etudiant
    new_etudiant = Etudiant(
        nom=etudiant.nom,
        age=etudiant.age,
        classe=etudiant.classe,
        departement=etudiant.departement,
        email=etudiant.email,
        password=hashed_password,
    )

    # Sauvegarder dans la base de données
    db.add(new_etudiant)
    db.commit()
    db.refresh(new_etudiant)

    return {"message": "Inscription réussie"}

# ---------------------------- ENDPOINT POUR CONNEXION ----------------------------

@app.post("/api/login")
def login(etudiant: EtudiantLogin, db: Session = Depends(get_db)):
    print(f"Requête de connexion reçue : {etudiant}")

    # Chercher l’utilisateur par email
    db_etudiant = db.query(Etudiant).filter(Etudiant.email == etudiant.email).first()
    if db_etudiant is None:
        print(f"Aucun utilisateur trouvé avec l'email : {etudiant.email}")
        raise HTTPException(status_code=400, detail="Identifiants invalides")
    
    # Vérification du mot de passe
    if not verify_password(etudiant.password, db_etudiant.password):
        print(f"Mot de passe incorrect pour l'email : {etudiant.email}")
        raise HTTPException(status_code=400, detail="Identifiants invalides")
    
    # Génération du token JWT si l'identification réussit
    access_token = create_access_token(data={"sub": db_etudiant.email})
    
    print(f"Connexion réussie pour l'email : {etudiant.email}")
    return {"access_token": access_token, "token_type": "bearer"}

