# power-laws-optimizing-demand-side-strategies

Based on this [DrivenData competition](https://www.drivendata.org/competitions/53/optimize-photovoltaic-battery/page/104/), the purpose of this project is to build an algorithm that controls a battery charging system and spends the least amount of money over a simulation period.

The competition completed in the Spring 2018, but the data is still available from [Schneider Electric](https://data.exchange.se.com/explore/dataset/power-laws-optimizing-demand-side-strategies-training-data/information/?disjunctive.site_id) (Must sign up for free log in to access). Due to license agreements, the raw data must be downloaded from Schneider Electric; this project assumes the raw data is then placed in the `data/` subdirectory.


## Structure of this repo

File | Description |
---- | ----- |
`├── data` | A directory that has all of the input data as `.csv`s that are provided by the competition. Now that the [DrivenData competition](https://github.com/drivendataorg/power-laws-optimization) has completed, you can find the data on [Schneider Electric's website](https://data.exchange.se.com/explore/dataset/power-laws-optimizing-demand-side-strategies-training-data/information/?disjunctive.site_id). <br></br>There are minor differences in data format and naming conventions between the DrivenData competition and on Scheider Electric's website, which are handled by `./prepare_data.py` |
`├── output` | A directory for storing the output of a single simulation run. |
`├── all_results` | This directory contains results from all of the runs executed. |
`├── simulate` | The Python code for the simulation. |
`·   ├── assets` | **A FOLDER FOR ANY TRAINED MODELS/DATA THAT NEEDS TO BE LOADED BY `battery_controller.py`** |
`·   ├── battery.py` | Contains an object for storing information about the battery. Some of the params of the Battery object include `(dis)charging capacity`, `(dis)charging efficiency`, and the `current charge` of the battery at the time of instantiation. |
`·   ├── simulate.py` | Main entrypoint. Controls and executes the simulations. Tracks energy costs of electrifying the site with and without battery, which inform level of effectiveness of `propose_state_of_charge` method in `./battery_controller.py`. |
`·   └──battery_controller.py` | Contains a `propose_state_of_charge` which suggests (dis)charging action based upon: <br></br>* Recent load / PV production at given timestep<br/>* Load / PV forecasts for future timesteps<br/>* Price of buying/selling energy at given timestep |
`├── Dockerfile` | The definition for the Docker container on which the simulation executes. |
`├── prepare_data.py` | File to account for differences between expected format of data from DrivenData and Schneider Electric |
`├── README.md` | About the project. |
`├── entrypoint.sh` | Called inside the container to execute the simulation. Can also be used locally. |
`├── requirements.txt` | The Python libraries that will be installed. Only the libraries in this official repo will be available. |
`└── run.sh` | The only command you need. Builds and runs simulations in the Docker container. |