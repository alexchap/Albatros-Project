
#include <math.h>

#include "damping.h"

// for now, multiple configurations are not supported
damping_config config;

void damp_init_config(bgp_proto *p, damping_config* conf)
{
	int i;
	double max_ratio, t;

	conf->ceiling = conf->reuse_threshold * exp(conf->tmax_hold / conf->half_time_unreachable) * log(2.0);

	conf->decay_array_size = conf->tmax_hold / DELTA_T;
	conf->decay_array = mb_alloc(p->p.pool, conf->decay_array_size * sizeof(double));

	conf->decay_array[0] = 1.0;
	conf->decay_array[1] = exp(log(0.5) * (1.0 / (conf->half_time_unreachable / DELTA_T)));
	for(i = 2; i < conf->decay_array_size; ++i) {
		conf->decay_array[i] = conf->decay_array[i-1] * conf->decay_array[1];
	}

	max_ratio = (double)conf->ceiling / conf->reuse_threshold;
	t = exp(log(2.0) / (conf->half_time_unreachable / conf->tmax_hold));
	if(max_ratio > t)
		max_ratio = t;

	conf->reuse_lists = mb_alloc(p->p.pool, N_REUSE_LISTS * sizeof(list));
	conf->reuse_lists_index = mb_alloc(p->p.pool, N_REUSE_LISTS * sizeof(int));
	conf->reuse_scale_factor = (double)(N_REUSE_LISTS / (max_ratio - 1));

	for(i = 0; i < N_REUSE_LISTS; ++i) {
		conf->reuse_lists_index = (int)((conf->half_time_unreachable / DELTA_T_REUSE) *
				log(1.0 / (conf->reuse_threshold * (1 + (i / scale_factor))) / log(0.5)));
	}
}
