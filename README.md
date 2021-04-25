# TheShow
## Environment setup
Install miniconda and setup virtual environment
``` bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_54.sh
bash https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_54.sh
conda env create --prefix ./.venv -f environment.yaml
```

To activate, run `conda activate ./.venv` from directory that contains virtual environment (.venv)

To remove virtual environment run `conda env remove -p ./.venv`

To see list of environments run `conda info --envs`

To use cookie_api.py for getting inventory and pack history, cookie.txt is required