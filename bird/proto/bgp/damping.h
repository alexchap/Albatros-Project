#ifndef _DAMPING_H_
#define _DAMPING_H_

#include "lib/lists.h"
#include "bgp.h"

// delta_t set to 1 sec for now
#define DELTA_T 1

/**
 * Per-route configuration
 */
typedef struct {
	int cut_threshold;
	int reuse_threshold;

	time_t tmax_hold;
	time_t half_time_reachable;
	time_t half_time_unreachable;

	int decay_array_size;
	double* decay_array;

	// computed configuration parameters
} damping_config;


struct damping_info_;
typedef struct damping_info_ damping_info;

struct damping_info_ {
	// Note : this needs to be first in the struct declaration
	// to simplify access code
	node reuse_list_node;

	int figure_of_merit;
	time_t last_time_udpated;

	// not used yet
	damping_config* config;
};

/**
 * Computes all the necessary parameters and
 * allocate the necessary tables (decay tables)
 */
void damp_init_config(bgp_proto *, damping_config *);

#endif /* _DAMPING_H_ */
