#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import httpx
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CyberChefOperations:
    def __init__(self):
        """
        Get all Cyber Chef operations, either by category or in entirety
        """
        self.ops_url = "https://raw.githubusercontent.com/gchq/CyberChef/refs/heads/master/src/core/config/Categories.json"
        self.request_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_all_data(self) -> dict:
        """Get all categories and operations data from the Cyber Chef GitHub project"""
        try:
            # Get JSON file from GitHub repo
            response = httpx.get(url=self.ops_url, headers=self.request_headers)
            response.raise_for_status()
            response_dict = response.json()
            return response_dict
        except httpx.RequestError as req_exc:
            log.error(f"Exception raised during HTTP GET request to {self.ops_url} - {req_exc}")
            log.warning("Continuing without grabbing updated CyberChef operations data...")

    def get_all_categories(self) -> list:
        """Get a list of all categories that CyberChef groups the operations by"""
        # Get all the data
        response_dict = self.get_all_data()

        # Parse response
        cyberchef_categories = []
        for category in response_dict:
            cyberchef_categories.append(category["name"])

        return cyberchef_categories

    def get_all_operations(self) -> list:
        """Get a list of all operations Cyber Chef can perform"""
        # Get all the data
        response_dict = self.get_all_data()

        # Parse response
        cyberchef_operations = []
        for category in response_dict:
            cyberchef_operations.extend(category["ops"])

        return cyberchef_operations

    def get_operations_by_category(self, category: str) -> list:
        """
        Get a list of operations belonging to a Cyber Chef category

        :param category: operations belonging to this category
        :return:
        """
        # Get all the data
        response_dict = self.get_all_data()

        # Parse response
        operations = []
        for category_obj in response_dict:
            if category_obj["name"].lower() == category.lower():
                operations.extend(category_obj["ops"])

        return operations
