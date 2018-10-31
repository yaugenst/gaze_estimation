#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import cv2
import numpy as np


def mono_calibrate(folder, square_size=25, save_output=False):
    term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6*9, 3), np.float32)
    objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2) * square_size

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    for fname in os.listdir(folder):
        img = cv2.imread(os.path.join(folder, fname))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)
            cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), term_crit)
            imgpoints.append(corners)

    objpoints = np.array(objpoints)
    imgpoints = np.array(imgpoints)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints,
                                                       gray.shape[::-1],
                                                       None, None,
                                                       criteria=term_crit)
    fovx, fovy, focalLength, principalPoint, aspectRatio = \
        cv2.calibrationMatrixValues(mtx, gray.shape[::-1], 5.2, 3.88)

    if save_output:
        with open(os.path.basename(os.path.normpath(folder))
                  + '_calibration.txt', 'w') as ofile:
            ofile.write("Average reprojection error: {}\n".format(ret))
            ofile.write("Camera intrinsic matrix:\n{}\n".format(mtx))
            ofile.write("Distortion coefficients:\n{}\n".format(dist))
            ofile.write("Per image rotation vectors:\n{}\n".format(rvecs))
            ofile.write("Per image translation vectors:\n{}\n"
                        .format(tvecs))
            ofile.write("Field of view in degress along "
                        "horizontal sensor axis:\n{}\n".format(fovx))
            ofile.write("Field of view in degress along "
                        "vertical sensor axis:\n{}\n".format(fovy))
            ofile.write("Focal length of lens in mm:\n{}\n"
                        .format(focalLength))
            ofile.write("Principal point in mm:\n{}\n"
                        .format(principalPoint))
            ofile.write("Pixel aspect ratio:\n{}".format(aspectRatio))

    return [ret, mtx, dist, rvecs, tvecs]


def stereo_calibrate(args, cam1_calib, cam2_calib, square_size=25):
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
    imgpoints = np.array(imgpoints)

    _, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
        objpoints[0], imgpoints[0], imgpoints[1],
        cam1_calib[1], cam1_calib[2],
        cam2_calib[1], cam2_calib[2],
        gray.shape[::-1], flags=cv2.CALIB_FIX_INTRINSIC, criteria=term_crit)

    print('Rotation matrix:\n{}'.format(R))
    print('Translation matrix:\n{}'.format(T))
    print('Essential matrix:\n{}'.format(E))
    print('Fundamental matrix:\n{}'.format(F))


def main(args):
    calibrations = []
    for folder in args.folders:
        calibrations.append(mono_calibrate(folder, 25, args.save))

    stereo_calibrate(args, calibrations[0], calibrations[1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folders', '-f', type=str, nargs='+', required=True,
                        help='List of folders with calibration images')
    parser.add_argument('--save', '-s', action='store_true',
                        help='Save calibrations to file')
    parser.add_argument('--cam1', type=str, nargs=1, required=True,
                        help='Calibration image of camera 1')
    parser.add_argument('--cam2', type=str, nargs=1, required=True,
                        help='Calibration image of camera 2')
    args = parser.parse_args()
    main(args)
