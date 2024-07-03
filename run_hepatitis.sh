conda create -n scrape python=3.11
conda activate scrape
pip install -r requirements.txt 

echo "Running the script"
python factiva_scrape_hepatitis.py