# -*- coding: utf-8
'''
Created on 13 мая 2014 г.

@author: pavel
'''

import nnsim_pykernel
import numpy as np
np.random.seed(seed=0)

MeanSpkPeriod = 20.

psn_tau = 3.

exc_neur_param = {'a': 0.02, 'b': 0.5, 'c': -40., 'd': 100., 'k': 0.5, 'Cm': 50., 
                       'Vr': -60., 'Vt': -45., 'Vpeak': 40., 'Vm': -60., 'Um': 0., 
                       'Erev_AMPA': 0., 'Erev_GABBA': -70., 'Isyn': 0., 'Ie': 0.,
                       'psn_seed': None, 'psn_rate': 0., 'psn_weight': 1.}

inh_neur_param = {'a': 0.03, 'b': -2.0, 'c': -50., 'd': 100., 'k': 0.7, 'Cm': 100., 
                       'Vr': -60., 'Vt': -40., 'Vpeak': 35., 'Vm': -60., 'Um': 0., 
                       'Erev_AMPA': 0., 'Erev_GABBA': -70., 'Isyn': 0., 'Ie': 0.,
                       'psn_seed': None, 'psn_rate': 0., 'psn_weight': 1.}

exc_syn_param = {'tau_psc': 3., 'tau_rec': 800., 'tau_fac': 0.00001, 
                      'U': 0.5, 'receptor_type': 1}

inh_syn_param = {'tau_psc': 7., 'tau_rec': 100., 'tau_fac': 1000., 
                      'U': 0.04, 'receptor_type': 2}

syn_default = {'y': 0., 'x': 1., 'u': 0., 'weight': 1., 'delay': 0.}

neur_arr = {'a': [], 'b': [], 'c': [], 'd': [], 'k': [], 'Cm': [], 
                       'Vr': [], 'Vt': [], 'Vpeak': [], 'Vm': [], 'Um': [], 
                       'Erev_AMPA': [], 'Erev_GABBA': [], 'Isyn': [], 'Ie': [], 
                       'psn_seed': [], 'psn_rate': [], 'psn_weight': []}

syn_arr = {'tau_psc': [], 'tau_rec': [], 'tau_fac': [], 'U': [], 
                    'y': [], 'x': [], 'u': [], 'weight': [], 'delay': [], 
                    'pre': [], 'post': [], 'receptor_type': []}

NumNodes = 0

NumConns = 0

def check_type(arg, ar_type=int):
    if type(arg) == list:
        for i in arg:
            if type(i) != ar_type:
                raise RuntimeError("Argument must be " + str(ar_type) + "or list of " + str(ar_type))
        return arg
    elif type(arg) != ar_type:
        raise RuntimeError("Argument must be " + str(ar_type) + "or list of " + str(ar_type))
    return [arg]
    
def fill_neurs(N, default_params, **kwargs):
    global neur_arr, NumNodes

    for key, value in kwargs.items():
        if type(value) != dict:
            neur_arr[key].extend([value]*N)
        elif type(value) == dict:
            std = value['std']
            mean = value['mean']
            neur_arr[key].extend(mean + std*np.random.randn(N))
        default_params.pop(key)
        
    for key, value in default_params.items():
            neur_arr[key].extend([value]*N)
    NumNodes += N
    return [i for i in xrange(NumNodes - N, NumNodes)]

def create(N, n_type="exc", **kwargs):
    if n_type == "exc":
        return fill_neurs(N, default_params=exc_neur_param, **kwargs)
    elif n_type == "inh":
        return fill_neurs(N, default_params=inh_neur_param, **kwargs)

def connect(pre, post, conn_spec='one_to_one', syn='exc', **kwargs):
    global syn_arr, NumConns
    pre = check_type(pre)
    post = check_type(post)
    pre_ext = []
    post_ext = []
    syn_ext ={}
    if(conn_spec == 'one_to_one'):
        if (len(pre) != len(post)):
                raise RuntimeError("Lengths of pre and post must be equal")
        pre_ext = pre
        post_ext = post
    elif (conn_spec == 'all_to_all'):
        for i in pre:
            pre_ext.extend([i]*len(post))
            post_ext.extend(post)
    elif type(conn_spec) == dict:
        if conn_spec['rule'] == 'fixed_total_num':
            for i in xrange(conn_spec['N']):
                pre_ext.append(pre[np.random.randint(len(pre))])
                post_ext.append(post[np.random.randint(len(post))])
    if (syn == "exc"):
        for key, value in exc_syn_param.items():
            syn_ext[key] = [value]*len(pre_ext)
    elif (syn == "inh"):
        for key, value in inh_syn_param.items():
            syn_ext[key] = [value]*len(pre_ext)
    
    for key, value in syn_default.items():
            syn_ext[key] = [value]*len(pre_ext)
    
    for key, value in kwargs.items():
        if type(value) != dict:
            syn_ext[key] = [value]*len(pre_ext)
        elif type(value) == dict:
            std = value['std']
            mean = value['mean']
            syn_ext[key] = np.array(mean + std*np.random.randn(len(pre_ext)), dtype='float32')

    syn_ext['pre'] = pre_ext
    syn_ext['post'] = post_ext
    for key, value in syn_ext.items():
        syn_arr[key].extend(value)

    NumConns += len(pre_ext)
    
    return [i for i in xrange(NumConns - len(pre_ext), NumConns)]

def init_recorder(rec_from_n=[], rec_from_s=[]):
    global rec_from_neur, rec_from_syn
    rec_from_neur = check_type(rec_from_n)
    rec_from_syn = check_type(rec_from_s)

def get_results():
    (Vm_, Um_, Isyn_, x_, y_, u_) = nnsim_pykernel.get_results()
    Vm = []
    Um = []
    Isyn = []
    x = []
    y = []
    u = []
    if len(Vm_) == 0:
        return (Vm, Um, Isyn, x, y, u)
        
    start = 0
    Tsim = len(Vm_)/len(rec_from_neur)
    stop = Tsim
    for i in range(len(rec_from_neur)):
        Vm.append(Vm_[start:stop])
        Um.append(Um_[start:stop])
        Isyn.append(Isyn_[start:stop])
        stop += Tsim
        start += Tsim
    
    if len(x_) == 0:
        return (Vm, Um, Isyn, x, y, u)

    start = 0
    Tsim = len(x_)/len(rec_from_syn)
    stop = Tsim
    for i in range(len(rec_from_syn)):
        x.append(x_[start:stop])
        y.append(y_[start:stop])
        u.append(u_[start:stop])
        stop += Tsim
        start += Tsim
    
    return (Vm, Um, Isyn, x, y, u)

def get_spk_times():
    global spk_times, n_spike
    (spk_times, n_spike) = nnsim_pykernel.get_spk_times()
   
    spikes = []
    for i in xrange(NumNodes):
        spikes.append([spk_times[NumNodes*sn + i]*tm_step for sn in xrange(n_spike[i])])
    return spikes

def order_spikes(spikes):
    times = []
    senders = []
    for i in xrange(NumNodes):
        times.extend(spikes[i])
        senders.extend([i]*len(spikes[i]))
    return (times, senders)

def simulate(h, SimTime):
    global tm_step
    tm_step = h
    nnsim_pykernel.init_network(h, NumNodes, NumConns, SimTime)
    psn_keys = ['psn_seed', 'psn_rate', 'psn_weight']

    args = {}
    for key, val in neur_arr.items():
        if key not in psn_keys:
            args[key] = np.array(val, dtype='float32')
    nnsim_pykernel.init_neurs(**args)

    psn_args = {}
    psn_args['psn_seed'] = np.array(np.random.randint(2147483647, size=NumNodes), dtype='uint32')
    for i in xrange(NumNodes):
        if neur_arr['psn_seed'][i] != None:
            psn_args['psn_seed'][i] = neur_arr['psn_seed'][i]

    psn_args['psn_rate'] = np.array(neur_arr['psn_rate'], dtype='float32')
    psn_args['psn_weight'] = np.array(neur_arr['psn_weight'], dtype='float32')
    psn_args['psn_tau'] = psn_tau
    nnsim_pykernel.init_poisson(**psn_args)
    
    args = {}
    for key, val in syn_arr.items():
        args[key] = np.array(val, dtype='float32')
    for key in ['pre', 'post', 'receptor_type']:
        args[key] = np.array(syn_arr[key], dtype='uint32')
    nnsim_pykernel.init_synapses(**args)
    
    args = {}
    args['sps_times'] = np.zeros(NumNodes*SimTime/MeanSpkPeriod, dtype='uint32')
    args['neur_num_spk'] = np.zeros(NumNodes, dtype='uint32')
    args['syn_num_spk'] = np.zeros(NumConns, dtype='uint32')
    nnsim_pykernel.init_spikes(**args)
    
    nnsim_pykernel.init_recorder(len(rec_from_neur), rec_from_neur, 
                                 len(rec_from_syn), rec_from_syn)

    nnsim_pykernel.simulate()


print "  --NNSIM--  "
