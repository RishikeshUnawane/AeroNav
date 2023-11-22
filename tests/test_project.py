def test_signUp(client):
    response = client.get("/")
    assert b"<title> Registration Form </title>" in response.data