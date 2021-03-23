# 6TiSCH traffic prediction example

* coap-server: A CoAP server example showing how to use the CoAP layer to develop server-side applications (/examples/coap/coap-example-server).
* coap-example-client: A CoAP client that polls the /actuators/toggle resource every 10 seconds and cycles through 4 resources on button press (target address is hard-coded) (/examples/coap/coap-example-client).

The examples can run either on a real device or as native.
In the latter case, just start the executable with enough permissions (e.g. sudo), and you will then be able to reach the node via tun.
A tutorial for setting up the CoAP server example and querying it is provided on the wiki.
