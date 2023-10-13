#!bash

mkdir ./datasets
mkdir ./datasets/raw
mkdir ./datasets/generated

wget https://dumps.wikimedia.org/other/clickstream/2023-05/clickstream-enwiki-2023-05.tsv.gz ./datasets/raw/clickstream-enwiki-2023-05.tsv.gz
wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz ./datasets/raw/enwiki-latest-categorylinks.sql.gz
gunzip ./datasets/raw/clickstream-enwiki-2023-05.tsv.gz
gunzip ./datasets/raw/enwiki-latest-categorylinks.sql.gz # TODO: this is a sql file, not a tsv file

pipenv install
pipenv shell
python -m spacy download en_core_web_sm
