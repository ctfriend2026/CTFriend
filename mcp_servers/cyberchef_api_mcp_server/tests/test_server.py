#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from mcp_servers.cyberchef_api_mcp_server.src.server import CyberChefRecipeOperation, bake_recipe, batch_bake_recipe, perform_magic_operation


def test_bake_recipe():
    test_input = "64 47 56 7a 64 41 3d 3d"
    test_recipe = [
        CyberChefRecipeOperation(op="From Hex", args=["Auto"]),
        CyberChefRecipeOperation(op="From Base64")
    ]
    recipe_response = bake_recipe(input_data=test_input, recipe=test_recipe)

    assert recipe_response["value"] == "test"


def test_batch_bake_recipe():
    test_input = [
        "64 47 56 7a 64 41 3d 3d",
        "64 47 56 7a 64 44 49 3d"
    ]
    test_recipe = [
        CyberChefRecipeOperation(op="From Hex", args=["Auto"]),
        CyberChefRecipeOperation(op="From Base64")
    ]
    recipe_response = batch_bake_recipe(batch_input_data=test_input, recipe=test_recipe)
    recipe_response_parse = [value.get("value") for value in recipe_response]

    assert recipe_response_parse == ["test", "test2"]


def test_perform_magic_operation():
    test_input = "64 47 56 7a 64 41 3d 3d"
    recipe_response = perform_magic_operation(input_data=test_input)

    assert recipe_response["value"][0]["data"] == "test"
    assert recipe_response["value"][1]["data"] == "dGVzdA=="
    assert recipe_response["value"][2]["data"] == test_input