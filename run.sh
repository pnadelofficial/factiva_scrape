ENV_NAME=scrape

if conda env list | grep -q "^${ENV_NAME}\s"; then
        echo "Conda environment ${ENV_NAME} already eixts. Activating..."
        conda activate scrape
else
        echo "Environment does not exist. Creating..."
        conda create -n scrape python=3.11
        conda activate scrape
        pip install -r requirements.txt
fi

PAGE_ARG=${1:-1}

echo "Running the script"
python factiva_scrape.py "$PAGE_ARG"

conda deactivate