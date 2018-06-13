#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configargparse
import matplotlib.pyplot as plt
from pyosb.fileio.eyeosbparser import EyeInfoParser
from pyosb.preprocess.preprocess import Preprocessor
from pyosb.gaze.mapper import GazeMapper


def main(options):
    # create pandas dataframe from json recordings and do some preprocessing
    parser = EyeInfoParser(options)
    pp = Preprocessor(parser.get_dataframe(), options)
    pp.preprocess_all()
    df = pp.get_dataframe()

    for key in df.keys():
        if all(ss not in key for ss in ["gaze"]):
            print("{0: <30} {1}".format(key, df[key][0]))

    fig, ax = plt.subplots(1, 1)

    ax.scatter(df['left_eye.pupilpos.x'], df['left_eye.pupilpos.y'])
    ax.scatter(df['left_eye.reflexpos.left.x'],
               df['left_eye.reflexpos.left.y'], marker='.')
    ax.scatter(df['left_eye.reflexpos.right.x'],
               df['left_eye.reflexpos.right.y'], marker='.')
    # ax.scatter(df['left_eye.reflex_center.x'],
    #            df['left_eye.reflex_center.y'], marker='.')
    ax.scatter(df['right_eye.pupilpos.x'], df['right_eye.pupilpos.y'])
    ax.scatter(df['right_eye.reflexpos.left.x'],
               df['right_eye.reflexpos.left.y'], marker='.')
    ax.scatter(df['right_eye.reflexpos.right.x'],
               df['right_eye.reflexpos.right.y'], marker='.')
    # ax.scatter(df['right_eye.reflex_center.x'],
    #            df['right_eye.reflex_center.y'], marker='.')
    ax.set_xlim([0, options.cam_x * options.cam_pp])
    ax.set_ylim([options.cam_y * options.cam_pp, 0])
    plt.show()

    # ax.scatter(df['gaze_target.x'], df['gaze_target.y'])
    # ax.scatter(df['gaze_point.x'], df['gaze_point.y'], marker='x')
    # ax.scatter(df['left_eye.gazepos.x'],
    #            df['left_eye.gazepos.y'], marker='.')
    # ax.scatter(df['right_eye.gazepos.x'],
    #            df['right_eye.gazepos.y'], marker='.')
    # ax.set_xlim([0, options.screen_x * options.screen_pp])
    # ax.set_ylim([options.screen_y * options.screen_pp, 0])
    # plt.show()

    mapper = GazeMapper(options, df)


if __name__ == '__main__':
    p = configargparse.ArgParser(default_config_files=['./config/config.ini'],
                                 ignore_unknown_config_file_keys=True)
    p.add('--config', is_config_file=True, help='Config file path')
    p.add('--recording', type=str, help='Input recording (json)')
    p.add('--output_dataframe', type=str,
          help='Output file for parsed recording')
    p.add('--n1', type=float, help='Refractive index n1')
    p.add('--n2', type=float, help='Refractive index n2')
    p.add('--cam_pp', type=float, help='Camera pixel pitch')
    p.add('--phi_cam', type=float, help='Camera phi')
    p.add('--theta_cam', type=float, help='Camera theta')
    p.add('--kappa_cam', type=float, help='Camera kappa')
    p.add('--screen_x', type=int, help='Screen x resolution')
    p.add('--screen_y', type=int, help='Screen y resolution')
    p.add('--screen_pp', type=float, help='Screen pixel pitch')
    p.add('--cam_x', type=int, help='Screen x resolution')
    p.add('--cam_y', type=int, help='Screen y resolution')
    options = p.parse_args()
    main(options)
