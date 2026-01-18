def test_register_user(client):
    response = client.post(
        "/users/",  
        json={"email": "test@example.com", "username": "testuser", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login_user(client):
    # register user first
    client.post(
        "/users/",
        json={"email": "login@example.com", "username": "loginuser", "password": "password123"}
    )
    
    response = client.post(
        "/auth/login", 
        data={"username": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()