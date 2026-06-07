"""
Fereastra principală a aplicației GUI PySide6.

Permite selectarea unui fișier text, trimiterea lui
unui worker prin coadă și afișarea rezultatului HTML.
"""

import multiprocessing
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QPushButton,
        QLineEdit,
        QTextEdit,
        QFileDialog,
        QLabel,
    )
    from PySide6.QtCore import QTimer
except ImportError:
    # Permite importul fără PySide6 instalat (util în teste)
    QMainWindow = object  # type: ignore[misc, assignment]

from lab05.worker import ConverterWorker


class MainWindow(QMainWindow):
    """Fereastra principală a aplicației de conversie text→HTML."""

    def __init__(self) -> None:
        """Inițializează fereastra și lansează workerul."""
        super().__init__()

        self.setWindowTitle("Convertor Text -> HTML")
        self.setMinimumSize(600, 400)

        # Cream cozile de comunicare (sunt thread/process safe)
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()

        # Instantiem si pornim procesul ascuns in fundal
        self.worker = ConverterWorker(self.input_queue, self.output_queue)
        self.worker.start()

        # Construim elementele vizuale
        self._build_ui()

        # Configuram un timer care la fiecare 100 milisecunde verifica
        # daca worker-ul ne-a trimis inapoi vreun rezultat pe coada de output
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_output)
        self.timer.start(100)

    def _build_ui(self) -> None:
        """Construiește interfața grafică.

        Componente necesare:
        - QLabel + QLineEdit pentru calea fișierului
        - QPushButton "Browse" — deschide QFileDialog
        - QPushButton "Upload" — citește fișierul și trimite în coadă
        - QTextEdit (read-only) pentru afișarea HTML-ului rezultat
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Containerul orizontal pentru bara de selectie fisier
        file_layout = QHBoxLayout()

        self.path_label = QLabel("Fisier text:")
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True) # Nu vrem ca utilizatorul sa scrie de mana in camp

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self._browse_file)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self._upload_file)

        file_layout.addWidget(self.path_label)
        file_layout.addWidget(self.path_input)
        file_layout.addWidget(self.browse_button)
        file_layout.addWidget(self.upload_button)

        main_layout.addLayout(file_layout)

        # Zona textului rezultat (mare si readonly)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        main_layout.addWidget(self.result_text)

    def _browse_file(self) -> None:
        """Deschide un dialog de selectare fișier și actualizează câmpul de cale."""
        # QFileDialog intoarce un tuplu, primul element este calea fișierului ales
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selectati un fisier text", "", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            self.path_input.setText(file_path)

    def _upload_file(self) -> None:
        """Citește fișierul selectat și îl trimite în input_queue."""
        file_path_str = self.path_input.text()

        if not file_path_str:
            self.result_text.setText("Va rugam selectati un fisier inainte de upload.")
            return

        try:
            # Citim tot continutul fisierului si il trimitem in coada catre worker
            file_path = Path(file_path_str)
            text_content = file_path.read_text(encoding="utf-8")
            self.input_queue.put(text_content)
            self.result_text.setText("Se proceseaza...")
        except Exception as e:
            self.result_text.setText(f"Eroare la citirea fisierului:\n{str(e)}")

    def _check_output(self) -> None:
        """Verifică dacă workerul a trimis rezultate în output_queue."""
        # Verificam daca avem elemente in coada de output fara a ne bloca interfața
        while not self.output_queue.empty():
            html_result = self.output_queue.get()
            # Setam textul convertit in fereastra principala
            self.result_text.setText(html_result)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Oprește workerul la închiderea ferestrei."""
        # Trimitem "pastila cu otrava" (None) pentru a scoate workerul din while True
        self.input_queue.put(None)

        # Asteptam maximum 1 secunda pentru ca procesul sa se incheie curat
        self.worker.join(timeout=1.0)

        # Daca nu s-a incheiat nici dupa timeout, il forțam (terminate) pentru a nu lasa procese orfane/zombie
        if self.worker.is_alive():
            self.worker.terminate()

        # Apelam eventul normal de inchidere
        super().closeEvent(event)