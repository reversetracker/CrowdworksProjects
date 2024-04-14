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

chroma = root.joinpath("chroma")

disease_chromadb = chroma.joinpath("disease")

insurance_chromadb = chroma.joinpath("insurance")

coverage_limit_chromadb = chroma.joinpath("coverage-limit")

insurance_requirements_chromadb = chroma.joinpath("required-documents")

matrix_collateral_name_chromadb = chroma.joinpath("matrix-collateral-name")

matrix_disease_name_chromadb = chroma.joinpath("matrix-disease-name")
