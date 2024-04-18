import collections
import itertools
import six


class Data(object):
    def __init__(self, featureSet):
        self.fvmap = None
        self.featureSet = featureSet
        self.names = None
        self.nm2id = None
        self.samps = None
        self.feats = None
        self.fvars = None
        self.deleted = set([])
        self.wghts = None
        self.parse(featureSet)
        self.process_data()
        # print("process_data!")

    def parse(self, featureSet):
        # print("self.featureSet", self.featureSet)
        # print("len(self.featureSet)", len(self.featureSet))
        self.names = self.featureSet[0]
        # print("self.name-data:",self.names,"over!")
        self.feats = [set([]) for n in self.names]
        # 映射names到id
        self.nm2id = {name: i for i, name in enumerate(self.names)}
        # print("nm2id:",self.nm2id)
        # 读取训练样本
        self.samps, self.wghts = [], []
        # print("self.featureSet[1:]", self.featureSet[1:])
        # 字典：line : w

        sample_counts = collections.Counter(
            tuple(sample) for sample in self.featureSet[1:])

        for i in range(len(self.featureSet[1:])):
            sample = self.featureSet[1:][i]
            # print("sample:", sample)
            for j, f in enumerate(sample):
                # print("self.featureSet[1:][i]:", self.featureSet[1:][i])
                # print("j, f:", j, str(f))
                if f and j < len(self.feats):
                    self.feats[j].add(f)
            if sample not in self.samps:
                self.samps.append(sample)
                count = sample_counts.get(tuple(sample), 0)
                self.wghts.append(count)
        # print("self.wghts:", self.wghts)
        # 输出结果：[{0, 1}, {0, 1}, {1}, {0}, {0, 1}] 集合的元素顺序不重要
        # self.feats = [sorted(s, reverse=True) for s in self.feats]
        # 输出结果：[[1, 0], [1, 0], [1], [0], [1, 0]]
        # print("feats:",self.feats)
        # print("samps:",self.samps)

    def process_data(self):
        # direct and opposite mappings for items
        idpool = itertools.count(start=1)
        FVMap = collections.namedtuple('FVMap', ['dir', 'opp'])
        self.fvmap = FVMap(dir={}, opp={})

        # mapping features to ids
        for i in range(len(self.names) - 1):
            feats = sorted(self.feats[i])
            if len(feats) != 2:
                for l in feats:
                    self.fvmap.dir[(self.names[i], l)] = next(idpool)
            else:
                var = next(idpool)
                self.fvmap.dir[(self.names[i], feats[0])] = var
                self.fvmap.dir[(self.names[i], feats[1])] = -var
        # print("sorted(feats):", self.feats)
        # all labels are marked with distinct ids
        for l in sorted(self.feats[-1]):
            self.fvmap.dir[(self.names[-1], l)] = next(idpool)

        # opposite mapping
        # 返回（key，value）的元组
        for key, val in six.iteritems(self.fvmap.dir):
            self.fvmap.opp[val] = key
        # encoding samples and filtering out features with only 1 value
        # print("self.fvmap.dir", self.fvmap.dir)
            for i in range(len(self.samps)):
                t = None
                try:
                    t = self.fvmap.dir[(self.names[-1], self.samps[i][-1])]
                except KeyError as e:
                    print("KeyError:", e)
                    break
                self.samps[i] = [self.fvmap.dir[(self.names[j], self.samps[i][j])] for j in range(
                    len(self.samps[i]) - 1) if self.samps[i][j] and len(self.feats[j]) > 1]
                self.samps[i].append(t)

        # determining feature variables (excluding class variables)
        for v, pair in six.iteritems(self.fvmap.opp):
            # print("stop!")
            if str(pair[0]) == self.names[-1]:
                self.fvars = v - 1
                break
