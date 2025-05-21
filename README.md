# 🎓 Plateforme de Formation en Ligne

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/formation-jira/valo)
[![GitHub issues](https://img.shields.io/github/issues/formation-jira/valo)](https://github.com/formation-jira/valo/issues)
[![GitHub forks](https://img.shields.io/github/forks/formation-jira/valo)](https://github.com/formation-jira/valo/network)
[![GitHub stars](https://img.shields.io/github/stars/formation-jira/valo)](https://github.com/formation-jira/valo/stargazers)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Bienvenue sur la plateforme de **formation en ligne** 🧑‍🏫 conçue pour permettre aux étudiants de suivre des cours variés, avec une interface moderne et une gestion complète côté administrateur.

---

## 🧭 Sommaire

- [🎯 Objectifs](#-objectifs)
- [🛠️ Fonctionnalités](#-fonctionnalités)
- [📦 Architecture Technique](#-architecture-technique)
- [🖥️ Frontend](#️-frontend)
- [⚙️ Backend](#️-backend)
- [🗃️ Structure de Données](#️-structure-de-données)
- [📈 Statistiques & Performances](#️-statistiques--performances)
- [🗂️ Gestion de Projet Agile](#️-gestion-de-projet-agile)
- [🚀 Lancement du Projet](#-lancement-du-projet)
- [📄 Livrables Finaux](#-livrables-finaux)
- [📬 Contact](#-contact)

---

## 🎯 Objectifs

- Permettre aux étudiants de suivre des **formations** en ligne par thème.
- Offrir une interface d’**administration complète** pour la gestion des utilisateurs et des cours.
- Intégrer des fonctionnalités avancées comme le **scraping de livres** 📚 et la **génération de résumés intelligents** avec IA 🤖.
- Mettre en œuvre une méthodologie **Scrum agile** pour une gestion efficace du projet.

---

## 🛠️ Fonctionnalités

### 👨‍🎓 Utilisateur (Étudiant)

- ✅ Inscription & connexion
- 👤 Gestion du profil
- 📚 Inscription aux formations
- 🎥 Accès aux cours (vidéos & documents)
- ⭐ Ajout/suppression de favoris
- 📜 Consultation des formations inscrites

### 🛡️ Administrateur

- 👥 Gestion des utilisateurs (CRUD, activation)
- 📘 Gestion des formations (CRUD)
- 📊 Statistiques globales (étudiants, formations, complétion)

### 🔍 Fonctionnalités avancées

- 📦 Scraping de livres (titre, prix, dispo, catégorie)
- 🎯 Recommandations par catégorie / prix
- 🧠 Résumés de livres avec API IA

---

## 📦 Architecture Technique

### 🖥️ Frontend
- Framework moderne (React/Next.js)
- Interface responsive et intuitive

### ⚙️ Backend
- Microservices REST :
  - Gestion utilisateurs
  - Formations & départements
  - Favoris
  - Recommandations & IA

---

## 🗃️ Structure de Données

- **Étudiants** → Appartiennent à un département
- **Formations** → Par thème
- **Favoris** → Ajout/suppression pour navigation rapide
- **Livres recommandés** → Scraping & stockage avec résumé intelligent

---

## 📈 Statistiques & Performances

- 📊 Suivi des indicateurs : formations populaires, taux de complétion
- ⚡ Base de données optimisée pour :
  - Favoris
  - Livres recommandés
- 🧠 Cache pour optimiser les lectures fréquentes

---

## 🗂️ Gestion de Projet Agile

- 🔁 Méthodologie **Scrum**
- 📋 **Backlog produit** avec user stories détaillées
- 📆 Sprints planifiés avec Jira / YouTrackServer
- 🔀 Suivi version & gestion bugs via GitHub
- 📚 Documentation continue via Confluence

### 🧑‍🤝‍🧑 Rôles recommandés

- 🧠 **Scrum Master** – Coordination
- 🎯 **Product Owner** – Vision produit & priorisation
- 🧑‍💻 **Développeurs** – Implémentation technique

---

## 🚀 Lancement du Projet

1. Clonez le repo :
   ```bash
   git clone https://github.com/formation-jira/valo.git
   cd valo
