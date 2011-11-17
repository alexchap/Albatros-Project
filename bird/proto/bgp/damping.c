#include <math.h>

#include "nest/bird.h"

#include "lib/slists.h"
#include "lib/timer.h"

#include "bgp.h"
#include "damping.h"

damping_config dcf;

static int get_reuse_list_index(int penalty)
{
	double r = ((double)penalty / dcf.cut_threshold) - 1.0;
	int index = r * dcf.reuse_scale_factor;
	if(index >= N_REUSE_LISTS)
		index = N_REUSE_LISTS-1;

	index = dcf.reuse_lists_index[index];
	index = (index + dcf.reuse_list_current_offset) % N_REUSE_LISTS;
	return index;
}

static int get_new_figure_of_merit(damping_info* info, bird_clock_t n)
{
	time_t diff = n - info->last_time_updated;
	int i = diff / DELTA_T;

	if(i >= dcf.decay_array_size)
		return 0;
	else
		return dcf.decay_array[i] * info->figure_of_merit;
}

// Note : will need some synchronization primitives for that!
static void reuse_timer_handler(void)
{
	int index;
	damping_info *info;
	snode *n;

	// reset timer

	// XXX : probably not the best solution : make a shallow copy
	// of the list's head so it can be re-initialized to an empty list
	slist l = dcf.reuse_lists[dcf.reuse_list_current_offset];
	s_init_list(&dcf.reuse_lists[dcf.reuse_list_current_offset]);

	dcf.reuse_list_current_offset++;

	WALK_SLIST(n, l) {
		info = (damping_info*)n;

		info->figure_of_merit = get_new_figure_of_merit(info, now);
		info->last_time_updated = now;

		if(info->figure_of_merit < dcf.reuse_threshold) {
			// reuse route
		} else {
			// put back route into another reuse list
			index = get_reuse_list_index(info->figure_of_merit);
			s_add_tail(&dcf.reuse_lists[index], n);
		}
	}
}

// name conflict with math's log function
// use log_tmp instead of log
#ifdef log
	#define log_tmp log
	#undef log
#endif

struct damping_config *new_damping_config(struct bgp_proto *p,
		int cut_threshold, int reuse_threshold,
		int tmax_hold,     int half_time_reachable,
		int half_time_unreachable)
{
	int i;
	double max_ratio, t;

	dcf.cut_threshold = cut_threshold;
	dcf.reuse_threshold = reuse_threshold;
	dcf.tmax_hold = tmax_hold;
	dcf.half_time_reachable = half_time_reachable;
	dcf.half_time_unreachable = half_time_unreachable;

	dcf.ceiling = dcf.reuse_threshold * exp(dcf.tmax_hold / dcf.half_time_unreachable) * log(2.0);

	dcf.decay_array_size = dcf.tmax_hold / DELTA_T;
	dcf.decay_array = mb_alloc(p->p.pool, dcf.decay_array_size * sizeof(double));

	dcf.decay_array[0] = 1.0;
	dcf.decay_array[1] = exp(log(0.5) * (1.0 / (dcf.half_time_unreachable / DELTA_T)));
	for(i = 2; i < dcf.decay_array_size; ++i) {
		dcf.decay_array[i] = dcf.decay_array[i-1] * dcf.decay_array[1];
	}

	max_ratio = (double)dcf.ceiling / dcf.reuse_threshold;
	t = exp(log(2.0) / (dcf.half_time_unreachable / dcf.tmax_hold));
	if(max_ratio > t)
		max_ratio = t;

	dcf.reuse_lists = mb_alloc(p->p.pool, N_REUSE_LISTS * sizeof(list));
	dcf.reuse_lists_index = mb_alloc(p->p.pool, N_REUSE_LISTS * sizeof(int));
	dcf.reuse_scale_factor = (double)(N_REUSE_LISTS / (max_ratio - 1));

	for(i = 0; i < N_REUSE_LISTS; ++i) {
		dcf.reuse_lists_index = (int)((dcf.half_time_unreachable / DELTA_T_REUSE) *
				log(1.0 / (dcf.reuse_threshold * (1 + (i / dcf.reuse_scale_factor)))
					/ log(0.5)));
	}

	dcf.reuse_list_current_offset = 0;
	return &dcf;
}

/* This function checks the damping parameters */
void damp_check(struct damping_config *dcf) {
      // TODO: check parameters !
}
