import unittest
import operator
import json
import bson

from webtest import TestApp

from kule import Kule

first = operator.itemgetter(0)


class KuleTests(unittest.TestCase):
    """
    Functionality tests for kule.
    """

    def setUp(self):
        self.kule = Kule(database="kule_test",
                         collections=["documents"])
        self.app = TestApp(self.kule.get_bottle_app())
        self.collection = self.kule.get_collection("documents")

    def test_empty_response(self):
        response = self.app.get("/documents")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json,
                         {'meta': {
                             'total_count': 0,
                             'limit': 20,
                             'offset': 0},
                          'objects': []})

    def test_get_list(self):
        self.collection.insert({"foo": "bar"})
        response = self.app.get("/documents")
        self.assertEqual(response.status_code, 200)
        objects = response.json.get("objects")
        meta = response.json.get("meta")
        self.assertEqual(1, len(objects))
        self.assertEqual(1, meta.get("total_count"))
        record = first(objects)
        self.assertEqual(record.get("foo"), "bar")

    def test_post_list(self):
        response = self.app.post("/documents", json.dumps({"foo": "bar"}),
                                 content_type="application/json")
        self.assertEqual(201, response.status_code)
        object_id = response.json.get("_id")
        query = {"_id": bson.ObjectId(object_id)}
        self.assertEqual(1, self.collection.find(query).count())
        record = self.collection.find_one(query)
        self.assertEqual(record.get("foo"), "bar")

    def tearDown(self):
        self.collection.remove()


unittest.main()