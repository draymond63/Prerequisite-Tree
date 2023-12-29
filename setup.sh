#!bash

mkdir -p ./datasets/raw
mkdir -p ./datasets/generated

sources=(
    https://dumps.wikimedia.org/other/clickstream/2023-05/clickstream-enwiki-2023-05.tsv.gz
    https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz
)

for source in "${sources[@]}"; do
    filename=$(basename $source)
    # if unzipped file already exists, skip
    if [[ -f ./datasets/raw/${filename%.*} ]]; then
        echo "File $filename already exists, skipping"
        continue
    fi
    wget $source -O ./datasets/raw/$filename --no-clobber
    # If extension is .gz, unzip
    if [[ $filename == *.gz ]]; then
        gunzip ./datasets/raw/$filename || exit
    fi
done

set -e
pipenv install
pipenv shell
python -m spacy download en_core_web_sm
python ./sqldump_to_csv.py ./datasets/raw/enwiki-latest-categorylinks.sql > ./datasets/raw/enwiki-latest-categorylinks.csv
