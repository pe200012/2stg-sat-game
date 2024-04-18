class Rule(object):
    def __init__(self, fvars = None, label = None, mapping = None):
        self.flits = fvars
        self.label = label
        self.fvmap = mapping
        conset = []
    def __str__(self):
        assert self.label, 'No class assigned'
        assert self.fvmap, 'No mapping from literals to feature-values'
        if self.flits:
            premise = []
            for l in self.flits:
                # print("l:", l)
                # feat, val = self.fvmap.opp[abs(l)]
                feat, val = self.fvmap.opp[l]
                # print("feat,val:", feat, val)
                # if l > 0:
                #     premise.append('{0}'.format(''))
                # else:
                premise.append('\'{0}: {1}\''.format(feat, val))
            if self.label in self.fvmap.opp:
                # target_class = self.fvmap.opp[self.label]
                # premise.append('{0}\'{1}: {2}\''.format('' if l > 0 else 'not', feat, val))
            # print("self.fvmap.opp[self.label]:", self.fvmap.opp[self.label][1])
            # target_class = self.fvmap.opp[self.label]
                return 'If {0} Then \'{1}: {2}\''.format(', '.join(premise), *self.fvmap.opp[self.label])
            #     return '{0}\'{1}: {2}\''.format(', '.join(premise), *self.fvmap.opp[self.label])
            else:
                return '{0}'.format(', '.join(premise))
        else:
            # 如果rule没有前提条件，返回True
            # return 'true \'{1}: {2}\''.format(*self.fvmap.opp[self.label])
            return 'True'

    def __len__(self):
        assert self.label, 'No class assigned'
        assert self.fvmap, 'No mapping from literals to feature-values'
        return len(self.flits) if self.flits else 0


    def extr0feat(self):
        # 筛选为true（0）的特征
        # print("self.fvmap.opp[self.label][1]:", self.fvmap.opp[self.label][1])
        # if self.fvmap.opp[self.label][1] == '0':
        featNum = []
        for l in self.flits:
            feat, val = self.fvmap.opp[l]
            if val == '1':
                featNum.append(feat)
            else:
                featNum.append("Not({0})".format(feat))
        return featNum