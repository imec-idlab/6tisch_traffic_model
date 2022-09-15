CONTIKI_PROJECT = traffic-predictor
all: $(CONTIKI_PROJECT)

# Do not try to build on Sky because of code size limitation
PLATFORMS_EXCLUDE = sky z1

# Configure with TSCH
MAKE_MAC = MAKE_MAC_TSCH

# Configure with RPL: Lite for non-storing and Classic for storing
MAKE_ROUTING = MAKE_ROUTING_RPL_CLASSIC
#MAKE_ROUTING = MAKE_ROUTING_RPL_LITE

# Configure as border router
MODULES += os/services/rpl-border-router

# Configure with Orchestra
MODULES += os/services/orchestra

CONTIKI=../../../..

# Include the CoAP implementation
include $(CONTIKI)/Makefile.dir-variables
MODULES += $(CONTIKI_NG_APP_LAYER_DIR)/coap

include $(CONTIKI)/Makefile.include
