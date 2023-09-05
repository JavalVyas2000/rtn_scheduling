import os
from rtn.rtn_model import RTN
from rtn.data_utils import create_model_data
import pandas as pd
import pytest


def test_24_hour_horizon():
    """
    The below function is implemented to test the a 24_hour example
    """
    task = pd.read_excel(os.path.join("data", "products_3.xlsx"), sheet_name="Tasks")
    resources = pd.read_excel(
        os.path.join("data", "products_3.xlsx"), sheet_name="Resources"
    )
    network = pd.read_excel(
        os.path.join("data", "products_3.xlsx"), sheet_name="Network"
    )
    supply = pd.read_excel(
        os.path.join("data", "products_3.xlsx"), sheet_name="Sup_Dem"
    )
    horizon = 24
    data = create_model_data(task, resources, network, supply, horizon)
    RTN_model = RTN(data, "gurobi")
    res = RTN_model.solve_model()
    ref_obj = 12
    assert pytest.approx(ref_obj) == res.obj(), "Error!!!"
