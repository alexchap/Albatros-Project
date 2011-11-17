#include <math.h>

#include "lib/slists.h"
#include "lib/timer.h"

#include "damping.h"

damping_config dcf;

static int get_reuse_list_index(int penalty)
{
	double r = ((double)penalty / config.cut_threshold) - 1.0;
	int index = r * config.scale_factor;
	if(index >= N_REUSE_LISTS)
		index = N_REUSE_LISTS-1;

	index = config.reuse_lists_index[index];
	index = (index + config.reuse_list_current_offset) % N_REUSE_LISTS;
	return index;
}

static int get_new_figure_of_merit(damping_info* info, bird_clock_t n)
{
	clock_diff_t diff = n - info->last_time_updated;
	int i = diff / DELTA_T;

	if(i >= info->decay_array_size)
		return 0;
	else
		return info->decay_array[i] * info->figure_of_merit;
}

// Note : will need some synchronization primitives for that!
static void reuse_timer_handler()
{
	int index;
	damp_info *info;
	snode *n;
	bird_clock_t t_diff;

	// reset timer

	// XXX : probably not the best solution : make a shallow copy
	// of the list's head so it can be re-initialized to an empty list
	slist l = config.reuse_lists[config.reuse_list_current_offset];
	s_init(&config.reuse_lists[config.reuse_list_current_offset]);

	config.reuse_list_current_offset++;

	WALK_SLIST(n, &l) {
		info = (damp_info*)n;

		info->figure_of_merit = get_new_figure_of_merit(info, now);
		info->last_time_updated = now;

		if(info->figure_of_merit < config.reuse_threshold) {
			// reuse route
		} else {
			// put back route into another reuse list
			index = get_reuse_list_index(info->figure_of_merit);
			s_add_tail(&config.reuse_lists[index], n);
		}
	}
}

struct damping_config *new_damping_config(bgp_proto *p, int cut_threshold, int reuse_threshold,
		int tmax_hold, int half_time_reachable, int half_time_unreachable)
{
         // XXX : is that accurate ?
        struct damping_config *conf = cfg_allocz(sizof(damping_config));
	conf->cut_threshold = cut_threshold;
	conf->reuse_threshold = reuse_threshold;
	conf->tmax_hold = tmax_hold;
	conf->half_time_reachable = half_time_reachable;
	conf->half_time_unreachable = half_time_unreachable;

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

	conf->reuse_list_current_offset = 0;
	//XXX : is that right ? return pointer to configuration ?!
	return &conf;
}

/* This function check the damping parameters */
void damp_check(struct damping_config *dcf) {
      // TODO: check parameters !

}
