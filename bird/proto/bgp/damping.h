#ifndef _DAMPING_H_
#define _DAMPING_H_

#include "lib/lists.h"
#include "bgp.h"

// delta_t set to 1 sec for now
#define DELTA_T 1

// ToDo : better values?
#define N_REUSE_LISTS 10

/**
 * Per-route configuration
 */
typedef struct {
	int cut_threshold;
	int reuse_threshold;

	time_t tmax_hold;
	time_t half_time_reachable;
	time_t half_time_unreachable;

	int ceiling;

	int decay_array_size;
	double* decay_array;

	int* reuse_list_index;
	list *reuse_lists;
} damping_config;

typedef struct {
	// Note : this needs to be first in the struct declaration
	// to simplify access code
	node reuse_list_node;

	int figure_of_merit;
	time_t last_time_udpated;

	// not used yet
	damping_config* config;
} damping_info;

/**
 * Computes all the necessary parameters and
 * allocate the necessary tables (decay tables)
 *
 * Note : may be necessary to add some arguments to this function,
 * since some of the configuration parameters are read from a 
 * config file.
 */
void damp_init_config(bgp_proto *, damping_config *);

#endif /* _DAMPING_H_ */
