from Certmon import app
with app.test_client() as c:
    response = c.get('/')
    assert response.status_code == 200