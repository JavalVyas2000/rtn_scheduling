import networkx as nx
import matplotlib.pyplot as plt
import pyomo.environ as pyo
import pandas as pd
from random import randint


class RTN:
    def __init__(self, data, solver="glpk"):
        self.I = data["I"]
        self.R = data["R"]
        self.idx = data["idx"]
        self.mu = data["mu"]
        self.nu = data["nu"]
        self.tau = data["tau"]
        self.Vmax = data["Vmax"]
        self.Vmin = data["Vmin"]
        self.X0 = data["X0"]
        self.Xmin = data["Xmin"]
        self.Xmax = data["Xmax"]
        self.pi = data["pi"]
        self.max_tau = data["max_tau"]
        self.horizon = data["horizon"]
        self.graph = data["graph"]
        self.Task_resources = data["Task_resources"]
        self.solver = solver

    def solve_model(self):
        """
        The below function builds the RTN model and solves it
        """
        m = pyo.ConcreteModel()
        ### Defining sets
        m.I = pyo.Set(initialize=self.I)  ### tasks
        m.R = pyo.Set(initialize=self.R)  ### resources
        m.Task_resources = pyo.Set(initialize=self.Task_resources)  ### Task resources
        m.T = pyo.Set(initialize=range(self.horizon + 1))  ### time points
        m.T1 = pyo.Set(
            initialize=range(1, self.horizon + 1)
        )  ### exclude time point 0, which is only for initialization
        m.Ir = pyo.Set(
            m.R, initialize={r: self.graph[r] for r in m.R}
        )  ### tasks associated with each resource r
        m.idx = pyo.Set(initialize=self.idx)  ### index for the parameters mu and nu

        ### Defining Parameters
        m.mu = pyo.Param(m.idx, initialize=self.mu)  ### mu parameter
        m.nu = pyo.Param(m.idx, initialize=self.nu)  ### nu parameter
        m.tau = pyo.Param(m.I, initialize=self.tau)  ### tau (task durations)
        m.Vmax = pyo.Param(m.I, initialize=self.Vmax)  ### Maximum Batch Size
        m.Vmin = pyo.Param(m.I, initialize=self.Vmin)  ### Minimum Batch Size
        m.X0 = pyo.Param(m.R, initialize=self.X0)  ### Initial Resource Levels
        m.Xmin = pyo.Param(m.R, initialize=self.Xmin)  ### Minimum Resource Levels
        m.Xmax = pyo.Param(m.R, initialize=self.Xmax)  ### Maximum Resource Levels
        m.pi = pyo.Param(m.R, m.T1, initialize=self.pi)  ### External Transfer

        ### Defining Variables
        m.X = pyo.Var(
            m.R, m.T, initialize=0, domain=pyo.NonNegativeReals
        )  ### Resources Levels
        for r in m.R:
            m.X[r, 0].fix(m.X0[r])  ### Initial Resource Levels
        m.N = pyo.Var(
            m.I, m.T1, initialize=0, domain=pyo.Binary
        )  ### Task Triggers (When N=1, the reactor gets consumed)
        # m.N = pyo.Var(m.I, m.T1,initialize=0, domain=pyo.NonNegativeIntegers)
        m.E = pyo.Var(
            m.I, m.T1, initialize=0, domain=pyo.NonNegativeReals
        )  ### Extent of Task (Here the batch size)

        ## Defining Constraints
        m.Balance = pyo.ConstraintList()
        for t in m.T1:
            for r in m.R:
                m.Balance.add(
                    m.X[r, t]
                    == m.X[r, t - 1]
                    + sum(
                        m.mu[i, r, theta] * m.N[i, t - theta]
                        + m.nu[i, r, theta] * m.E[i, t - theta]
                        for i in m.Ir[r]
                        for theta in range(self.max_tau + 1)
                        if theta <= m.tau[i] and t - theta >= 1
                    )
                    + m.pi[r, t]
                )

        @m.Constraint(m.T1, m.R)
        def Resource_min(m, t, r):
            return m.X[r, t] >= m.Xmin[r]

        @m.Constraint(m.T1, m.R)
        def Resource_max(m, T1, R):
            return m.X[R, T1] <= m.Xmax[R]

        @m.Constraint(m.T1, m.I)
        def Batch_min(m, T1, I):
            return m.Vmin[I] * m.N[I, T1] <= m.E[I, T1]

        @m.Constraint(m.T1, m.I)
        def Batch_max(m, T1, I):
            return m.Vmax[I] * m.N[I, T1] >= m.E[I, T1]

        # Defining objective
        m.obj = pyo.Objective(
            expr=sum(m.N[i, t] for i in m.I for t in m.T1), sense=pyo.minimize
        )

        # solve
        solver = pyo.SolverFactory(self.solver)
        solver.options['Threads']=8
        m.res = solver.solve(m, tee=False)
        # m.pprint()
        m.obj.display()
        

        return m

    def plot_gantt_chart(self, m):
        """
        The below function plots a gantt chart for the optimal schedule from the RTN model.
        """

        tasks_done = []
        task_duration = []
        task_start = []
        reactor = {}

        for i in m.Task_resources:
            reactor[i] = [0] * m.Xmax[i]
        reactor_used = []
        color_avail = []
        n = len(m.I)
        for i in range(n):
            color_avail.append("#%06X" % randint(0, 0xFFFFFF))
        colors = []
        color_label = {}
        counter = 0

        plt.figure()
        schedule = pd.DataFrame()
        for j in range(self.horizon + 1):
            for i in m.N:
                if i[1] == counter:
                    if m.N[i].value >= 1:
                        flag = 0
                        for n in range(int(m.N[i].value)):
                            for l in m.Task_resources:
                                if i[0] in self.graph[l]:
                                    for k in range(len(reactor[l])):
                                        flag = 0
                                        if j >= reactor[l][k]:
                                            tasks_done.append(i[0])
                                            task_duration.append(self.tau[i[0]])
                                            task_start.append(counter)
                                            reactor[l][k] = j + self.tau[i[0]]
                                            reactor_used.append(
                                                str(l) + "_" + str(k + 1)
                                            )
                                            colors.append(
                                                color_avail[self.I.index(i[0])]
                                            )
                                            if i[0] not in color_label:
                                                color_label[i[0]] = color_avail[
                                                    self.I.index(i[0])
                                                ]
                                            flag = 1
                                            break
            counter += 1

        schedule = pd.DataFrame(
            [tasks_done, task_start, task_duration, reactor_used, colors],
            index=["Task", "Start", "Duration", "Reactor", "Color"],
        )
        schedule = schedule.transpose()
        schedule["Finish"] = schedule["Start"] - schedule["Duration"]

        plt.barh(
            y=schedule["Reactor"],
            width=schedule["Duration"],
            left=schedule["Start"],  # - schedule["Start"][0],
            edgecolor="black",
            color=schedule["Color"],
        )
        plt.grid(axis="x")
        unique_labels = list(set(schedule["Task"]))
        unique_handles = []
        unique_colors = []
        for task_id in unique_labels:
            unique_handles.append(
                plt.Rectangle((0, 0), 1, 1, color=color_label[task_id])
            )
            unique_colors.append(color_label[task_id])
        plt.legend(unique_handles, unique_labels, bbox_to_anchor=(1, 1))
        plt.title("GANTT Chart")
        plt.show()

    def get_resource_levels(self, m):
        """
        This function is used to check the resource levels as respect to time.
        """
        ### Visualizing the schedule.
        X = m.X.get_values()  # get resource levels
        E = m.E.get_values()  # get batch sizes
        resources = pd.DataFrame(
            columns=self.R, data={r: [X[r, t] for t in m.T] for r in self.R}
        )
        resource_levels = resources.iloc[:, 0 : len(X)]
        plt.plot(resource_levels, drawstyle="steps-post")
        plt.xlabel("Time")
        plt.ylabel("Resource Level")
        plt.title("Resource Levels")
        plt.show()

    def network(self):
        """
        This function plots the network based on the input data using networkx.
        """
        ### Creating the Graph for visualization
        G = nx.Graph()
        ### Adding the positions of the nodes
        nodes = self.I + self.R
        edges = []
        for i in self.R:
            for j in self.I:
                if j in self.graph[i]:
                    edges.append((i, j))

        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        pos = nx.kamada_kawai_layout(G)

        ### Assigning name to the network
        G.graph["name"] = "RTN Network"

        ### Adding nodes and edges to the graph
        for i in pos:
            G.add_node(i, label=i)
        for i in self.graph.keys():
            for j in self.graph[i]:
                G.add_edge(i, j)

        ### Plotting the network graph
        fig = plt.figure()
        labels = {node: node for node in nodes}
        for node in nodes:
            if node in self.R:
                nx.draw_networkx_nodes(
                    G,
                    pos,
                    [node],
                    node_shape="o",
                    node_size=800,
                    node_color="yellow",
                    edgecolors="black",
                )
            elif node in self.I:
                nx.draw_networkx_nodes(
                    G,
                    pos,
                    [node],
                    node_shape="s",
                    node_size=800,
                    node_color="red",
                    edgecolors="black",
                )
            else:
                nx.draw_networkx_nodes(
                    G,
                    pos,
                    [node],
                    node_shape="s",
                    node_size=800,
                    node_color="orange",
                    edgecolors="black",
                )
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos, labels)
        plt.show()
