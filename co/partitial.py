import numpy as np
import networkx as nx
from networkx.readwrite import json_graph
import json
import random
import copy
import itertools
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import math


def complete_graph_gen(n,graph_file_name):
    '''
    生成完全图,随机给每一条边赋予权重并保存
    '''
    G = nx.complete_graph(n)
    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(0,10)

    with open(graph_file_name, 'w') as f:
        json_G = json_graph.node_link_data(G)
        json.dump(json_G, f)
    return G

def load_graph(graph_file_name):
    '''
    加载图，json文件
    '''
    with open(graph_file_name, 'r') as f:
            json_G = json.load(f)
            G = json_graph.node_link_graph(json_G)
    return G

def vector_construct(X0, X1):
    '''
    构建一个0/1向量，在X1中的节点对应位置为1
    '''
    vec = np.zeros(len(X0)*2, dtype=np.int8)
    for i in range(len(X1)):
        vec[X1[i]] = 1
    return vec

def calculate_weight(Adj, X0, X1):
    '''
    计算指定分组方式的权重和
    公式：
        (v_2_T x v_1) x Adj, 然后将结果矩阵中所有位置的值相加
    '''
    vec_1 = vector_construct(X0, X1)
    #print("vec:\n",vec_1)
    vec_2 = vector_construct(X1, X0)
    vec_2_T = vec_2.reshape(vec_2.shape[0], 1)
    #print("vec_2_T:\n",vec_2_T)
    cross_edge_matrix = np.outer(vec_2_T, vec_1)
    #print("cross edge matrix:\n",cross_edge_matrix)
    cross_edge_weight_matrix = cross_edge_matrix * Adj
    #print("cross weight matrix:\n",cross_edge_weight_matrix)
    weight = np.concatenate(cross_edge_weight_matrix).sum()
    return weight

def plot_weight(weight_list):
    plt.figure()
    ax = plt.gca()
    plt.plot(weight_list,'r-',label='Weight')            
    plt.legend(fontsize=18)
    plt.title('weight curve',fontsize=15)
    plt.savefig('./weight.png')
    return
    

def partition(Adj, max_step=300000):
    #进行分组初始化
    node_size = Adj.shape[0]
    node_list = [i for i in range(0,node_size)]
    random.shuffle(node_list)
    #print("node list:\n",node_list)
    X0 = node_list[:int(node_size/2)]
    X1 = node_list[int(node_size/2):]

    weight_list = []
    weight = calculate_weight(Adj, X0, X1)
    print("init weight:",weight)
    weight_list.append(weight)

    #使用启发式算法进行改进,直到找不到改进解
    for i in range(max_step):
        #找出所有的点交换对
        neighbor = list(itertools.product(X0, X1))
        #random.shuffle(neighbor)
        weight_old = weight
        #尝试neighbor中的所有改进，采用最先找到的改进方式
        for item in neighbor:
            X0_tmp = copy.deepcopy(X0)
            X0_tmp.remove(item[0])
            X0_tmp.append(item[1])
            X1_tmp = copy.deepcopy(X1)
            X1_tmp.remove(item[1])
            X1_tmp.append(item[0])

            weight_tmp = calculate_weight(Adj, X0_tmp, X1_tmp)
            #print("weight tmp:", weight_tmp)

            if weight_tmp < weight:
                X0 = X0_tmp
                X1 = X1_tmp
                weight = weight_tmp
                weight_list.append(weight)
                break  

        if (i+1) % 10 == 0:
            print("Iter: %d, weight: %d"%(i+1, weight))

        if weight == weight_old:
            print("No more improve in this round.")
            print("Total iter:%d, the lowest weight is:%d"%(i+1, weight))
            #print("Weight list:",weight_list)
            plot_weight(weight_list)
            break
    return


def partition_SA(Adj, T_max = 10000, T_min = 1, limit=300):
    '''
    模拟退火算法版
    @params:
        Adj: 邻接矩阵
        T_max: 起始温度
        T_min: 终止温度
        limit: 最多连续接受坏解的次数
    '''
    #进行分组初始化
    node_size = Adj.shape[0]
    node_list = [i for i in range(0,node_size)]
    random.shuffle(node_list)
    #print("node list:\n",node_list)
    X0 = node_list[:int(node_size/2)]
    X1 = node_list[int(node_size/2):]

    weight_list = []
    weight = calculate_weight(Adj, X0, X1)
    print("init weight:",weight)
    weight_list.append(weight)

    T_now = T_max
    iteration = 0
    stop_time = 0
    #使用模拟退火算法进行解改进，直至温度降到T_min或者连续50轮没有改进
    while T_now > T_min:
        if stop_time >= 50:
            break

        iteration += 1
        #SA Process       
        bad_improve = 0
        while True:
            #找出一个未出现过的交换对
            switch_pair_history = []
            while True:
                switch_pair = []
                switch_pair.append(random.choice(X0))
                switch_pair.append(random.choice(X1))
                if switch_pair not in switch_pair_history:
                    switch_pair_history.append(switch_pair)
                    break
            #尝试neighbor中的所有改进，采用最先找到的改进方式
            X0_tmp = copy.deepcopy(X0)
            X0_tmp.remove(switch_pair[0])
            X0_tmp.append(switch_pair[1])
            X1_tmp = copy.deepcopy(X1)
            X1_tmp.remove(switch_pair[1])
            X1_tmp.append(switch_pair[0])

            weight_tmp = calculate_weight(Adj, X0_tmp, X1_tmp)
            #若当前接是改进，直接取这个解
            if weight_tmp < weight:
                X0 = X0_tmp
                X1 = X1_tmp
                weight = weight_tmp
                weight_list.append(weight)
                break
            else:
                p = math.exp((weight - weight_tmp)/T_now)
                nonce = random.random()
                if nonce <= p:
                    X0 = X0_tmp
                    X1 = X1_tmp
                    weight = weight_tmp
                    weight_list.append(weight) 
                    break
                else:
                    bad_improve += 1

            if bad_improve >= limit:
                bad_improve = 0 
                stop_time += 1
                break

              
        T_now = T_max / (1 + iteration)
        if iteration % 10 == 0:
            print("Iter: %d, weight: %d"%(iteration, weight))

    print("SA stopped.")
    print("Total iter:%d, the lowest weight is:%d"%(iteration, weight))
    plot_weight(weight_list)

    return


def main():
    random.seed(datetime.now())
    graph_file_name='./k100.json'
    n=100
    #G = complete_graph_gen(n, graph_file_name)
    G = load_graph(graph_file_name)
    Adj = np.array(nx.adjacency_matrix(G).todense())
    partition_SA(Adj,limit=1000)

    # plot_graph(color_G)

if __name__ == '__main__':
    main()