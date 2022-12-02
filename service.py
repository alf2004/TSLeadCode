import os
import psycopg2
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import requests
import time
import base64
import random


CONFIG = {
    'database': {
        'name': os.environ.get('POSTGRES_DB'),
        'user': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'host': os.environ.get('POSTGRES_HOST'),
        'port': os.environ.get('POSTGRES_PORT')
    }
}

conn = psycopg2.connect(
    host=CONFIG['database']['host'],
    port=CONFIG['database']['port'],
    dbname=CONFIG['database']['name'],
    user=CONFIG['database']['user'],
    password=CONFIG['database']['password']
)

def send_postback(lead_id: int, click_id: str, key: str, lead_code: str, value: str):
    i = 0
    while i < 5:
        i += 1
        response = requests.get(f'https://tsyndicate.com/api/v1/cpa/action?key={key}&lead_code={lead_code}&click_id={click_id}&value={value}')
        with open("postback.txt", mode="a") as postback_file:
            content = f"{i} attempt send postback ID {lead_id}: {response.status_code}\n"
            postback_file.write(content)

        try:
            cur = conn.cursor()
            cur.execute("""
                update leads
                set postback_attempts = %s,
                    postback_last_status_code = %s,
                    postback_last_msg = %s,
                    postback_last_attempt_at = now()
                where id = %s
            """, (i, response.status_code, response.text, lead_id)
                        )
            conn.commit()
        except:
            conn.rollback()

        if response.status_code == 200:
            break
        else:
            time.sleep(5 ** i)


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/pb", response_class=JSONResponse)
    async def get_postback(
            background_tasks: BackgroundTasks,
            click_id: str = '',
            clickid: str = '',
            key: str = '',
            value: str = ''
    ):
        if not click_id:
            click_id = clickid

        if not click_id or not key or not (value and value != ''):
            raise HTTPException(status_code=400, detail='Unknown postback')

        lead_code = base64.urlsafe_b64encode(random.randbytes(18))

        lead_id = 0
        try:
            cur = conn.cursor()
            cur.execute(
                'insert into leads (click_id, lead_key, lead_code, lead_value) values (%s, %s, %s, %s) returning id',
                (click_id, key, lead_code, value)
            )
            lead_id = cur.fetchone()[0]
            conn.commit()
        except:
            conn.rollback()

        background_tasks.add_task(send_postback, lead_id, click_id, key, lead_code, value)
        return {
            'result': 'ok',
            'id': lead_id,
            'clickid': click_id,
            'key': key,
            'value': value,
            'leadcode': lead_code
        }

    return app
