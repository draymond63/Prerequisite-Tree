#!/bin/bash

data_dir=./datasets/raw

mkdir -p $data_dir
mkdir -p ./datasets/generated

sources=(
    https://dumps.wikimedia.org/other/clickstream/2023-05/clickstream-enwiki-2023-05.tsv.gz
    https://quarry.wmcloud.org/run/730104/output/0/tsv
    https://norvig.com/ngrams/count_1w.txt
    https://www.wordfrequency.info/samples/wordFrequency.xlsx # https://www.wordfrequency.info/files.asp
)

declare -A filemap
filemap=(
    ["tsv"]="enwiki-categories.tsv"
    ["count_1w.txt"]="google-1grams.tsv"
)

for source in "${sources[@]}"; do
    filename=$(basename $source)
    # If filename in filemap, use that instead
    if [[ -v filemap[$filename] ]]; then
        filename=${filemap[$filename]}
    fi
    # if unzipped file already exists, skip
    if [[ -f $data_dir/${filename%.*} ]]; then
        echo "File $filename already exists, skipping"
        continue
    fi
    wget $source -O $data_dir/$filename --no-clobber
    # If extension is .gz, unzip
    if [[ $filename == *.gz ]]; then
        gunzip $data_dir/$filename || exit
    fi
done

set -e
pipenv install
pipenv shell
python -m spacy download en_core_web_sm
