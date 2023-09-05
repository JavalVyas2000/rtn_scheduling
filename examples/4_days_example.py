import os
from rtn.rtn_model import RTN
from rtn.data_utils import create_model_data
import pandas as pd

task = pd.read_excel(os.path.join("..", "data", "case_4_days.xlsx"), sheet_name="Tasks")
resources = pd.read_excel(
    os.path.join("..", "data", "case_4_days.xlsx"), sheet_name="Resources"
)
network = pd.read_excel(
    os.path.join("..", "data", "case_4_days.xlsx"), sheet_name="Network"
)
supply = pd.read_excel(
    os.path.join("..", "data", "case_4_days.xlsx"), sheet_name="Sup_Dem"
)
horizon = 24 * 4
data = create_model_data(task, resources, network, supply, horizon)
RTN_model = RTN(data, "gurobi")
RTN_model.network()
res = RTN_model.solve_model()
RTN_model.plot_gantt_chart(res)
RTN_model.get_resource_levels(res)
