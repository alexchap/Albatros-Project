#ifndef _DAMPING_H_
#define _DAMPING_H_

#include "lib/timer.h"
#include "lib/slists.h"

// delta_t set to 1 sec for now
#define DELTA_T 1

// ToDo : better values?
#define N_REUSE_LISTS 10
#define DELTA_T_REUSE 5

struct protocol;
struct slist;
struct rte;
struct bgp_conn;

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

	struct rte* route;
	struct bgp_conn* bgp_connection;
} damping_info;

/**
 * Computes all the necessary parameters and
 * allocate the necessary tables (decay tables)
 *
 * Note 1: may be necessary to add some arguments to this function,
 * since some of the configuration parameters are read from a
 * config file.
 * XXX : see compiler's warning. Incompatible pointer type in cf-parse.y
 * this may cause some undefined behaviour.
 */
struct damping_config *new_damping_config(struct bgp_proto*, int cut_threshold,
                                   int reuse_threshold, int tmax_hold, 
								   int half_time_reachable, int half_time_unreachable);

// Check damping configuration
void damp_check(damping_config *);

void damp_remove_route(struct bgp_proto*, struct rte*);
void damp_add_route(struct bgp_proto*, struct rte*);

#endif /* _DAMPING_H_ */
