# 📱 DOCUMENTATION TECHNIQUE INTÉGRALE : CIF CONNECT

Ce document est le guide unique pour la création de l'application mobile de chat anonyme du CIF. Il détaille chaque concept, chaque outil et chaque étape du développement.

---

## 1. LES NOTIONS TECHNIQUES DÉTAILLÉES (Le Savoir)

### A. Architecture Client-Serveur (API)
* **Le Client (Mobile - Flet) :** L'interface graphique. Elle ne contient aucune donnée de chat. Elle "demande" les informations au serveur et les "affiche".
* **Le Serveur (Backend - FastAPI) :** Le gardien des données. Il reçoit les messages, vérifie qu'ils sont corrects (pas de mots interdits), les enregistre dans SQLite et les renvoie à tous les téléphones connectés.

### B. Communication Temps Réel (WebSockets)
Contrairement au Web classique (InterPam), on utilise un **WebSocket**. 
* **Concept :** C'est une ligne téléphonique qui reste décrochée. Dès que quelqu'un parle, tout le monde entend.
* **Outil :** `fastapi.WebSocket` côté serveur et `flet.Page.on_message` ou un client WebSocket côté mobile.

### C. L'Asynchronisme (`async` / `await`)
Indispensable pour que l'app ne plante pas pendant un chargement.
* `async def` : Définit une tâche qui peut tourner en parallèle.
* `await` : Dit à l'application "Attends que le message soit envoyé au serveur avant de vider le champ de texte, mais reste réactive".

---

## 2. CONFIGURATION DE L'ENVIRONNEMENT (Le Matériel)

### Installations requises :
1.  **Python 3.10+**
2.  **VS Code** + extension Python.
3.  **Android Studio** : Obligatoire pour obtenir le **SDK Android** et la commande `adb`. C'est ce qui transforme ton Python en `.apk`.
4.  **Terminal (PowerShell ou Bash) :** Tape cette commande pour installer les outils :
    `pip install fastapi uvicorn flet websockets sqlalchemy email-validator`

---

## 3. GUIDE DE DÉVELOPPEMENT DÉTAILLÉ (Le Comment)

### ÉTAPE 1 : Créer le Serveur (Le cerveau)
Le fichier `backend/main.py` doit contenir :
* **Une liste de connexions :** `active_connections: List[WebSocket] = []`.
* **Une fonction de diffusion :** Une boucle `for connection in active_connections: await connection.send_text(message)`.
* **Le point d'entrée :** `@app.websocket("/ws")`. C'est l'adresse que l'app mobile appellera.

### ÉTAPE 2 : Créer l'Interface (Le visuel)
Le fichier `mobile_app/main.py` utilise les composants Flet :
* **ft.ListView() :** L'élément crucial. Tu lui ajoutes des `ft.Text()` à chaque nouveau message reçu. Active l'option `auto_scroll=True`.
* **ft.TextField() :** Pour la saisie. Utilise l'événement `on_submit` pour envoyer le message en appuyant sur "Entrée".
* **Le Thread de réception :** Une fonction `async` qui tourne en boucle pour écouter si le serveur envoie un nouveau message.

### ÉTAPE 3 : Anonymat et Sécurité (Le Système CIF)
* **Authentification par email :** Comme pour InterPam, tu demandes l'email. Tu vérifies qu'il finit par `@interfamilia.com` (ou ton domaine).
* **Générateur de Pseudos :** Une liste d'adjectifs et d'animaux en Python.
    * *Exemple :* `random.choice(adjectifs) + " " + random.choice(animaux)`.
* **Lien Email-Pseudo :** Dans ta base SQLite, tu as une table `Users` avec `email`, `pseudo`, `date_inscription`. **Seul l'admin a accès à cette table.**

### ÉTAPE 4 : Déploiement (TwilightParadox)
* **Transfert :** Utilise `SCP` ou `FileZilla` pour envoyer ton dossier `backend`.
* **Uvicorn :** Pour lancer le serveur en production : `uvicorn main:app --host 0.0.0.0 --port 8000`.
* **Nginx & SSL :** Tu dois configurer un "Reverse Proxy". C'est un tunnel sécurisé (HTTPS/WSS). Sans cela, Android bloquera la connexion pour "insécurité".

### ÉTAPE 5 : Création du fichier APK (La Finalisation)
C'est l'étape magique. Dans le dossier `mobile_app`, lance :
`flet build apk`
* **Détail :** Flet va créer un dossier `build` contenant ton application. Tu pourras l'envoyer par mail ou WhatsApp sur ton téléphone pour l'installer.

---

## 4. MODÉRATION ET RÈGLES (Sécurité CIF)

### Système de Shadowban
Si un élève est toxique, le serveur reçoit ses messages mais **ne les renvoie à personne d'autre**. L'élève croit qu'il parle, mais il est seul.
* *Technique :* Ajouter une colonne `is_shadowbanned` (booléen) dans la table `Users`.

### Filtre de Mots Interdits
Une liste `BLACKLIST = ["mot1", "mot2"]`.
* *Action :* Si `any(word in message.lower() for word in BLACKLIST)`, le serveur refuse le message et envoie un avertissement en rouge à l'élève.

### Logs d'Urgence
Table `admin_logs` qui enregistre : `Heure | Email | Message`.
* **Règle :** Ces logs ne sont jamais supprimés. Ils servent de preuve en cas de problème disciplinaire au collège.

---

## 5. STRUCTURE DES DOSSIERS

```text
CIF_CONNECT/
├── backend/
│   ├── main.py (FastAPI)
│   ├── database.py (SQLite)
│   └── words_filter.py (Blacklist)
├── mobile_app/
│   ├── main.py (Flet UI)
│   └── assets/ (Images/Icons)
└── README.md (Ce fichier)

Projet initié en 2026 - Collège Inter Familia
