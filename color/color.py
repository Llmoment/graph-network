import networkx as nx
from networkx.readwrite import json_graph
import json
import numpy as np
import random
import os
import random
from datetime import datetime
import itertools
import matplotlib.pyplot as plt
plt.switch_backend('agg')

GRAPH_FILE = './random.json'

def graph_gen_old(n, p, seed = None, save = False, load = False):
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


def complete_graph_gen(n,graph_file_name):
    '''
    生成完全图并保存
    '''
    G = nx.complete_graph(n)
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

def coloring(G,graph_file_name):    # 两种颜色black，red
    edges=list(G.edges(data=True)) #EdgeView类型转list类型，用于打乱,data=True输出带属性的边 e.g. (0,1,{'color':'black'})
    node_list=list(G.nodes())
    random.shuffle(edges)
    i=1
    num=len(edges)
    for edge in edges:
        print("{}/{}".format(i,num))
        # printProgress(i, num, prefix='Progress:', suffix='Complete', barLength=50)
        i+=1
        node1,node2=edge[0],edge[1]
        node_list.remove(node1)   # node1
        node_list.remove(node2)   # node2
        weight_black,weight_red=0.0,0.0 # 若当前边染黑色或红色，产生同色K4的概率总和
        for node3,node4 in list(itertools.combinations(node_list,2)):   # 剩余节点中取出2个节点，组成k4
            num_black,num_red=0,0   # 已染色的黑色边、红色边的数量
            for k4_node1,k4_node2 in list(itertools.combinations([node1,node2,node3,node4],2)): #遍历k4的6条边，读取目前已染色的情况            
                if G.edges[k4_node1,k4_node2] !={}: # 已染色
                    if G.edges[k4_node1,k4_node2]['color'] == 'black':
                        num_black+=1
                    else:
                        num_red+=1
            # 计算权重
            if num_black>0 and num_red == 0:
                weight_black += 1/2**(6-num_black-1) # 当前边染黑，剩下的边随机染色，有同色K4的概率为1/2**(6-k)
                weight_red += 0 # 当前边染红，产生同色K4的概率为0
            elif num_red>0 and num_black==0:
                weight_black += 0
                weight_red += 1/2**(6-num_red-1)
            elif num_red==0 and num_black==0:
                weight_black += 1/2**(6-num_black-1)
                weight_red += 1/2**(6-num_red-1)                
            else:   # 都大于0，不可能产生同色K4
                # weight_black +=0
                # weight_red +=0
                pass
        # 结束遍历当前边的K4，决定染什么颜色
        if weight_black < weight_red:
            G.add_edges_from([(node1,node2)],color='black')
        elif weight_red < weight_black:
            G.add_edges_from([(node1,node2)],color='red')
        else:   # 两者相等，随机取
            if random.random()>0.5:
                G.add_edges_from([(node1,node2)],color='black')
            else:
                G.add_edges_from([(node1,node2)],color='red')
        node_list.append(node1)
        node_list.append(node2)
    with open(graph_file_name, 'w') as f:   # 保存染过色的图
        json_G = json_graph.node_link_data(G)
        json.dump(json_G, f)
    return G



def find_same_color_K4(G):
    same_color_K4=0
    for node1,node2,node3,node4 in list(itertools.combinations(G.nodes(),4)):
        color_list=[G.edges[node1,node2]['color'],
                    G.edges[node1,node3]['color'],
                    G.edges[node1,node4]['color'],
                    G.edges[node2,node3]['color'],
                    G.edges[node2,node4]['color'],
                    G.edges[node3,node4]['color']]
        if len(set(color_list))==1:
            same_color_K4+=1
    return same_color_K4

def printProgress(iteration, total, prefix='', suffix='', decimals=1, barLength=100):
    """
    Call in a loop to create a terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    import sys
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '#' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def main():
    graph_file_name='./random_shuffle.json'
    n=200
    G = nx.complete_graph(n)   # 完全图Kn
    color_G = coloring(G,graph_file_name)   # 生成染色图并保存
    # color_G = load_graph(graph_file_name)   # 加载已染色的图
    num_same_color_K4=find_same_color_K4(color_G)
    print("完全图K{}经过染色，有{}个同色K4".format(n,num_same_color_K4))

    # plot_graph(color_G)

if __name__ == '__main__':
    main()
