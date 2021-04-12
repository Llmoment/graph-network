import networkx as nx
from networkx.readwrite import json_graph
import json
import numpy as np
import random
import os
import random
from datetime import datetime

GRAPH_FILE = './random.json'

def graph_gen(n, p, seed = None, save = False, load = False):
    '''
    从文件中读取或生成新的随机图
    @params:
        n 节点总数
        p 连边概率
        seed 随机种子
        load 为False时生成新图
        save 是否保存新图
    '''
    if load:
        with open(GRAPH_FILE, 'r') as f:
            json_G = json.load(f)
            G = json_graph.node_link_graph(json_G)    
    else:    
        G = nx.generators.random_graphs.gnp_random_graph(n, p, seed)
        if save:
            with open(GRAPH_FILE, 'w') as f:
                json_G = json_graph.node_link_data(G)
                json.dump(json_G, f)
    return G

def find_dominate_begging(G, start = 0):
    '''
    选择逻辑：随机选取不在当前支配范围内的节点
    '''
    node_set = set(G)
    dominate_set = {start}
    dominated_nodes = set(G[start])
    remain = node_set - dominated_nodes - dominate_set
    print(dominated_nodes)
    while remain:
        v = remain.pop()
        dominate_set.add(v)
        new_dominated_nodes = set(G[v]) - dominate_set
        dominated_nodes |= new_dominated_nodes
        remain -= new_dominated_nodes
    return dominate_set

def get_start(degree_G, G, p=1):
    '''
    以p的概率获取度最大的节点
    '''
    nonce = random.random()
    if nonce <= p:
        #从度最大的节点中随机选取一个
        max_degree = degree_G[0][1]
        max_degree_nodelist = []
        for i in range(len(degree_G)):
            if degree_G[i][1] == max_degree:
                max_degree_nodelist.append(degree_G[i][0])
            else:
                break
        return random.sample(max_degree_nodelist, 1)[0]
    else: 
        return random.sample(list(G.ndoes()), 1)[0]
    
def delta_size(G, dominated_nodes, node):
    '''
    计算节点node带来的支配集增长量
    '''
    dominated_nodes_bar = dominated_nodes | set(G[node])
    delta = len(dominated_nodes_bar) - len(dominated_nodes)
    return delta

def select_node_greedy(G, dominated_nodes, p):
    '''
    以概率p返回当前支配集大小增量最大的节点
    '''
    remain = set(G) - dominated_nodes
    nonce = random.random()
    if nonce < p:
        selected_node_list = []
        max_delta = 0
        for _, node in enumerate(remain):
            delta = delta_size(G, dominated_nodes, node)
            if delta > max_delta:
                selected_node_list = [node]
                max_delta = delta
            elif delta == max_delta:
                selected_node_list.append(node)
        return random.sample(selected_node_list, 1)[0]
    else:
        return random.sample(remain, 1)[0]


def find_dominate_greedy(G, p = 1.):
    '''
    每次以概率p选取不在当前被支配节点中的使得支配集增长最大的节点
    '''
    #获取降序排序的节点度序列
    degree_G = sorted(list(G.degree), key = lambda x:x[1], reverse = True)  
    remain = set(G)
    start = get_start(degree_G, G)
    dominate_set = {start}
    dominated_nodes = set(G[start])
    remain = remain - dominated_nodes - dominate_set
    while remain:
        v = select_node_greedy(G, dominated_nodes | dominate_set, p)
        remain.remove(v)
        dominate_set.add(v)
        new_dominated_nodes = set(G[v]) - dominate_set
        dominated_nodes |= new_dominated_nodes
        remain -= new_dominated_nodes
    return dominate_set



def main():
    random.seed(datetime.now())
    G = graph_gen(100, 0.5, None, False, True)
    dominate_set = find_dominate_greedy(G)
    print(dominate_set)
    print(nx.algorithms.dominating.is_dominating_set(G,dominate_set))
    return


if __name__ == '__main__':
    main()
