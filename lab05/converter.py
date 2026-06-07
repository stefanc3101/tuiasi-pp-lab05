"""
Convertor text → HTML.

Prima linie din text devine titlu <h1>.
Blocurile separate de linii goale devin paragrafe <p>.
"""


class TextToHtmlConverter:
    """Convertește text simplu în HTML structurat."""

    def convert(self, text: str) -> str:
        """Convertește textul în HTML.

        Prima linie devine <h1>, blocurile separate de linie goală
        devin paragrafe <p>.

        Args:
            text: Textul de convertit.

        Returns:
            String HTML valid.
        """
        # Returnam un schelet HTML valid daca textul este gol,
        # exact asa cum cere testul test_text_gol_returneaza_html_minimal
        if not text.strip():
            return "<!DOCTYPE html>\n<html>\n<body>\n</body>\n</html>"

        # Impartim textul dupa linii goale consecutive pentru a gasi blocurile
        blocks = text.strip().split("\n\n")

        # Filtram eventualele blocuri goale ramase accidental
        valid_blocks = [b.strip() for b in blocks if b.strip()]

        if not valid_blocks:
            return "<!DOCTYPE html>\n<html>\n<body>\n</body>\n</html>"

        # Prima linie (primul element din primul bloc) devine h1
        first_block_lines = valid_blocks[0].split("\n")
        title = first_block_lines[0].strip()

        html_output = f"<h1>{title}</h1>\n"

        # Daca primul bloc avea si alte linii sub titlu, le unim si le facem primul paragraf
        if len(first_block_lines) > 1:
            remaining_first_block = "<br>\n".join(line.strip() for line in first_block_lines[1:])
            html_output += f"<p>{remaining_first_block}</p>\n"

        # Restul blocurilor (index 1 si mai departe) devin paragrafe standard
        for block in valid_blocks[1:]:
            formatted_block = "<br>\n".join(line.strip() for line in block.split("\n"))
            html_output += f"<p>{formatted_block}</p>\n"

        return html_output.strip()