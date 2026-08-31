# The PIMMUR Principles: Ensuring Validity in Collective Behavior of LLM Societies
## Installation
We have provided a standalone Multi-Agent System tutorial. You can download `standalone_MAS_tutorial.ipynb` directly, and upload it to google colab to run an example simulation without the need of cloning the repository manually.

All test was excuted on Ubuntu 24.04.1 LTS, using `python==3.10.12`
Clone the repo and install dependencies
```bash
git clone https://github.com/JXZhou0224/PIMMUR.git
cd PIMMUR
pip install -r requirements.txt
```
This should take less than 5 minutes to set up.
## Executing the LLM test for Unawarenes and Min-control
Go to the `Unaware&ControlTest` folder.

To interactively test new prompts, run:
```bash
export OPENAI_API_KEY="YOUR_API_KEY"
python run.py --mode interactive --model gpt-4o-2024-11-20 --api openai
```
If run successfully, you should see model's response on the command line.
To test more models, see the scripts in `scripts.sh` for reference.

To execute our complete *Unawareness* and *Min-control* test, switch the `--mode` to `unawareness` or `steering` respectively.

## Executing the Multi-Agent System
Go to the `MAS` folder.

First, set your configuration in the `configs` folder. To run specifc simulation. run
```bash
python run.py --config <path_to_the corresponding_config_file>
```

To process the results， go to the result file and excute the `vis.py` file under the folder will produce a visualization for the result

## Customization
To run your own simulation using our framework. You need to implement your own config generator and simluation class like the ones under `config_generators.py` and `simulation.py`. The config you generated will be passed on directly to the Simulation. If you need to run a dataset, you can define your own execution function in `run.py`. In `configs\ConfigTemplate.json` provides the minimal configs you need to include in your config file.
