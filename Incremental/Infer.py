
from pysat.formula import CNF
from pysat.solvers import Solver


class Node:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None


class Mysolver:

    def __init__(self, k, numfeature, numclasses, data, terms):
        self.data = data
        self.k = k
        self.numfeature = numfeature
        self.numclasses = numclasses
        self.localindex = 0
        self.myslover = Solver(name='m22')
        self.numadderrElement = 0
        self.toUpdate = True
        self.X = []
        self.F = []
        self.CL = []
        self.Used = []
        self.Compter = []
        self.terms = terms
        self.minint = -2147483648
        # 1.内部节点index 从1开始    特征index从0开始    每个内部节点上都必须存放至少一个特征
        for i in range(1, pow(2, self.k)):
            one = []
            for j in range(self.numfeature):
                one.append(self.getVarF(i, j))
            self.myslover.add_clause(one)

        # 2.叶子index 从0开始        标签index从0开始   每个叶子节点上都必须存放至少一个标签
        for i in range(pow(2, k)):
            one = []
            for j in range(self.numclasses):
                # self.getVarCL(i, j)
                one.append(self.getVarCL(i, j))
                one.append(-self.getVarCL(i, j))
            self.myslover.add_clause(one)
        # 3.第三个初始化                               每个内部节点上都只能存放一个特征
        for i in range(1, pow(2, self.k)):
            for f1 in range(self.numfeature):
                for f2 in range(f1+1, self.numfeature):
                    one = []
                    one.append(-self.getVarF(i, f1))
                    one.append(-self.getVarF(i, f2))
                    self.myslover.add_clause(one)

    # (1).第0个错误样本，j深度,也是从0开始

    def getVarX(self, e, j):
        if e+1 > len(self.X):
            self.X.append([])
            self.localindex += 1
            self.X[e].append(self.localindex)
            return self.X[e][j]
        else:
            if j+1 > len(self.X[e]):
                self.localindex += 1
                self.X[e].append(self.localindex)
                return self.X[e][j]
            else:
                return self.X[e][j]

    # (2).内部节点index q和特征index j得到变量index    前面主要变量
    def getVarF(self, q, j):

        if q > len(self.F):
            self.F.append([])
            self.localindex += 1
            self.F[q-1].append(self.localindex)
            return self.localindex

        else:

            if j+1 > len(self.F[q-1]):
                self.localindex += 1
                self.F[q-1].append(self.localindex)
                return self.localindex
            else:
                return self.F[q-1][j]

    # (3).根据叶子节点index q和标签index cl得到变量index    前面主要变量
    def getVarCL(self, q, cl):
        if q+1 > len(self.CL):
            self.CL.append([])
            self.localindex += 1
            self.CL[q].append(self.localindex)
            return self.CL[q][cl]
        else:
            if cl+1 > len(self.CL[q]):
                self.localindex += 1
                self.CL[q].append(self.localindex)
                return self.CL[q][cl]
            else:
                return self.CL[q][cl]
    # (4)求赋予标签的叶子节点的变量Index

    def getVarUsed(self, q):
        if q+1 > len(self.Used):
            self.localindex += 1
            self.Used.append(self.localindex)
            return self.Used[q]
        else:
            return self.Used[q]

    # (5)求HHH
    def getVarCompter(self, i, j):
        if i+1 > len(self.Compter):
            self.Compter.append([])
            self.localindex += 1
            self.Compter[i].append(self.localindex)
            return self.Compter[i][j]
        else:
            if j+1 > len(self.Compter[i]):
                self.localindex += 1
                self.Compter[i].append(self.localindex)
                return self.Compter[i][j]
            else:
                return self.Compter[i][j]

    # 1.求解约束并得到返回模型
    def inferModel(self, maxNumberOfleaves):
        if maxNumberOfleaves == 0:
            sign = self.myslover.solve()
        if maxNumberOfleaves > 0:
            sign = self.myslover.solve([-self.getVarCompter(pow(2, self.k),
                                                            maxNumberOfleaves+1)
                                        ]
                                       )

        return sign

    # *******************************************2.添加H 最大节点约束1个
    def addMaxOneleave(self, maxNumberOfleaves):
        self.myslover.solve(-self.getVarCompter(pow(2, self.k),
                                                maxNumberOfleaves+1)
                            )
    # *************************************************************

    # 2.会进行此函数操作，则sign肯定为true,得到模型  返回root节点
    def getModel(self):
        # innernode = ['#']
        # leavernode = ['#']
        # 第一个节点在index为1d的地方
        tree = ['#']
        # 第i个变量在index为i的地方
        model = ['#']
        # 前面放的是每个内部节点对应每一个特征变量，叶子节点上放每一个标签model=[#,1,0,1,1]类似的
        model = model + self.myslover.get_model()
        # 1.为非叶子赋值特征
        for q in range(1, pow(2, self.k)):
            for f in range(self.numfeature):
                if model[self.getVarF(q, f)] > 0:
                    # 1.简单结果数组
                    tree.append(f)
                    # 2.复杂tree
                    # node = Node(self.data[0][f])
                    # innernode.append(node)
                    break
        # 2.为叶子赋值类标签  第0个标签为-1，第1个标签为-2
        for q in range(pow(2, self.k)):
            flag = False
            for cl in range(self.numclasses):
                if model[self.getVarCL(q, cl)] > 0:
                    flag = True
                    # 1.简单数组
                    tree.append(-(cl + 1))
                    # 2.复杂tree
                    # node = Node(str(self.terms[cl]))
                    # leavernode.append(node)
                    break
            if flag is False:
                # 1.简单数组
                tree.append(self.minint)
                # 2.复杂tree
                # node = Node(str(self.terms[cl]))
                # leavernode.append(node)

        # 内部节点
        # for i in range(1, pow(2, self.k-1)):
        #     innernode[i].left = innernode[i*2+1]
        #     innernode[i].right = innernode[i*2]

        # # 叶子节点
        # start = 1
        # for i in range(pow(2, self.k-1), pow(2, self.k)):
        #     innernode[i].left = leavernode[start+1]
        #     innernode[i].right = leavernode[start]
        #     start += 2
        return tree

    # 3.对于错误样本，添加特征约束  q从1开始，lvl是深度,从0开始
    def addConstraints_feature(self, newElement, nb, clause,  q, lvl):

        if nb == 0:
            return
        idNewElement = self.numadderrElement
        # i*2左边
        clause.append(self.getVarX(idNewElement, lvl))
        # for i in range(len(newElement)-1):
        for i in range(len(newElement[0])):
            # if newElement[i]:
            if newElement[0][i]:
                clause.append(-self.getVarF(q, i))
                self.myslover.add_clause(clause)
                clause.pop()
        self.addConstraints_feature(newElement, nb - 1, clause, q * 2, lvl + 1)
        clause.pop()
        # i*2+1右边
        clause.append(-self.getVarX(idNewElement, lvl))
        # for i in range(len(newElement)-1):
        for i in range(len(newElement[0])):
            #  if not newElement[i]:
            if not newElement[0][i]:
                clause.append(-self.getVarF(q, i))
                self.myslover.add_clause(clause)
                clause.pop()
        self.addConstraints_feature(
            newElement, nb - 1, clause, q * 2+1, lvl + 1)
        clause.pop()
        return

    # 4.对于错误样本，添加标签约束
    def addConstraints_class(self, clause, q, lvl, cl):
        if lvl == self.k:
            for x in cl:
                clause.append(self.getVarCL(q, x))
            self.myslover.add_clause(clause)
            for i in range(len(cl)):
                clause.pop()
            for i in range(self.numclasses):
                # if i is not cl:
                if i not in cl:
                    clause.append(-self.getVarCL(q, i))
                    self.myslover.add_clause(clause)
                    clause.pop()
            return
        idNewElement = self.numadderrElement
        clause.append(self.getVarX(idNewElement, lvl))
        self.addConstraints_class(clause, q * 2, lvl + 1, cl)
        clause.pop()
        clause.append(-self.getVarX(idNewElement, lvl))
        self.addConstraints_class(clause, q * 2+1, lvl + 1, cl)
        clause.pop()
        return

    # 5.添加最小化叶子节点约束
    def addConstraints_MaxLeaves(self):
        for q in range(pow(2, self.k)+1):
            for j in range(pow(2, self.k)+1):
                self.getVarCompter(q, j)
        for q in range(pow(2, self.k)):
            for c in range(self.numclasses):
                clause = []
                clause.append(-self.getVarCL(q, c))
                clause.append(self.getVarUsed(q))
                self.myslover.add_clause(clause)

        clause = []
        clause.append(self.getVarCompter(0, 0))
        self.myslover.add_clause(clause)
        for q in range(pow(2, self.k)):
            for j in range(q+1):
                clause = []
                clause.append(-self.getVarUsed(q))
                clause.append(-self.getVarCompter(q, j))
                clause.append(self.getVarCompter(q+1, j+1))
                self.myslover.add_clause(clause)
                clause = []
                clause.append(-self.getVarCompter(q, j))
                clause.append(self.getVarCompter(q+1, j))
                self.myslover.add_clause(clause)
    # 6.添加约束

    def add(self, newElement):
        k = self.k
        clause = []
        self.addConstraints_feature(newElement, k, clause, 1, 0)
        # print("self.X==============错误样本在深度的哪边", self.X)
        # print("self.F==============节点上放什么特征", self.F)
        # print("self.CL==============叶子节点上对应哪个标签", self.CL)
        self.addConstraints_class(clause, 0, 0, newElement[-1])
        self.numadderrElement += 1
        self.toUpdate = True

    def simplifyTree(self, tree):
        # print("未简化------", tree)
        for i in range(len(tree)-1, 0, -1):
            if tree[i] == self.minint:
                if i % 2 == 1:
                    brother = i - 1
                else:
                    brother = i + 1
                self.replace(tree, int(i / 2), brother)
        # print("------", tree)

    def replace(self, tree, a, b):
        Replace = [[a, b]]
        while (len(Replace) >= 1):
            a, b = Replace[0]
            Replace.pop(0)
            if b < len(tree):
                tree[a] = tree[b]
                Replace.append([a*2, b*2])
                Replace.append([a*2+1, b*2+1])
            else:
                tree[a] = self.minint + 1

    def tree_root(self, tree):
        nodelist = ['#']*len(tree)
        for i in range(len(tree)-1, 0, -1):
            if tree[i] >= 0:
                node = Node(self.data[0][tree[i]])
                node.left = nodelist[i*2+1]
                node.right = nodelist[i*2]
                nodelist[i] = node
            if (tree[i] < 0) & (tree[i] != self.minint + 1):
                node = Node(str(self.terms[-tree[i]-1]))
                nodelist[i] = node
            if tree[i] == self.minint + 1:
                continue
        return nodelist[1]
