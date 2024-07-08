conda create -n scrape python=3.11
conda activate scrape
pip install -r requirements.txt 

PAGE_ARG = $1

echo "Running the script"
python factiva_scrape.py "$PAGE_ARG"