import pandas as pd
from collections import defaultdict


def create_model_data(task, resources, network, sd, H, solver="glpk"):
    """
    Task:
    T[0] - Task name
    T[1] - Time taken for task to be executed
    T[2] - Minimum Batch size that can be processed
    T[3] - Maximum Batch size that can be processed
    """
    """
    Resources:
    Res[0] - Resource name 
    Res[1] - Initial Inventory 
    Res[2] - Minimum Inventory 
    Res[3] - Maximum Inventory 
    Res[4] - If resource is used to execute task 
    """
    """
    Network:
    N[0] - from_node
    N[1] - to_node
    N[2] - Amount consumed/Produced 
    N[3] - Recycling ratio if any 
    """
    """ 
    Supply/Demand
    header[0] - Resource    
    header[1] - Demand/Supply (demand is with a negative sign) 
    header[2] - Time of demand/supply
    """

    I = []
    R = []
    nodes = []
    Task_resources = []

    tau = {}  ### Duration of task
    X0 = {}  ### Initial resource level
    Xmin = {}  ### Minimum resource level
    Xmax = {}  ### Maximum resource level
    Vmin = {}  ### Minimum Batch Size
    Vmax = {}  ### Maximum Batch Size

    idx = []
    mu = {}
    nu = {}

    pi = {}
    max_tau = 0

    horizon = H

    N = network.columns
    T = task.columns
    Res = resources.columns
    header = sd.columns

    graph = defaultdict(list)

    def addEdge(graph, u, v):
        graph[u].append(v)

    for i in range(len(task)):
        nodes.append(task[T[0]][i])
        I.append(task[T[0]][i])
        tau[task[T[0]][i]] = task[T[1]][i]
        if tau[task[T[0]][i]] > max_tau:
            max_tau = tau[task[T[0]][i]]
        Vmin[task[T[0]][i]] = task[T[2]][i]
        Vmax[task[T[0]][i]] = task[T[3]][i]

    for i in range(len(resources)):
        nodes.append(resources[Res[0]][i])
        R.append(resources[Res[0]][i])
        X0[resources[Res[0]][i]] = resources[Res[1]][i]
        Xmin[resources[Res[0]][i]] = resources[Res[2]][i]
        Xmax[resources[Res[0]][i]] = resources[Res[3]][i]
        if resources[Res[4]][i] == 1:
            Task_resources.append(resources[Res[0]][i])

    def checkNetworkData(network):
        """
        The below function checks for
        1. valid names in from_node
        2. valid names in to_node
        3. valid connections of task being connceted to resources and vice-versa
        4. Amount consumed
        """
        for i in range(len(network)):
            assert (
                network[N[0]][i] in R or network[N[0]][i] in I
            ), f"Node name {network[N[0]][i]} not in tasks or resources"
            assert (
                network[N[1]][i] in R or network[N[1]][i] in I
            ), f"Node name {network[N[1]][i]} not in tasks or resources"
            assert (network[N[1]][i] in R and network[N[0]][i] in I) or (
                network[N[0]][i] in R and network[N[1]][i] in I
            ), f"Tasks connected with tasks or resources connected with resources, check row {i}"
            assert (
                network[N[2]][i] >= -1
            ), f"Amount consumed should be between greater than or equal to -1, check row {i+1}"
            if len(N) > 3:
                assert (
                    network[N[3]][i] >= 0
                ), f"Recycling ratio should be positive, check row {i+1}"

    def checkTaskData(task):
        for i in range(len(task)):
            assert len(task[T[0]][i]) > 0, f"Invalid task name, possibly a None type"
            assert (
                task[T[1]][i] >= 0
            ), f"Time taken by {task[T[1]][i]} cannot be negative"
            assert (
                task[T[1]][i] % 1 == 0
            ), f"Time taken by {task[T[1]][i]} should be an integer"
            assert (
                task[T[2]][i] >= 0
            ), f"Minimum batch size should be positive, check row {i+1}"
            assert (
                task[T[3]][i] >= 0
            ), f"Maximum batch size should be positive, check row {i+1}"
            assert (
                task[T[2]][i] <= task[T[3]][i]
            ), f"Minimum batch size should be lesser than maximum batch size, check row {i+1}"

    def checkResourceData(resources):
        for i in range(len(resources)):
            assert (
                len(resources[Res[0]][i]) > 0
            ), f"Invalid resource name, possibly a None type"
            assert (
                resources[Res[1]][i] >= 0
            ), f"Initial inventory for {resources[Res[1]][i]} cannot be negative"
            assert (
                resources[Res[2]][i] >= 0
            ), f"Minimum inventory for {resources[Res[1]][i]} should be positive"
            assert (
                resources[Res[3]][i] >= 0
            ), f"Maximum inventory for {resources[Res[1]][i]} should be positive"
            assert (
                resources[Res[2]][i] <= resources[Res[3]][i]
            ), f"Minimum inventory of {resources[Res[1]][i]} should be lesser than maximum inventory"
            assert (
                resources[Res[4]][i] == 0 or resources[Res[4]][i] == 1
            ), f"This column can take values of either 0 or 1, check row {i+1}"

    def checkSupDemData(sd):
        for i in range(len(sd)):
            assert len(sd[header[0]][i]) > 0, f"Invalid resource name, possibly None"
            assert sd[header[0]][i] in R, f"Invalid resource name {sd[header[0]][i]}"

    def checkTaskNames(I, R):
        for i in I:
            assert i not in R, f"Task and resources have the same name {i}"

    checkNetworkData(network)
    checkTaskData(task)
    checkResourceData(resources)
    checkTaskNames(I, R)
    checkSupDemData(sd)
    for i in range(len(network)):
        ### Resource is Produced/Task_resource
        if network[N[0]][i] in I:
            if network[N[1]][i] not in Task_resources:
                for theta in range(tau[network[N[0]][i]] + 1):
                    mu[network[N[0]][i], network[N[1]][i], theta] = 0
                    if theta == tau[network[N[0]][i]]:
                        nu[network[N[0]][i], network[N[1]][i], theta] = network[N[2]][i]
                    else:
                        nu[network[N[0]][i], network[N[1]][i], theta] = 0
                    idx.append((network[N[0]][i], network[N[1]][i], theta))

            else:
                for theta in range(tau[network[N[0]][i]] + 1):
                    nu[network[N[0]][i], network[N[1]][i], theta] = 0
                    if theta == 0:
                        mu[network[N[0]][i], network[N[1]][i], theta] = -network[N[2]][
                            i
                        ]
                    elif theta == tau[network[N[0]][i]]:
                        mu[network[N[0]][i], network[N[1]][i], theta] = network[N[2]][i]
                    else:
                        mu[network[N[0]][i], network[N[1]][i], theta] = 0
                    idx.append((network[N[0]][i], network[N[1]][i], theta))
            addEdge(graph, network[N[1]][i], network[N[0]][i])
        else:
            for theta in range(tau[network[N[1]][i]] + 1):
                mu[network[N[1]][i], network[N[0]][i], theta] = 0
                if theta == 0:
                    nu[network[N[1]][i], network[N[0]][i], theta] = network[N[2]][i]
                else:
                    nu[network[N[1]][i], network[N[0]][i], theta] = 0
                if len(network.columns) > 3:
                    if theta == tau[network[N[1]][i]]:
                        nu[network[N[1]][i], network[N[0]][i], theta] = network[N[3]][i]
                idx.append((network[N[1]][i], network[N[0]][i], theta))
            addEdge(graph, network[N[0]][i], network[N[1]][i])

    for i in resources[Res[0]]:
        for t in range(1, horizon + 1):
            pi[i, t] = 0
    for i in range(len(sd)):
        pi[sd[header[0]][i], sd[header[2]][i]] = sd[header[1]][i]

    data = {
        "tau": tau,
        "X0": X0,
        "Xmin": Xmin,
        "Xmax": Xmax,
        "Vmin": Vmin,
        "Vmax": Vmax,
        "mu": mu,
        "nu": nu,
        "pi": pi,
        "I": I,
        "R": R,
        "idx": idx,
        "max_tau": max_tau,
        "graph": graph,
        "horizon": horizon,
        "Task_resources": Task_resources,
    }

    return data
