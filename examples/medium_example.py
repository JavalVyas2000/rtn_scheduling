import os
from rtn.rtn_model import RTN
from rtn.data_utils import create_model_data
import pandas as pd

task = pd.read_excel(os.path.join("..", "data", "products_3.xlsx"), sheet_name="Tasks")
resources = pd.read_excel(
    os.path.join("..", "data", "products_3.xlsx"), sheet_name="Resources"
)
network = pd.read_excel(
    os.path.join("..", "data", "products_3.xlsx"), sheet_name="Network"
)
supply = pd.read_excel(
    os.path.join("..", "data", "products_3.xlsx"), sheet_name="Sup_Dem"
)
horizon = 24
data = create_model_data(task, resources, network, supply, horizon)
RTN_model = RTN(data, "gurobi")
RTN_model.network()
opt = RTN_model.solve_model()
RTN_model.plot_gantt_chart(opt)
RTN_model.get_resource_levels(opt)
