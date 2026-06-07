"""
Logica jocului P2P (bonus).

Doi jucători comunică prin cozi System-V, iar scorurile
sunt stocate în SQLite prin GameDatabase.
"""

import sysv_ipc
from lab05.game_db import GameDatabase


class Game:
    """Logica jocului P2P cu comunicare prin cozi System-V."""

    def __init__(self, player_name: str, db_path: str = "scores.db") -> None:
        """Inițializează jocul pentru un jucător.

        Args:
            player_name: Numele acestui jucător.
            db_path: Calea către baza de date SQLite.
        """
        # Salvam numele jucatorului si cream conexiunea la baza de date
        self.player_name = player_name
        self.db = GameDatabase(db_path)

        # Initializam coada System-V folosind o cheie generica (ex: 1234)
        # Folosim IPC_CREAT pentru a o crea daca nu exista deja in sistemul de operare
        self.queue = sysv_ipc.MessageQueue(1234, sysv_ipc.IPC_CREAT)

    def send_move(self, move: str) -> None:
        """Trimite o mutare celuilalt jucător prin coada System-V.

        Args:
            move: Mutarea de trimis (ex: "rock", "paper", "scissors").
        """
        # Convertim string-ul in bytes inainte de a-l trimite prin coada
        self.queue.send(move.encode('utf-8'))

    def receive_move(self) -> str:
        """Primește mutarea celuilalt jucător.

        Returns:
            Mutarea primită ca string.
        """
        # receive() returneaza un tuplu (mesaj_bytes, tip_mesaj)
        # Extragem doar mesajul si il decodificam inapoi in string format utf-8
        message, _ = self.queue.receive()
        return message.decode('utf-8')

    def play_round(self, my_move: str) -> str:
        """Joacă o rundă: trimite mutarea și determină câștigătorul.

        Args:
            my_move: Mutarea acestui jucător.

        Returns:
            "win", "lose" sau "draw".
        """
        # Trimitem mutarea noastra
        self.send_move(my_move)

        # Asteptam mutarea adversarului (apel blocant pana cand exista un mesaj in coada)
        opp_move = self.receive_move()

        # Logica standard pentru Piatra-Foarfece-Hartie
        if my_move == opp_move:
            result = "draw"
        elif (my_move == "rock" and opp_move == "scissors") or \
             (my_move == "scissors" and opp_move == "paper") or \
             (my_move == "paper" and opp_move == "rock"):
            result = "win"
            # Adaugam 1 punct in baza de date in caz de victorie
            self.db.insert_score(self.player_name, 1)
        else:
            result = "lose"

        return result

    def close(self) -> None:
        """Curăță resursele (cozi, conexiune DB)."""
        # Inchidem conexiunea la baza de date
        self.db.close()

        # Incercam sa stergem coada din sistemul de operare pentru a elibera memoria IPC
        try:
            self.queue.remove()
        except sysv_ipc.ExistentialError:
            # Ignoram eroarea daca respectiva coada a fost deja stearsa de celalalt jucator
            pass