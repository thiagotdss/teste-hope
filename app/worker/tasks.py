from app.worker.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.consulta import Consulta, ConsultaStatus
from app.core.logging import logger
from app.core.config import settings
import requests
import time

@celery_app.task
def processar_consulta(consulta_id: str):
    db = SessionLocal()

    try:
        consulta = db.query(Consulta).filter(
            Consulta.id == consulta_id
        ).first()

        logger.info(
            "Processando consulta no worker - consulta_id=%s",
            consulta.id,
        )

        if not consulta:
            logger.error(
                "Consulta não encontrada - consulta_id=%s",
                consulta_id,
            )
            return

        consulta.status = ConsultaStatus.PROCESSING
        db.commit()

        max_tentativas = 3

        for tentativa in range(max_tentativas):
            consulta.tentativas += 1
            db.commit()

            logger.info(
                "Tentativa de integração - consulta_id=%s | tentativa=%s",
                consulta_id,
                consulta.tentativas,
            )

            try:
                resposta = requests.post(
                    f"{settings.url_fake_api}/fake/customer?cenario=erro",
                    timeout=10,
                    json={
                        "documento": consulta.documento,
                        "tipo": consulta.tipo,
                    },
                )

                resposta.raise_for_status()

                consulta.resultado = resposta.json()
                consulta.status = ConsultaStatus.SUCCESS
                db.commit()

                logger.info(
                    "Consulta processada com sucesso - consulta_id=%s",
                    consulta_id,
                )

                return

            except (
                requests.exceptions.HTTPError,
                requests.exceptions.Timeout,
            ) as exc:
                consulta.ultimo_erro = str(exc)

                if isinstance(exc, requests.exceptions.HTTPError):
                    if resposta.status_code not in (500, 503):
                        consulta.status = ConsultaStatus.ERROR
                        consulta.ultimo_erro = str(exc)
                        db.commit()
                        return

                if tentativa == max_tentativas - 1:
                    consulta.status = ConsultaStatus.ERROR
                    db.commit()

                    logger.error(
                        "Consulta encerrada após máximo de tentativas "
                        "- consulta_id=%s | tentativas=%s | erro=%s",
                        consulta_id,
                        consulta.tentativas,
                        exc,
                    )

                    return

                tempo_espera = 2 ** (tentativa + 1)

                logger.warning(
                    "Erro temporário na integração - consulta_id=%s "
                    "| tentativa=%s | retry_em=%ss",
                    consulta_id,
                    consulta.tentativas,
                    tempo_espera,
                )

                time.sleep(tempo_espera)

    finally:
        db.close()