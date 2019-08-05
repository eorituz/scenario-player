from unittest.mock import patch

import pytest
from web3.gas_strategies.time_based import fast_gas_price_strategy, medium_gas_price_strategy

from scenario_player.utils.configuration.base import ConfigMapping
from scenario_player.utils.configuration.settings import (
    PFSSettingsConfig,
    ScenarioConfigurationError,
    ServiceSettingsConfig,
    SettingsConfig,
    UDCSettingsConfig,
)


class TestSettingsConfig:
    def test_is_subclass_of_config_mapping(self, minimal_yaml_dict):
        """The class is a subclass of :class:`ConfigMapping`."""
        assert isinstance(SettingsConfig(minimal_yaml_dict), ConfigMapping)

    @pytest.mark.parametrize("key", ["notify", "timeout", "chain", "gas_price"])
    def test_class_returns_expected_default_for_key(
        self, key, expected_defaults, minimal_yaml_dict
    ):
        """If supported  keys are absent, sensible defaults are returned for them when accessing
        them as a class attribute."""
        config = SettingsConfig(minimal_yaml_dict)

        try:
            actual = getattr(config, key)
        except AttributeError as e:
            raise AssertionError(e)

        assert expected_defaults["settings"][key] == actual

    def test_settings_attr_returns_service_settings_config_instance(self, minimal_yaml_dict):
        config = SettingsConfig(minimal_yaml_dict)
        assert isinstance(config.services, ServiceSettingsConfig)

    @pytest.mark.parametrize(
        "value, raises",
        argvalues=[("super-fast", True), (1.22, True), (11, False), ("fast", False)],
        ids=[
            "Unknown strategy key",
            "Non-int number",
            "valid integer value",
            "Valid strategy ket",
        ],
    )
    def test_validate_raises_exception_for_invalid_gas_price_values(
        self, value, raises, minimal_yaml_dict
    ):
        minimal_yaml_dict["settings"]["gas_price"] = value
        try:
            SettingsConfig(minimal_yaml_dict)
        except ScenarioConfigurationError:
            if not raises:
                pytest.fail("Raised ScenarioConfigurationError unexpectedly!")

    def test_gas_price_strategy_returns_a_callable(self, minimal_yaml_dict):
        """The :attr:`SettingsConfig.gas_price_strategy` returns a callable."""
        config = SettingsConfig(minimal_yaml_dict)
        assert callable(config.gas_price_strategy)

    @pytest.mark.parametrize(
        "strategy, expected_func",
        argvalues=[("fast", fast_gas_price_strategy), ("medium", medium_gas_price_strategy)],
    )
    def test_gas_price_strategy_property_returns_strategy_from_web3(
        self, strategy, expected_func, minimal_yaml_dict
    ):
        """The gas price strategy is dynamically fetched."""
        minimal_yaml_dict["settings"]["gas_price"] = strategy
        config = SettingsConfig(minimal_yaml_dict)
        assert config.gas_price_strategy == expected_func


class TestServiceSettingsConfig:
    def test_is_subclass_of_config_mapping(self, minimal_yaml_dict):
        """The class is a subclass of :class:`ConfigMapping`."""
        assert isinstance(ServiceSettingsConfig(minimal_yaml_dict), ConfigMapping)

    def test_pfs_attribute_returns_pfs_settings_config(self, minimal_yaml_dict):
        config = ServiceSettingsConfig(minimal_yaml_dict)
        assert isinstance(config.pfs, PFSSettingsConfig)

    def test_ucd_attribute_returns_udc_settings_config(self, minimal_yaml_dict):
        config = ServiceSettingsConfig(minimal_yaml_dict)
        assert isinstance(config.udc, UDCSettingsConfig)


class TestPFSSettingsConfig:
    def test_is_subclass_of_config_mapping(self, minimal_yaml_dict):
        """The class is a subclass of :class:`ConfigMapping`."""
        assert isinstance(PFSSettingsConfig(minimal_yaml_dict), ConfigMapping)

    def test_url_attribute_returns_default_none_if_key_absent(self, minimal_yaml_dict):
        config = PFSSettingsConfig(minimal_yaml_dict)
        assert config.url is None

    def test_url_attribute_returns_url_key_value_if_key_present(self, minimal_yaml_dict):
        minimal_yaml_dict["settings"]["services"] = {"pfs": {"url": "custom_url"}}
        config = PFSSettingsConfig(minimal_yaml_dict)
        assert config.url == "custom_url"


class TestUDCSettingsConfig:
    def test_is_subclass_of_config_mapping(self, minimal_yaml_dict):
        """The class is a subclass of :class:`ConfigMapping`."""
        assert isinstance(UDCSettingsConfig(minimal_yaml_dict), ConfigMapping)

    @pytest.mark.parametrize(
        "key, expected",
        argvalues=[("enable", False), ("address", None), ("token", {"deposit": False})],
    )
    def test_attributes_whose_key_is_absent_return_expected_default(
        self, key, expected, minimal_yaml_dict
    ):
        config = UDCSettingsConfig(minimal_yaml_dict)
        MISSING = object()
        assert getattr(config, key, MISSING) == expected

    @pytest.mark.parametrize(
        "key, expected",
        argvalues=[("enable", True), ("address", "walahoo"), ("token", {"deposit": True})],
    )
    def test_attributes_return_for_key_value_if_key_present(
        self, key, expected, minimal_yaml_dict
    ):
        minimal_yaml_dict["settings"] = {"services": {"udc": {key: expected}}}
        config = UDCSettingsConfig(minimal_yaml_dict)
        MISSING = object()
        assert getattr(config, key, MISSING) == expected
