from DT import DT1_Infer
import math

from DT.DT1_Infer import evenValid


class learnSatDT:
    def __init__(self, data, numFeature, numClass, terms):

        self.data = data

        self.dataNumFeature = numFeature #用到

        self.dataNumClass = numClass

        self.terms = terms

    # 1.找到最佳决策树
    def findOptimalTree(self, minNumberTree):
        while True:
            # print("进行到节点个数为")
            # print(minNumberTree)
            if minNumberTree > self.dataNumFeature:
                return False, False
            # 开始根据minNumberTree节点个数学习最佳决策树
            tree, root = self.inferTree(
                minNumberTree)
            # 1.找到了一棵树
            if tree:
                # print("找到树了")
                break
            # print("没找到，继续增加节点个数")
            minNumberTree += 2
        return tree, root
    # 2.根据模型得到解空间，还未赋予特征
    def getTreeModel(self, model, infer):
        # 存放叶子的index
        leaf = []
        # 存放内部节点的index
        innerNode = []
        # 存放内部节点的左右孩子的index
        relaNode = {}
        # 存放所有节点的父母的index
        parentNode = {}
        model = ["#"] + model
        # print(model)
        for j in range(1, infer.numberTree + 1):
            # 是否为叶子
            if model[infer.getVarV(j)] > 0:
                leaf.append(j)
            else:
                innerNode.append(j)
            # 左孩子、右孩子、父母
            a = min(2 * j, infer.numberTree - 1)
            LR = evenValid(j + 1, a, j, infer.numberTree)
            for k in LR:
                if model[infer.getVarL(j, k)] > 0:
                    relaNode[j] = [k, k + 1]
                    parentNode[k] = j
                    parentNode[k + 1] = j
        return leaf, innerNode, relaNode, parentNode

    # 3.求深度
    def depth(self, parentNode, minNumberTree):
        pr = parentNode[minNumberTree]
        count = 1
        while pr != 1:
            pr = parentNode[pr]
            count += 1
        return count

    # 4.找到最佳决策树
    def inferTree(self, minNumberTree):
        # 1.固定深度k,初始化
        infer1 = DT1_Infer.Mysolver(self.data, self.dataNumFeature, self.dataNumClass, minNumberTree, self.terms)
        infer2 = DT1_Infer.Mysolver(self.data, self.dataNumFeature, self.dataNumClass, minNumberTree, self.terms)
        # 2.添加空间约束
        infer1.getSpace()
        dep = []
        # print("+++++++++")
        for model in infer1.myslover.enum_models():
            # print("换一个模型")
            # 得到叶子的index[]、内部节点的index []、关系index {}、父母index {}
            leaf, innerNode, relaNode, parentNode = self.getTreeModel(model, infer1)
            # print(leaf, innerNode, relaNode, parentNode)
            d = self.depth(parentNode, minNumberTree)
            if d in dep:
                continue
            else:
                dep.append(d)
            infer2.addConstraints_sample(leaf, innerNode, relaNode, parentNode)
            sign = infer2.myslover.solve()
            if sign:
                tree = infer2.getModel(leaf, innerNode)
                # 将关系加入
                tree.append(relaNode)
                root = infer2.tree_root(tree)
                return tree, root
            infer2.clear_reset()
        return False, False








































        # 3.添加全部样本约束
        sign = infer.inferSpace()
        # 4.开始推断模型
        if sign:
            print("可以得到模型了")
            tree = infer.getModel()
            root = infer.tree_root(tree)
            return tree, root
        return False, False



