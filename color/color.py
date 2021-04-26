import networkx as nx
from networkx.readwrite import json_graph
import json
import numpy as np
import random
import os
import random
from datetime import datetime
import matplotlib.pyplot as plt
plt.switch_backend('agg')

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

def plot_graph(G):
    '''
    图绘制
    '''
    edge_color_list = []
    for (s, d, c) in G.edges.data('color'):
        edge_color_list.append(c)
    nx.draw_circular(G, node_size=1, node_color='black', edge_color=edge_color_list)
    ax = plt.gca()
    ax.margins(0.20)
    plt.axis("off")
    plt.savefig("color.jpg")
    return

def dye(G, node_pair, color):
    '''
    将某条边染色为r或者g
    @params:
        node_pair: 一个元组
    '''
    if color != 'r' and color != 'black':
        print("Color should be r or black")
        return
    G[node_pair[0]][node_pair[1]]['color'] = color
    return  

def coloring():
    return

def main():
    G = graph_gen(100, 0.1, load=True)
    '''
    #获取G中所有的环
    cycle_basis = nx.algorithms.cycles.cycle_basis(G) #len = 392
    #获取4圈的列表
    four_cycle = [] # len = 71
    for cycle in cycle_basis:
        if len(cycle) == 4:
            four_cycle.append(cycle)
    '''
    for a in list(G.edges()):
        nonce = random.random()
        if nonce < 0.5 :
            dye(G, a, 'black')
        else:
            dye(G, a , 'r')
    plot_graph(G)

if __name__ == '__main__':
    main()
