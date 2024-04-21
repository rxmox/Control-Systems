import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
import math
import control as ct


def eval_poly(poly, k):
    n = poly.shape[0] - 1

    p_at_k = 0
    for ii in range(n+1):
        p_at_k += poly[ii]*k**(n-ii)
    
    return p_at_k


def enel441_partial_fraction_expansion(num, den):
    ## returns partial fraction expansion. This function cannot deal with repeated poles. I will fail in that case.

    poles = np.roots(den)
    num_poles = poles.shape[0]
    coeff = np.zeros(num_poles, dtype=np.csingle)

    for ii in range(num_poles):
        nn = eval_poly(num, poles[ii])
        dd = 1
        for jj in range(num_poles):
            if ii != jj:
                dd *= (poles[ii] - poles[jj])
        
        coeff[ii] = nn/dd
    return poles, coeff
            
            
def enel441_step_response(num, den, t, fig=[], ax=[]):
    if not fig: 
        fig, ax = plt.subplots(1,1)

    poles, coefficients = enel441_partial_fraction_expansion(num, den)

    # Plot the step reponse (assume initial conditions are zero)
    N = t.shape[0]
    out_step = np.zeros(N, dtype=np.csingle)
    for ii in range(poles.shape[0]):
        out_step += coefficients[ii]*np.exp(poles[ii]*t)
    
    ax.plot(t,out_step.real, label='Step Response')
    ax.set_title(r'Step response')
    ax.set_xlabel('Time (s)')

    plt.xlim(t[0], t[-1])

    return fig, ax, out_step


def enel441_rise_time(t, out_step, ax):
    final_value = out_step[-1]
    
    ii = 0
    while out_step[ii] < final_value*0.1:
        ii += 1
    
    start_index = ii
    
    while out_step[ii] < final_value*0.9:
        ii += 1
        
    end_index = ii
    
    
    rise_time = t[end_index] - t[start_index]
    
    ax.plot(t[start_index], out_step[start_index], 'k.')
    ax.plot(t[end_index], out_step[end_index], 'k.')
    
    ax.plot([t[0], t[start_index]], [out_step[start_index], out_step[start_index]], 'k:')
    ax.plot([t[start_index], t[start_index]], [out_step[start_index], 0], 'k:')
    ax.plot([t[0], t[end_index]], [out_step[end_index], out_step[end_index]], 'k:')
    ax.plot([t[end_index], t[end_index]], [out_step[end_index], 0], 'k:')
    
    ax.arrow(t[start_index], out_step[start_index], rise_time, 0, head_length = 0.1, head_width = 0.025, length_includes_head = True )
    ax.arrow(t[end_index], out_step[start_index], -rise_time, 0, head_length = 0.1, head_width = 0.025, length_includes_head = True )
    
    ax.text(t[start_index] + rise_time/2, out_step[start_index] + 0.05, 'Tr', horizontalalignment='center')
    return rise_time


def enel441_peak_overshoot(t, out_step, ax):
    final_value = out_step[-1]
    
    index_peak_overshoot = np.argmax(out_step)
    peak_overshoot = out_step[index_peak_overshoot]
    peak_overshoot_percent = (peak_overshoot-final_value)/final_value*100
    
    ax.plot(t[index_peak_overshoot], peak_overshoot, 'k.')
    
    ax.plot([t[0], t[-1]], [final_value, final_value], 'k:')
    ax.plot([t[0], t[index_peak_overshoot]], [peak_overshoot, peak_overshoot], 'k:')
    ax.plot([t[index_peak_overshoot], t[index_peak_overshoot]], [peak_overshoot, 0], 'k:')
    
    ax.arrow(t[index_peak_overshoot], final_value, 0, peak_overshoot-final_value, head_length = 0.1, head_width = 0.025, length_includes_head = True )
    ax.arrow(t[index_peak_overshoot], peak_overshoot, 0, -peak_overshoot+final_value, head_length = 0.1, head_width = 0.025, length_includes_head = True )
    
    ax.text(t[index_peak_overshoot], final_value + (peak_overshoot-final_value)/2, 'PO', verticalalignment='center')
    
    return t[index_peak_overshoot], peak_overshoot_percent



def enel441_settling_time(t, out_step, ax):
    final_value = out_step[-1]
    
    ii = t.shape[0] - 1
    while out_step[ii] < 1.02*final_value and out_step[ii] > 0.98*final_value:
        ii -= 1
    
    index_settling_time = ii   
    
    ax.plot(t[index_settling_time], out_step[index_settling_time], 'k.')
    
    #uncomment to add annotations (when your function is ready)
    ax.plot([t[0], t[-1]], [0.98*final_value, 0.98*final_value], 'k:')
    ax.plot([t[0], t[-1]], [1.02*final_value, 1.02*final_value], 'k:')
    if out_step[index_settling_time] > final_value:
        ax.text(t[index_settling_time], out_step[index_settling_time], 'Ts', verticalalignment='bottom')
    else:
        ax.text(t[index_settling_time], out_step[index_settling_time], 'Ts', verticalalignment='top')
    
    return t[index_settling_time]


def enel441_s_plane_plot(num_sys, den_sys, fig=[], ax=[]):
    if not fig: 
        fig, ax = plt.subplots(1,1)
    
    poles_sys = np.roots(den_sys)
    for pp in poles_sys:
        ax.plot(np.real(pp), np.imag(pp), 'bx' )

    zeros_sys = np.roots(num_sys)
    for zz in zeros_sys:
        ax.plot(np.real(zz), np.imag(zz), 'ro')

    x_min1 = np.min(np.real(poles_sys))-0.5
    if zeros_sys.shape[0] > 0:
        x_min2 = np.min(np.real(zeros_sys))-0.5
    else: x_min2 = 0
    x_min3 = -0.5

    x_max1 = np.max(np.real(poles_sys))+0.5
    if zeros_sys.shape[0] > 0:
        x_max2 = np.max(np.real(zeros_sys))+0.5
    else:
        x_max2 = 0
    x_max3 = 0.5

    plt.xlim(np.min(np.array([x_min1, x_min2, x_min3])), np.max(np.array([x_max1, x_max2, x_max3])))
    ax.grid(True)
    ax.spines['left'].set_position('zero')
    # turn off the right spine/ticks
    ax.spines['right'].set_color('none')
    ax.yaxis.tick_left()
    # set the y-spine
    ax.spines['bottom'].set_position('zero')

    # turn off the top spine/ticks
    ax.spines['top'].set_color('none')
    ax.xaxis.tick_bottom()
    ax.set_title('S-Plane Plot')
    ax.set_xlabel('Real[s]')
    ax.set_ylabel('Imag[s]')

    ax.xaxis.set_label_coords(0.5,-0.01)
    ax.yaxis.set_label_coords(-0.01,0.5)
    return fig, ax

def roots_to_polynomial(roots_poly):
    poly = np.array([1])
    for rr in roots_poly:
        poly = np.convolve(poly, np.array([1, -rr]))
    return np.real(poly)


def enel441_plot_step_response_bounds_per_pole(num, den, t, ax):
    N = t.shape[0]
    
    poles, coefficients = enel441_partial_fraction_expansion(num, den)
    num_poles = poles.shape[0]

    resp_poles = np.zeros((N,num_poles))
    pole_strs = []
    jj = 0
    is_step_resp = False
    for ii in range(num_poles):
        if np.abs(poles[ii]) > 1e-10:
            resp_poles[:,jj] = 2*np.abs(coefficients[ii])*np.exp(np.real(poles[ii])*t)  # bound is due to real portion of pole only
            pole_strs.append('{:.2f}'.format(poles[ii]))
            jj += 1
        else: 
            offset = np.abs(coefficients[ii])
            is_step_resp = True
    
    if is_step_resp:
        for ii in range(num_poles-1):
            ax.plot(t, resp_poles[:,ii]+offset, '--', color='C'+str(ii), label='p='+pole_strs[ii])
            ax.plot(t, -resp_poles[:,ii]+offset, '--', color='C'+str(ii))
    else:
        for ii in range(num_poles):
            ax.plot(t, resp_poles[:,ii], '--', color='C'+str(ii), label='p='+pole_strs[ii])
            ax.plot(t, -resp_poles[:,ii], '--', color='C'+str(ii))

    ax.legend()  




def enel441_get_reasonable_freq_range(num, den, N):
    roots_den = np.roots(den)
    den_corner_freqs = np.abs(roots_den)
    
    if num.shape[0]>1:
        roots_num = np.roots(num)   
        num_corner_freqs = np.abs(roots_num)
        omega_min = np.min( [np.min(den_corner_freqs), np.min(num_corner_freqs)] )
        omega_max = np.max( [np.max(den_corner_freqs), np.max(num_corner_freqs)] )
    else:
        omega_min = np.min(den_corner_freqs)
        omega_max = np.max(den_corner_freqs)
        
    omega = np.logspace(np.log10(omega_min/100),np.log10(omega_max*100),num=N)
    return omega


def enel441_fourier_transform(num,den,omega):
    N = omega.shape[0]
    
    G_jw = np.zeros(N,dtype=np.csingle)
       
    ii = 0
    for w in omega:
        jomega = 1j*w
        num_jw = 0
        jj = num.shape[0] - 1
        for nn in num:
            num_jw += nn*(jomega**jj)
            jj -= 1
        
        den_jw = 0
        jj = den.shape[0] - 1
        for dd in den:
            den_jw += dd*(jomega**jj)
            jj -= 1
        #print(den_jw)
        #print(num_jw)
        G_jw[ii] = num_jw/den_jw
        ii += 1
    return G_jw

def find_nearest(arr, value):
    idx = (np.abs(arr - value)).argmin()
    return idx

def get_range_X(num,den,N):

    roots_den = np.roots(den)
    roots_num = np.roots(num)
    den_corner_freqs = np.abs(roots_den)
    num_corner_freqs = np.abs(roots_num)

    omega_min = np.min( [np.min(den_corner_freqs), np.min(num_corner_freqs)] )
    omega_max = np.max( [np.max(den_corner_freqs), np.max(num_corner_freqs)] )
    omega = np.logspace(np.log10(omega_min/100),np.log10(omega_max*100),num=N)
    return omega



def enel441_approximate_bode(num_sys,den_sys,omega):
    N = omega.shape[0]
    
    roots_den = np.roots(den_sys)
    den_corner_freqs = np.abs(roots_den)
    num_poles = roots_den.shape[0]
    
    if num_sys.shape[0]>1:
        roots_num = np.roots(num_sys)
        num_corner_freqs = np.abs(roots_num)
        num_zeros = roots_num.shape[0] 
    else:
        num_zeros = 0
        num_corner_freqs = []
        roots_num = []

    # calculate DC offset
    dc_offset = num_sys[0]/den_sys[0]
    for rr in roots_den:
        dc_offset /= rr

    for rr in roots_num:
        dc_offset *= rr

    dc_offset = 20*np.log10(np.abs(dc_offset))


    pole_approx_mag = np.zeros((N,num_poles))
    pole_approx_phase = np.zeros((N,num_poles))
    slope_neg = -20*np.log10(omega)
    ii = 0
    print(num_poles)
    print(den_corner_freqs)
    for cf in den_corner_freqs:
        corner_idx = find_nearest(omega,cf)
        pole_approx_mag[corner_idx:N,ii] = slope_neg[corner_idx:N] - slope_neg[corner_idx]
        p1 = find_nearest(omega,cf/10)
        p2 = find_nearest(omega,cf*10)
        pole_approx_phase[p1:p2,ii] = -np.linspace(0,math.pi/2,p2-p1)
        pole_approx_phase[p2:N,ii] = -math.pi/2
        ii += 1

    zero_approx_mag = np.zeros((N,num_zeros))
    zero_approx_phase = np.zeros((N,num_zeros))
    slope_pos = 20*np.log10(omega)
    ii = 0
    for cf in num_corner_freqs:
        corner_idx = find_nearest(omega,cf)
        zero_approx_mag[corner_idx:N,ii] = slope_pos[corner_idx:N] - slope_pos[corner_idx]
        p1 = find_nearest(omega,cf/10)
        p2 = find_nearest(omega,cf*10)
        zero_approx_phase[p1:p2,ii] = np.linspace(0,math.pi/2,p2-p1)
        zero_approx_phase[p2:N,ii] = math.pi/2
        ii += 1

    approx_response_mag = np.sum(pole_approx_mag, axis=1) + np.sum(zero_approx_mag, axis=1) + dc_offset
    approx_response_phase = np.sum(pole_approx_phase, axis=1) + np.sum(zero_approx_phase, axis=1)

    fig, ax = plt.subplots(num_poles+num_zeros+1,2, figsize=(6.4*2,(num_poles+num_zeros+1)*2))
    for ii in range(num_poles):
        ax[ii,0].semilogx(omega,pole_approx_mag[:,ii], label='pole={:.2f}'.format(roots_den[ii]))
        ax[ii,0].legend()
        ax[ii,0].set_xlabel('Frequency (rad)')
        ax[ii,0].set_ylabel('Mag (dB)')
        ax[ii,0].set_title('Magnitude - Pole Approximation')

        ax[ii,1].semilogx(omega,pole_approx_phase[:,ii], label='pole={:.2f}'.format(roots_den[ii]))
        ax[ii,1].legend()
        ax[ii,1].set_xlabel('Frequency (rad)')
        ax[ii,1].set_ylabel('Freq (rad)')
        ax[ii,1].set_title('Phase - Pole Approximation')

    for ii in range(num_zeros):
        ax[num_poles+ii,0].semilogx(omega,zero_approx_mag[:,ii], label='zero={:.2f}'.format(roots_num[ii]))
        ax[num_poles+ii,0].legend()
        ax[num_poles+ii,0].set_xlabel('Frequency (rad)')
        ax[num_poles+ii,0].set_ylabel('Mag (dB)')
        ax[num_poles+ii,0].set_title('Magnitude - Zero Approximation')

        ax[num_poles+ii,1].semilogx(omega,zero_approx_phase[:,ii], label='zero={:.2f}'.format(roots_num[ii]))
        ax[num_poles+ii,1].legend()
        ax[num_poles+ii,1].set_xlabel('Frequency (rad)')
        ax[num_poles+ii,1].set_ylabel('Freq (rad)')
        ax[num_poles+ii,1].set_title('Phase - Zero Approximation')

    G_jw = enel441_fourier_transform(num_sys,den_sys,omega)
    ax[num_poles+num_zeros,0].semilogx(omega,20*np.log10(np.absolute(G_jw)), label='Actual')
    ax[num_poles+num_zeros,0].semilogx(omega,approx_response_mag, label='Approximation')
    ax[num_poles+num_zeros,0].set_title('Magnitude Response of System')
    ax[num_poles+num_zeros,0].set_xlabel('Frequency (rad)')
    ax[num_poles+num_zeros,0].set_ylabel('Magnitude (dB)')
    ax[num_poles+num_zeros,0].legend()

    ax[num_poles+num_zeros,1].semilogx(omega,np.angle(G_jw), label='Actual')
    ax[num_poles+num_zeros,1].semilogx(omega,approx_response_phase, label='Approximation')
    ax[num_poles+num_zeros,1].set_title('Phase Response of System')
    ax[num_poles+num_zeros,1].set_xlabel('Frequency (rad)')
    ax[num_poles+num_zeros,1].set_ylabel('Phase (rad)')
    ax[num_poles+num_zeros,1].legend()

    fig.tight_layout(pad=1.5)
    plt.show()



def enel441_annotated_bode_plot(num, den, omega):    
    roots_den = np.roots(den)
    den_corner_freqs = np.abs(roots_den)
    
    if num.shape[0]>1:
        roots_num = np.roots(num)
        num_corner_freqs = np.abs(roots_num)
    else:
        num_corner_freqs = np.array([])
        
    den_corner_freqs = np.array([])
    num_corner_freqs = np.array([])
    
    corner_freq_indeces_poles = np.zeros(den_corner_freqs.shape[0], dtype=int)
    ii = 0
    for cf in den_corner_freqs:
        corner_freq_indeces_poles[ii] = find_nearest(omega,cf)
        ii += 1
    
    corner_freq_indeces_zeros = np.zeros(num_corner_freqs.shape[0],dtype=int)
    ii = 0
    for cf in num_corner_freqs:
        corner_freq_indeces_zeros[ii] = find_nearest(omega,cf)
        ii += 1

    G_jw = enel441_fourier_transform(num,den,omega)
    fig, ax = plt.subplots(2,1)
    mag_plot = 20*np.log10(np.abs(G_jw))
    ax[0].semilogx(omega, mag_plot) 
    ax[0].set_title('Magnitude')
    ax[0].set_xlabel('Frequency (rad)')
    ax[0].set_ylabel('Mag (dB)')
    ax[0].plot(omega[corner_freq_indeces_poles], mag_plot[corner_freq_indeces_poles], 'kx')
    ax[0].plot(omega[corner_freq_indeces_zeros], mag_plot[corner_freq_indeces_zeros], 'ko')
    
    phase_plot = np.angle(G_jw)
    ax[1].semilogx(omega, phase_plot)
    ax[1].set_title('Phase')
    ax[1].set_xlabel('Frequency (rad)')
    ax[1].set_ylabel('Freq (rad)')
    ax[1].plot(omega[corner_freq_indeces_poles], phase_plot[corner_freq_indeces_poles], 'kx')
    ax[1].plot(omega[corner_freq_indeces_zeros], phase_plot[corner_freq_indeces_zeros], 'ko')

    fig.tight_layout(pad=1.5)


def enel441_bode(G_jw, omega, fig=[], ax=[], label=[]):
    if not fig: 
        fig, ax = plt.subplots(2,1)

    
    mag_plot = 20*np.log10(np.abs(G_jw))
    ax[0].semilogx(omega, mag_plot, label=label) 
    ax[0].set_title('Magnitude')
    ax[0].set_xlabel('Frequency (rad)')
    ax[0].set_ylabel('Mag (dB)')
    
    phase_plot = np.unwrap(np.angle(G_jw))
    ax[1].semilogx(omega, 180/math.pi*phase_plot)
    ax[1].set_title('Phase')
    ax[1].set_xlabel('Frequency (rad)')
    ax[1].set_ylabel('Phase (rad)')

    fig.tight_layout(pad=1.5)
    return fig, ax



def enel441_sim_closed_loop(P,K,t,r,d,n):
    L = K*P
    S = 1/(1+L)
    T = L/(1+L)   

    y_r = ct.forced_response(T,t,r) 
    y_n = ct.forced_response(T,t,n) 
    y_d = ct.forced_response(P*S,t,d) 

    y = y_r.y + y_d.y + y_n.y

    u_r = ct.forced_response(K*S,t,r) 
    u_d = ct.forced_response(S,t,d) 
    u_n = ct.forced_response(K*S,t,d) 

    u = u_r.y + u_d.y - u_n.y

    return np.squeeze(y), np.squeeze(u)


def enel441_sim_open_loop(P,t,u,d):    
    y_r = ct.forced_response(P,t,u) 
    y_d = ct.forced_response(P,t,d) 
    y = np.squeeze(y_r.y) + np.squeeze(y_d.y)  
    return y


def enel441_make_open_and_closed_loop_plots(t,r,d,n,y2,y1):
    fig,ax = plt.subplots(1,3, figsize=(15,5) )
    ax[0].plot(t,r)
    ax[0].set_xlabel('Time (s)')
    #ax[0].set_ylabel('Speed (km/h)')
    ax[0].set_title('Desired Output')
    ax[1].plot(t,d)
    ax[1].set_xlabel('Time (s)')
    ax[1].set_ylabel('Disturbance')
    ax[1].set_title('Disturbance')   
    ax[2].plot(t,n)    
    ax[2].set_xlabel('Time (s)')
    ax[2].set_ylabel('Measurement Noise')
    ax[2].set_title('Measurement Noise')
        
    fig.tight_layout()
    
    fig,ax = plt.subplots(1,1, figsize=(15,5))
    ax.plot(t,r, label='Desired Output')
    ax.plot(t,y1, label='Measured Output Using Open Loop Control')   
    ax.plot(t,y2, label='Measured Output Using Closed Loop Control') 
    ax.set_xlabel('Time (s)')
    #ax.set_ylabel('Speed (km/h)')
    ax.set_title('Comparison of Desired and Measured Output')
    plt.legend()


def plot_input_to_plant(K,P,r,d,t):
    L = K*P
    S = 1/(1+L)
    T = L/(1+L)   

    X_r = K*S
    X_d = S
    
    u_r = ct.forced_response(X_r,t,r) 
    u_d = ct.forced_response(X_d,t,d) 

    u = u_r.y + u_d.y

    fig, ax = plt.subplots(1)
    ax.plot(t, np.squeeze(u),label='Input to Car In Closed-Loop')
    ax.set_title('Response of Plant input')
    ax.set_xlabel('Time (s)')
     
    return fig, ax


def enel441_root_locus(num,den,k_range):
    N = len(k_range)

    if len(num) == len(den):
        print('Nothing to do.')
        num_padded = num    
    else:
        num_padded = np.concatenate((np.zeros(len(den)-len(num)), num))

    closed_loop_poles = np.zeros((N,den.shape[0]-1),dtype=np.csingle)
    for ii in range(N):
        den_closed_loop = den + k_range[ii]*num_padded
        closed_loop_poles[ii,:] = np.roots(den_closed_loop)
    
    fig, ax = plt.subplots(1,1)
    ax.plot(np.real(closed_loop_poles),np.imag(closed_loop_poles), 'k.' )
    ax.plot(np.real(closed_loop_poles[0,:]),np.imag(closed_loop_poles[0,:]), 'rx' )
    ax.plot(np.real(closed_loop_poles[-1,:]),np.imag(closed_loop_poles[-1,:]), 'bo' )
    return fig, ax
