from hopcroftkarp import HopcroftKarp
from tarjan import tarjan
from time import time

class CostaImproved:
    def __init__(self, graph, left, right):
        self.graph = graph
        self.left = left
        self.right = right
        hk = HopcroftKarp(graph)
        self.matching = hk.maximum_matching()
        self.E_w = set()
        self.E_0 = set()
        self.E_1 = set()

    def imperfect_labelling(self, position):
        """ Time = O(n + m)
        :param position:
        :return:
        """
        label = set()
        layer = {vertex for vertex in position if vertex not in self.matching}
        visited = set()
        while len(layer) != 0:
            label.update(layer)
            new_layer = set()  # new list for subsequent layers
            for vertex in layer:
                if vertex in position:
                    visited.add(vertex)
                    for neighbour in self.graph[vertex]:
                        if neighbour not in visited and (vertex not in self.matching or neighbour != self.matching[vertex]):
                            new_layer.add(neighbour)
                else:
                    visited.add(vertex)
                    for neighbour in self.graph[vertex]:
                        if neighbour not in visited and (vertex in self.matching and neighbour == self.matching[vertex]):
                            new_layer.add(neighbour)
            layer = new_layer
        return label

    def decomp_imperfect_matching(self):
        # if the maximum matching is imperfect, this bit partitions the vertices into
        # the Dulmage-Mendelsohn sets
        """
        :param self.graph: bipartite graph
        :param left: left vertex set
        :param right: right vertex set
        :return: the Dulmage-Mendelsohn sets (A_left, B_left, C_left, A_right, B_right, C_right)
        """
        star_label = self.imperfect_labelling(self.left)
        circle_label = self.imperfect_labelling(self.right)
        A_left = {vertex for vertex in star_label if vertex in self.left}
        B_right = {vertex for vertex in star_label if vertex in self.right}
        B_left = {vertex for vertex in circle_label if vertex in self.left}
        A_right = {vertex for vertex in circle_label if vertex in self.right}
        C_left = self.left - A_left - B_left
        C_right = self.right - A_right - B_right
        return A_left, B_right, B_left, A_right, C_left, C_right

    def construct_directed_graph(self, graph, left, right):
        # if matching is perfect, construct a digraph..
        # an empty dictionary to build the digraph
        directed_graph = {}

        for vertex in left:
            for neighbour in graph[vertex]:
                if self.matching[vertex] == neighbour:
                    directed_graph[vertex] = [neighbour]
                else:
                    directed_graph[neighbour] = [vertex]

        # check all unmatched edges that have not been oriented
        for vertex in right:
            for neighbour in graph[vertex]:
                if self.matching[vertex] != neighbour and neighbour not in directed_graph[vertex]:
                    directed_graph[vertex].append(neighbour)

        return directed_graph

    def find_strongly_connected_component(self, graph, left, right):
        """
        Tarjan algorithm finds the strongly connected components from
        the constructed directed graph

        Time: O(n + m)
        """
        directed_graph = self.construct_directed_graph(graph, left, right)
        return tarjan(directed_graph)

    def edge_part_perfect(self, graph, left, right):
        # classify the edges according to the strongly connected component
        # their endpoint belongs
        sccs = self.find_strongly_connected_component(graph, left, right)
        # print(sccs)
        for scc in sccs:
            # the least number of vertices that makes up an alternating cycle is 4
            if len(scc) >= 4:
                # edges whose endpoints belong to these scc's are weakly persistent
                for vertex in scc:
                    if vertex in left:
                        for neighbour in graph[vertex]:
                            if neighbour in scc:
                                self.E_w.add((vertex, neighbour))

        for vertex in self.matching:
            # matched edges that are not weakly persistent are 1-persistent
            if (vertex in left) and (vertex, self.matching[vertex]) not in self.E_w:
                self.E_1.add((vertex, self.matching[vertex]))

        for vertex in left:
            # all other edges are zero-persistent
            for neighbour in graph[vertex]:
                if ((vertex, neighbour) not in self.E_w) and ((vertex, neighbour) not in self.E_1):
                    self.E_0.add((vertex, neighbour))

    def edge_partitioning(self):
        """
        If the maximum matching is perfect, it runs the decomposition of perfect matching, otherwise
        it runs the decomposition for imperfect matching.
        """
        if len(self.matching) == len(self.graph):
            self.edge_part_perfect(self.graph, self.left, self.right)

        else:
            left_plus, right_plus, left_star, right_star, left_unlabelled, right_unlabelled = self.decomp_imperfect_matching()

            for vertex in self.left:
                for neighbour in self.graph[vertex]:
                    if (vertex in left_star and neighbour in right_plus) or \
                            (vertex in left_star and neighbour in right_unlabelled) or \
                            (vertex in left_unlabelled and neighbour in right_plus):
                        self.E_0.add((vertex, neighbour))

            for vertex in self.left:
                for neighbour in self.graph[vertex]:
                    if (vertex in left_star and neighbour in right_star) or \
                            (vertex in left_plus and neighbour in right_plus):
                        self.E_w.add((vertex, neighbour))

            graph_prime = {}
            for vertex in left_unlabelled:
                graph_prime[vertex] = set([neighbour for neighbour in self.graph[vertex] if neighbour in right_unlabelled])
            for vertex in right_unlabelled:
                graph_prime[vertex] = set([neighbour for neighbour in self.graph[vertex] if neighbour in left_unlabelled])
            self.edge_part_perfect(graph_prime, left_unlabelled, right_unlabelled)

        return self.E_1, self.E_w, self.E_0

g = {'a': {1, 3}, 'b': {1, 2, 4}, 'c': {1, 3}, 'd': {3, 5, 6}, 'e': {5}, 'f': {4, 7},
         'g': {5}, 1: {'a', 'b', 'c'}, 2: {'b'}, 3: {'a', 'b', 'c'}, 4: {'b', 'f', 'e'},
         5: {'d', 'e', 'g'}, 6: {'d'}, 7: {'f'}}
l = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
r = set(range(1, 8))

C = CostaImproved(g, l, r)
m = HopcroftKarp(g)
maximum_matching = m.maximum_matching()
E1, Ew, E0 = C.edge_partitioning()
#print('Bipartite graph: ' + str(m))
print('Maximum Matching:' + str(maximum_matching))
print('one-persistent edges: ' + str(E1))
print('weakly-persistent edges: ' + str(Ew))
print('zero-persistent edges: ' + str(E0))
