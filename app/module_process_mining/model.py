from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from app.module_process_mining.utils import *

import json


def build_process_data(process_data):
    for column_name in ["case_id", "event", "timestamp"]:
        if column_name not in process_data.columns.values:
            raise ValueError('Datatable must contain a column labelled "%column_name%".'
                             .replace("%column_name%", column_name))
    process_data["timestamp"] = pd.to_datetime(process_data["timestamp"])
    process_data["timestamp_day"] = pd.DatetimeIndex(process_data.timestamp).normalize()
    process_data.sort_values(by=["case_id", "timestamp"], inplace=True)

    # creation of next node column
    colToAdd = process_data.iloc[1:][["case_id", "event"]].reset_index(drop=True).rename(columns={"case_id": "case_id_next",
                                                                                        "event": "event_next"})
    colToAdd.loc[len(colToAdd)] = ['noNextEvent', 'noNextEvent']
    colToAdd.loc[colToAdd['case_id_next'] != process_data['case_id'], ['event_next']] = 'noNextEvent'
    process_data['_event_next'] = colToAdd['event_next']
    # creation of currentNode##nextNode concatenation
    process_data['_currentNode##nextNode'] = process_data['event'] + '##' + process_data['_event_next']

    #creation of the entire path column
    paths = process_data.groupby('case_id')['event'].apply(lambda x: '##'.join(x))
    process_data['event_path'] = process_data[['case_id']].join(paths, on='case_id')['event']

    process_data.set_index("case_id", drop=False, inplace=True)
    return process_data


class AbstractProcessModel(ABC):
    # Instantiation
    @abstractmethod
    def __init__(self, name):
        self.name = name
        self._process_filter_list = []

    # Filter management
    def add_filter(self, new_process_filter):
        self._process_filter_list.append(new_process_filter)
        self.apply_filter(new_process_filter)

    def remove_filter(self, filter_idx):
        del self._process_filter_list[filter_idx]
        self.apply_all_filters()

    def get_process_filter_list(self):
        return self._process_filter_list

    def print_all_filters(self):
        print(self._process_filter_list)

    @abstractmethod
    def apply_filter(self, filter):
        pass

    @abstractmethod
    def apply_all_filters(self):
        pass

    @abstractmethod
    def clean_filters(self):
        self._process_filter_list = []

    @abstractmethod
    def get_filters_information(self):
        pass

    # Getters for filtered and/or aggregated data
    @abstractmethod
    def get_graph_definition(self):
        pass

    @abstractmethod
    def get_piechart(self):
        pass

    @abstractmethod
    def get_daily_barchart(self):
        pass

    # Communication with front-end
    @abstractmethod
    def message_to_send(self):
        pass


class PandasProcessModel(AbstractProcessModel):
    # Class methods and attributes
    __process_data = None

    @classmethod
    def set_process_data(cls, data):
        cls.__process_data = build_process_data(data)
        cls.__case_id_amount = len(np.unique(cls.__process_data.case_id))

    # Instantiation
    def __init__(self, name):
        super().__init__(name)
        self.__filtered_data_idx = np.ones(len(self.__process_data), dtype=bool)

    # Filter management
    def apply_filter(self, filter):
        filtered_process_data = self.get_filtered_process_data()
        filtered_rows = filter.filtering_function(filtered_process_data[filter.filter_by])
        self.__filtered_data_idx = (self.__process_data.case_id
                                    .isin(filtered_process_data[filtered_rows].index))

    def apply_all_filters(self):
        if len(self._process_filter_list) == 0:
            self.__filtered_data_idx = np.ones(len(self.__process_data), dtype=bool)
        else:
            filtered_indexes = []
            for filter in self._process_filter_list:
                selected_rows = filter.filtering_function(self.__process_data[filter.filter_by])
                filtered_indexes.append(self.__process_data.case_id.isin(self.__process_data[selected_rows].index))
            self.__filtered_data_idx = conjunction(filtered_indexes)

    def clean_filters(self):
        super().clean_filters()
        self.__filtered_data_idx = np.ones(len(self.__process_data), dtype=bool)

    def get_filters_information(self):
        return {'filtered_case_id_amount': len(self.get_filtered_process_data().case_id.unique()),
                'total_case_id_amount': self.__case_id_amount,
                'filter_list': [{'id': ind, 'text': str(filter_item)}
                                for ind, filter_item in enumerate(self._process_filter_list)]}

    # Getters for filtered and/or aggregated data
    def get_process_data(self):
        return self.__process_data

    def get_filtered_data_idx(self):
        return self.__filtered_data_idx

    def get_filtered_process_data(self):
        return self.__process_data.loc[self.__filtered_data_idx]

    def get_aggregated_data(self, groupby, value, method):
        methods = {
            "count_unique": (lambda x: float(len(x.unique())))
        }
        grouped = self.get_filtered_process_data()[[groupby, value]].groupby(groupby)
        if method == "count":
            aggregated = grouped.count()
        elif method == "sum":
            aggregated = grouped.sum()
        else:
            if method in methods:
                aggregate_method = methods[method]
            else:
                aggregate_method = method
            aggregated = grouped.aggregate({
                value: aggregate_method
            })
        aggregated_data = aggregated.reset_index().transpose()
        return aggregated_data.values

    def get_graph_definition(self):
        filtered_process_data = self.get_filtered_process_data()

        # Graph position
        graph_position = {"class": "go.GraphLinksModel",
                          "nodeDataArray": [
                              {"key": "Process Start", "color": "#FED402", "npoints": 325899, "fixed": "true"},
                              {"key": "PO Requisition", "color": "lightgrey", "npoints": 23991},
                              {"key": "Create PO", "color": "lightgrey", "npoints": 325899, "fixed": "true"},
                              {"key": "Approve PO", "color": "lightgrey", "npoints": 4581},
                              {"key": "Goods Receipt", "color": "lightgrey", "npoints": 325804, "fixed": "true"},
                              {"key": "Invoice Gross", "color": "lightgrey", "npoints": 894, "fixed": "true"},
                              {"key": "Vendor Credit Memo", "color": "lightgrey", "npoints": 3},
                              {"key": "Vendor Invoice", "color": "lightgrey", "npoints": 3},
                              {"key": "No Hold", "color": "lightgrey", "npoints": 318992, "fixed": "true"},
                              {"key": "Auto Release", "color": "lightgrey", "npoints": 438},
                              {"key": "Manual Release", "color": "lightgrey", "npoints": 4537},
                              {"key": "Payment", "color": "lightgrey", "npoints": 240507, "fixed": "true"},
                              {"key": "Account Maintenance", "color": "lightgrey", "npoints": 95},
                              {"key": "Process End", "color": "#FED402", "npoints": 325899, "fixed": "true"},
                          ],
                          "linkDataArray": [
                              {"from": "Process Start", "to": "PO Requisition"},
                              {"from": "PO Requisition", "to": "Create PO"},
                              {"from": "Process Start", "to": "Create PO"},
                              {"from": "Create PO", "to": "Approve PO", "dash": [30, 2]},
                              {"from": "Approve PO", "to": "Goods Receipt", "dash": [30, 2]},
                              {"from": "Create PO", "to": "Goods Receipt"},
                              {"from": "Goods Receipt", "to": "Process End"},
                              {"from": "Goods Receipt", "to": "Invoice Gross", "dash": [3, 2]},
                              {"from": "Goods Receipt", "to": "Vendor Invoice", "dash": [3, 2]},
                              {"from": "Goods Receipt", "to": "No Hold"},
                              {"from": "Goods Receipt", "to": "Vendor Credit Memo", "dash": [3, 2]},
                              {"from": "Goods Receipt", "to": "Manual Release", "dash": [30, 2]},
                              {"from": "Goods Receipt", "to": "Auto Release", "dash": [3, 2]},
                              {"from": "Vendor Invoice", "to": "No Hold", "dash": [3, 2]},
                              {"from": "Invoice Gross", "to": "No Hold", "dash": [3, 2]},
                              {"from": "No Hold", "to": "Payment"},
                              {"from": "Auto Release", "to": "Payment", "dash": [3, 2]},
                              {"from": "No Hold", "to": "Process End"},
                              {"from": "Account Maintenance", "to": "Process End", "dash": [3, 2]},
                              {"from": "Payment", "to": "Account Maintenance", "dash": [3, 2]},
                              {"from": "Payment", "to": "Process End"},
                              {"from": "Manual Release", "to": "Process End", "dash": [30, 2]},
                              {"from": "Vendor Credit Memo", "to": "Process End", "dash": [3, 2]}
                          ]};

        # Graph nodes
        graph_nodes = filtered_process_data["event"].unique()

        # Graph edges
        concat_table = filtered_process_data[filtered_process_data["_event_next"] != 'noNextEvent']
        grouped = concat_table[["case_id", "user", "event", "_event_next"]].groupby(["event", "_event_next"])
        aggregated = grouped.aggregate({
            "case_id": len,
            "user": np.count_nonzero
        })

        graph_edges = [(index[0], index[1], json.loads(row.to_json(orient='index'))) for index, row in aggregated.iterrows()]
        # TODO Nodes have no attributes. This needs to be implemented later.
        return {'graph_nodes': list(graph_nodes),
                'graph_edges': graph_edges,
                'graph_position': graph_position}

    def get_daily_barchart(self, value="timestamp", method="count"):
        categories, values = self.get_aggregated_data("timestamp_day", value, method)
        categories = pd.to_datetime(categories).astype(np.int64)/1e6
        return list(zip(categories, list(values)))

    def get_piechart(self, groupby, value="timestamp", method="count", top=10):
        unsort_cat, unsort_val = self.get_aggregated_data(groupby, value, method)
        sorted_list = sorted(zip(unsort_val, unsort_cat), reverse=True)
        categories = [y for x, y in sorted_list]
        values = [x for x, y in sorted_list]
        if top == "all":
            pass
        elif isinstance(top, str) and top[-1] == "%":
            top_idx = get_first_percent(values, float(top[:-1])) + 1
            categories = categories[:top_idx]
            values = values[:top_idx]
        else:
            categories = categories[:top]
            values = values[:top]
        return [
            {
                "name": category,
                "y": amount
            }
            for category, amount in zip(categories, values)
        ]

    # Communication with front-end
    def message_to_send(self):
        message = {
            'filterList' : self.get_filters_information(),
            "graph": self.get_graph_definition(),
            "eventtypePieChartData": self.get_piechart("event"),
            "userPieChartData": self.get_piechart("user"),
            "barChartData": self.get_daily_barchart()
        }
        # TODO other message attributes
        return message


class AbstractFilter(ABC):
    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)


class PandasFilter(ABC):
    @abstractmethod
    def filtering_function(self, x):
        pass


class RangeFilter(AbstractFilter):
    def __init__(self, filter_by, range_from, range_to):
        self.filter_by = filter_by
        self.range_from = range_from
        self.range_to = range_to

    def __str__(self):
        return str(self.filter_by) + ': [' + str(self.range_from) + ' - ' + str(self.range_to) + ']'


class ListFilter(AbstractFilter):
    def __init__(self, filter_by, filter_list):
        self.filter_by = filter_by
        self.filter_list = filter_list

    def __str__(self):
        return str(self.filter_by) + ': ' + ",".join([str(elt) for elt in self.filter_list])


class LinkFilter(AbstractFilter):
    def __init__(self, node_from, node_to):
        self.filter_by = '_currentNode##nextNode'
        self.node_from = node_from
        self.node_to = node_to

    def __str__(self):
        return str(self.filter_by) + ': [' + str(self.node_from) + ' - ' + str(self.node_to) + ']'


class PandasRangeFilter(RangeFilter, PandasFilter):
    def filtering_function(self, x):
        return (self.range_from <= x) & (x < self.range_to)


class PandasListFilter(ListFilter, PandasFilter):
    def filtering_function(self, x):
        return x.isin(self.filter_list)


class PandasLinkFilter(LinkFilter, PandasFilter):
    def filtering_function(self, x):
        return self.node_from + '##' + self.node_to == x
