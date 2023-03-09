PREDICT=$1
COOJA=$2
RETRANSMISSIONS=$3
SIM_DIRECTORY=$4
MESSAGE_TYPE=$5
PREDICTION_TIME=$6

echo "Evaluating $MESSAGE_TYPE predictions in : $SIM_DIRECTORY with $PREDICTION_TIME s interval"

if [ $PREDICT == 1 ]
then
    python3 traffic_predictor.py 0 $PREDICTION_TIME $SIM_DIRECTORY
fi
if [ $COOJA == 1 ]
then 
    python3 cooja_parser.py $RETRANSMISSIONS $PREDICTION_TIME $SIM_DIRECTORY
fi
python3 compare.py $SIM_DIRECTORY $MESSAGE_TYPE