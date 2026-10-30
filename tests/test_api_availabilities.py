def create_space(client):
    body = {
        "spaceName": "Sala Informatica",
        "type": "meeting_room",
        "capacity": 10,
        "description": "Sala con computadores",
    }
    return client.post("/spaces", json=body).json()["spaceId"]


def availability_body(space_id, weekday="monday", opening="09:00:00", closing="18:00:00"):
    return {
        "spaceId": space_id,
        "weekday": weekday,
        "opening_time": opening,
        "closing_time": closing,
    }


def create_availability(client):
    space_id = create_space(client)
    response = client.post("/availabilities", json=availability_body(space_id))
    return response.json()["availabilityId"]


# Crear


def test_create_availability_returns_201(client):
    space_id = create_space(client)

    response = client.post("/availabilities", json=availability_body(space_id))

    assert response.status_code == 201
    assert response.json()["weekday"] == "monday"
    assert response.json()["opening_time"] == "09:00:00"


def test_create_availability_closing_before_opening_returns_400(client):
    space_id = create_space(client)
    body = availability_body(space_id, opening="18:00:00", closing="09:00:00")

    response = client.post("/availabilities", json=body)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BUSINESS_RULE_VIOLATION"


def test_create_availability_space_not_found_returns_404(client):
    response = client.post("/availabilities", json=availability_body("id-que-no-existe"))

    assert response.status_code == 404


def test_create_availability_invalid_weekday_returns_422(client):
    space_id = create_space(client)

    response = client.post("/availabilities", json=availability_body(space_id, weekday="lunes"))

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# Obtener lista


def test_get_availability_found_returns_200(client):
    availability_id = create_availability(client)

    response = client.get(f"/availabilities/{availability_id}")

    assert response.status_code == 200
    assert response.json()["closing_time"] == "18:00:00"


def test_get_availability_not_found_returns_404(client):
    response = client.get("/availabilities/id-que-no-existe")

    assert response.status_code == 404


def test_list_availabilities_returns_all(client):
    create_availability(client)
    create_availability(client)

    response = client.get("/availabilities")

    assert response.status_code == 200
    assert len(response.json()) == 2


# Actualizar


def test_update_availability_changes_closing_time(client):
    availability_id = create_availability(client)

    response = client.put(f"/availabilities/{availability_id}", json={"closing_time": "20:00:00"})

    assert response.status_code == 200
    assert response.json()["closing_time"] == "20:00:00"


def test_update_availability_invalid_schedule_returns_400(client):
    availability_id = create_availability(client)

    response = client.put(f"/availabilities/{availability_id}", json={"opening_time": "19:00:00"})

    assert response.status_code == 400


def test_update_availability_not_found_returns_404(client):
    response = client.put("/availabilities/id-que-no-existe", json={"closing_time": "20:00:00"})

    assert response.status_code == 404


# Borrar


def test_delete_availability_returns_204(client):
    availability_id = create_availability(client)

    response = client.delete(f"/availabilities/{availability_id}")

    assert response.status_code == 204

    
    response = client.get(f"/availabilities/{availability_id}")

    assert response.status_code == 404


def test_delete_availability_not_found_returns_404(client):
    response = client.delete("/availabilities/id-que-no-existe")

    assert response.status_code == 404
