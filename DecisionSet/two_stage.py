import collections
import itertools

import numpy as np
import six
from z3 import Optimize, And, Or, Not, Bool, PbLe, Implies, PbGe, sat

from DecisionSet.rule import Rule


# A decision set implementation based on Ignatiev (2021)
#
# the TwoStage class is intended to have a similar interface with
# `Learn_DS` in Minds2.py to serve as a drop-in replacement
#
# Two stage method consist of several constraints, notably hard clauses and soft ones:
# 1. hard clause: feature are single valued. There can be at most one feature value for each feature.
#    This can be constrained by pseudo-boolean function (pb leq)
# 2. hard clause: for a given term, its literal must at least cover one training example of its class, and
#    discriminate all others of different classes, where `discriminate` means any of the literal(feature) select
#    the opposite value of corresponding feature value in the training example, and `cover` means not discriminate
# 3. soft clause: preference to discard features from the term.
#    for feature `f` with values {v1,v2,..,vn}, the preference is encoded as `And(not(v1), not(v2), ..., not(vn))`
#
# For training a specific class, with all instances covered by terms, the
# objective is to minimize the number of terms


# Spec for input data
# example:
#
# {'deleted': set(),
#  'feats': [{'0'}, {'1', '0'}, {'1', '0'}, {'1', '0'}, {'1'}, {'1', '0'}, {'1'}],
#  'featureSet': [['v1 == v2',
#                  'v1 == 0',
#                  'v1 == 1',
#                  'v2 == 1',
#                  'v1 >= 0',
#                  'v2 > 1',
#                  'target'],
#                 ['0', '1', '0', '1', '1', '0', '1'],
#                 ['0', '0', '1', '0', '1', '0', '1'],
#                 ['0', '1', '0', '0', '1', '1', '1']],
#  'fvars': 6,
#  'fvmap': FVMap(dir={('v1 == v2', '0'): 1, ('v1 == 0', '0'): 2, ('v1 == 0', '1'): -2, ('v1 == 1', '0'): 3, ('v1 == 1', '1'): -3, ('v2 == 1', '0'): 4, ('v2 == 1', '1'): -4, ('v1 >= 0', '1'): 5, ('v2 > 1', '0'): 6, ('v2 > 1', '1'): -6, ('target', '1'): 7}, opp={1: ('v1 == v2', '0'), 2: ('v1 == 0', '0'), -2: ('v1 == 0', '1'), 3: ('v1 == 1', '0'), -3: ('v1 == 1', '1'), 4: ('v2 == 1', '0'), -4: ('v2 == 1', '1'), 5: ('v1 >= 0', '1'), 6: ('v2 > 1', '0'), -6: ('v2 > 1', '1'), 7: ('target', '1')}),
#  'names': ['v1 == v2',
#            'v1 == 0',
#            'v1 == 1',
#            'v2 == 1',
#            'v1 >= 0',
#            'v2 > 1',
#            'target'],
#  'nm2id': {'target': 6,
#            'v1 == 0': 1,
#            'v1 == 1': 2,
#            'v1 == v2': 0,
#            'v1 >= 0': 4,
#            'v2 == 1': 3,
#            'v2 > 1': 5},
#  'samps': [[-2, 3, -4, 6, 7], [2, -3, 4, 6, 7], [-2, 3, 4, -6, 7]],
#  'vmiss': [{0, 4}, {0, 4}, {0, 4}],
#  'wghts': [1, 1, 1]}


# skip feature r in term j
def svar(r, j):
    return Bool("s_{0}_{1}".format(r, j))


# in term j, feature value r is present
def pvar(r, j):
    return Bool("p_{0}_{1}".format(r, j))


def nvar(r, j):
    return Bool("n_{0}_{1}".format(r, j))


# coverage
def avar(q, j):
    return Bool("a_{0}_{1}".format(q, j))


# select term j
def bvar(j):
    return Bool("b_{0}".format(j))


class TwoStage:
    def __init__(self, data):
        self.nof_terms = None
        self.conset = {}
        self.data = data
        self.samps = {
            self.data.fvmap.dir[(self.data.names[-1], v)]: []
            for v in sorted(self.data.feats[-1])
        }
        self.covrs = {
            self.data.fvmap.dir[(self.data.names[-1], v)]: []
            for v in sorted(self.data.feats[-1])
        }
        for i, s in enumerate(self.data.samps):
            self.samps[s[-1]].append(i)
        self.binarize()
        self.get_missing()
        self.cost = 0

    def binarize(self):
        FFMap = collections.namedtuple("FFMap", ["dir", "opp"])
        self.ffmap = FFMap(dir={}, opp={})
        curr_id = 0
        vfmap = {}

        for r, (name, feats) in enumerate(
            zip(self.data.names[:-1], self.data.feats[:-1])
        ):
            fgroup = []
            if len(feats) != 2:
                vars_ = sorted([self.data.fvmap.dir[name, v] for v in feats])
                for i, var in enumerate(vars_):
                    vfmap[var] = [-v for v in vars_]
                    vfmap[var][i] = var
                    self.ffmap.opp[i + curr_id] = var
                    fgroup.append(i + curr_id)
                curr_id += len(feats)
            else:
                var = self.data.fvmap.dir[name, sorted(feats)[0]]
                vfmap[var] = [var]
                vfmap[-var] = [-var]
                self.ffmap.opp[curr_id] = var
                fgroup.append(curr_id)
                curr_id += 1
            self.ffmap.dir[r] = fgroup

        lengths = np.array([len(arr) for arr in self.data.samps])
        minlen = min(lengths)

        if np.all(lengths == lengths[0]):
            for i in range(len(self.data.samps)):
                samp, out = self.data.samps[i][:-1], self.data.samps[i][-1]
                self.data.samps[i] = []

                for l in samp:
                    self.data.samps[i].extend(vfmap[l])
                self.data.samps[i].append(out)
        else:
            samps = []
            for i in range(len(self.data.samps)):
                samp, out = (
                    self.data.samps[i][: minlen - 1],
                    self.data.samps[i][minlen - 1:],
                )
                vsamp = list(itertools.chain.from_iterable(
                    [vfmap[x] for x in samp]))
                p = [vsamp + [k] for k in out]
                samps += p
            self.data.samps = samps
        self.nof_feats = curr_id

    def get_missing(self):
        self.data.vmiss = []
        for s in self.data.samps:
            missing = []
            if len(s) < self.nof_feats + 1:
                r = i = 0
                while i < len(s) - 1:
                    if (
                        r
                        in self.ffmap.dir[
                            self.data.nm2id[self.data.fvmap.opp[abs(s[i])][0]]
                        ]
                    ):
                        i += 1
                    else:
                        missing.append(r)
                    r += 1
                    if r > 200:
                        break
                # adding the rest of the features
                missing.extend(range(r, self.nof_feats))
            # set is needed for testing inclusion
            self.data.vmiss.append((set(missing)))

    def compute(self):
        self.cost = 0
        self.time = 0.0
        self.labels = sorted(self.samps.keys())
        upperbound = 2*max([len(self.samps[l]) for l in self.labels])
        nof_terms = 1
        remaining = self.labels.copy()

        while remaining:
            if nof_terms > upperbound:
                print("DEBUG:: Two stage failed to find a solution")
                return self.covrs, {}
            newremaining = remaining.copy()
            for label in remaining:
                enc = self.encode(label, nof_terms=nof_terms)

                res = enc.check()
                if res == sat:
                    model = enc.model()
                    self.extract_cover(label, model)
                    newremaining.remove(label)
                else:
                    print(
                        f"DEBUG:: label {label} unsat at nof_terms {nof_terms}")
            remaining = newremaining
            nof_terms = nof_terms + 1
        print("DEBUG:: Two stage computed")
        return self.covrs, self.conset

    def extract_cover(self, label, model):
        for j in range(1, self.nof_terms + 1):
            if not model[bvar(j)]:
                continue
            premise = []
            for r in range(1, self.nof_feats + 1):
                if model[pvar(r, j)]:
                    id_orig = self.ffmap.opp[r - 1]
                    premise.append(id_orig)
                elif model[nvar(r, j)]:
                    id_orig = self.ffmap.opp[r - 1]
                    premise.append(-id_orig)

            rule = Rule(fvars=premise, label=label, mapping=self.data.fvmap)

            if int(self.data.fvmap.opp[label][1]) in self.conset:
                self.conset[int(self.data.fvmap.opp[label][1])
                            ].append(rule.extr0feat())
            else:
                self.conset[int(self.data.fvmap.opp[label][1])] = [
                    rule.extr0feat()]
            self.covrs[label].append(rule)
            self.cost += len(rule)
        return self.covrs

    def encode(self, label, nof_terms=1):
        print(f"DEBUG:: encoding for label {label}, nof_term = {nof_terms}")
        self.nof_terms = nof_terms
        enc = Optimize()

        # feature is single valued:
        # for these features with more than 1 value, check that at most one
        # value is true
        for feats in six.itervalues(self.ffmap.dir):
            if len(feats) > 2:
                for j in range(1, self.nof_terms + 1):
                    lits = [((pvar(r + 1, j)), 1) for r in feats]
                    enc.add(PbLe(lits, 1))

        # discriminate opposing examples
        if len(self.labels) == 1:
            other_labels = set(self.samps.keys())
        else:
            other_labels = set(self.labels)
        other_labels.remove(label)
        other_labels = sorted(other_labels)
        for j in range(1, self.nof_terms + 1):
            for opposite in other_labels:
                for q in self.samps[opposite]:
                    cl = []
                    shift = 0
                    for r in range(1, self.nof_feats + 1):
                        if r - 1 in self.data.vmiss[q]:
                            cl.append(Not(svar(r, j)))
                            shift += 1
                        elif self.data.samps[q][r - 1 - shift] > 0:
                            cl.append(nvar(r, j))
                        else:
                            cl.append(pvar(r, j))
                    enc.add(Or(cl))

        # all instances are covered
        for j in range(1, self.nof_terms + 1):
            for q in self.samps[label]:
                cr = avar(q + 1, j)

                cl = []
                shift = 0
                for r in range(1, self.nof_feats + 1):
                    if r - 1 in self.data.vmiss[q]:
                        cl.append(svar(r, j))
                        shift += 1
                    elif self.data.samps[q][r - 1 - shift] > 0:
                        cl.append(Not(nvar(r, j)))
                    else:
                        cl.append(Not(pvar(r, j)))
                # cr -> not discriminate
                enc.add(Implies(cr, And(cl)))
            enc.add(Or([avar(q + 1, j) for q in self.samps[label]]))
        for q in self.samps[label]:
            enc.add(
                PbGe(
                    [
                        (And(avar(q + 1, j), bvar(j)), 1)
                        for j in range(1, self.nof_terms + 1)
                    ],
                    1,
                )
            )

        for j in range(1, self.nof_terms + 1):
            # preference to discard feature
            for feature, vals in self.ffmap.dir.items():
                for r in vals:
                    # skip -> not present
                    enc.add(
                        Implies(svar(feature, j), And(
                            Not(pvar(r, j)), Not(nvar(r, j))))
                    )
                # skip if possible
                enc.add_soft(svar(feature, j))
            # smallest rule cover: minimize the number of terms
            enc.add_soft(Not(bvar(j)))

        # break symmetry
        for j in range(1, self.nof_terms + 1):
            cl = []
            for q in self.samps[label]:
                notCovered = [ Not(avar(q + 1, k)) for k in range(1, j-1)]
                cl.append(And(And(notCovered), avar(q + 1, j)))
            enc.add(Or(cl))

        return enc
