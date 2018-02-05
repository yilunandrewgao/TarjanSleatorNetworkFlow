import pygraphviz
from functools import reduce

# Node class for tree with cost
class TwC_Node:

	def __init__(self, name, cost, children = None, parent = None):
		self.name = name
		self.cost = cost
		if children:
			self.children = children
		else:
			self.children = []
		self.parent = parent

	def findroot(self):

		v_cur = self

		while v_cur.parent:
			v_cur = v_cur.parent

		return v_cur

	def findcost(self):

		#find mininmum cost
		v_cur = self
		min_node = v_cur
		min_cost = v_cur.cost

		while v_cur.parent:
			v_cur = v_cur.parent

			if v_cur.cost <= min_cost:
				min_cost = v_cur.cost
				min_node = v_cur

		return min_node, min_cost

	def addcost(self, x):

		v_cur = self

		while v_cur.parent:

			v_cur.cost += x
			v_cur = v_cur.parent

		v_cur.cost += x

		return 1

	def link(self, w):

		# if v is not a root
		if self.parent:
			return 0
		else:
			w.children.append(self)
			self.parent = w

			return 1

	def cut(self):

		# if v is a root
		if not self.parent:
			return 0
		else:
			# remove the edge leading to v's parent
			# remove v from v's parent's children list
			self.parent.children.remove(self)
			self.parent = None
			return 1

	def toNum(self):
		return ord(self.name) - 97

	def __repr__(self):

		return "(" + self.name + ", " + str(self.cost) + ")"

	def getGraph(self, A):

		if not self.children:

			A.add_node(self)

		else:

			visited = []
			queue = [self]

			while queue:

				node = queue.pop(0)
				if node not in visited:
					visited.append(node)
					
					for child in node.children:
						queue.append(child)
						A.add_edge(node, child)

		return A

	# prints a tree starting at node, self
	def visualize(self, filename):

		A = pygraphviz.AGraph(directed = True)

		A = self.getGraph(A)

		A.layout(prog = 'dot')

		A.draw(filename)


# Forest class for trees with cost
class TwC_Forest():

	def __init__(self, roots):
		self.roots = roots

	def findroot(self, v):
		return v.findroot()

	def findcost(self, v):
		return v.findcost()

	def addcost(self, v, x):
		return v.addcost(x)

	def link(self, v,w):
		#if v is a root, link and remove v from roots
		if v.link(w):
			self.roots.remove(v)

	def cut(self, v):
		# if v is not a root, cut and add v to roots
		if v.cut():
			self.roots.append(v)

	def visualize(self, filename):

		A = pygraphviz.AGraph(directed = True)

		for root in self.roots:
			A = root.getGraph(A)

		A.layout(prog = 'dot')

		A.draw(filename)

	def __repr__(self):

		return reduce(lambda x, y: x+y, map(TwC_Node.__repr__,self.roots))



# Test Code
if __name__ == "__main__":

	node_a = TwC_Node("a", 10)
	node_b = TwC_Node("b", 10)
	node_c = TwC_Node("c", 10)
	node_d = TwC_Node("d", 10)
	node_e = TwC_Node("e", 10)
	node_f = TwC_Node("f", 10)



	f = TwC_Forest([node_a, node_b, node_c, node_d, node_e])
	f.link(node_a,node_b)
	f.addcost(node_a, 10)
	f.link(node_c, node_a)
	print (f.findroot(node_c))
	f.visualize("ForestWithCost.png")


	node_a.link(node_b)
	node_a.addcost(10)
	node_c.link(node_b)
	node_a.findroot().visualize("TreeWithCost.png")



