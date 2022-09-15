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
 *      Project configuration.
 * \author
 *      Dries Van Leemput <dries.vanleemput@ugent.be>
 */

/* Set to enable TSCH security */
#ifndef WITH_SECURITY
#define WITH_SECURITY 0
#endif /* WITH_SECURITY */

/* USB serial takes space, free more space elsewhere */
#define SICSLOWPAN_CONF_FRAG 1
//#define UIP_CONF_BUFFER_SIZE 160

/*******************************************************/
/******************* Configure TSCH ********************/
/*******************************************************/

/* IEEE802.15.4 PANID */
#define IEEE802154_CONF_PANID 0x353

/* Do not start TSCH at init, wait for NETSTACK_MAC.on() */
#define TSCH_CONF_AUTOSTART 0

/* 6TiSCH minimal schedule length.
 * Larger values result in less frequent active slots: reduces capacity and saves energy. */
#define TSCH_SCHEDULE_CONF_DEFAULT_LENGTH 3

#if WITH_SECURITY

/* Enable security */
#define LLSEC802154_CONF_ENABLED 1

#endif /* WITH_SECURITY */

/******************************************************/
/******************* Configure RPL ********************/
/******************************************************/

/* Choose MOP */
#define RPL_STORING 1
#if RPL_STORING
#define RPL_CONF_MOP RPL_MOP_STORING_MULTICAST
#else
#define RPL_CONF_MOP RPL_MOP_NON_STORING
#endif

/* Disable (DIO) probing */
#define RPL_CONF_WITH_PROBING 0

/* Disable DAO refreshing */ 
#define RPL_CONF_DIO_REFRESH_DAO_ROUTES 0
#define RPL_CONF_WITH_DAO_ACK 1

/******************************************************/
/******************* Configure INT ********************/
/******************************************************/

/* Enable Inband Telemetry Implementation */
#define TSCH_CONF_WITH_INT 1
#if RPL_STORING
#define INT_STRATEGY_DAO 1
#define INT_BITMAP 0x8F
#else
#define INT_STRATEGY_LEAF_PERIODICAL 1
#define INT_PERIOD 200
#define INT_BITMAP 0x88
#endif

/*******************************************************/
/******************* Configure CoAP ********************/
/*******************************************************/

/* Enable client-side support for COAP observe */
#define COAP_OBSERVE_CLIENT 1
#define INT_COAP_INTERVAL   60
