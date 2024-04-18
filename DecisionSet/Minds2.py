import collections
from pysat.card import *
from pysat.formula import CNF, WCNF
from pysat.solvers import Solver as pysat_Solver
from pysat.examples.rc2 import RC2
import six
from DecisionSet.data import Data
from DecisionSet.rule import Rule
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import itertools


class Learn_DS(object):
    def __init__(self, data):
        self.conset = {}
        self.data = data
        self.reset_idpool()
        self.samps = {self.data.fvmap.dir[(
            self.data.names[-1], v)]: [] for v in sorted(self.data.feats[-1])}
        self.covrs = {self.data.fvmap.dir[(
            self.data.names[-1], v)]: [] for v in sorted(self.data.feats[-1])}
        print("测试self.data.name:", self.data.names)
        print("测试self.samps:", self.samps)
        print("测试self.data.samps:", self.data.samps)
        # self.data.samps遍历之后未发生变化，self.samps：{12: [5, 6, 8], 13: [0, 1, 2], 14: [3, 9], 15: [4, 7]} 最后的class：对应的索引数组
        for i, s in enumerate(self.data.samps):
            print("测试i:", i)
            print("测试s:", s)
            self.samps[s[-1]].append(i)
        print("测试self.samps遍历后:", self.samps)
        self.binarize()
        # get missing values for each sample
        self.get_missing()
        self.cost = 0
    # 为变量或者原子命题生成唯一的标识符

    def reset_idpool(self):
        self.idpool = IDPool(start_from=1)

    # one-hot编码
    def binarize(self):
        FFMap = collections.namedtuple('FFMap', ['dir', 'opp'])
        self.ffmap = FFMap(dir={}, opp={})
        curr_id = 0
        # 将特征id映射到特征id列表
        vfmap = {}

        # 重写样本
        for r, (name, feats) in enumerate(zip(self.data.names[:-1], self.data.feats[:-1])):
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

        # 重写samples
        # arr_np = np.array(self.data.samps)
        # lengths = np.array([len(subarray) for subarray in arr_np])
        lengths = np.array([len(arr) for arr in self.data.samps])
        minlen = min(lengths)

        if np.all(lengths == lengths[0]):  # 二元编码
            for i in range(len(self.data.samps)):
                # 最后一个元素是out，其他元素在samp中===> 需要考虑多个class的情况
                samp, out = self.data.samps[i][:-1], self.data.samps[i][-1]
                self.data.samps[i] = []

                for l in samp:
                    self.data.samps[i].extend(vfmap[l])
                self.data.samps[i].append(out)
        else:
            # one-hot编码
            # for i in range(len(self.data.samps)):
            #     samp, out = self.data.samps[i][:minlen - 1], self.data.samps[i][minlen - 1:]
            #     # print("测试one-hot，samp：", samp)
            #     self.data.samps[i] = []
            #     for m in samp:
            #         self.data.samps[i].extend(vfmap[m])
            #     for l in out:
            #         label_idx = out.index(l) #位置l处的元素
            #         encoder = OneHotEncoder()
            #         one_hot_label = encoder.fit_transform([[label_idx]]).toarray().flatten()
            #         print(f"DEBUG:: {label_idx} {one_hot_label}")
            #         self.data.samps[i].extend(one_hot_label)
            print("DEBUG:: experimental onehot!!!")
            samps = []
            for i in range(len(self.data.samps)):
                samp, out = self.data.samps[i][:minlen -
                                               1], self.data.samps[i][minlen - 1:]
                vsamp = list(itertools.chain.from_iterable(
                    [vfmap[x] for x in samp]))
                p = [vsamp + [k] for k in out]
                samps += p
            self.data.samps = samps
        self.nof_feats = curr_id
        # print("binarize完成！")

    def get_missing(self):
        self.data.vmiss = []
        for s in self.data.samps:
            missing = []
            if len(s) < self.nof_feats + 1:
                r = i = 0
                while i < len(s) - 1:
                    if r in self.ffmap.dir[self.data.nm2id[self.data.fvmap.opp[abs(s[i])][0]]]:
                        i += 1
                    else:
                        missing.append(r)
                    r += 1
                # adding the rest of the features
                missing.extend(range(r, self.nof_feats))
            # set is needed for testing inclusion
            self.data.vmiss.append((set(missing)))
        # print("get_missing完成！")

    def compute(self):
        self.cost = 0
        nof_terms = 1
        self.time = 0.0
        # depending on this option, we compute either one class or all of them 默认all
        computed = 0
        self.labels = sorted(self.samps.keys())
        while True:
            for label in self.labels:
                # print("label:", label)
                if self.covrs[label]:
                    continue
                # resetting the pool of ids
                self.reset_idpool()
                # the main part is encoding：返回cnf公式
                enc = self.encode(label, nof_terms=nof_terms)
                with pysat_Solver(name='glucose3', bootstrap_with=enc.clauses) as s:
                    res = s.solve()
                    if res:
                        model = s.get_model()
                        model = self.optimize(enc)
                        self.extract_cover(label, model)
                        computed += 1
                        if computed >= len(self.data.feats[-1]):
                            # 添加时间
                            return self.covrs, self.conset
            else:
                nof_terms += 1

    def encode(self, label, nof_terms=1):
        self.nof_terms = nof_terms
        enc = CNF()

        # constraints 6：每个rule必须至少有一个特征r中的literal
        for j in range(1, self.nof_terms + 1):
            enc.append([-self.svar(j, r)
                       for r in range(1, self.nof_feats + 1)])

        # constraints 7：
        for j in range(1, self.nof_terms + 1):
            for r in range(1, self.nof_feats + 1):
                d0 = self.dvar0(j, r)
                p0 = [-self.svar(j, r), self.lvar(j, r)]
                enc.append([d0, -p0[0], -p0[1]])
                enc.append([-d0, p0[0]])
                enc.append([-d0, p0[1]])
                d1 = self.dvar1(j, r)
                p1 = [-self.svar(j, r), -self.lvar(j, r)]
                enc.append([d1, -p1[0], -p1[1]])
                enc.append([-d1, p1[0]])
                enc.append([-d1, p1[1]])

        # constraints 8:
        if len(self.labels) == 1:
            other_labels = set(self.samps.keys())
        else:
            other_labels = set(self.labels)
        other_labels.remove(label)
        other_labels = sorted(other_labels)
        for j in range(1, self.nof_terms + 1):
            for lb in other_labels:
                for q in self.samps[lb]:
                    cl = []
                    shift = 0
                    for r in range(1, self.nof_feats + 1):
                        if r - 1 in self.data.vmiss[q]:
                            # this feature is missing in q'th sample
                            cl.append(-self.svar(j, r))
                            shift += 1
                        elif self.data.samps[q][r - 1 - shift] > 0:
                            cl.append(self.dvar1(j, r))
                        else:
                            cl.append(self.dvar0(j, r))
                    enc.append(cl)

        # constraints 9:
        for j in range(1, self.nof_terms + 1):
            for q in self.samps[label]:
                cr = self.crvar(j, q + 1)
                cl = []
                shift = 0
                for r in range(1, self.nof_feats + 1):
                    # 样本q在特征r上的取值 ------- 还有一种情况：特征r对应的值没有呢
                    if r - 1 in self.data.vmiss[q]:
                        cl.append(-self.svar(j, r))
                        shift += 1
                    elif self.data.samps[q][r - 1 - shift] > 0:
                        cl.append(self.dvar1(j, r))
                    else:
                        cl.append(self.dvar0(j, r))
                enc.append([cr] + cl)  # 组合成新的list,list的元素之间是or
                for l in cl:
                    enc.append([-cr, -l])

        self.add_bsymm(enc)

        # constraints 5 精度按照100  有问题
        for q in self.samps[label]:
            enc.append([self.crvar(j, q + 1)
                       for j in range(1, self.nof_terms + 1)])

        # at most one value can be chosen for a feature
        for feats in six.itervalues(self.ffmap.dir):
            if len(feats) > 2:
                for j in range(1, self.nof_terms + 1):
                    lits = [self.dvar0(j, r + 1) for r in feats]
                    onev = CardEnc.atmost(
                        lits, top_id=enc.nv, encoding=EncType.cardnetwrk)
                    enc.extend(onev.clauses)
        return enc

    def add_bsymm(self, enc):
        for j in range(2, self.nof_terms + 1):
            enc.append([self.eqvar(j, 0)])
            enc.append([-self.gtvar(j, 0)])
            enc.append([self.gtvar(j, self.nof_feats)])
            for r in range(1, self.nof_feats + 1):
                # constraint 11
                # left hand side
                lhs = -self.eqvar(j, r)
                # term1
                enc.append([-self.teqvar(j, r, 1), self.svar(j - 1, r)])
                enc.append([-self.teqvar(j, r, 1), -self.svar(j, r)])
                enc.append([self.teqvar(j, r, 1), -
                           self.svar(j - 1, r), self.svar(j, r)])
                # term2
                enc.append([-self.teqvar(j, r, 2), -self.svar(j - 1, r)])
                enc.append([-self.teqvar(j, r, 2), self.svar(j, r)])
                enc.append([self.teqvar(j, r, 2), self.svar(
                    j - 1, r), -self.svar(j, r)])
                # term3
                enc.append([-self.teqvar(j, r, 3), self.dvar1(j - 1, r)])
                enc.append([-self.teqvar(j, r, 3), self.dvar0(j, r)])
                enc.append([self.teqvar(j, r, 3), -
                           self.dvar1(j - 1, r), -self.dvar0(j, r)])
                # term4
                enc.append([-self.teqvar(j, r, 4), self.dvar0(j - 1, r)])
                enc.append([-self.teqvar(j, r, 4), self.dvar1(j, r)])
                enc.append([self.teqvar(j, r, 4), -
                           self.dvar0(j - 1, r), -self.dvar1(j, r)])
                # right-hand side
                cl = [-self.eqvar(j, r - 1),
                      self.teqvar(j, r, 1),
                      self.teqvar(j, r, 2),
                      self.teqvar(j, r, 3),
                      self.teqvar(j, r, 4)]
                # final clauses
                enc.append([-lhs] + cl)
                for l in cl:
                    enc.append([-l, lhs])
                # constraint 12
                # left-hand side
                lhs = self.gtvar(j, r)
                # term1
                enc.append([-self.tgtvar(j, r, 1), self.eqvar(j, r - 1)])
                enc.append([-self.tgtvar(j, r, 1), -self.svar(j - 1, r)])
                enc.append([-self.tgtvar(j, r, 1), self.svar(j, r)])
                enc.append([self.tgtvar(j, r, 1), -self.eqvar(j, r - 1),
                           self.svar(j - 1, r), -self.svar(j, r)])
                # term2
                enc.append([-self.tgtvar(j, r, 2), self.eqvar(j, r - 1)])
                enc.append([-self.tgtvar(j, r, 2), self.dvar1(j - 1, r)])
                enc.append([-self.tgtvar(j, r, 2), self.dvar0(j, r)])
                enc.append([self.tgtvar(j, r, 2), -self.eqvar(j,
                           r - 1), -self.dvar1(j - 1, r), -self.dvar0(j, r)])
                # right-hand side
                cl = [self.gtvar(j, r - 1),
                      self.tgtvar(j, r, 1),
                      self.tgtvar(j, r, 2)]
                # final clause
                enc.append([-lhs] + cl)
                for l in cl:
                    enc.append([-l, lhs])

    # 对于rule j，特征r中的literal，是否被跳过
    def svar(self, j, r):
        return self.idpool.id('s_{0}{1}'.format(j, r))

    # rule j的特征r是否区分值0
    def dvar0(self, j, r):
        return self.idpool.id('d0_{0}{1}'.format(j, r))

    # rule j的特征r是否区分值1
    def dvar1(self, j, r):
        return self.idpool.id('d1_{0}{1}'.format(j, r))

    # 在不跳过特征的情况下，规则j的特征r上的文字
    def lvar(self, j, r):
        return self.idpool.id('l_{0}{1}'.format(j, r))

    # 是否使用rule j覆盖eq属于E+
    def crvar(self, j, q):
        return self.idpool.id('cr_{0}{1}'.format(j, q))

    # 当且仅当样本q被覆盖时为True
    def cvvar(self, q):
        return self.idpool.id('cv_{0}'.format(q))

    def eqvar(self, j, r):
        return self.idpool.id('eq_{0}_{1}'.format(j, r))

    def gtvar(self, j, r):
        return self.idpool.id('gt_{0}_{1}'.format(j, r))

    def tgtvar(self, j, r, i):
        return self.idpool.id('tg_{0}_{1}_{2}'.format(j, r, i))

    def teqvar(self, j, r, i):
        return self.idpool.id('te_{0}_{1}_{2}'.format(j, r, i))

    def optimize(self, enc):
        model = [-v for v in range(enc.nv)]
        all_vars = set()

        # MaxSAT formula to work with
        formula = WCNF()
        # hard clause
        for cl in enc.clauses:
            formula.append(cl)
        for j in range(1, self.nof_terms + 1):
            for r in range(1, self.nof_feats + 1):
                formula.append([-self.dvar1(j, r), 1])
                formula.append([-self.dvar0(j, r), 1])
                all_vars.add(self.dvar1(j, r))
                all_vars.add(self.dvar0(j, r))
        hitman = RC2(formula, solver='glucose3', adapt=True,
                     exhaust=True, incr=False, minz=False, trim=0)
        # hs = list(filter(lambda v: v > 0 and v in all_vars, hitman.compute()))
        hs = hitman.compute()
        if hs is not None:
            hs = list(filter(lambda v: v > 0 and v in all_vars, hs))
            for e in hs:
                model[e - 1] = e
        hitman.delete()
        # for e in hs:
        #     model[e - 1] = e
        return model
    # 从model中提取DS

    def extract_cover(self, label, model):
        for j in range(1, self.nof_terms + 1):
            premise = []
            for r in range(1, self.nof_feats + 1):
                if model[self.dvar0(j, r) - 1] > 0:
                    id_orig = self.ffmap.opp[r - 1]
                    premise.append(id_orig)
                elif model[self.dvar1(j, r) - 1] > 0:
                    id_orig = self.ffmap.opp[r - 1]
                    premise.append(-id_orig)
            # creating the rule
            rule = Rule(fvars=premise, label=label, mapping=self.data.fvmap)
            # print('c1 cover:', str(rule))

            if int(self.data.fvmap.opp[label][1]) in self.conset:
                self.conset[int(self.data.fvmap.opp[label][1])
                            ].append(rule.extr0feat())
            else:
                self.conset[int(self.data.fvmap.opp[label][1])] = [
                    rule.extr0feat()]
            # print("conset:", self.conset)
            # if self.data.fvmap.opp[label][1] == '0':
            #     # conset中追加为true的DS
            #     self.conset.append(rule.extr0feat())
            # print("conset:",self.conset)
            self.covrs[label].append(rule)
            self.cost += len(rule)
        return self.covrs
