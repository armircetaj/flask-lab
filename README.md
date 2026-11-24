# Flask Bookshelf

## Installazione

Crea e attiva il venv:

    python -m venv .venv
    .\.venv\Scripts\activate

Installa i pacchetti:

    pip install -r requirements.txt

## File .env

L'app legge le impostazioni dal file `.env`, che si crea copiando l'esempio

    copy .env-example .env

Poi apri il file `.env` e cambia i valori:

| Variabile | Spiegazione |
|-----------|---------|
| SECRET_KEY | variabile segreta per le sessioni, usa un testo lungo e casuale |
| DATABASE_URL | dove si trova il database, di default `sqlite:///bookshelf.db` |

## Database

Il database è un file SQLite che si crea con le migrations:

    flask db upgrade

Il file si trova nella cartella `instance/`.

Se si cambia `models.py`, bisogna creare una nuova migration:

    flask db migrate
    flask db upgrade

## Creazione di un admin

Al signup viene sempre creato un utente normale, invece per creare un admin si usa un comando scritto in `app.py`.
All'esecuzione del comando chiede due parametri, cioe' nome e password

    flask create-admin USERNAME PASSWORD

Il comando crea un utente con il ruolo `admin` e lo salva nel database.

## Come avviare l'app

    python -m app
Oppure
    flask run

## Test

Per far partire i test:

    python -m pytest

