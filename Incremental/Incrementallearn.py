from Incremental import Infer
import math


class increlearn:
    def __init__(self, data, numFeature, numClass):

        self.data = data
        self.datanumfeature = numFeature
        self.datanumclass = numClass

    # 1.从SynDT而来  1,false,false
    def findOptimalTree(self, minNumberForK, doNodeMinimization, terms):
        # print("findOptimalTree=============================================",
        #       math.ceil(math.log2(self.datanumfeature)))
        while True:
            # 固定深度推断最佳决策树
            # 根据特征值设置一个最大深度，如果在最小深度和最大深度内找不到，则真的找不到这棵树
            if minNumberForK > math.ceil(math.log2(self.datanumfeature+1)):
                return False, False
            # print(self.datanumfeature)
            # if minNumberForK > math.ceil(math.log2(self.datanumfeature+2)):
            #     return False, False
            # 进行方法的选择
            tree, root = self.inferTree(
                minNumberForK, doNodeMinimization, terms)
            # 1.找到了一棵树
            if tree:
                # print("tree不为空")
                break
            minNumberForK += 1
            # print("增加了一个深度,", minNumberForK)
        return tree, root
    # 2.最小化节点个树

    def minimizeNode(self, infer, tree1):

        tree = tree1
        # print("最小化节点个数前", tree)

        infer.addConstraints_MaxLeaves()
        FMin = 1
        FMax = pow(2, infer.k)
        # print("*************************", infer.k)
        while FMin != FMax:
            nombreMaxFeuille = (int)((FMax + FMin) / 2)
            if infer.inferModel(nombreMaxFeuille):
                tmp = infer.getModel()
                element = self.distinguish(tmp)
                if len(element) == 0:
                    # tree = infer.getModel()
                    tree = tmp
                    FMax = nombreMaxFeuille
                else:
                    # print("添加错误样本", element)
                    infer.add(element)
            else:
                FMin = nombreMaxFeuille + 1
        # print("最小化节点个数后", tree)
        return tree
    # 3.推断决策树方法一，固定深度，先得到最佳决策树，后最小化

    def inferTree(self, k, doNodeMinimization, terms):
        # print("inferTree", k)
        # 固定深度k,初始化
        infer = Infer.Mysolver(k, self.datanumfeature,
                               self.datanumclass, self.data, terms)
        # 推断有解
        while infer.inferModel(0):
            # print("是否可以得到模型,并打印每个变量的取值情况", infer.inferModel(0))
            # print(infer.myslover.get_model())
            # 得到模型 root=[]
            tree = infer.getModel()
            # print("打印得到的模型tree set", tree)
            # 判断模型
            element = self.distinguish(tree)
            # print("打印错误样本", element)
            # 1.找到了正确分类的模型
            if len(element) == 0:
                # 需要最小化节点数
                # print("未最小化------", tree)
                if doNodeMinimization:
                    tree = self.minimizeNode(infer, tree)
                infer.simplifyTree(tree)
                root = infer.tree_root(tree)
                # self.Ptree(root)
                return tree, root
            # 没有找到，添加约束
            infer.add(element)
        # print("结束一次深度", k)
        return False, False


# **************************************************************************

    # 推断决策树方法二：不管是doNodeMinimization的值是多少，在最小化过程中得到最佳,没有用到minimizeNode方法


    def inferTree1(self, k, doNodeMinimization, terms):
        root = False
        tree = False
        # 固定深度k,初始化
        infer = Infer.Mysolver(k, self.datanumfeature,
                               self.datanumclass, self.data, terms)
        infer.addConstraints_MaxLeaves()
        # print(k, ":", infer.inferModel(0))
        # 推断有解
        FMin = 1
        FMax = pow(2, infer.k)
        while FMin != FMax:
            sign = False
            nombreMaxFeuille = (int)((FMax + FMin) / 2)
            # print(FMax, FMin, nombreMaxFeuille, "-----------")
            while infer.inferModel(nombreMaxFeuille):
                tree = infer.getModel()
                # print("可以推断模型", tree)
                element = self.distinguish(tree)
                # 最佳决策树
                if len(element) == 0:
                    tree = infer.getModel()
                    # print("+++++++", tree)
                    infer.simplifyTree(tree)
                    root = infer.tree_root(tree)
                    FMax = nombreMaxFeuille
                    sign = True
                    break
                # 非最佳决策树
                else:
                    tree = False
                    root = False
                    # print("错误样本", element)
                    infer.add(element)
            # 固定的nombreMaxFeuille下推断不出最佳决策树
            if sign is False:
                # print("Fmin++", tree)
                FMin = nombreMaxFeuille + 1
        # print("infer1111=========", tree)
        return tree, root
# ***********************************************************************************8

    def distinguish(self, tree):
        # flag = True
        for elem in self.data[1:]:
            # if flag is True:
            #     flag = False
            #     continue
            pos = 1
            while True:
                feature = tree[pos]
                if feature < 0:
                    # 分类正确
                    if -feature-1 not in elem[-1]:
                        return elem
                    break
                if elem[0][feature] == 1:
                    pos = pos * 2 + 1
                else:
                    pos = pos * 2
        return []

    def Ptree(self, node):
        # print(node.val)
        if node.left is None:
            return

        self.Ptree(node.left)

        self.Ptree(node.right)
