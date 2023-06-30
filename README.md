# 6tisch_traffic_model
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