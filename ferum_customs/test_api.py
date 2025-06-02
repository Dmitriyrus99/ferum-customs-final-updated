from frappe import test
from ferum_customs import api

def test_validate_service_request():
    """ Test validate_service_request method """
    doc = api.validate_service_request("test_docname")
    assert doc is not None
    assert doc.name == "test_docname"
