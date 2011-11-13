
#include <math.h>

#include "damping.h"

// for now, multiple configurations are not supported
damping_config config;

void damp_init_config(bgp_proto *p, damping_config* conf)
{
	int i;

	conf->decay_array_size = conf->tmax_hold / DELTA_T;
	conf->decay_array = mb_alloc(p->p.pool, conf->decay_array_size * sizeof(double));

	conf->decay_array[0] = 1.0;
	conf->decay_array[1] = exp(log(0.5) * (1.0 / (conf->half_time_unreachable / DELTA_T)));
	for(i = 2; i < conf->decay_array_size; ++i) {
		conf->decay_array[i] = conf->decay_array[i-1] * conf->decay_array[1];
	}
}
