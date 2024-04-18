import copy
import itertools
from DecisionSet.data import Data
from pysat.formula import WCNF
from pysat.examples.rc2 import RC2, RC2Stratified
import threading


class ConsistencyCheck(object):
    def __init__(self, data):
        # self.featureSet = featureSet
        # data = Data(featureSet)
        self.status = True if len(data.feats[-1]) > 1 else False
        if not self.status:
            return
        # self.init_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime
        self.data = data
        self.dbin = copy.deepcopy(data)

        # binarizing the data properly(正确二值化数据）
        for i in range(len(self.data.samps)):
            samp_bin = self.data.samps[i][:-1]
            for l in samp_bin:
                l = int(l)
                if l > 0:
                    name, lit = self.data.fvmap.opp[l]
                    j = self.data.nm2id[name]
                    if len(self.data.feats[j]) > 2:
                        samp_bin += [-self.data.fvmap.dir[(name, l)] for l in sorted(
                            self.data.feats[j].difference(set([lit])))]
            self.dbin.samps[i] = samp_bin

            # clusterizing samples(聚类样本)
            self.clust = {self.data.fvmap.dir[(
                self.data.names[-1], v)]: [] for v in self.data.feats[-1]}
            try:
                for i, s in enumerate(self.data.samps):
                    self.clust[s[-1]].append(i)
            except KeyError:
                # exit whole program
                print('c0 error: inconsistent data')
                import SynDS
                SynDS.programTimeOut1()
                SynDS.programTimeOut2()

            # creating a formula
            self.formula = WCNF()
            self.formula.nv = len(data.samps)
            self.formula.topw = len(data.samps) + 1

            # soft clauses and their weights
            for i, sample in enumerate(data.samps):
                self.formula.soft.append([i + 1])
                self.formula.wght.append(data.wghts[i])

            # hard clauses (pairwise overlapping samples)
            for c1, c2 in itertools.combinations(self.clust.keys(), 2):
                for i in self.clust[c1]:
                    samp = set([-l for l in self.dbin.samps[i]])
                    for j in self.clust[c2]:
                        if not samp.intersection(set(self.dbin.samps[j])):
                            self.formula.hard.append([-i - 1, -j - 1])

    def do(self):
        # call  a MaxSAT solver
        # deciding whether or not to stratify
        if max(self.formula.wght) > min(self.formula.wght):
            MXS = RC2Stratified
            # print("使用RC2S")
        else:
            MXS = RC2
            # print("使用RC2S")

        # here we use MSE18 configuration 'b'
        with MXS(self.formula, solver='g3', adapt=True, exhaust=True, incr=False, minz=True, trim=0, verbose=0) as rc2:
            # print("进入MXS")
            rc2.compute()
            model = rc2.model[:]
            self.consistent = list(
                map(lambda l: l - 1, filter(lambda l: 0 < l <= self.formula.nv, model)))
            # print("self.consistent:",self.consistent)
        if len(self.consistent) == len(self.data.samps):
            return True
        else:
            return False

    def remove_inconsistent(self):
        # print("进入remove")
        # Take a smallest subset of all inconsistent samples out.
        samps = [self.data.samps[i] for i in self.consistent]
        wghts = [self.data.wghts[i] for i in self.consistent]
        self.data.samps_filt = len(self.data.samps) - len(samps)
        self.data.wghts_filt = len(self.data.wghts) - sum(wghts)
        self.data.samps = samps
        self.data.wghts = wghts
        # print("sample:", self.data.samps, len(self.data.samps))
        # print("wghts:", self.data.wghts)
        # print('c0 filtering out {0} samples ({1} left)'.format(self.data.samps_filt, len(self.data.samps))) #6    8
        # print('c0 filtering out {0} weights ({1} left)'.format(self.data.wghts_filt, sum(self.data.wghts))) #8    12
        # recomputing the number of classes
        classes = set([])
        for sample in self.data.samps:
            classes.add(sample[-1])

        # for i in self.featureSet:

        # removing variables for unnecessary classes
        self.data.deleted = set([])
        deleted_vars = set([])
        for l in self.data.feats[-1]:
            pair = (self.data.names[-1], l)
            var = self.data.fvmap.dir[pair]

            if var not in classes:
                del (self.data.fvmap.dir[pair])
                del (self.data.fvmap.opp[var])
                self.data.deleted.add(l)
                deleted_vars.add(var)

        self.data.feats[-1] = list(
            filter(lambda x: x not in self.data.deleted, self.data.feats[-1]))
        self.data.deleted = deleted_vars

        # updating status
        self.status = True if len(classes) > 1 else False
        # self.time = resource.getrusage(resource.RUSAGE_SELF).ru_utime - self.init_time
        # self.time += resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime
