# TSCH #
EB_PERIOD       = 16.0                  # Beacon period [s]
SF_PERIOD       = 3.97                  # EB slotframe length [s]
L_EB            = 37                    # Beacon length [B]
L_MAC_HDR       = 23                    # MAC header [B]
L_EACK          = 19                    # EACK length [B]

# RPL #
IMAX            = 1048.0                # Maximum Trickle interval [s]
L_DIO           = 96                    # DIO length [B]
DAO_PERIOD      = 15.0*60               # DAO period [B] (DAG lifetime, between 15 min and 22.5 min (RPL classic))
L_DAO_NS        = 85                    # DAO length non-storing mode [B]
L_DAO_S         = 76                    # DAO length storing mode [B]
L_DAO_ACK       = 43                    # DAO ACK length [B]

# CoAP
COAP_PERIOD     = 3*60                  # CoAP period [s]
L_COAP_RQ       = 16                    # CoAP request payload [B]
L_COAP_RP       = 30                    # CoAP response payload [B]
L_TOT_HDR       = 49                    # IP, UDP and CoAP header length

# NETWORK
N               = 10                    # Number of nodes
ROOT            = 1                     # Root ID
SERVER          = 8                     # Server ID
COOJA_OFFSET    = 384                   # Offset between ASN and Cooja time [ms]

# PREDICTION
INT_PERIOD      = 15*60                 # INT period [s]
P_INTERVAL      = 900                   # Prediction interval [s]
PROTOCOL        = "Total"               # Choose protocol (Total, CoAP, DAO, DAO ACK, DIO, EB, EACK)
RT              = False                 # Predict in real-time (True) or evaluate after simulation with actual values from cooja (False)
SIM_DIR         = "Simulations/Test"    # Simulation directory for non-real-time predictions
EB_INT          = True                  # Enable optional EB telemetry
DIO_INT         = False                 # Enable optional DIO telemetry
DAO_INT         = True                  # Enable optional DAO telemetry

# ANALYSIS
START_OFFSET    = 4500                  # Optional offset at start of the simulation [predictions]
END_OFFSET      = 2500                  # Optional offset at end of the simulation [predictions]