def create_space(client, name="Sala Norte", type="meeting_room", capacity=10):
    body = {
        "spaceName": name,
        "type": type,
        "capacity": capacity,
        "description": "Sala con proyector",
    }
    response = client.post("/spaces", json=body)
    return response.json()["spaceId"]


def test_health_check(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_space_returns_201(client):
    body = {
        "spaceName": "Sala Norte",
        "type": "meeting_room",
        "capacity": 10,
        "description": "Sala con proyector",
    }

    response = client.post("/spaces", json=body)

    assert response.status_code == 201
    assert response.json()["spaceName"] == "Sala Norte"


def test_create_space_invalid_capacity_returns_422(client):
    body = {
        "spaceName": "Sala Norte",
        "type": "meeting_room",
        "capacity": 0,  
        "description": "Sala con proyector",
    }

    response = client.post("/spaces", json=body)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# Obtener


def test_get_space_found_returns_200(client):
    space_id = create_space(client)

    response = client.get(f"/spaces/{space_id}")

    assert response.status_code == 200
    assert response.json()["spaceName"] == "Sala Norte"


def test_get_space_not_found_returns_404(client):
    response = client.get("/spaces/id-que-no-existe")

    assert response.status_code == 404


# Actualizar


def test_update_space_changes_capacity(client):
    space_id = create_space(client)

    response = client.put(f"/spaces/{space_id}", json={"capacity": 15})

    assert response.status_code == 200
    assert response.json()["capacity"] == 15


def test_update_space_not_found_returns_404(client):
    response = client.put("/spaces/id-que-no-existe", json={"capacity": 15})

    assert response.status_code == 404


def test_update_space_invalid_capacity_returns_422(client):
    space_id = create_space(client)

    response = client.put(f"/spaces/{space_id}", json={"capacity": 0})

    assert response.status_code == 422


# Borrar


def test_delete_space_returns_204(client):
    space_id = create_space(client)

    response = client.delete(f"/spaces/{space_id}")

    assert response.status_code == 204

    # después de borrarlo, ya no debe existir
    response = client.get(f"/spaces/{space_id}")

    assert response.status_code == 404


def test_delete_space_not_found_returns_404(client):
    response = client.delete("/spaces/id-que-no-existe")

    assert response.status_code == 404


def test_delete_space_with_reservations_returns_409(client):
    space_id = create_space(client)
    company = {
        "companyName": "Acme Ltda",
        "rut": "12345678-9",
        "email": "contacto@acme.cl",
        "phone": "+56912345678",
        "address": "Av. Siempre Viva 123",
    }
    company_id = client.post("/companies", json=company).json()["companyId"]
    reservation = {
        "spaceId": space_id,
        "companyId": company_id,
        "start_date": "2026-09-20T10:00:00",
        "end_date": "2026-09-20T11:00:00",
        "reason": "Reunión de equipo",
    }
    client.post("/reservations", json=reservation)

    response = client.delete(f"/spaces/{space_id}")

    assert response.status_code == 409


# Listado


def test_list_spaces_returns_items_and_total(client):
    create_space(client, name="Sala A")
    create_space(client, name="Sala B")

    response = client.get("/spaces")

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 2


def test_list_spaces_filter_by_type(client):
    create_space(client, name="Sala A", type="meeting_room")
    create_space(client, name="Oficina B", type="office")

    response = client.get("/spaces?type=office")

    assert response.json()["total"] == 1
    assert response.json()["items"][0]["spaceName"] == "Oficina B"


def test_list_spaces_filter_by_min_capacity(client):
    create_space(client, name="Chica", capacity=2)
    create_space(client, name="Grande", capacity=20)

    response = client.get("/spaces?min_capacity=10")

    assert response.json()["total"] == 1
    assert response.json()["items"][0]["spaceName"] == "Grande"


def test_list_spaces_sorted_by_capacity_ascending(client):
    create_space(client, name="Grande", capacity=20)
    create_space(client, name="Chica", capacity=2)

    response = client.get("/spaces?sort_by=capacity&direction=asc")

    names = [item["spaceName"] for item in response.json()["items"]]
    assert names == ["Chica", "Grande"]


def test_list_spaces_pagination(client):
    create_space(client, name="Sala A")
    create_space(client, name="Sala B")
    create_space(client, name="Sala C")

    response = client.get("/spaces?page=1&limit=2")

    assert len(response.json()["items"]) == 2
    assert response.json()["total"] == 3
    assert response.json()["total_pages"] == 2


def test_list_spaces_invalid_sort_field_returns_422(client):
    response = client.get("/spaces?sort_by=campo_que_no_existe")

    assert response.status_code == 422


def test_list_spaces_invalid_page_returns_422(client):
    response = client.get("/spaces?page=0")

    assert response.status_code == 422
