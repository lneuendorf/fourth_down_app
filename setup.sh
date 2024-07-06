conda env create -f environment.yml
conda activate 4th-down
python -m ipykernel install --user --name=4th-down --display-name "4th-down"

# update env: conda env update -f environment.yml --prune