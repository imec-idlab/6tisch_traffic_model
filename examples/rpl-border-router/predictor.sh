PREDICT=$1
COOJA=$2

echo "Evaluating predictions"

if [ $PREDICT == 1 ]
then
    python3 traffic_predictor.py
fi
if [ $COOJA == 1 ]
then 
    python3 cooja_parser.py 1
fi
python3 compare.py