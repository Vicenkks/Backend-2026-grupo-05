def create_company(client, name="compania generica", rut="12345678-9", email="contacto@gmail.cl"):
    body = {
        "companyName": name,
        "rut": rut,
        "email": email,
        "phone": "+56912345678",
        "address": "calle 123",
    }
    response = client.post("/companies", json=body)
    return response.json()["companyId"]


# Crear


def test_create_company_returns_201(client):
    body = {
        "companyName": "compania generica",
        "rut": "12345678-9",
        "email": "contacto@gmail.cl",
        "phone": "+56912345678",
        "address": "calle 123",
    }

    response = client.post("/companies", json=body)

    assert response.status_code == 201
    assert response.json()["companyName"] == "compania generica"
    assert response.json()["rut"] == "12345678-9"


def test_create_company_rut_without_hyphen_returns_422(client):
    body = {
        "companyName": "compania generica",
        "rut": "123456789", 
        "email": "contacto@gmail.cl",
        "phone": "+56912345678",
        "address": "calle 123",
    }

    response = client.post("/companies", json=body)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_company_invalid_email_returns_422(client):
    body = {
        "companyName": "compania generica",
        "rut": "12345678-9",
        "email": "correo-invalido",
        "phone": "+56912345678",
        "address": "calle 123",
    }

    response = client.post("/companies", json=body)

    assert response.status_code == 422


def test_create_company_name_too_short_returns_422(client):
    body = {
        "companyName": "co",  
        "rut": "12345678-9",
        "email": "contacto@acme.cl",
        "phone": "+56912345678",
        "address": "calle 123",
    }

    response = client.post("/companies", json=body)

    assert response.status_code == 422


#Obtener


def test_get_company_found_returns_200(client):
    company_id = create_company(client)

    response = client.get(f"/companies/{company_id}")

    assert response.status_code == 200
    assert response.json()["companyName"] == "compania generica"


def test_get_company_not_found_returns_404(client):
    response = client.get("/companies/id-que-no-existe")

    assert response.status_code == 404


# Actualizar


def test_update_company_changes_phone(client):
    company_id = create_company(client)

    response = client.put(f"/companies/{company_id}", json={"phone": "+56900000000"})

    assert response.status_code == 200
    assert response.json()["phone"] == "+56900000000"


def test_update_company_not_found_returns_404(client):
    response = client.put("/companies/id-que-no-existe", json={"phone": "+56900000000"})

    assert response.status_code == 404


def test_update_company_invalid_email_returns_422(client):
    company_id = create_company(client)

    response = client.put(f"/companies/{company_id}", json={"email": "correo-invalido"})

    assert response.status_code == 422


# Borrar


def test_delete_company_returns_204(client):
    company_id = create_company(client)

    response = client.delete(f"/companies/{company_id}")

    assert response.status_code == 204

    
    response = client.get(f"/companies/{company_id}")

    assert response.status_code == 404


def test_delete_company_not_found_returns_404(client):
    response = client.delete("/companies/id-que-no-existe")

    assert response.status_code == 404


def test_delete_company_with_reservations_returns_409(client):
    company_id = create_company(client)
    space = {
        "spaceName": "Sala Norte",
        "type": "meeting_room",
        "capacity": 10,
        "description": "Sala con proyector",
    }
    space_id = client.post("/spaces", json=space).json()["spaceId"]
    reservation = {
        "spaceId": space_id,
        "companyId": company_id,
        "start_date": "2026-09-20T10:00:00",
        "end_date": "2026-09-20T11:00:00",
        "reason": "Reunión de equipo",
    }
    client.post("/reservations", json=reservation)

    response = client.delete(f"/companies/{company_id}")

    assert response.status_code == 409


# Listado


def test_list_companies_returns_items_and_total(client):
    create_company(client, name="compania generica A", rut="11111111-1", email="a@correo.cl")
    create_company(client, name="compania generica B", rut="22222222-2", email="b@correo.cl")

    response = client.get("/companies")

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 2


def test_list_companies_sorted_by_name_ascending(client):
    create_company(client, name="Zeta Ltda", rut="11111111-1", email="z@correo.cl")
    create_company(client, name="Alfa Ltda", rut="22222222-2", email="a@correo.cl")

    response = client.get("/companies?sort_by=companyName&direction=asc")

    names = [item["companyName"] for item in response.json()["items"]]
    assert names == ["Alfa Ltda", "Zeta Ltda"]


def test_list_companies_pagination(client):
    create_company(client, name="Empresa A", rut="11111111-1", email="a@correo.cl")
    create_company(client, name="Empresa B", rut="22222222-2", email="b@correo.cl")
    create_company(client, name="Empresa C", rut="33333333-3", email="c@correo.cl")

    response = client.get("/companies?page=1&limit=2")

    assert len(response.json()["items"]) == 2
    assert response.json()["total"] == 3
    assert response.json()["total_pages"] == 2


def test_list_companies_invalid_sort_field_returns_422(client):
    response = client.get("/companies?sort_by=campo_que_no_existe")

    assert response.status_code == 422
