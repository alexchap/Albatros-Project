/*
 *      BIRD -- The Border Gateway Protocol
 *
 *      (c) 2011 Alexandre Chappuis <alexandre.chappuis@epfl.ch>,
 *		 Bastian Marquis <bastian.marquis@epfl.ch> and 
 *		 David Klopfenstein <david.klopfenstein@epfl.ch>
 *
 *      Can be freely distributed and used under the terms of the GNU GPL.
 */

#ifndef _DAMPING_H_
#define _DAMPING_H_

#include "nest/route.h"
#include "lib/timer.h"
#include "lib/slists.h"

struct protocol;
struct slist;
struct bgp_conn;
struct net;

/* Per BGP instance configuration */
typedef struct damping_config {
	int cut_threshold;		/* Value above which a route is suppressed */
	int reuse_threshold;		/* Value below which a route is reused */

	time_t tmax_hold;		/* Max time a route can be suppressed */
	time_t half_time_reachable;	/* Decay parameter for reachable prefixes */
	time_t half_time_unreachable;	/* Decay parameter for unreachable prefixes */

	int ceiling;			/* Maximum penalty allowed */

	int decay_array_size;		/* Size of decay arrays */
	double* decay_array;		/* Array containing all possible decay values */

	double reuse_scale_factor;	

	int reuse_list_current_offset;  /* Current offset for reuse_list_index */
	int* reuse_lists_index;		/* The indexes of reuse lists */
	struct slist *reuse_lists;	/* The reuse lists */
} damping_config;

/* Per route structure */
typedef struct damping_info {
	struct fib_node n;		/* A reference to the fib containing all damping_infos */ 

	snode reuse_list_node;		/* A reference to the reuse lists */
	slist *current_reuse_list;	/* Pointer to the current reuse list */

	int figure_of_merit;		 /* Penalty */
	time_t last_time_updated;	 /* Last time the route was updated */

	struct bgp_conn* bgp_connection; /* A pointer to the BGP connection */

	ip_addr prefix;			 /* The prefix */
	int pxlen;			 /* The prefix length */
	struct rta *attrs;		 /* Route attributes */
} damping_info;

void damping_reuse_timer_handler(struct timer*);

/* Functions called from  packets.c or bgp.c */
void damping_config_check(struct damping_config * dcf);
struct damping_config *damping_config_new(int reuse_threshold, int cut_threshold,
		int tmax_hold, int half_time_reachable, int half_time_unreachable);
void damping_config_init(struct damping_config * dcf);
void damp_remove_route(struct bgp_proto*, net *n, ip_addr*, int);
void damp_add_route(struct bgp_proto*, struct rte*, ip_addr*, int);

/* Default configuration values used by config.Y */
#define DEFAULT_CUT_THRESHOLD		1500
#define DEFAULT_REUSE_THRESHOLD		750 
#define DEFAULT_HALF_TIME_REACHABLE	900
#define DEFAULT_HALF_TIME_UNREACHABLE	900
#define DEFAULT_TMAX_HOLD		3000

/* Other parameters */
#define N_REUSE_LISTS			10	/* Number of reuse lists */
#define DELTA_T_REUSE			15	/* Reuse time granularity */
#define DELTA_T				1	/* Time granularity */
#define DEFAULT_FIGURE_OF_MERIT		1000	/* Default penalty */

#endif /* _DAMPING_H_ */
