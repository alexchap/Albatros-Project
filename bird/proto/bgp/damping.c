/*
 *      BIRD -- The Border Gateway Protocol
 *
 *      (c) 2011 Alexandre Chappuis <alexandre.chappuis@epfl.ch>,
 *               Bastian Marquis <bastian.marquis@epfl.ch> and
 *               David Klopfenstein <david.klopfenstein@epfl.ch>
 *
 *      Can be freely distributed and used under the terms of the GNU GPL.
 */

/** Doc: BGP Route Flap Damping
 *
 * This is the implementation of RFC 2439 BGP Route flap damping.
 * Routes that are constantly withdrawn and readvertised can be
 * automatically suppressed for a given time, until they become
 * stable again.
 * Each prefix has a penalty. When this penalty excesses a threshold
 * (cut_threshold), the prefix is suppressed. Penalties are decayed over
 * time. Once they sink to a value that is small enough (reuse_threshold),
 * they can be reused.
 *
 * The configuration can be done by BGP instance, first by enabling
 * route damping and then by setting some configuration parameters :
 * -> cut_threshold : the penalty above which a route is suppressed
 * -> reuse_threshold : the penalty below which a route is reused
 * -> tmax_hold : the maximum time a route can be suppressed
 * -> half_time : decay parameter for unreachable routes.
 *
 * There are two main functions that are responsible of updating the
 * penalties for the following events :
 * - Withdrawals are received : damping_remove_route is called
 * - Other updates are received : damping_add_route is called
 *
 * Implementation is done following the requirements of RFC 2439. The
 * system of reuse lists and reuse index arrays is used for efficiency reasons.
 */

#define LOCAL_DEBUG 1

#include <math.h>

#include "nest/bird.h"
#include "lib/timer.h"
#include "nest/cli.h"
#include "conf/conf.h"
#include "bgp.h"
#include "damping.h"

/**
 * A new damping configuration is allocated for the BGP instance
 */
struct damping_config *damping_config_new(int reuse_threshold, int cut_threshold,
    int tmax_hold, int half_time)
{
  struct damping_config * dcf = cfg_alloc(sizeof(damping_config));
  dcf->cut_threshold          = cut_threshold;
  dcf->reuse_threshold        = reuse_threshold;
  dcf->tmax_hold              = tmax_hold;
  dcf->half_time  = half_time;

  DBG("BGP:Damping: New damping_config, with parameters (cut_threshold %d, reuse_threshold %d,"
      "tmax_hold %d, half_time %d)\n",
      cut_threshold, reuse_threshold, tmax_hold, half_time);
  return dcf;
}

// name conflict between bird's log macro and math.h's log function
#ifdef log
#undef log
#endif

/**
 * Once the parameters are known from the configuration file, we can process them
 * to create the runtime configuration. We need to allocate the reuse lists, to
 * compute the decay arrays and compute the ceiling (= max penalty).
 */
void damping_config_init(struct damping_config *dcf)
{

  int i;
  double max_ratio, t;

  dcf->ceiling = (int) ((double)dcf->reuse_threshold * exp((double)dcf->tmax_hold / dcf->half_time) * log(2.0));

  dcf->decay_array_size = dcf->tmax_hold / DELTA_T;
  dcf->decay_array = cfg_alloc(dcf->decay_array_size * sizeof(double));

  dcf->decay_array[0] = 1.0;
  dcf->decay_array[1] = exp(log(0.5) * (1.0 / (dcf->half_time / DELTA_T)));
  for (i = 2; i < dcf->decay_array_size; ++i)
    {
      dcf->decay_array[i] = dcf->decay_array[i-1] * dcf->decay_array[1];
    }

  max_ratio = (double)dcf->ceiling / dcf->reuse_threshold;
  t = exp(log(2.0) / (dcf->half_time / dcf->tmax_hold));
  if (max_ratio > t)
    max_ratio = t;

  dcf->reuse_lists        = cfg_alloc(N_REUSE_LISTS * sizeof(slist));
  dcf->reuse_lists_index  = cfg_alloc(N_REUSE_LISTS * sizeof(int));
  dcf->reuse_scale_factor = ((double)N_REUSE_LISTS / (max_ratio - 1));

  for (i = 0; i < N_REUSE_LISTS; ++i)
    {
      dcf->reuse_lists_index[i] = (int)(((double)dcf->half_time / DELTA_T_REUSE) *
					log(1.0 / ((double)dcf->reuse_threshold * (1.0 + ((double)i / dcf->reuse_scale_factor)))) / log(0.5));

      s_init_list(dcf->reuse_lists + i);
    }
  dcf->reuse_list_current_offset = 0;

  DBG("BGP:Damping: Runtime parameters computed : ceiling %d, decay_array size %d\n",
      dcf->ceiling, dcf->decay_array_size);
  return;
}

/* This function checks the damping parameters */
void damping_config_check(struct damping_config * dcf)
{
  if (dcf->reuse_threshold >= dcf->cut_threshold)
    cf_error("Reuse threshold must be smaller than the cut threshold");

  int ceiling = (int) (dcf->reuse_threshold * exp((double)dcf->tmax_hold / dcf->half_time) * log(2.0));
  if (ceiling <= 0)
    cf_error("Wrong parameters for damping, leading to a negative ceiling !");
  if (ceiling <= dcf->cut_threshold)
    cf_error("Error, the cut threshold must be smaller than the ceiling %d",ceiling);
  return;
}

static inline void damp_free_damping_info(damping_info *info)
{
  rta_free(info->attrs);
}

static inline int is_suppressed(damping_info *info)
{
  return (info->current_reuse_list != NULL);
}

static int get_reuse_list_index(int penalty, struct damping_config *dcf)
{
  double r = ((double)penalty / dcf->cut_threshold) - 1.0;
  int index = r * dcf->reuse_scale_factor;
  if (index >= N_REUSE_LISTS)
    index = N_REUSE_LISTS-1;

  index = dcf->reuse_lists_index[index];
  index = (index + dcf->reuse_list_current_offset) % N_REUSE_LISTS;
  return index;
}

static int get_new_figure_of_merit(damping_info* info,
                                   bird_clock_t n, struct damping_config *dcf)
{
  time_t diff = n - info->last_time_updated;
  int i = diff / DELTA_T;

  if (i >= dcf->decay_array_size)
    {
      return 0;
    }
  else
    {
      return (int)(dcf->decay_array[i] * (double)info->figure_of_merit);
    }
}


/* RFC 2439 §4.8.7 */
#define GET_DAMPING_FROM_NODE(l) \
	(damping_info*)((char*)l - (unsigned long)(&((damping_info*)(NULL))->reuse_list_node))

void damping_reuse_timer_handler(struct timer* t)
{
  DBG("BGP:Damping: Reuse timer event\n");
  damping_config *dcf = (damping_config*)t->data;
  int index;
  damping_info *info;
  snode *n, *nxt;
  rte *tmp_rte;
  struct bgp_proto *p;
  struct proto *pro;
  struct proto_stats *stats;

  // make a copy of the list's head so that it can be reinitialized without
  // losing all informations
  slist l = dcf->reuse_lists[dcf->reuse_list_current_offset];
  s_init_list(&dcf->reuse_lists[dcf->reuse_list_current_offset]);

  tm_start(t, DELTA_T_REUSE);
  if (dcf->reuse_list_current_offset== N_REUSE_LISTS-1)
    {
      dcf->reuse_list_current_offset=0;
    }
  else
    {
      dcf->reuse_list_current_offset++;
    }


  WALK_SLIST_DELSAFE(n, nxt, l)
  {
    info = GET_DAMPING_FROM_NODE(n);
    DBG("BGP:Damping: Penalty found for route %I/%d (%d) and decayed to ",
			info->prefix, info->pxlen, info->figure_of_merit);
    p = info->bgp_connection->bgp;
    pro = &(p->p);
    stats = &(pro->stats);

    info->figure_of_merit = get_new_figure_of_merit(info, now, dcf);
	s_rem_node(&info->reuse_list_node);

    DBG("%d\n", info->figure_of_merit);
    info->last_time_updated = now;

    if (info->figure_of_merit < dcf->reuse_threshold)
      {
        // reuse the route
        DBG("BGP:Damping: This prefix can be reused !");
        tmp_rte      = rte_get_temp(info->attrs);
        tmp_rte->net = net_get(p->p.table, info->prefix, info->pxlen);
        rte_update(p->p.table, tmp_rte->net, &p->p, &p->p, tmp_rte);
		info->current_reuse_list = NULL;
        stats->imp_updates_damped--;
      }
    else
      {
        // Insert into another reuse list
        index = get_reuse_list_index(info->figure_of_merit, dcf);
        s_add_tail(&dcf->reuse_lists[index], &info->reuse_list_node);
        info->current_reuse_list = &(dcf->reuse_lists[index]);
      }
  }
  return;
}

/* RFC 2439 §4.8.2 */
void damping_remove_route(struct bgp_proto *proto, net *n, ip_addr *addr, int pxlen)
{
  DBG("BGP:Damping: damping_remove_route for prefix %I/%d\n", *addr, pxlen);
  damping_info *info          = fib_find(&proto->damping_info_fib, addr, pxlen);
  struct damping_config *dcf  = proto->cf->dcf;
  struct bgp_conn *connection = proto->conn;
  struct proto *pro = &(proto->p);
  struct proto_stats *stats = &(pro->stats);
  struct rte *route;
  time_t t_diff;
  int index;

  if (info == NULL)
    {
      if((route = rte_find(n, &proto->p)) == NULL) {
		  // a withdrawal for a route that doesn't exist was 
		  // received -> exit
		  rte_update(connection->bgp->p.table,
				  n, &(connection->bgp->p),
				  &(connection->bgp->p), NULL);
		  return;
	  }
	  info                    = fib_get(&proto->damping_info_fib, addr, pxlen);
      info->bgp_connection    = connection;
      info->figure_of_merit   = DEFAULT_FIGURE_OF_MERIT;
      info->last_time_updated = now;
      info->prefix            = *addr;
      info->pxlen             = pxlen;
	  info->attrs             = rta_clone(route->attrs);
      rte_update(connection->bgp->p.table,
                 n, &(connection->bgp->p),
                 &(connection->bgp->p), NULL);
      DBG("BGP:Damping: New alloc for prefix %I/%d that is withdrawn\n", *addr, pxlen);
      return;
    }

  t_diff = now - info->last_time_updated;
  index  = t_diff / DELTA_T;
  if (index >= dcf->decay_array_size)
    {
      DBG("BGP:Damping: Penalty reset for prefix %I/%d\n", *addr, pxlen);
      info->figure_of_merit = DEFAULT_FIGURE_OF_MERIT;
    }
  else
    {
      info->figure_of_merit = get_new_figure_of_merit(info, now,dcf) + DEFAULT_FIGURE_OF_MERIT;
      DBG("BGP:Damping: New figure of merit for %I/%d\n : %d\n", *addr,
          pxlen, info->figure_of_merit);
      if (info->figure_of_merit > dcf->ceiling)
        {
          info->figure_of_merit = dcf->ceiling;
          DBG("BGP:Damping: Max penalty for prefix %I/%d\n", *addr, pxlen);
        }
    }

  index = get_reuse_list_index(info->figure_of_merit, dcf);
  if (is_suppressed(info))
    {
      s_rem_node(&info->reuse_list_node);
	  info->current_reuse_list = NULL;
    }
  else
    {
      rte_update(connection->bgp->p.table,
                 n, &(connection->bgp->p),
                 &(connection->bgp->p), NULL);
      stats->imp_updates_damped++;
    }

  DBG("BGP:Damping: Prefix %I/%d added to reuse list\n", *addr, pxlen);
  if (info->figure_of_merit >= dcf->cut_threshold)
    {
      s_add_tail(&(dcf->reuse_lists[index]), &info->reuse_list_node);
      info->current_reuse_list = &(dcf->reuse_lists[index]);
    }
  info->last_time_updated  = now;
  return;
}

/* RFC 2439 §4.8.3 */
void damping_add_route(struct bgp_proto *proto, rte *route, ip_addr *addr, int pxlen)
{
  DBG("BGP:Damping: damping_add_route for prefix %I/%d\n",*addr,pxlen);
  damping_info *info          = fib_find(&proto->damping_info_fib, addr, pxlen);
  damping_config *dcf         = proto->cf->dcf;
  struct bgp_conn *connection = proto->conn;
  struct proto *pro           = &(proto->p);
  struct proto_stats *stats   = &(pro->stats);
  time_t diff;
  int index;

  if (info == NULL)
    {
      // no previous instability history -> just add the route
      rte_update(connection->bgp->p.table,
                 route->net, &(connection->bgp->p),
                 &(connection->bgp->p), route);
      return;
    }

  diff = now - info->last_time_updated;
  index = diff / DELTA_T;
  if (index >= dcf->decay_array_size)
    {
      DBG("BGP:Damping: Penalty reset for prefix %I/%d\n", *addr, pxlen);
      info->figure_of_merit = 0;
    }
  else
    {
      info->figure_of_merit = get_new_figure_of_merit(info, now, dcf);
      DBG("BGP:Damping: New figure of merit for %I/%d : %d\n",
          *addr, pxlen,
          info->figure_of_merit);
    }

  if (!is_suppressed(info) && info->figure_of_merit < dcf->cut_threshold)
    {
      // rte not suppressed and acceptable penalty term -> use it
      DBG("BGP:Damping: Penalty OK (%d/%d) for unsupressed route with prefix %I/%d\n",
          info->figure_of_merit,
          dcf->cut_threshold,
          *addr, pxlen);
      rte_update(connection->bgp->p.table,
                 route->net, &(connection->bgp->p),
                 &(connection->bgp->p), route);
    }
  else if (is_suppressed(info) && info->figure_of_merit < dcf->reuse_threshold)
    {
      s_rem_node(&info->reuse_list_node);
      info->current_reuse_list = NULL;
      DBG("BGP:Damping: Penalty OK (%d/%d) for supressed route with prefix %I/%d\n",
          info->figure_of_merit,
          dcf->cut_threshold,
          *addr, pxlen);
      rte_update(connection->bgp->p.table,
                 route->net, &(connection->bgp->p),
                 &(connection->bgp->p), route);

      stats->imp_updates_damped--;
    }
  else
    {
      index = get_reuse_list_index(info->figure_of_merit, dcf);
      DBG("BGP:Damping: Penalty KO(%d, %d) for prefix %I/%d. Suppressing.\n",
          info->figure_of_merit,
          dcf->cut_threshold,
          *addr, pxlen);
      if (is_suppressed(info))
        {
          s_rem_node(&info->reuse_list_node);
        }
      else
        {
          stats->imp_updates_damped++;
        }
      s_add_tail(&dcf->reuse_lists[index], &info->reuse_list_node);
      info->current_reuse_list = &dcf->reuse_lists[index];
    }

  info->last_time_updated = now;
  if (info->figure_of_merit < dcf->reuse_threshold / 2.0)
    {
      DBG("BGP:Damping: Route %I/%d penalty has reached 0\n", *addr, pxlen);
      damp_free_damping_info(info);
      fib_delete(&proto->damping_info_fib, info);
    }
  return;
}

/* Show dampened path */
void show_dampened_paths(struct proto *p)
{
  struct bgp_proto *proto = (struct bgp_proto *) p;
  struct fib* damping_info_fib = &(proto->damping_info_fib);
  struct damping_info *info;
  int total_routes = 0;

  DBG("BGP:Damping: Show dampened paths called\n");
  cli_msg(-1007,"   Current Route Flap Damping parameters");
  cli_msg(-1007,"     Reuse threshold       : %d", proto->cf->dcf->reuse_threshold);
  cli_msg(-1007,"     Cut threshold         : %d", proto->cf->dcf->cut_threshold);
  cli_msg(-1007,"     Max suppress time     : %d", proto->cf->dcf->tmax_hold);
  cli_msg(-1007,"     Max penalty (ceiling) : %d", proto->cf->dcf->ceiling);
  cli_msg(-1007,"   Dampened routes");

  FIB_WALK(damping_info_fib, fn)
  {
    info = (struct damping_info *) fn;
    if (is_suppressed(info))
      {
        total_routes++;
        cli_msg(-1007,"     %I/%d, current penalty %d, last updated %d seconds ago",
                info->prefix, info->pxlen,info->figure_of_merit, now - info->last_time_updated);

      }
  }
  FIB_WALK_END;
  if (total_routes == 0)
    {
      cli_msg(-1007,"     No route is currently damped. Congrats !");
    }
  else
    {
      cli_msg(-1007,"");
      cli_msg(-1007,"     Total : %d",total_routes);
    }
  cli_msg(0, "");

}

