#ifndef _DAMPING_H_
#define _DAMPING_H_


#include "lib/timer.h"
#include "lib/slists.h"

// delta_t set to 1 sec for now
#define DELTA_T 1

// ToDo : better values?
#define N_REUSE_LISTS 10
#define DELTA_T_REUSE 15

struct protocol;
struct slist;
struct bgp_conn;
struct net;

/**
 * BGP damping config
 */
typedef struct damping_config {
	int cut_threshold;
	int reuse_threshold;

	time_t tmax_hold;
	time_t half_time_reachable;
	time_t half_time_unreachable;

	int ceiling;

	int decay_array_size;
	double* decay_array;

	double reuse_scale_factor;

	int reuse_list_current_offset;
	int* reuse_lists_index;
	struct slist *reuse_lists;

	timer *reuse_list_timer;
} damping_config;

typedef struct damping_info {
	snode reuse_list_node;
	slist *current_reuse_list;

	int figure_of_merit;
	time_t last_time_updated;

	struct bgp_conn* bgp_connection;

	ip_addr prefix;
	int pxlen;
	struct rta *attrs;
} damping_info;

/* Alloc damping configuration with basic parameters */
struct damping_config *damping_config_new(int reuse_threshold, int cut_threshold, int tmax_hold, int half_time_reachable, int half_time_unreachable);

/* Compute all remaining parameters for a damping configuration */
void damping_config_init(struct damping_config * dcf);

/* Check damping configuration */
void damp_check(struct damping_config * dcf);

/* Process unreachable messages (RFC §4.8.2) */
void damp_remove_route(struct bgp_proto*, net *n, ip_addr*, int);

/* Process route advertisments (RFC §4.8.3) */
void damp_add_route(struct bgp_proto*, struct rte*, ip_addr*, int);


#endif /* _DAMPING_H_ */
