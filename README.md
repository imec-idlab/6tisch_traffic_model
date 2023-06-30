# 6tisch_traffic_model
This repository contains the related code for the paper *[Analytical traffic model of 6TiSCH using real-time in-band telemetry](https://doi.org/10.1016/j.iot.2023.100847)*.

This repository is not intended for commercial use. Please contact us if you intend to use this repository for commercial applications.
If you use this repository for research purposes, please cite our paper, as well as the paper introducing In-band Network telemetry:

### BIBTEX ###
```
@article{VANLEEMPUT2023100847,
title = {Analytical traffic model of 6TiSCH using real-time in-band telemetry},
journal = {Internet of Things},
volume = {23},
pages = {100847},
year = {2023},
issn = {2542-6605},
doi = {https://doi.org/10.1016/j.iot.2023.100847},
url = {https://www.sciencedirect.com/science/article/pii/S2542660523001701},
author = {Dries {Van Leemput} and Jeroen Hoebeke and Eli {De Poorter}},
}

@article{8882280,
author={Karaagac, Abdulkadir and De Poorter, Eli and Hoebeke, Jeroen},
journal={IEEE Transactions on Network and Service Management}, 
title={In-Band Network Telemetry in Industrial Wireless Sensor Networks}, 
year={2020},
volume={17},
number={1},
pages={517-531},
doi={10.1109/TNSM.2019.2949509}
}
```
### IEEE ###
> [1] D. V. Leemput, J. Hoebeke, E. De Poorter, Analytical traffic model of 6tisch using real-time in-band telemetry,” Internet of Things, vol. 23, p. 100847, 2023, doi: 10.1016/j.iot.2023.100847.
> [2] A. Karaagac, E. De Poorter and J. Hoebeke, "In-Band Network Telemetry in Industrial Wireless Sensor Networks," in IEEE Transactions on Network and Service Management, vol. 17, no. 1, pp. 517-531, March 2020, doi: 10.1109/TNSM.2019.2949509.

## Traffic predictor tutorial for cooja
Below you can find a short tutorial on how to use the traffic predictor with cooja. This only works with Ubuntu 18.04.
### Step 1: Start cooja simulator
- Open a new terminal and navigate to `tools/cooja/`.
- Execute `ant run`, or `ant run_bigmem` for longer simulations.
- Open the `examples/6tisch/traffic-predictor/6tisch-full-stack10P2P2.csc` simulation.
- Compile and create all nodes.
### Step 2: Connect to 6LBR via serial socket
- Open a new terminal and navigate to `examples/rpl-border-router/`.
- Execute `make TARGET=cooja connect-router-cooja >> topology.log` to connect to the 6LBR and log its output in `topology.log`.
- Keep the terminal open to continue logging.
### Start the traffic predictor
- Open new terminal and navigate to `examples/rpl-border-router/`.
- Configure the network and traffic predictor parameters in `config.py`.
- Execute `predictor.sh` for non-storing mode or `predictor_sm.sh` for storing mode.
- A new prediction will be printed out every second for all nodes, as soon as the predictor has received telemetry from all nodes.