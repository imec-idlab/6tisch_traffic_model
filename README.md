# Real-time traffic predictor for 6TiSCH
Below you can find a short tutorial on how to use the traffic predictor with Cooja.
### Step 1: Start cooja simulator
- Open a new terminal and navigate to `tools/cooja/`.
- Execute `ant run`, or `ant run_bigmem` for longer simulations.
- Open the `examples/6tisch/traffic-predictor/6tisch-full-stack10P2P2.csc` simulation.
- Compile and create all nodes.
### Step 2: Connect to 6LBR via serial socket
- Open a new terminal and navigate to `examples/rpl-border-router/`.
- Execute `make TARGET=cooja connect-router-cooja | tee topology.log` to connect to the 6LBR and log its output in `topology.log`.
- Keep the terminal open to continue logging.
### Start the traffic predictor
- Open new terminal and navigate to `examples/rpl-border-router/`.
- Execute `python3 traffic_predictor_sm.py 1 <prediction_time>`, 1 indicates we are predicting in real-time and `<prediction_time>` is the prediction interval in seconds.
- A new prediction will be printed out every second for all nodes, as soon as the predictor has received telemetry from all nodes.
- In `traffic_predictor_sm.py`, `n.print_n(1, 1, prediction_interval)` on line 347 allows you to enable or disable control traffic telemetry info (first parameter) and traffic per protocol (second parameter).