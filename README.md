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

To use cookie_api.py for getting inventory and pack history, cookie.json is required

To know which collections have been completed, include a tracker.json file with status for each team.

If at work need proxies set `{'http':'http://172.23.137.193:8080', 'https':'http://172.23.137.193:8080'}`