import math
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib.ticker import ScalarFormatter
np.random.seed(0)
rc('text', usetex=True)
rc('font', **{'family': "sans-serif"})
params = {'text.latex.preamble': [r'\usepackage{amsmath}']}
mpl.rcParams['axes.xmargin'] = 0
mpl.rcParams['axes.ymargin'] = 0

# number of nodes (max: 50)
n = 50

# preparation
INF = 1e9
epsilon = 1e-15
In = np.identity(n)
On = np.zeros((n, n))


class FixedOrderFormatter(ScalarFormatter):
    def __init__(self, order_of_mag=0, useOffset=True, useMathText=True):
        self._order_of_mag = order_of_mag
        ScalarFormatter.__init__(self, useOffset=useOffset,
                                 useMathText=useMathText)

    def _set_orderOfMagnitude(self, range):
        self.orderOfMagnitude = self._order_of_mag


def event_trigger_func(x, xk, sigma, eta):
    # define triggering rule
    if math.fabs(x - xk) > sigma * x + eta:
        return 1
    else:
        return 0


def plot_data(K, L, sigma, eta, d_table, choice):
    # define time and gap
    Time = 1000000
    h = 0.00015

    # define propotion of infected pepole
    x = np.zeros([Time, n])
    x0 = np.random.rand(n)
    x0[0] /= 3
    x[0] = x0
    xk = x0

    # define event and objective list
    event = np.zeros([Time, n])
    d_table_list = np.array([d_table for i in range(Time)])
    u_transition = np.zeros([Time - 1, n])
    v_transition = np.zeros([Time - 1, n])

    # for i in range(n):
    #    if W[1][i] == 1 and choice == 3:
    #        D[i][i] *= 1.3

    Bn = B / (10 * D_base_max)
    Dn = D / (10 * D_base_max)
    Kn = K / (10 * D_base_max)
    Ln = L / (10 * D_base_max)
    Dn[0][0] *= 1.15

    # collect transition data of propotion of infected pepole and triggerring event
    for k in range(Time - 1):

        # # choice 1 has no control input
        if choice == 1:
            x[k + 1] = x[k] + h * \
                (-Dn.dot(x[k]) + (In - np.diag(x[k])).dot(Bn.T).dot(x[k]))

        # # In the case of using feedback controller
        else:
            for i in range(n):
                # # choice 2 is the case of continuous controller
                if choice == 2 and event_trigger_func(x[k][i], xk[i], 0, 0) == 1:
                    xk[i] = x[k][i]
                    event[k + 1][i] = 1

                # # choice 3 is the case of event-triggered controller
                elif choice == 3 and event_trigger_func(x[k][i], xk[i], sigma[i], eta[i]) == 1:
                    xk[i] = x[k][i]
                    event[k + 1][i] = 1
            x[k + 1] = x[k] + h * (-(Dn * 1.1 + Kn.dot(np.diag(xk))).dot(x[k]) + (
                In - np.diag(x[k])).dot(Bn.T - Ln.dot(np.diag(xk)).T).dot(x[k]))

    # plot data
    # # subplot 1 is the transition data of x
    fig = plt.figure(figsize=(16, 9.7))
    ax1 = fig.add_axes((0, 0, 1, 1))
    cm = plt.cm.get_cmap('cubehelix', 1.2 * n)

    for i in range(n):
        ax1.plot(x.T[i], lw=3, color=cm(i))

    # # # plot setting
    ax1.set_xlabel(r'$t$', fontsize=60)
    ax1.set_ylabel(
        r'$x_i(t)$', fontsize=60)
    ax1.set_xticks([0, 1000000])
    ax1.xaxis.set_major_formatter(FixedOrderFormatter(4, useMathText=True))
    ax1.xaxis.offsetText.set_fontsize(0)
    ax1.ticklabel_format(style="sci", axis="x", scilimits=(4, 4))
    ax1.tick_params(axis='x', labelsize=60)
    ax1.set_yscale('log')
    ax1.set_ylim([0.005, 1])
    ax1.set_yticks([0.01, 0.1, 1])
    ax1.set_yticklabels([r'$10^{-2}$', r'$10^{-1}$', r'$1$'])
    ax1.tick_params(axis='y', labelsize=60)
    ax1.grid(which='major', alpha=0.8, linestyle='dashed')

    if choice == 1:
        fig.savefig("./images/x_all_zeroinput_log.pdf",
                    bbox_inches="tight", dpi=300)
    elif choice == 2:
        fig.savefig("./images/x_all_continuous_log.pdf",
                    bbox_inches="tight", dpi=300)
    elif choice == 3:
        fig.savefig("./images/x_all_event_log.pdf", bbox_inches="tight", dpi=300)


if __name__ == '__main__':
    D_base_max = 1.8
    D = np.load('./data/matrix/D.npy')
    B = np.load('./data/matrix/B.npy')
    K = np.load('./data/matrix/K.npy')
    L = np.load('./data/matrix/L.npy')
    sigma = np.load('./data/matrix/sigma.npy')
    eta = np.load('./data/matrix/eta.npy')
    W = np.load('data/matrix/W.npy')
    d_table = np.load('data/matrix/d_table.npy')

    # plot data
    plot_data(K, L, sigma, eta, d_table, choice=3)
