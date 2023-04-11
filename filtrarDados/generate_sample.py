import os
import tarfile
import click
import checksumdir
import pandas as pd


@click.command()
@click.option("--query-expr", default="", help="DataFrame querying expresion.")
def generate_dataset(query_expr):
    if query_expr == "":
        print("please set --query-expr parameter")
        exit()

    chunks_uri = (
        "https://www.dropbox.com/s/3kaqg3ntj5zougd/MICRODADOS_ENEM_2019.csv.tar.xz"
    )
    chunks_tar = "MICRODADOS_ENEM_2019.csv.tar.xz"
    chunks_dir = "MICRODADOS_ENEM_2019_CHUNKS"
    chunks_checksum = "718aae27698996383c5ac982d8d2dcaf"

    invalid = False
    if os.path.isdir(chunks_dir):
        print("veryfing chunks integrity...")
        checksum = checksumdir.dirhash(chunks_dir)
        invalid = True if checksum != chunks_checksum else False

    if invalid or not os.path.isdir(chunks_dir):
        os.rmdir(chunks_dir) if os.path.isdir(chunks_dir) else None

        print("downloading...")
        os.system("wget -q --show-progress {}".format(chunks_uri))

        with tarfile.open(chunks_tar) as f:
            print("extracting...")
            f.extractall(chunks_dir)

    chunks_files = ["{}/{}".format(chunks_dir, f) for f in os.listdir(chunks_dir)]

    print("generating dataset...")
    filtered_data = [
        pd.read_csv(chunk, encoding="ISO-8859-1", delimiter=";").query(query_expr)
        for chunk in chunks_files
    ]
    filtered_data = pd.concat(filtered_data)

    dest = "MICRODADOS_ENEM_2019_FILTERED.csv"
    filtered_data.to_csv(dest, index=False)

    print("done")


if __name__ == "__main__":
    generate_dataset()
