#!bash

data_dir=./datasets/raw

mkdir -p $data_dir
mkdir -p ./datasets/generated

sources=(
    https://dumps.wikimedia.org/other/clickstream/2023-05/clickstream-enwiki-2023-05.tsv.gz
    https://quarry.wmcloud.org/run/730104/output/0/tsv
    # https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz
    # https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz
)

for source in "${sources[@]}"; do
    filename=$(basename $source)
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

mv $data_dir/tsv $data_dir/enwiki-categories.tsv

set -e
pipenv install
pipenv shell
python -m spacy download en_core_web_sm
