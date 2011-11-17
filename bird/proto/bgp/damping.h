#ifndef _DAMPING_H_
#define _DAMPING_H_

#include "lib/lists.h"
#include "lib/timer.h"
#include "bgp.h"

// delta_t set to 1 sec for now
#define DELTA_T 1

// ToDo : better values?
#define N_REUSE_LISTS 10
#define DELTA_T_REUSE

/**
 * Per-route configuration
 * XXX: isn't it per bgp_instance configuration ?
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

	double reuse_scale_factor;

	int reuse_list_current_offset;
	int* reuse_lists_index;
	list *reuse_lists;
} damping_config;

// XXX: per route configuration -> yes !
typedef struct {
	// Note : this needs to be first in the struct declaration
	// to simplify access code
	node reuse_list_node;

	int figure_of_merit;
	bird_clock_t last_time_udpated;

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
struct damping_config *new_damping_config(bgp_proto *, int cut_threshold,
                                   int reuse_threshold, int tmax_hold, 
				   int half_time_reachable, int half_time_unreachable);

// Check damping configuration
void damp_check(damping_config *);

#endif /* _DAMPING_H_ */
