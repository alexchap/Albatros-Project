#define LOCAL_DEBUG 1

#include <math.h>
#include <assert.h>

#include "nest/bird.h"
#include "lib/timer.h"
#include "bgp.h"
#include "damping.h"
#include "conf/conf.h"



static void damp_free_damping_info(damping_info *info)
{
	rta_free(info->attrs);
	assert(info->current_reuse_list == NULL);
}

static inline int is_suppressed(damping_info *info)
{
	return (info->current_reuse_list == NULL);
}

static int get_reuse_list_index(int penalty,struct damping_config *dcf)
{
	double r = ((double)penalty / dcf->cut_threshold) - 1.0;
	int index = r * dcf->reuse_scale_factor;
	if(index >= N_REUSE_LISTS)
		index = N_REUSE_LISTS-1;

	index = dcf->reuse_lists_index[index];
	index = (index + dcf->reuse_list_current_offset) % N_REUSE_LISTS;
	return index;
}

static int get_new_figure_of_merit(damping_info* info, bird_clock_t n, struct damping_config *dcf)
{
	time_t diff = n - info->last_time_updated;
	int i = diff / DELTA_T;

	if(i >= dcf->decay_array_size)
		return 0;
	else
		return dcf->decay_array[i] * info->figure_of_merit;
}

static void reuse_timer_handler(struct timer* t, struct damping_config *dcf)
{
	int index;
	damping_info *info;
	snode *n, *nxt;
	rte *tmp_rte;
	struct bgp_proto *p;

<<<<<<< HEAD
	// make a copy of the list's head so that it can be reinitialized without
	// losing all informations
	slist l = dcf.reuse_lists[dcf.reuse_list_current_offset];
	s_init_list(&dcf.reuse_lists[dcf.reuse_list_current_offset]);
=======
	// XXX : probably not the best solution : make a shallow copy
	// of the list's head so it can be re-initialized to an empty list
	slist l = dcf->reuse_lists[dcf->reuse_list_current_offset];
	s_init_list(&dcf->reuse_lists[dcf->reuse_list_current_offset]);
>>>>>>> 74ddd9bb14c4a26b937d96281739850fc908cf8b

	tm_start(t, DELTA_T_REUSE);

	dcf->reuse_list_current_offset++;

	WALK_SLIST_DELSAFE(n, nxt, l) {
		info = (damping_info*)n;
		p = info->bgp_connection->bgp;

		info->figure_of_merit = get_new_figure_of_merit(info, now,dcf);
		info->last_time_updated = now;

		if(info->figure_of_merit < dcf->reuse_threshold) {
			tmp_rte = rte_get_temp(info->attrs);
			tmp_rte->net = net_get(p->p.table, info->prefix, info->pxlen);
			rte_update(p->p.table, tmp_rte->net, &p->p, &p->p, tmp_rte);
		} else {
			// put back route into another reuse list
			index = get_reuse_list_index(info->figure_of_merit,dcf);
			s_add_tail(&dcf->reuse_lists[index], n);
			info->current_reuse_list = &(dcf->reuse_lists[index]);
		}
	}
}

// name conflict with math's log function
// use log_tmp instead of log
#ifdef log
	#define log_tmp log
	#undef log
#endif

struct damping_config *damping_config_new(int reuse_threshold, int cut_threshold,int tmax_hold,int half_time_reachable,int half_time_unreachable)
{
	struct damping_config * dcf = cfg_alloc(sizeof(damping_config)); 
	dcf->cut_threshold = cut_threshold;
	dcf->reuse_threshold = reuse_threshold;
	dcf->tmax_hold = tmax_hold;
	dcf->half_time_reachable = half_time_reachable;
	dcf->half_time_unreachable = half_time_unreachable;

	DBG("BGP:Damping : New damping_config, with parameters (%d, %d, %d, %d, %d)\n", cut_threshold,
			reuse_threshold, tmax_hold, half_time_reachable, half_time_unreachable);

	return dcf;

}

// Note : the reuse timer will need to be allocated later (init function?)
// All other parameters, once we know the basic parameters
void damping_config_init(struct damping_config *dcf) {

	int i;
	double max_ratio, t;
	dcf->ceiling = (int) (dcf->reuse_threshold * exp((double)dcf->tmax_hold / dcf->half_time_unreachable) * log(2.0));

	dcf->decay_array_size = dcf->tmax_hold / DELTA_T;
	dcf->decay_array = cfg_alloc(dcf->decay_array_size * sizeof(double));

	dcf->decay_array[0] = 1.0;
	dcf->decay_array[1] = exp(log(0.5) * (1.0 / (dcf->half_time_unreachable / DELTA_T)));
	for(i = 2; i < dcf->decay_array_size; ++i) {
		dcf->decay_array[i] = dcf->decay_array[i-1] * dcf->decay_array[1];
	}

	max_ratio = (double)dcf->ceiling / dcf->reuse_threshold;
	t = exp(log(2.0) / (dcf->half_time_unreachable / dcf->tmax_hold));
	if(max_ratio > t)
		max_ratio = t;

	dcf->reuse_lists = cfg_alloc(N_REUSE_LISTS * sizeof(list));
	dcf->reuse_lists_index = cfg_alloc(N_REUSE_LISTS * sizeof(int));
	dcf->reuse_scale_factor = (double)(N_REUSE_LISTS / (max_ratio - 1));

	for(i = 0; i < N_REUSE_LISTS; ++i) {
		dcf->reuse_lists_index[i] = (int)((dcf->half_time_unreachable / DELTA_T_REUSE) *
				log(1.0 / (dcf->reuse_threshold * (1 + (i / dcf->reuse_scale_factor)))
					/ log(0.5)));
	}

	dcf->reuse_list_current_offset = 0;
	return;
}

/* This function checks the damping parameters */
void damp_check(struct damping_config * dcf)
{
      if(dcf->reuse_threshold >= dcf->cut_threshold)
	    cf_error("Reuse threshold must be smaller than the cut threshold");

      int ceiling = (int) (dcf->reuse_threshold * exp((double)dcf->tmax_hold / dcf->half_time_unreachable) * log(2.0));
      if(ceiling<=0)
	    cf_error("Wrong parameters for damping, leading to a negative ceiling !");

}

void damp_remove_route(struct bgp_proto *proto, net *n, ip_addr *addr, int pxlen)
{
	
	DBG("BGP:Damping: damp_remove_route for prefix %I/%d\n",addr,pxlen);
	damping_info *info = fib_get(&proto->damping_info_fib, addr, pxlen);
	struct damping_config *dcf = proto->cf->dcf;
	struct bgp_conn *connection = proto->conn;
	struct rte *route;
	time_t t_diff;
	int index;

	if(info->bgp_connection == NULL) {
		info->bgp_connection = connection;
		info->figure_of_merit = 1;
		info->last_time_updated = now;
		route = rte_find(n, &proto->p);
		info->attrs = rta_clone(route->attrs);
		if(route == NULL) {
			// ToDo
			// not sure whether this can happen or not
			// given that the route is being removed,
			// it should exist and rte_find should normally
			// not return NULL
			DBG("BGP:Damping : problem with rte_find");
			assert(!"shoulnd't happen");
		}
		DBG("BGP:Damping: New alloc for prefix %I/%d\n",addr,pxlen);
		
		// XXX : hope this will work!
		rte_update(connection->bgp->p.table,
				n, &(connection->bgp->p),
				&(connection->bgp->p), NULL);
		return;
	}

	t_diff = now - info->last_time_updated;
	index = t_diff / DELTA_T;
	if(index >= dcf->decay_array_size) {
		DBG("BGP:Damping: Penalty reset for prefix %I/%d\n",addr,pxlen);
		info->figure_of_merit = 1;
		return;
	}

	info->figure_of_merit = get_new_figure_of_merit(info, now,dcf) +1;
	if(info->figure_of_merit > dcf->ceiling) {
		info->figure_of_merit = dcf->ceiling;
		DBG("BGP:Damping: Max penalty for prefix %I/%d\n",addr,pxlen);
        }
	index = get_reuse_list_index(info->figure_of_merit,dcf);
	if(!is_suppressed(info)) {
		s_rem_node(&(info->reuse_list_node));
		// if the route is not in a reuse list, it has not been suppressed yet,
		// and it needs to be removed
		rte_update(connection->bgp->p.table,
				n, &(connection->bgp->p),
				&(connection->bgp->p), NULL);
	}

	s_add_tail(&(dcf->reuse_lists[index]), &(info->reuse_list_node));
	DBG("BGP:Damping: Prefix %I/%d added to reuse list\n",addr,pxlen);
	info->current_reuse_list = &(dcf->reuse_lists[index]);
}

void damp_add_route(struct bgp_proto *proto, rte *route, ip_addr *addr, int pxlen)
{
	
	damping_info *info = fib_find(&proto->damping_info_fib, addr, pxlen);
	struct damping_config *dcf = proto->cf->dcf;
	struct bgp_conn *connection = proto->conn;
	time_t diff;
	int index;

	if(info == NULL) {
		rte_update(connection->bgp->p.table,
				route->net, &(connection->bgp->p),
				&(connection->bgp->p), route);
		return;
	}

	diff = now - info->last_time_updated;
	index = diff / DELTA_T;
	if(index >= dcf->decay_array_size) {
		DBG("BGP:Damping: Penalty reset for prefix %I/%d\n",addr,pxlen);
		info->figure_of_merit = 0;
	} else {
		info->figure_of_merit = get_new_figure_of_merit(info, now,dcf);
	}
	if(!is_suppressed(info) && info->figure_of_merit < dcf->cut_threshold) {
		// rte not suppressed and acceptable penalty term -> use it
		DBG("BGP:Damping: Penalty OK for prefix %I/%d\n",addr,pxlen);
		rte_update(connection->bgp->p.table,
				route->net, &(connection->bgp->p),
				&(connection->bgp->p), route);
	} else if(is_suppressed(info) && info->figure_of_merit < dcf->reuse_threshold) {
		s_rem_node((snode*)info);
		info->current_reuse_list = NULL;
		DBG("BGP:Damping: Penalty OK for prefix %I/%d\n",addr,pxlen);
		rte_update(connection->bgp->p.table,
				route->net, &(connection->bgp->p),
				&(connection->bgp->p), route);
	} else {
		index = get_reuse_list_index(info->figure_of_merit,dcf);
		if(is_suppressed(info))
			s_rem_node((snode*)info);
		DBG("BGP:Damping: Penalty KO for prefix %I/%d. It will be suppressed.\n",addr,pxlen);
		s_add_tail(&dcf->reuse_lists[index], (snode*)info);
		info->current_reuse_list = &dcf->reuse_lists[index];
	}

	if(info->figure_of_merit > 0) {
		info->last_time_updated = now;
	} else {
		damp_free_damping_info(info);
		// Note : do fib_delete also de-allocate memory?
		fib_delete(&proto->damping_info_fib, info);
	}
}

