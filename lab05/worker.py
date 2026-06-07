"""
Worker proces pentru conversia text → HTML.

Primește text dintr-o coadă de intrare, îl convertește
și trimite rezultatul în coada de ieșire.
"""

import multiprocessing
from lab05.converter import TextToHtmlConverter


class ConverterWorker(multiprocessing.Process):
    """Proces worker care realizează conversia în fundal."""

    def __init__(
        self,
        input_queue: multiprocessing.Queue,
        output_queue: multiprocessing.Queue,
    ) -> None:
        """Inițializează workerul cu cozile de comunicare.

        Args:
            input_queue: Coada din care se citește textul de convertit.
            output_queue: Coada în care se scrie rezultatul HTML.
        """
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.converter = TextToHtmlConverter()

    def run(self) -> None:
        """Bucla principală a workerului.

        Citește mesaje din input_queue, le convertește și
        trimite rezultatul în output_queue.
        Workerul se oprește când primește None ca mesaj.
        """
        # Aceasta bucla ruleaza intr-un proces separat de sistemul de operare
        while True:
            # Preluam un mesaj din coada de intrare (blocheaza executia pana cand primeste ceva)
            text_data = self.input_queue.get()

            # Conditia de oprire a procesului: primirea obiectului None
            if text_data is None:
                break

            # Convertim datele folosind clasa noastra
            html_result = self.converter.convert(text_data)

            # Trimitem rezultatul inapoi prin coada de iesire catre fereastra
            self.output_queue.put(html_result)