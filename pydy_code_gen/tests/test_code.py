#!/usr/bin/env python

# standard libary
import os
import shutil
import glob

# external libraries
import numpy as np
from numpy import testing

# local libraries
from pydy_code_gen.code import numeric_right_hand_side
from models import generate_mass_spring_damper_equations_of_motion


def TestCode():

    def test_numeric_right_hand_side(self):

        m, k, c, g, F, x, v = np.random.random(7)

        args = {'constants': np.array([m, k, c, g]),
                'specified': np.array([F])}

        states = np.array([x, v])

        mass_matrix, forcing_vector, constants, coordinates, speeds, specified = \
            generate_mass_spring_damper_equations_of_motion()

        expected_dx = np.array([v, 1.0 / m * (-c * v + m * g - k * x + F)])

        backends = ['lambdify', 'theano', 'cython']

        for backend in backends:
            rhs = numeric_right_hand_side(mass_matrix, forcing_vector,
                                          constants, coordinates, speeds,
                                          specified, generator=backend)
            dx = rhs(states, 0.0, args)

            testing.assert_allclose(dx, expected_dx)

        # Now try it with a function defining the specified quantities.
        args['specified'] = lambda x, t: np.sin(t)

        t = 14.345

        expected_dx = np.array([v, 1.0 / m * (-c * v + m * g - k * x +
                                              np.sin(t))])

        for backend in backends:
            rhs = numeric_right_hand_side(mass_matrix, forcing_vector,
                                          constants, coordinates, speeds,
                                          specified, generator=backend)
            dx = rhs(states, t, args)

            testing.assert_allclose(dx, expected_dx)

        # Now try it without specified values.
        mass_matrix, forcing_vector, constants, coordinates, speeds, specified = \
            generate_mass_spring_damper_equations_of_motion(external_force=False)

        expected_dx = np.array([v, 1.0 / m * (-c * v + m * g - k * x)])

        for backend in backends:
            rhs = numeric_right_hand_side(mass_matrix, forcing_vector,
                                          constants, coordinates, speeds,
                                          specified, generator=backend)
            dx = rhs(states, 0.0, args)

            testing.assert_allclose(dx, expected_dx)

    def teardown(self):

        # clean up the cython crud
        files = glob.glob('multibody_system*')
        for f in files:
            os.remove(f)
        shutil.rmtree('build')
