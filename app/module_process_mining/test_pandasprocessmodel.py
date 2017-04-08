# In command shell, run '>> py.test' with right config to run test
# can be done within PyCharm if pytest is default tester

import datetime
import io

import pytest

from .model import *


def data():
    datatable_csv = """case_id,event,timestamp,user
1111,written,15/07/2016,marchand
1111,sent,16/07/2016,marchand
1111,received,17/07/2016,rioust
2222,written,18/07/2016,blasco
2222,sent,19/07/2016,blasco
2222,received,20/07/2016,burel
2222,forwarded,21/07/2016,burel
2222,received,22/07/2016,rioust
3333,written,23/07/2016,blasco
3333,deleted,24/07/2016,blasco
4444,written,25/07/2016,rioust
4444,sent,26/07/2016,rioust
4444,received,27/07/2016,marchand
4444,received,28/07/2016,burel
4444,received,29/07/2016,blasco"""
    return pd.read_csv(io.StringIO(datatable_csv), delimiter=',')

PandasProcessModel.set_process_data(data())


@pytest.fixture()
def ppm():
    return PandasProcessModel('A first test')


@pytest.fixture()
def list_filter():
    return PandasListFilter('user', ['marchand'])


@pytest.fixture()
def range_filter():
    return PandasRangeFilter('timestamp', datetime.datetime(2016, 7, 17), datetime.datetime(2016, 7, 23))

@pytest.fixture()
def link_filter():
    return PandasLinkFilter('written', 'sent')


def test_add_list_filter(ppm, list_filter):
    ppm.add_filter(list_filter)
    assert ppm.get_process_filter_list()[-1] == list_filter
    assert list(ppm.get_filtered_data_idx()) == [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]


def test_add_range_filter(ppm, range_filter):
    ppm.add_filter(range_filter)
    assert ppm.get_process_filter_list()[-1] == range_filter
    assert list(ppm.get_filtered_data_idx()) == [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]

def test_add_link_filter(ppm, link_filter):
    print(ppm.get_filtered_process_data())
    ppm.add_filter(link_filter)
    print(ppm.get_filtered_data_idx())
    assert list(ppm.get_filtered_data_idx()) == [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1]


def test_apply_several_filters(ppm, list_filter, range_filter):
    ppm.add_filter(list_filter)
    ppm.add_filter(range_filter)
    assert list(ppm.get_filtered_data_idx()) == [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def test_apply_all_filters(ppm, list_filter, range_filter):
    ppm.add_filter(list_filter)
    ppm.add_filter(range_filter)
    ppm.apply_all_filters()
    assert list(ppm.get_filtered_data_idx()) == [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def test_remove_filter(ppm, list_filter, range_filter):
    ppm.add_filter(list_filter)
    ppm.add_filter(range_filter)
    ppm.remove_filter(1)
    assert range_filter not in ppm.get_process_filter_list()
    assert list(ppm.get_filtered_data_idx()) == [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    ppm.remove_filter(0)
    assert list_filter not in ppm.get_process_filter_list()
