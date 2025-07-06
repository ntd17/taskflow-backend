import requests

BASE_URL = "http://backend:5000/api"

def register_user(username, email, password):
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.post(url, json=data)
    return response

def login_user(username, password):
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data)
    return response

def create_board(token, title):
    url = f"{BASE_URL}/boards"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title}
    response = requests.post(url, json=data, headers=headers)
    return response

def get_boards(token):
    url = f"{BASE_URL}/boards"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def update_board(token, board_id, title):
    url = f"{BASE_URL}/boards/{board_id}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title}
    response = requests.put(url, json=data, headers=headers)
    return response

def delete_board(token, board_id):
    url = f"{BASE_URL}/boards/{board_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    return response

def add_member(token, board_id, email):
    url = f"{BASE_URL}/boards/{board_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"email": email}
    response = requests.post(url, json=data, headers=headers)
    return response

def remove_member(token, board_id, user_id):
    url = f"{BASE_URL}/boards/{board_id}/members/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    return response

def create_list(token, board_id, title, position=None):
    url = f"{BASE_URL}/boards/{board_id}/lists"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title}
    if position is not None:
        data["position"] = position
    response = requests.post(url, json=data, headers=headers)
    return response

def get_lists(token, board_id):
    url = f"{BASE_URL}/boards/{board_id}/lists"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def update_list(token, list_id, title=None, position=None):
    url = f"{BASE_URL}/lists/{list_id}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {}
    if title is not None:
        data["title"] = title
    if position is not None:
        data["position"] = position
    response = requests.put(url, json=data, headers=headers)
    return response

def delete_list(token, list_id):
    url = f"{BASE_URL}/lists/{list_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    return response

def reorder_lists(token, orders):
    url = f"{BASE_URL}/lists/reorder"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"orders": orders}
    response = requests.post(url, json=data, headers=headers)
    return response

def create_card(token, list_id, title, description=None, position=None):
    url = f"{BASE_URL}/lists/{list_id}/cards"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title}
    if description is not None:
        data["description"] = description
    if position is not None:
        data["position"] = position
    response = requests.post(url, json=data, headers=headers)
    return response

def get_cards(token, list_id):
    url = f"{BASE_URL}/lists/{list_id}/cards"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def get_card(token, card_id):
    url = f"{BASE_URL}/cards/{card_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def update_card(token, card_id, title=None, description=None, list_id=None, position=None):
    url = f"{BASE_URL}/cards/{card_id}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {}
    if title is not None:
        data["title"] = title
    if description is not None:
        data["description"] = description
    if list_id is not None:
        data["list_id"] = list_id
    if position is not None:
        data["position"] = position
    response = requests.put(url, json=data, headers=headers)
    return response

def delete_card(token, card_id):
    url = f"{BASE_URL}/cards/{card_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    return response

def reorder_cards(token, orders):
    url = f"{BASE_URL}/cards/reorder"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"orders": orders}
    response = requests.post(url, json=data, headers=headers)
    return response

def reset_test_user(username):
    url = f"{BASE_URL}/auth/reset-test-user"
    data = {"username": username}
    try:
        response = requests.post(url, json=data)
        print("Reset Test User Response:", response.status_code, response.json())
    except Exception as e:
        print("Error during reset test user:", str(e))

def main():
    # Test user registration and login
    username = "testuser"
    email = "testuser@example.com"
    password = "testpassword"

    # Reset test user before registration
    reset_test_user(username)

    print("Registering user...")
    r = register_user(username, email, password)
    print(r.status_code, r.json())

    print("Logging in user...")
    r = login_user(username, password)
    print(r.status_code, r.json())
    if r.status_code != 200:
        print("Login failed, aborting tests.")
        return
    token = r.json()["access_token"]

    # Test board creation
    print("Creating board...")
    r = create_board(token, "Test Board")
    try:
        print(r.status_code, r.json())
    except Exception:
        print(r.status_code, r.text)
    if r.status_code != 201:
        print("Board creation failed, aborting tests.")
        return
    board_id = r.json()["id"]

    # Test get boards
    print("Getting boards...")
    r = get_boards(token)
    print(r.status_code, r.json())

    # Test update board
    print("Updating board...")
    r = update_board(token, board_id, "Updated Test Board")
    print(r.status_code, r.json())

    # Test add member (add self for simplicity)
    print("Adding member...")
    r = add_member(token, board_id, email)
    print(r.status_code, r.json())

    # Test remove member (remove self)
    user_id = r.json().get("members", [{}])[0].get("id", None)
    if user_id:
        print("Removing member...")
        r = remove_member(token, board_id, user_id)
        print(r.status_code, r.json())

    # Test create list
    print("Creating list...")
    r = create_list(token, board_id, "Test List")
    print(r.status_code, r.json())
    if r.status_code != 201:
        print("List creation failed, aborting tests.")
        return
    list_id = r.json()["id"]

    # Test get lists
    print("Getting lists...")
    r = get_lists(token, board_id)
    print(r.status_code, r.json())

    # Test update list
    print("Updating list...")
    r = update_list(token, list_id, title="Updated Test List")
    print(r.status_code, r.json())

    # Test reorder lists
    print("Reordering lists...")
    orders = [{"id": list_id, "position": 0}]
    r = reorder_lists(token, orders)
    print(r.status_code, r.json())

    # Test create card
    print("Creating card...")
    r = create_card(token, list_id, "Test Card", description="Card description")
    print(r.status_code, r.json())
    if r.status_code != 201:
        print("Card creation failed, aborting tests.")
        return
    card_id = r.json()["id"]

    # Test get cards
    print("Getting cards...")
    r = get_cards(token, list_id)
    print(r.status_code, r.json())

    # Test get card
    print("Getting card...")
    r = get_card(token, card_id)
    print(r.status_code, r.json())

    # Test update card
    print("Updating card...")
    r = update_card(token, card_id, title="Updated Test Card")
    print(r.status_code, r.json())

    # Test reorder cards
    print("Reordering cards...")
    orders = [{"id": card_id, "position": 0, "list_id": list_id}]
    r = reorder_cards(token, orders)
    print(r.status_code, r.json())

    # Test delete card
    print("Deleting card...")
    r = delete_card(token, card_id)
    print(r.status_code, r.json())

    # Test delete list
    print("Deleting list...")
    r = delete_list(token, list_id)
    print(r.status_code, r.json())

    # Test delete board
    print("Deleting board...")
    r = delete_board(token, board_id)
    print(r.status_code, r.json())

if __name__ == "__main__":
    main()
