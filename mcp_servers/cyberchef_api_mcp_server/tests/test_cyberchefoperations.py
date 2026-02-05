#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from mcp_servers.cyberchef_api_mcp_server.src.cyberchefoperations import CyberChefOperations


cyberchef_ops = CyberChefOperations()


def test_get_all_data():
    all_data = cyberchef_ops.get_all_data()
    assert len(all_data) > 1


def test_get_all_categories():
    all_cats = cyberchef_ops.get_all_categories()
    assert len(all_cats) > 1


def test_get_all_operations():
    ops = cyberchef_ops.get_all_operations()
    assert len(ops) > 1


def test_get_all_operations_by_category_pass():
    ops_by_cat = cyberchef_ops.get_operations_by_category(category="Data Format")
    assert len(ops_by_cat) > 1


def test_get_all_operations_by_category_fail():
    ops_by_cat = cyberchef_ops.get_operations_by_category(category="Not A Category")
    assert len(ops_by_cat) == 0