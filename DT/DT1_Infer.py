import math

from pysat.formula import CNF
from pysat.solvers import Solver
import itertools

class Node:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None
# 左孩子
def evenValid(a, b, i, numTree):
    tmp = []
    if i + 1 <= a <= numTree - 1 and a % 2 == 0:
        tmp.append(a)
    if i + 1 <= b <= numTree - 1 and b % 2 == 0 and a != b:
        tmp.append(b)
    return tmp


def oddValid(a, b, i, numTree):
    tmp = []
    if i + 2 <= a <= numTree and a % 2 == 1:
        tmp.append(a)
    if i + 2 <= b <= numTree and b % 2 == 1 and a != b:
        tmp.append(b)
    return tmp


class Mysolver:

    def __init__(self, data, dataNumFeature, dataNumClass, numberTree, terms):
        # 树的节点个数
        self.data = data
        self.dataNumFeature = dataNumFeature
        self.dataNumClass = dataNumClass
        self.numberTree = numberTree
        self.terms = terms
        self.myslover = Solver(name='m22') #g3
        self.localindex = 0
        self.V = {}
        self.R = {}
        self.L = {}
        self.P = {}
        self.D = {}
        self.A = {}
        self.U = {}
        self.C = {}
    # (1).第i个节点是否为叶子的index
    def getVarV(self, i):
        dt = i
        if dt not in self.V.keys():
            self.localindex += 1
            self.V[dt] = self.localindex
        return self.V[dt]

    # (2).第i个节点的左孩子是第j个节点
    def getVarL(self, i, j):
        dt = (i, j)
        if dt not in self.L.keys():
            self.localindex += 1
            self.L[dt] = self.localindex
        return self.L[dt]

    # (3).i的右孩子j
    def getVarR(self, i, j):
        dt = (i, j)
        if dt not in self.R.keys():
            self.localindex += 1
            self.R[dt] = self.localindex
        return self.R[dt]

    # (4).j的父母是i
    def getVarP(self, i, j):
        dt = (i, j)
        if dt not in self.P.keys():
            self.localindex += 1
            self.P[dt] = self.localindex
        return self.P[dt]

    #(2-1).第i个节点的左孩子是第j个节点
    def getVarL1(self, i, j):
        dt = (i, j)
        if dt not in self.L.keys():
            self.localindex += 1
            self.L[dt] = self.localindex
            self.myslover.add_clause([-self.localindex])
        return self.L[dt]

    # (3-1).i的右孩子j
    def getVarR1(self, i, j):
        dt = (i, j)
        if dt not in self.R.keys():
            self.localindex += 1
            self.R[dt] = self.localindex
            self.myslover.add_clause([-self.localindex])
        return self.R[dt]

    # (4-1).j的父母是i
    def getVarP1(self, i, j):
        dt = (i, j)
        if dt not in self.P.keys():
            self.localindex += 1
            self.P[dt] = self.localindex
            self.myslover.add_clause([-self.localindex])
        return self.P[dt]
    # (5).第j个节点到根节点的路径上，r特征放的节点的走向是否与0相反
    def getVarD(self, r, j, b):
        dt = (r, j, b)
        if dt not in self.D.keys():
            self.localindex += 1
            self.D[dt] = self.localindex
        return self.D[dt]

    # (6).特征r是否被分配到j节点
    def getVarA(self, r, j):
        dt = (r, j)
        if dt not in self.A.keys():
            self.localindex += 1
            self.A[dt] = self.localindex
        return self.A[dt]

    # (7).从j节点到根节点是否存在特征r
    def getVarU(self, r, j):
        dt = (r, j)
        if dt not in self.U.keys():
            self.localindex += 1
            self.U[dt] = self.localindex
        return self.U[dt]

    # (8).j叶子节点是否放的是c特征，是的话=1；否则为0
    def getVarC(self, j, c):
        dt = (j, c)
        if dt not in self.C.keys():
            self.localindex += 1
            self.C[dt] = self.localindex
        return self.C[dt]

    # (5).获取决策树的空间
    def getSpace(self):
        self.V[1] = 1
        self.myslover.add_clause([-1])
        self.localindex = self.localindex + 1
        # 2.如果是叶子，则一定没有左孩子--------子句（2）
        for i in range(1, self.numberTree + 1):
            a = min(2 * i, self.numberTree - 1)
            LR = evenValid(i + 1, a, i, self.numberTree)
            if len(LR) == 0:
                one = [self.getVarV(i)]
                self.myslover.add_clause(one)
                # print(one)
            else:
                for j in LR:
                    one = [-self.getVarV(i), -self.getVarL(i, j)]
                    self.myslover.add_clause(one)
                    # print(one)
        # print("子句2结束")

        # 3.左孩子推出右孩子--------子句（3）
        for i in range(1, self.numberTree + 1):
            a = min(2 * i, self.numberTree - 1)
            LR = evenValid(i + 1, a, i, self.numberTree)
            if len(LR) >= 1:
                for j in LR:
                    one = [-self.getVarL(i, j), self.getVarR(i, j + 1)]
                    oneReverse = [self.getVarL(i, j), -self.getVarR(i, j + 1)]
                    self.myslover.add_clause(one)
                    # print(one)
                    self.myslover.add_clause(oneReverse)
                    # print(oneReverse)
        # print("子句3结束")
        # 4.非叶子节点必须有左孩子--------子句（4）
        for i in range(1, self.numberTree + 1):
            a = min(2 * i, self.numberTree - 1)
            LR = evenValid(i + 1, a, i, self.numberTree)
            if len(LR) == 1:
                one = [self.getVarV(i), self.getVarL(i, LR[0])]
                self.myslover.add_clause(one)
            elif len(LR) == 2:
                one = [self.getVarV(i), self.getVarL(i, LR[0]), self.getVarL(i, LR[1])]
                two = [self.getVarV(i), -self.getVarL(i, LR[0]), -self.getVarL(i, LR[1])]
                # XOR1 = [-self.getVarL(i, LR[0]), -self.getVarL(i, LR[1])]
                # XOR2 = [self.getVarL(i, LR[0]), self.getVarL(i, LR[1])]
                self.myslover.add_clause(one)
                self.myslover.add_clause(two)
                # self.myslover.add_clause(XOR1)
                # self.myslover.add_clause(XOR2)
                # print(one, XOR2, XOR1)
        # print("子句4结束")
        # 5.左孩子和父母的关系--------子句（5）
        for i in range(1, self.numberTree + 1):
            a = min(2 * i, self.numberTree - 1)
            LR = evenValid(i + 1, a, i, self.numberTree)
            b = min(2 * i + 1, self.numberTree)
            RR = oddValid(i + 2, b, i, self.numberTree)
            # 子句（5）-1
            for j in LR:
                one = [-self.getVarP(j, i), self.getVarL(i, j)]
                two = [self.getVarP(j, i), -self.getVarL(i, j)]
                self.myslover.add_clause(one)
                self.myslover.add_clause(two)
                # print(one, two)
            for j in RR:
                one = [-self.getVarP(j, i), self.getVarR(i, j)]
                two = [self.getVarP(j, i), -self.getVarR(i, j)]
                self.myslover.add_clause(one)
                self.myslover.add_clause(two)
                # print(one, two)
        # print("子句5结束")
        # 6.一个节点只能对应一个父母-----子句（6）
        for j in range(2, self.numberTree + 1):
            down = math.floor(j / 2)
            up = min(j - 1, self.numberTree)
            one = []
            for i in range(down, up + 1):
                # 对应子句（6）
                one.append(self.getVarP1(j, i))
                for k in range(i + 1, up + 1):
                    self.myslover.add_clause([-self.getVarP(j, i), -self.getVarP1(j, k)])
                    # print([-self.getVarP(j, i), -self.getVarP(j, k)])
            self.myslover.add_clause(one)
            # print(two)
        # print("子句6结束")
        # print("getspace结束")
        # print(self.V)
        # print(self.L)
        # print(self.R)
        # print(self.P)

    # (7).得到模型
    def getModel(self, leafIndex, innerNodeIndex):
        model = ['#']
        innerNode = {}
        leaf = {}
        model = model + self.myslover.get_model()
        # print(model)
        for j in innerNodeIndex:
            # j节点不是叶子
            for r in range(1, self.dataNumFeature + 1):
                if model[self.getVarA(r, j)] > 0:
                    # 1.简单结果数组
                    innerNode[j] = r
                    break
        # j节点是叶子
        for j in leafIndex:
            for r in range(1, self.dataNumClass + 1):
                if model[self.getVarC(j, r)] > 0:
                    # 1.简单结果数组
                    leaf[j] = r
                    break
        tree = [innerNode, leaf]
        return tree

    # 根据tree生成决策树节点的形式,左边走向为1
    def tree_root(self, tree):
        # print("样本训练完打印tree")
        # print(tree)
        # 1.innerNode里面放的是innerNode对应的特征
        innerNode = tree[0]
        # 2.leaf里面放的是leaf对应的标签
        leaf = tree[1]
        # 3.relaNode里面放的是内部节点对应的左右的节点的index
        relaNode = tree[2]
        nodelist = ['#'] * (self.numberTree + 1)
        # 叶子
        for key, value in leaf.items():
            node = Node(str(self.terms[value - 1]))
            nodelist[key] = node
        # 内部节点
        for key, value in reversed(list(innerNode.items())):
                node = Node(self.data[0][value - 1])
                LR = relaNode[key][1]
                RR = relaNode[key][0]
                node.left = nodelist[LR]
                node.right = nodelist[RR]
                nodelist[key] = node
        return nodelist[1]

    # (8).为所有的样本添加子句约束||数据、特征个数、类的个数、类的集合
    def addConstraints_sample(self, leaf, innerNode, relaNode, parentNode):
        for i in leaf:
            self.myslover.add_clause([self.getVarV(i)])
        for i in innerNode:
            self.myslover.add_clause([-self.getVarV(i)])
        for key, value in relaNode.items():
            self.myslover.add_clause([self.getVarL(key, value[0])])
            self.myslover.add_clause([self.getVarR(key, value[1])])
            self.myslover.add_clause([self.getVarP(value[0], key)])
            self.myslover.add_clause([self.getVarP(value[1], key)])
        # 约束（7）和（8）的初始化
        for r in range(1, self.dataNumFeature + 1):
            self.myslover.add_clause([-self.getVarD(r, 1, 0)])
            self.myslover.add_clause([-self.getVarD(r, 1, 1)])
            # print([-self.getVarD(r, 1, 0)], [-self.getVarD(r, 1, 1)])
        # 约束（7）和（8）
        # print("7和8约束开始")
        for r in range(1, self.dataNumFeature + 1):
            for j in range(2, self.numberTree + 1):
                pnt = parentNode[j]
                oneSever = [[-self.getVarD(r, j, 0)]]
                oneEight = [[-self.getVarD(r, j, 1)]]
                # 约束（7）和（8）-----正过来
                oneSever.append([self.getVarP(j, pnt), self.getVarD(r, pnt, 0)])
                oneSever.append([self.getVarA(r, pnt), self.getVarR1(pnt, j)])
                oneEight.append([self.getVarP(j, pnt), self.getVarD(r, pnt, 1)])
                oneEight.append([self.getVarA(r, pnt), self.getVarL1(pnt, j)])
                combosSever = itertools.product(*oneSever)
                combosEight = itertools.product(*oneEight)
                for combo1 in combosSever:
                    combo1 = list(combo1)
                    self.myslover.add_clause(combo1)
                    # print(combo1)
                for combo2 in combosEight:
                    combo2 = list(combo2)
                    self.myslover.add_clause(combo2)
                    # print(combo2)
                # 约束（7）和（8）-----反过来
                oneSever = [-self.getVarP(j, pnt), -self.getVarD(r, pnt, 0), self.getVarD(r, j, 0)]
                twoSever = [-self.getVarA(r, pnt), -self.getVarR1(pnt, j), self.getVarD(r, j, 0)]
                self.myslover.add_clause(oneSever)
                self.myslover.add_clause(twoSever)
                # print(oneSever, twoSever)
                oneEight = [-self.getVarP(j, pnt), -self.getVarD(r, pnt, 1), self.getVarD(r, j, 1)]
                twoEight = [-self.getVarA(r, pnt), -self.getVarL1(pnt, j), self.getVarD(r, j, 1)]
                self.myslover.add_clause(oneEight)
                self.myslover.add_clause(twoEight)
                # print(oneEight, twoEight)
        # print("9约束开始")
        #  约束（9）----
        for j in range(2, self.numberTree + 1):
            for r in range(1, self.dataNumFeature + 1):
                # 约束（9）-1
                pnt = parentNode[j]
                one = [-self.getVarU(r, pnt), -self.getVarP(j, pnt), -self.getVarA(r, j)]
                self.myslover.add_clause(one)
                # print(one)
                # 约束（9）-2
                # 1.正
                one = [[-self.getVarU(r, j)], [self.getVarA(r, j)], [self.getVarU(r, pnt), self.getVarP(j, pnt)]]
                one = itertools.product(*one)
                for one1 in one:
                    one1 = list(one1)
                    self.myslover.add_clause(one1)
                    # print(one1)
                # 2.反
                one_reverse = [-self.getVarA(r, j), self.getVarU(r, j)]
                self.myslover.add_clause(one_reverse)
                # print(one_reverse)
                one_reverse = [-self.getVarU(r, pnt), -self.getVarP(j, pnt), self.getVarU(r, j)]
                self.myslover.add_clause(one_reverse)
                # print(one_reverse)
        # print("10约束开始")
        #  约束（10）----
        for j in innerNode:
            # 每个内部节点上必须放一个特征
            for r in range(1, self.dataNumFeature + 1):
                for k in range(r + 1, self.dataNumFeature + 1):
                    self.myslover.add_clause([-self.getVarA(r, j), -self.getVarA(k, j)])
                    # print([-self.getVarA(r, j), -self.getVarA(k, j)])
            # 每个内部节点上必须放特征
            one = []
            for r in range(1, self.dataNumFeature + 1):
                one.append(self.getVarA(r, j))
            self.myslover.add_clause(one)
            # print(one)
        #print("11约束开始")
        for j in leaf:
            for r in range(1, self.dataNumFeature + 1):
                self.myslover.add_clause([-self.getVarA(r, j)])
        # print("12，13，14约束开始")
        # 约束（12）和（13）和（14）每个叶子节点至少放一个类
        for j in leaf:
            atLeastclass = []
            for c in range(self.dataNumClass):
                atLeastclass.append(self.getVarC(j, c + 1))
                for pt in self.data[1:]:
                    # 样本如果不属于该类c
                    if c not in pt[1]:
                        one = [-self.getVarC(j, c + 1)]
                        for r in range(1, self.dataNumFeature + 1):
                            one.append(self.getVarD(r, j, pt[0][r-1]))
                        self.myslover.add_clause(one)
                        # print(one)
            self.myslover.add_clause(atLeastclass)
            # print(atLeastclass)
        # print("===============================")
        # print("V:",self.V)
        # print("R:",self.R)
        # print("L:",self.L)
        # print("P:",self.P)
        # print("D:",self.D)
        # print("A:",self.A)
        # print("U:",self.U)
        # print("C:",self.C)
        # print(self.myslover)
    
    def clear_reset(self):
        
        self.localindex = 0
        self.V = {}
        self.R = {}
        self.L = {}
        self.P = {}
        self.D = {}
        self.A = {}
        self.U = {}
        self.C = {}
        self.myslover.delete()
        self.myslover = Solver(name='m22')












