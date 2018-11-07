#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt


cam1_matrix = np.array([
    [3.28096059e+03, 0.00000000e+00, 9.69093680e+02],
    [0.00000000e+00, 3.28086485e+03, 8.28389419e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
cam1_dist = np.array([-1.18342721e-01,
                      6.40528615e-02,
                      6.70611000e-05,
                      -1.27527496e-03])
cam2_matrix = np.array([
    [3.36073182e+03, 0.00000000e+00, 1.19890016e+03],
    [0.00000000e+00, 3.35485021e+03, 7.90126077e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
cam2_dist = np.array([-1.34503278e-01,
                      1.97805440e-01,
                      1.25122839e-04,
                      4.13394379e-03])


def stereo_calibrate(args, square_size=25):
    term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((1, 6*9, 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2) * square_size

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    # image list for plotting (with chessboard corners)
    images = []

    for image in [args.cam1, args.cam2]:
        img = cv2.imread(image[0])
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # this is specific to the image - we have two chessboards in the image,
        # and for this we need to use the left one
        if image == args.cam2:
            gray[:, 1000:] = 0

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)
            cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), term_crit)
            imgpoints.append([corners])
            cv2.drawChessboardCorners(img, (9, 6), corners, ret)
            images.append(img)

    objpoints = np.array(objpoints)

    if args.show:
        fig, ax = plt.subplots(1, 2)
        ax[0].imshow(images[0])
        ax[1].imshow(images[1])
        plt.show()

    _, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
        objpoints[0], imgpoints[0], imgpoints[1],
        cam1_matrix, cam1_dist,
        cam2_matrix, cam2_dist,
        gray.shape[::-1], flags=cv2.CALIB_FIX_INTRINSIC, criteria=term_crit)

    return R, T, E, F


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cam1', type=str, nargs=1, required=True,
                        help='Calibration image of camera 1')
    parser.add_argument('--cam2', type=str, nargs=1, required=True,
                        help='Calibration image of camera 2')
    parser.add_argument('--show', '-s', action='store_true',
                        help='Show calibration results')
    args = parser.parse_args()
    R, T, E, F = stereo_calibrate(args)

    print('Rotation matrix:\n{}'.format(R))
    print('Translation matrix:\n{}'.format(T))
    print('Essential matrix:\n{}'.format(E))
    print('Fundamental matrix:\n{}'.format(F))

    img = cv2.imread(args.cam2[0])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray[:, :1000] = 0
    term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((1, 6*9, 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2) * 38
    _, corners = cv2.findChessboardCorners(gray, (9, 6), None)

    _, rvec, tvec = cv2.solvePnP(objp, corners, cam2_matrix, cam2_dist)

    # fig, ax = plt.subplots(1, 2)
    # ax[0].imshow(img)
    # ax[1].imshow(gray, cmap='gray')
    # plt.show()

    rmat, _ = cv2.Rodrigues(rvec)

    print('Rotation matrix:\n{}'.format(rmat))
    print('Translation matrix:\n{}'.format(tvec))

    print(tvec - T)
    print(T - tvec)
    # print(objp * rmat + tvec)