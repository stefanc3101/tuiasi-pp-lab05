"""
Baza de date SQLite pentru jocul P2P (bonus).

Stochează scorurile jucătorilor în fișierul scores.db.
"""

import sqlite3
from pathlib import Path


class GameDatabase:
    """CRUD simplu pentru scorurile jocului P2P."""

    def __init__(self, db_path: str = "scores.db") -> None:
        """Inițializează conexiunea la baza de date și creează tabela dacă lipsește.

        Args:
            db_path: Calea către fișierul SQLite.
        """
        # Deschidem conexiunea la fisierul de baza de date (il va crea automat daca nu exista)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)

        # Cream cursorul si executam querry-ul de creare tabela (doar daca aceasta nu exista deja)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player TEXT NOT NULL,
                score INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def insert_score(self, player: str, score: int) -> None:
        """Inserează un scor nou pentru un jucător."""
        cursor = self.conn.cursor()
        # Folosim placeholders (?) pentru a preveni SQL Injection
        cursor.execute(
            "INSERT INTO scores (player, score) VALUES (?, ?)",
            (player, score)
        )
        self.conn.commit()

    def get_scores(self, player: str) -> list[tuple[int, str, int, str]]:
        """Returnează toate scorurile unui jucător."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, player, score, timestamp FROM scores WHERE player = ?", (player,))
        # Preluam toate rezultatele gasite de query (fetchall returneaza o lista de tuple)
        return cursor.fetchall()

    def get_top_scores(self, limit: int = 10) -> list[tuple[int, str, int, str]]:
        """Returnează cele mai mari scoruri din baza de date."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, player, score, timestamp FROM scores ORDER BY score DESC LIMIT ?",
            (limit,)
        )
        return cursor.fetchall()

    def close(self) -> None:
        """Închide conexiunea la baza de date."""
        if self.conn:
            self.conn.close()