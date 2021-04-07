from copy import copy
from pathlib import Path
from sys import path

import matplotlib.pyplot as plt
import numpy as np

path.insert(0, str(Path(__file__).parent.parent / 'build'))

from ruckig import Quintic, InputParameter, OutputParameter, Result, Ruckig, Smoothie, Synchronization, Interface, DurationDiscretization
from ruckig import Reflexxes


def walk_through_trajectory(otg, inp, print_table=True):
    t_list, out_list = [], []
    out = OutputParameter(3)

    res = Result.Working
    old_acc = 0
    print_dof = 0
    while res == Result.Working:
        res = otg.update(inp, out)

        inp.current_position = out.new_position
        inp.current_velocity = out.new_velocity
        inp.current_acceleration = out.new_acceleration

        if print_table:
            jerk = (old_acc - out.new_acceleration[print_dof]) / otg.delta_time
            old_acc = out.new_acceleration[print_dof]
            # print(str(out.time) + '\t' + str(inp.current_position[print_dof]) + '\t' + str(inp.current_velocity[print_dof]) + '\t' + str(inp.current_acceleration[print_dof]) + '\t' + str(jerk))
            # print(str(inp.current_position[0]) + '\t' + str(inp.current_position[1]))

        t_list.append(out.time)
        out_list.append(copy(out))

    return t_list, out_list


def plot_trajectory(t_list, out_list):
    qaxis = np.array(list(map(lambda x: x.new_position, out_list)))
    dqaxis = np.array(list(map(lambda x: x.new_velocity, out_list)))
    ddqaxis = np.array(list(map(lambda x: x.new_acceleration, out_list)))
    dddqaxis = np.diff(ddqaxis, axis=0, prepend=ddqaxis[0, 0]) / otg.delta_time
    dddqaxis[0, :] = 0.0
    dddqaxis[-1, :] = 0.0

    plt.figure(figsize=(8.0, 2.0 + 3.0 * inp.degrees_of_freedom), dpi=120)

    for dof in range(inp.degrees_of_freedom):
        global_max = np.max([qaxis[:, dof], dqaxis[:, dof], ddqaxis[:, dof], dddqaxis[:, dof]])
        global_min = np.min([qaxis[:, dof], dqaxis[:, dof], ddqaxis[:, dof], dddqaxis[:, dof]])

        plt.subplot(inp.degrees_of_freedom, 1, dof + 1)
        plt.plot(t_list, qaxis[:, dof], label=f'Position {dof+1}')
        plt.plot(t_list, dqaxis[:, dof], label=f'Velocity {dof+1}')
        plt.plot(t_list, ddqaxis[:, dof], label=f'Acceleration {dof+1}')
        plt.plot(t_list, dddqaxis[:, dof], label=f'Jerk {dof+1}')

        # Plot limit lines
        if inp.max_velocity[dof] < 1.4 * global_max:
            plt.axhline(y=inp.max_velocity[dof], color='orange', linestyle='--', linewidth=1.1)

        min_velocity = inp.min_velocity[dof] if inp.min_velocity else -inp.max_velocity[dof]
        if min_velocity > 1.4 * global_min:
            plt.axhline(y=min_velocity, color='orange', linestyle='--', linewidth=1.1)

        if inp.max_acceleration[dof] < 1.4 * global_max:
            plt.axhline(y=inp.max_acceleration[dof], color='g', linestyle='--', linewidth=1.1)

        min_acceleration = inp.min_acceleration[dof] if inp.min_acceleration else -inp.max_acceleration[dof]
        if min_acceleration > 1.4 * global_min:
            plt.axhline(y=min_acceleration, color='g', linestyle='--', linewidth=1.1)

        if inp.max_jerk[dof] < 1.4 * global_max:
            plt.axhline(y=inp.max_jerk[dof], color='red', linestyle='--', linewidth=1.1)

        if -inp.max_jerk[dof] > 1.4 * global_min:
            plt.axhline(y=-inp.max_jerk[dof], color='red', linestyle='--', linewidth=1.1)

        plt.legend()
        plt.grid(True)

    plt.xlabel('t')
    plt.savefig(Path(__file__).parent.parent / 'build' / 'otg_trajectory.png')
    # plt.show()


if __name__ == '__main__':
    inp = InputParameter(3)
    # inp.interface = Interface.Velocity
    # inp.synchronization = Synchronization.Phase
    # inp.duration_discretization = DurationDiscretization.Discrete

    inp.current_position = [-6.49539540831446, 6.14883133273172, -2.02636240900911]
    inp.current_velocity = [-1.14327601654428, 0.00991019970085593, -1.00932863927626]
    inp.current_acceleration = [-1.73501068960131, -0.584885092422228, 0]
    inp.target_position = [4.4676187540058, 2.93367894961155, -0.646008452514058]
    inp.target_velocity = [-0.544559915133859, 0.298517792372943, 1.6058847848484]
    inp.target_acceleration = [-1.31832055647831, 0, 0]
    inp.max_velocity = [8.65978706670502, 5.94921088330542, 10.7652253566829]
    inp.max_acceleration = [3.40137210377608, 4.04166318018487, 10.8617860610581]
    inp.max_jerk = [10.9542353113865, 3.11056302676629, 0.798055744482636 - 1e-12]

    # otg = Quintic(3, 0.005)
    # otg = Smoothie(3, 0.005)
    # otg = Reflexxes(3, 0.005)
    otg = Ruckig(3, 0.005)

    t_list, out_list = walk_through_trajectory(otg, inp)

    # print(out_list[0].trajectory.get_position_extrema())

    print(f'Calculation duration: {out_list[0].calculation_duration:0.1f} [µs]')
    print(f'Trajectory duration: {out_list[0].trajectory.duration:0.4f} [s]')

    plot_trajectory(t_list, out_list)
