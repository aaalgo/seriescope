#!/usr/bin/env python3
import os
import h5py
import scipy.io as sio
from glob import glob
import numpy as np
#import wfdb

STAGE_NAMES = ['nonrem1', 'nonrem2', 'nonrem3', 'rem', 'undefined', 'wake']

HZ = 200
CHANNELS = 13

CHANNEL_NAMES = ['F3-M2', 'F4-M1', 'C3-M2', 'C4-M1', 'O1-M2', 'O2-M1', 'E1-M2',
                 'Chin1-Chin2', 'ABD', 'CHEST', 'AIRFLOW', 'SaO2', 'ECG']

class Sample:
    # this is a representation of one sample
    # Construct with  Sample(some_directory_path)
    # A Sample object has the following fields:
    #   name    e.g. tr05-1176
    #   L       number of samples; most arrays should be of this length. e.g. 5304000 
    #           should be 200Hz.
    #
    #   signal  signal data, numpy array shape=(13,L) dtype=int16
    #
    #   ----------- for test casese the following two fields are None
    #   arousal numpy array shape=(L,) dtype=int8   (converted from original float64)
    #
    #           this is the label:
    #               +1: arousal signals
    #                0: non-arousal
    #               -1: not scored
    #
    #   stages  stage labels, numpy array shape=(L,) dtype=int8 values=0,1,2,3,4,5

    # currently not handled:
    #   .arousal file
    #   .hea file

    def __init__ (self, path = None):
        # construct the sample from a directory specified by path
        # do all sanity checks
        # ar[0] e.g.:  ...../tr05-1176.arousal
        self.name = None
        self.L= None
        self.signal = None
        self.arousal = None
        self.stages = None
        if path is None:
            return

        ar = glob(os.path.join(path, '*.arousal'))
        assert len(ar) == 1

        name = os.path.basename(ar[0]).split('.')[0]
        self.name = name

        # load mat file
        v = sio.loadmat(os.path.join(path, '%s.mat' % name))
        # v should be like {'val': data}
        # data is 13x?, int16
        assert 'val' in v
        assert len(v) == 1
        data = v['val']
        assert data.shape[0] == CHANNELS
        assert data.dtype == np.int16
        L = data.shape[1]  # number of samples
        self.L = L
        self.signal = data[:, :]

        # load arousal.mat
        arousal_path = os.path.join(path, '%s-arousal.mat' % name)
        if os.path.exists(arousal_path):
            with h5py.File(arousal_path, 'r') as f:
                # the h5 file has two fields
                assert len(f.keys()) == 2
                if True:    # make sure the #refs# field contains no information
                    refs = f['#refs#']
                    assert len(refs.keys()) == 1
                    ref = refs['a']
                    assert ref.shape == (2,)
                    assert ref[0] == 0 and ref[1] == 0
                # work on the data field, which should contain arousals and sleep_stages only
                data = f['data']
                assert len(data.keys()) == 2
                arousal = data['arousals']
                stages = data['sleep_stages']

                assert arousal.shape == (L, 1)
                assert arousal.dtype == np.float64
                arousal = arousal[:, 0]
                # make sure arousal only has 3 values: -1, 0, 1
                self.arousal = arousal.astype(np.int8)
                assert np.all(self.arousal == arousal)
                assert np.all(self.arousal <= 1)
                assert np.all(self.arousal >= -1)
                assert len(stages.keys()) == len(STAGE_NAMES)

                checksum = np.zeros((L,), dtype=np.uint8)
                labels = np.zeros((L,), dtype=np.uint8)
                for l, key in enumerate(STAGE_NAMES):
                    # l is 0,1,2,3,4,5
                    stage = stages[key]
                    assert stage.dtype == np.uint8
                    assert stage.shape == (1, L)
                    stage = stage[0, :]
                    assert np.all(stage <= 1)
                    checksum += stage
                    labels[stage == 1] = l
                    pass
                assert np.all(checksum == 1)
                self.stages = labels
                pass
            pass

        # load .hea file
        # format: https://physionet.org/physiotools/wag/header-5.htm
        with open(os.path.join(path, '%s.hea' % name), 'r') as f:
            line = f.readline()
            a, nc, hz, l = line.strip().split(' ')
            assert a == name
            assert int(nc) == 13
            assert int(hz) == HZ
            assert int(l) == L
            for ch in range(13):
                line = f.readline()
                # e.g. tr05-1176.mat 16+24 1/uV 16 0 6 -22 0 F3-M2
                fname, fmt, unit, bits, zero, init, cksum, block, desc = line.strip().split(' ')
                assert fname == name + '.mat'
                assert fmt == '16+24'
                if ch == 11:    # SaO2
                    assert unit == '655.35(-32768)/%'
                elif ch == 12:  # ECG
                    assert unit == '1000/mV'
                else:
                    assert unit == '1/uV'
                    pass
                assert bits == '16' # ADC resolution
                assert zero == '0'  # ADC zero
                # skip init
                # skip ckum
                assert block == '0'
                assert desc == CHANNEL_NAMES[ch]
                pass
            pass
        pass

    def downsample (self, stride=20):
        self.signal = self.signal[:, ::stride]
        self.arousal = self.arousal[::stride]
        self.stages = self.stages[::stride]
        self.L = self.signal.shape[1]
        pass

    def save_raw (self, path):
        data = np.empty((15, self.L), dtype=np.float32)
        data[0, :] = self.arousal
        data[1, :] = self.stages
        data[2:15, :] = self.signal
        data[0, :] *= 15000
        data[1, :] *= 5000
        data[2:6, :] *= 400
        data[6:8, :] *= 100
        data[9,:] *= 100
        data[10,:] *= 100
        data[11,:] *= 100
        data[12, :] *= 1000
        data[13, :] *= 10
        data[14, :] *= 10
        np.clip(data, -30000, 30000, out=data)
        data = data.astype(np.int16)
        np.copy(np.transpose(data), order='C').tofile(path)
        pass

    def to_picpac (self):
        # picpac input is 2D
        L = self.signal.shape[1]
        data = np.empty((15, L), dtype=np.int16)
        data[0, :] = self.arousal
        data[1, :] = self.stages
        data[2:, :] = self.signal
        return data

    def from_picpac (self, batch):
        # picpac output is 3D with last dimension = 1
        assert len(batch.shape) == 3
        assert batch.shape[2] == 1
        self.L = batch.shape[1]
        self.arousal = batch[0, :, 0].astype(np.int8)
        self.stages = batch[1, :, 0].astype(np.int8)
        self.signal = batch[2:, :, 0].astype(np.int16)
        pass

    pass

def unpack_picpac_batch (sample):
    # unpack a picpac batch, refer to import.py
    assert sample.shape[1] == 15
    y = sample[:, 0, :, 0]     # extract labels
    m = np.ones_like(y, dtype=np.float32)
    m[y == -1] = 0          # set mask of unevaluated samples to 0, leave others to 1
    #y[y == -1] = 0
    np.clip(y, 0, 1, out=y) # change -1 to 0
    s = sample[:, 1, :, 0]     # stages
    x = sample[:, 2:, :, 0]    # signals
    return x.astype(np.float32), y.astype(np.int32), m, s.astype(np.int32)

if __name__ == '__main__':
    #ann = wfdb.rdann('sample/tr05-1176', 'arousal')
    #print(ann)
    #print(wfdb.show_ann_labels())
    s = Sample('data/raw/training/tr03-0061')
    print(s.L)
    s.save_raw('sample1.data')
    #print(s.name)

