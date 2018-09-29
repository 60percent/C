import unittest
import copy
from cmdb.config_item import *

from cmdb.orm.validation_config_type import ValidationConfigType
from cmdb.custom_exception import CException
from cmdb.orm import version as version_util

class TestValidationConfigType(unittest.TestCase):
    def test_validateConfigType(self):
        valid_data = {
            "name": "VM",
            "namespace": "ppcDemo",
            "inheritance": "Vertex",
            "properties": []
        }
        self.assertTrue(ValidationConfigType.validateConfigType(valid_data))

        valid_data["properties"] = [
                {
                    "name": "CPU",
                    "type": "INTEGER"
                    }
                ]
        self.assertTrue(ValidationConfigType.validateConfigType(valid_data))

        error_name_data = copy.deepcopy(valid_data)
        error_name_data["name"] = "VM1.1?"
        self.assertRaises(CException, ValidationConfigType.validateConfigType, error_name_data)

        error_namespace_data = copy.deepcopy(valid_data)
        error_namespace_data["namespace"] = "1@1-?"
        self.assertRaises(CException, ValidationConfigType.validateConfigType, error_namespace_data)


        error_properties_data = copy.deepcopy(valid_data)
        error_properties_data["properties"] = [
            {
                "name": "CPU",
                "type": "INVALID_TYPE"
            }
        ]
        self.assertRaises(CException, ValidationConfigType.validateConfigType, error_properties_data)

        error_properties_data = copy.deepcopy(valid_data)
        error_properties_data["properties"] = [
            {
                "name": "CPU??invalidaname",
                "type": "INTEGER"
            }
        ]
        self.assertRaises(CException, ValidationConfigType.validateConfigType, error_properties_data)
    
    
    def test_validateQueryPath(self):
        self.assertTrue(ValidationConfigType.validateQueryPath("demoPPC", "demoVM", "1.1.0"))
        self.assertRaises(CException, ValidationConfigType.validateQueryPath, "demoPPC-error-namespace", "demoVM", "1.1.0")
        self.assertRaises(CException, ValidationConfigType.validateQueryPath, "demoPPC", "demoVM?", "1.1@X")
        self.assertRaises(CException, ValidationConfigType.validateQueryPath, "demoPPC", "demoVM", "1.1@X")

    def test_validateID(self):
        self.assertTrue(ValidationConfigType.validateID("demoPPC-demoVM-1.1.0"))
        self.assertRaises(CException, ValidationConfigType.validateID, "demoPPC-demoVM-1.1.?")

    def test_version(self):
        self.assertEqual(version_util.stringify("1.2.34"), "1_2_34")
        self.assertEqual(version_util.parse("1_2_34"), "1.2.34")
        self.assertEqual(version_util.increase("1.2.34"), "2.2.34")
        self.assertEqual(version_util.increase("1.2.34", 1), "1.3.34")
