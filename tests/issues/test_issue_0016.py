from codice_fiscale import codice_fiscale


def test_issue_0016():
    """
    Decode return GIRGENTI (soppresso) instead of AGRIGENTO
    """
    data = codice_fiscale.decode("LNNFNC80A01A089K")
    expected_birthplace = {
        "code": "A089",
        "province": "AG",
        "name": "AGRIGENTO",
    }
    birthplace = data["birthplace"]
    assert birthplace["code"] == expected_birthplace["code"]
    assert birthplace["name"].upper() == expected_birthplace["name"]
    assert birthplace["province"] == expected_birthplace["province"]
