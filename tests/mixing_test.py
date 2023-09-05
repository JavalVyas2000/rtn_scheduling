from rtn.rtn_model import RTN
from rtn.data_utils import create_model_data
import pandas as pd
import pytest
import os


def test_mixing():
    """
    The below function is implemented to test the mixing example
    """
    task = pd.read_excel(os.path.join("data", "products_2.xlsx"), sheet_name="Tasks")
    resources = pd.read_excel(
        os.path.join("data", "products_2.xlsx"), sheet_name="Resources"
    )
    network = pd.read_excel(
        os.path.join("data", "products_2.xlsx"), sheet_name="Network"
    )
    supply = pd.read_excel(os.path.join("data", "products_2.xlsx"), sheet_name="Supply")
    horizon = 4
    data = create_model_data(task, resources, network, supply, horizon)
    RTN_model = RTN(data, "gurobi")
    res = RTN_model.solve_model()
    ref_obj = 4
    assert pytest.approx(ref_obj) == res.obj(), "Error!!!"
