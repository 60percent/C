# some useful docs:
# - flask tests: http://flask.pocoo.org/docs/1.0/testing/
# - Response object: http://flask.pocoo.org/docs/1.0/api/#response-objects
# - test client: http://werkzeug.pocoo.org/docs/0.14/test/#werkzeug.test.Client

import os
import cmdb
import unittest
import string
import random
from cmdb.orm.config_type import ConfigType
from cmdb.orm.version import increase

# generate a random name, like 'TA5fG94GFKE'
def random_name():
    return 'T' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

# generate a random configtype
def random_data():
    # add a prefix to ensure the first letter is not number
    name = random_name()
    return {
        "name": name,
        "namespace": "TestPPC1",
        "inheritance": "Vertex",
        "properties": [
            {
                "name": "IP",
                "type": "STRING"
            }
        ]
    }


class ConfigTypeTestCase(unittest.TestCase):

    def setUp(self):
        self.app = cmdb.create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app.config['BASIC_AUTH_FORCE'] = False # disable basic auth

    def tearDown(self):
        pass

    def create_congfig_type(self, data):
        res = self.client.post('/api/v1/ConfigType', json=data)
        return res.get_json()


    def delete_congfig_type(self, id):
        res = self.client.delete('/api/v1/ConfigType/%s' % id)
        return res.get_json()

    def test_401(self):
        self.app.config['BASIC_AUTH_FORCE'] = True # enable basic auth, only for this case
        res = self.client.get('/api/v1/ConfigType')
        assert res.status_code == 401

    def test_200(self):
        res = self.client.get('/api/v1/ConfigType')
        assert res.status_code == 200

    def test_createConfigType(self):
        data = random_data()
        res_json = self.create_congfig_type(data)

        # success
        assert res_json["err"] == 0
        assert res_json["data"]["id"] == ConfigType.get_friendly_name(data["namespace"], data["name"])
        # fail, when create the same config type
        res2_json = self.create_congfig_type(data)
        assert res2_json["err"] == 109
        self.delete_congfig_type(res_json["data"]["id"])

        # create edge
        data = random_data()
        data["inheritance"] = "E"
        res_json = self.create_congfig_type(data)

        assert res_json["err"] == 0
        assert res_json["data"]["id"] == ConfigType.get_friendly_name(data["namespace"], data["name"])

        self.delete_congfig_type(res_json["data"]["id"])


    def test_createConfigType_with_inheritance(self):
        data = random_data()
        res_json = self.create_congfig_type(data)

        # success
        assert res_json["err"] == 0
        assert res_json["data"]["id"] == ConfigType.get_friendly_name(data["namespace"], data["name"])

        data2 = random_data()
        # inherit data1
        data2['inheritance'] = res_json["data"]["id"]
        res_json2 = self.create_congfig_type(data2)

        assert res_json2["err"] == 0
        assert res_json2["data"]["id"] == ConfigType.get_friendly_name(data2["namespace"], data2["name"])

        # inherit data2
        data3 = random_data()
        data3['inheritance'] = res_json2["data"]["id"]
        res_json3 = self.create_congfig_type(data3)

        assert res_json3["err"] == 0
        assert res_json3["data"]["id"] == ConfigType.get_friendly_name(data3["namespace"], data3["name"])

        self.delete_congfig_type(res_json["data"]["id"])
        self.delete_congfig_type(res_json2["data"]["id"])
        self.delete_congfig_type(res_json3["data"]["id"])

        # inherit not exist
        data4 = random_data()
        data4['inheritance'] = 'A-dasfadas1edef-1.0.0'
        res_json4 = self.create_congfig_type(data4)
        assert res_json4["err"] == 104

    def test_createConfigTypeWithYaml(self):
        namespace = "TestPPC1"
        name = random_name()
        data = """
        namespace: %s
        name: %s
        inheritance: Vertex
        properties:
          - name: IP
            type: STRING
        """ % (namespace, name)
        res_json = self.client.open(method="post", path='/api/v1/ConfigType', data=data, content_type="application/x-yaml").get_json()

        # success
        assert res_json["err"] == 0
        assert res_json["data"]["id"] == ConfigType.get_friendly_name(namespace, name)

        self.delete_congfig_type(res_json["data"]["id"])


    def test_batchCreateConfigType(self):
        data1 = random_data()
        data2 = random_data()

        data = [data1, data2]

        res = self.client.post('/api/v1/ConfigType', json=data)
        res_json = res.get_json()

        # success
        assert res_json["err"] == 0
        assert res_json["data"][0]["id"] == ConfigType.get_friendly_name(data1["namespace"], data1["name"])
        assert res_json["data"][1]["id"] == ConfigType.get_friendly_name(data2["namespace"], data2["name"])

        # delete
        # self.delete_congfig_type(res_json["data"][0]["id"])
        self.delete_congfig_type(res_json["data"][1]["id"])

        # create, but the data[0] is already exist
        res_json = self.client.post('/api/v1/ConfigType', json=data).get_json()

        # already exist
        assert res_json["err"] == 109

    def test_createConfigType_with_error(self):
        res_json = self.create_congfig_type(None)

        assert res_json["err"] == 100

        res_json = self.create_congfig_type([])
        assert res_json["err"] == 100

    def test_updateConfigType(self):
        data = random_data()
        res_json = self.create_congfig_type(data)

        # create success
        assert res_json["err"] == 0
        assert res_json["data"]["id"] == ConfigType.get_friendly_name(data["namespace"], data["name"])
        # update with put
        data["properties"] = [{
            "name": "CPU",
            "type": "INTEGER"
        }]
        name = data["namespace"] + "-" + data["name"]
        res2_json = self.client.put('/api/v1/ConfigType/%s'%name, json=data).get_json()
        assert res2_json["err"] == 0
        assert res2_json["data"]["version"] == increase(res_json["data"]["version"])
        assert res2_json["data"]["properties"][0]["name"] == data["properties"][0]["name"]

        # update with patch
        data["properties"] = [{
            "name": "BandWidth",
            "type": "INTEGER"
        }]
        res3_json = self.client.patch('/api/v1/ConfigType/%s'%name, json=data).get_json()
        assert res3_json["err"] == 0
        assert res3_json["data"]["version"] == increase(res2_json["data"]["version"], 1)
        assert res3_json["data"]["properties"][1]["name"] == data["properties"][0]["name"]

        self.delete_congfig_type(res_json["data"]["id"])

    def test_updateConfigType_by_path(self):
        data = random_data()
        res_json = self.create_congfig_type(data)

        # create success
        assert res_json["err"] == 0
        assert res_json["data"]["id"] == ConfigType.get_friendly_name(data["namespace"], data["name"])
        # update with put
        data["properties"] = [{
            "name": "CPU",
            "type": "INTEGER"
        }]
        res2_json = self.client.put('/api/v1/ConfigType/%s/%s'% (data['namespace'], data['name']),  json=data).get_json()
        assert res2_json["err"] == 0
        assert res2_json["data"]["version"] == increase(res_json["data"]["version"])
        assert res2_json["data"]["properties"][0]["name"] == data["properties"][0]["name"]


        # update with patch
        data["properties"] = [{
            "name": "BandWidth",
            "type": "INTEGER"
        }]
        res3_json = self.client.patch('/api/v1/ConfigType/%s/%s'% (data['namespace'], data['name']), json=data).get_json()
        assert res3_json["err"] == 0
        assert res3_json["data"]["version"] == increase(res2_json["data"]["version"], 1)
        assert res3_json["data"]["properties"][1]["name"] == data["properties"][0]["name"]
        self.delete_congfig_type(res_json["data"]["id"])

    def test_getConfigType(self):
        data = random_data()
        res_json = self.create_congfig_type(data)

        # success
        assert res_json["err"] == 0

        # get
        res2 = self.client.get('/api/v1/ConfigType/%s' % res_json["data"]["id"])
        res2_json = res2.get_json()
        assert res_json["err"] == 0
        assert res_json["data"]["id"] == res2_json["data"]["id"]

        self.delete_congfig_type(res_json["data"]["id"])


    def test_getConfigType_by_path(self):
        data = random_data()
        res_json = self.create_congfig_type(data)

        # success
        assert res_json["err"] == 0

        # get
        d = res_json["data"]
        res2 = self.client.get('/api/v1/ConfigType/%s/%s/%s' % (d["namespace"], d['name'], d['version']))
        res2_json = res2.get_json()
        assert res_json["err"] == 0
        assert res_json["data"]["id"] == res2_json["data"]["id"]

        self.delete_congfig_type(res_json["data"]["id"])


        # can't get not existed data
        res_json3 = self.client.get('/api/v1/ConfigType/MyDemo1/A/1.0.0').get_json()
        assert res_json3["err"] == 112


    def test_deleteConfigType(self):
        data = random_data()
        res_json = self.create_congfig_type(data)

        # create success
        assert res_json["err"] == 0

        # delete
        res2_json = self.delete_congfig_type(res_json["data"]["id"])

        # delete success
        assert res2_json["err"] == 0

        # can not get it
        res3 = self.client.get('/api/v1/ConfigType/%s' % res_json["data"]["id"])
        res3_json = res3.get_json()
        assert res3_json["err"] == 112


        # delete not exist
        res_json = self.client.delete('/api/v1/ConfigType/%s' % res_json["data"]["id"]).get_json()
        assert res_json["err"] == 112

    def test_deleteConfigType_by_path(self):
        data = random_data()
        res_json = self.create_congfig_type(data)

        # create success
        assert res_json["err"] == 0

        # delete
        d = res_json["data"]
        res2 = self.client.delete('/api/v1/ConfigType/%s/%s/%s' % (d["namespace"], d['name'], d['version']))
        res2_json = res2.get_json()

        # delete success
        assert res2_json["err"] == 0

        # can not get it
        res3 = self.client.get('/api/v1/ConfigType/%s' % res_json["data"]["id"])
        res3_json = res3.get_json()
        assert res3_json["err"] == 112




if __name__ == '__main__':
    unittest.main()
