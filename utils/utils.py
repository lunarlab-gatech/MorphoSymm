#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 25/1/22
# @Author  : Daniel Ordonez 
# @email   : daniels.ordonez@gmail.com
import numpy as np
import pybullet_data
import torch
from pybullet import GUI, DIRECT, COV_ENABLE_GUI, COV_ENABLE_SEGMENTATION_MARK_PREVIEW, COV_ENABLE_DEPTH_BUFFER_PREVIEW, \
    COV_ENABLE_MOUSE_PICKING
from pybullet_utils import bullet_client

def test_model_equivariance():
    pass

def pprint_dict(d : dict):
    str = []
    d_sorted = dict(sorted(d.items()))
    for k, v in d_sorted.items():
        str.append(f"{k}={v}")
    return "-".join(str)

def configure_bullet_simulation(gui=True):
    BACKGROUND_COLOR = '--background_color_red=%.2f --background_color_green=%.2f --background_color_blue=%.2f' % \
                       (0.960, 0.960, 0.960)

    if gui:
        pb = bullet_client.BulletClient(connection_mode=GUI, options=BACKGROUND_COLOR)
    else:
        pb = bullet_client.BulletClient(connection_mode=DIRECT)
    pb.configureDebugVisualizer(COV_ENABLE_GUI, 0)
    pb.configureDebugVisualizer(COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)
    pb.configureDebugVisualizer(COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
    pb.configureDebugVisualizer(COV_ENABLE_MOUSE_PICKING, 0)

    pb.resetSimulation()
    pb.setPhysicsEngineParameter(deterministicOverlappingPairs=1)
    pb.setAdditionalSearchPath(pybullet_data.getDataPath())
    # Load floor
    # floor_id = pb.loadURDF("plane.urdf", basePosition=[0, 0, 0.0], useFixedBase=1)
    return pb

def symbolic_matrix(base_name, rows, cols):
    from sympy import Symbol

    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    w = np.empty((rows, cols), dtype=object)
    for r in range(rows):
        for c in range(cols):
            var_name = "%s%d,%d" % (base_name, r + 1, c + 1)
            w[r, c] = Symbol(var_name.translate(SUB))
    return w


def permutation_matrix(oneline_notation):
    d = len(oneline_notation)
    P = np.zeros((d, d))
    assert d == len(np.unique(oneline_notation)), np.unique(oneline_notation, return_counts=True)
    P[range(d), np.abs(oneline_notation)] = 1
    return P


def is_canonical_permutation(ph):
    return np.allclose(ph @ ph, np.eye(ph.shape[0]))


def append_dictionaries(dict1, dict2, recursive=True):
    result = {}
    for k in set(dict1) | set(dict2):
        item1, item2 = dict1.get(k, 0), dict2.get(k, 0)
        if isinstance(item1, list) and (isinstance(item2, int) or isinstance(item2, float)):
            result[k] = item1 + [item2]
        elif isinstance(item1, int) or isinstance(item1, float):
            result[k] = [item1, item2]
        elif isinstance(item1, torch.Tensor) and isinstance(item2, torch.Tensor):
            result[k] = torch.cat((item1, item2))
        elif isinstance(item1, dict) and isinstance(item2, dict) and recursive:
            result[k] = append_dictionaries(item1, item2)
    return result


import unicodedata
import re
def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

if __name__ == "__main__":

    a = (2, 3, 0, 1)
    P = permutation_matrix(a)
    assert is_canonical_permutation(P)