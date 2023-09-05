### Importing necessary libraries
from rtn.rtn_model import RTN
from rtn.data_utils import create_model_data
import pandas as pd
import pytest


def test_recycling():
    """
    The below function is implemented to test the recycling example
    """
    task = pd.read_excel("data/recycling.xlsx", sheet_name="Task")
    resources = pd.read_excel("data/recycling.xlsx", sheet_name="Resources")
    network = pd.read_excel("data/recycling.xlsx", sheet_name="Network")
    supply = pd.read_excel("data/recycling.xlsx", sheet_name="Sup_Dem")
    horizon = 4
    data = create_model_data(task, resources, network, supply, horizon)
    RTN_model = RTN(data, "gurobi")
    res = RTN_model.solve_model()
    ref_obj = 1
    assert pytest.approx(ref_obj) == res.obj(), "Error!!!"
