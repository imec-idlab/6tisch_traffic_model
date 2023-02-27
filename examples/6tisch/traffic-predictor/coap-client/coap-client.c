/*
 * Copyright (c) 2013, Institute for Pervasive Computing, ETH Zurich
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the Institute nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * This file is part of the Contiki operating system.
 */

/**
 * \file
 *     CoAP client example.
 * \author
 *      Matthias Kovatsch <kovatsch@inf.ethz.ch>
 *      Dries Van Leemput <dries.vanleemput@ugent.be>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "contiki-net.h"
#include "coap-engine.h"
#include "coap-blocking-api.h"
#include "net/routing/routing.h"
#include "random.h"
#include "net/netstack.h"

#include "sys/node-id.h"

/* Log configuration */
#include "coap-log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL  LOG_LEVEL_APP

#define SERVER_EP "coap://[fd00::208:8:8:8]"

#define SEND_INTERVAL		  3*60*CLOCK_SECOND

PROCESS(coap_client, "CoAP Client");
AUTOSTART_PROCESSES(&coap_client);

static struct etimer et;

/* Example URIs that can be queried. */
#define NUMBER_OF_URLS 5
/* leading and ending slashes only for demo purposes, get cropped automatically when setting the Uri-Path */
char *service_urls[NUMBER_OF_URLS] =
{ ".well-known/core", "test/chunks"};

/* This function is will be passed to COAP_BLOCKING_REQUEST() to handle responses. */
void
client_chunk_handler(coap_message_t *response)
{
  const uint8_t *chunk;

  if(response == NULL) {
    puts("Request timed out");
    return;
  }

  int len = coap_get_payload(response, &chunk);

  printf("|%.*s", len, (char *)chunk);
}
PROCESS_THREAD(coap_client, ev, data)
{
  static coap_endpoint_t server_ep;
  PROCESS_BEGIN();

  NETSTACK_MAC.on();

  static coap_message_t request[1];      /* This way the packet can be treated as pointer as usual. */

  coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &server_ep);

  /* Spread out CoAP GET messages to prevent network flooding */
  if(node_id < 9){
    etimer_set(&et, ((node_id-1)*CLOCK_SECOND*(SEND_INTERVAL/9)) % (SEND_INTERVAL));
  } else {
    etimer_set(&et, ((node_id-2)*CLOCK_SECOND*(SEND_INTERVAL/9)) % (SEND_INTERVAL));
  }
  

  while(1) {
    PROCESS_YIELD();

    if(etimer_expired(&et)) {
      printf("--Toggle timer--\n");
      etimer_set(&et, SEND_INTERVAL);
      if(NETSTACK_ROUTING.node_is_reachable()) {
        /* prepare request, TID is set by COAP_BLOCKING_REQUEST() */
        coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
        int resource = 1;
        coap_set_header_uri_path(request, service_urls[resource]);

        const char msg[] = "Toggle!";

        coap_set_payload(request, (uint8_t *)msg, sizeof(msg) - 1);

        LOG_INFO_COAP_EP(&server_ep);
        LOG_INFO_("\n");

        COAP_BLOCKING_REQUEST(&server_ep, request, client_chunk_handler);

        printf("\n--Done--\n");
      } else {
        LOG_INFO("Not reachable yet\n");
      }      
    }
  }

  PROCESS_END();
}
