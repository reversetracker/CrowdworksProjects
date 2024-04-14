import os

from pathlib import Path

root = Path(os.path.dirname(__file__)).parent

home = root.joinpath("rag_backend")

static = home.joinpath("static")

logging = root.joinpath("logging.yaml")

sqlite3 = root.joinpath("sqlite3.db")

fixtures = root.joinpath("fixtures")

pdf_file = fixtures.joinpath("upload_test_1.pdf")

csv_file = fixtures.joinpath("upload_test_1.csv")
