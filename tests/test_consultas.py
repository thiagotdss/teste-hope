from unittest.mock import Mock, patch

from app.db.database import SessionLocal
from app.models.consulta import Consulta, ConsultaStatus
from app.worker.tasks import processar_consulta
import requests

#Valida se criou e marcou status pendente no registro da consulta
def test_criar_consulta(client):
    with patch("app.services.consulta.processar_consulta.delay") as mock_delay:
        response = client.post(
            "/api/v1/consultas",
            json={
                "documento": "12345678901",
                "tipo": "CPF",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["status"] == "PENDING"

    mock_delay.assert_called_once()

#Validação de payload inválido
def test_criar_consulta_payload_invalido(client):
    response = client.post(
        "/api/v1/consultas",
        json={
            "documento": "abc",
            "tipo": "CPF",
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"]["code"] == "INVALID_DOCUMENT"

#Procurando um registro que nao existe
def test_consulta_inexistente(client):
    response = client.get(
        "/api/v1/consultas/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404

#Moca a resposta da API fake e testa processamento do worker.
def test_processamento_sucesso():
    db = SessionLocal()
    consulta = Consulta(
        documento="12345678901",
        tipo="CPF",
    )
    db.add(consulta)
    db.commit()
    db.refresh(consulta)

    resposta_mock = Mock()
    resposta_mock.status_code = 200
    resposta_mock.json.return_value = {
        "nome": "Cliente Teste",
        "score": 742,
        "situacao": "REGULAR",
    }

    with patch(
        "app.worker.tasks.requests.post",
        return_value=resposta_mock,
    ):
        processar_consulta.run(str(consulta.id))

    db.refresh(consulta)

    assert consulta.status == ConsultaStatus.SUCCESS
    assert consulta.tentativas == 1
    assert consulta.resultado["score"] == 742

    db.delete(consulta)
    db.commit()
    db.close()


#Moca a resposta da API fake para 503 e testa processamento do worker.
def test_processamento_falha_api():
    db = SessionLocal()

    consulta = Consulta(
        documento="12345678901",
        tipo="CPF",
    )

    db.add(consulta)
    db.commit()
    db.refresh(consulta)

    resposta_mock = Mock()
    resposta_mock.status_code = 503

    erro = requests.exceptions.HTTPError("503 Service Unavailable")
    resposta_mock.raise_for_status.side_effect = erro

    with patch(
        "app.worker.tasks.requests.post",
        return_value=resposta_mock,
    ), patch(
        "app.worker.tasks.time.sleep",
    ):
        processar_consulta.run(str(consulta.id))

    db.refresh(consulta)

    assert consulta.status == ConsultaStatus.ERROR
    assert consulta.tentativas == 3
    assert consulta.ultimo_erro is not None

    db.delete(consulta)
    db.commit()
    db.close()