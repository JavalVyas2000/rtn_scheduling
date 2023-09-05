### Importing necessary libraries
import os
from rtn.rtn_model import RTN
from rtn.data_utils import create_model_data
import pandas as pd
import pytest


def test_infeasible():
    """
    The below function is implemented to test the infeasibility
    """
    task = pd.read_excel(os.path.join("data", "infeasibility.xlsx"), sheet_name="Tasks")
    resources = pd.read_excel(
        os.path.join("data", "infeasibility.xlsx"), sheet_name="Resources"
    )
    network = pd.read_excel(
        os.path.join("data", "infeasibility.xlsx"), sheet_name="Network"
    )
    supply = pd.read_excel(
        os.path.join("data", "infeasibility.xlsx"), sheet_name="Sup_Dem"
    )
    horizon = 2
    data = create_model_data(task, resources, network, supply, horizon)
    RTN_model = RTN(data, "gurobi")
    res = RTN_model.solve_model()
    ref_status = "infeasible"
    ref_obj = 0
    assert ref_status == res.res.solver.termination_condition, "Error!!!"
    assert ref_obj == res.obj(), "Error!!!"
