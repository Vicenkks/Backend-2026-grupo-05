"""Functional rubric checks against PostgreSQL through psycopg2.
Owns two disposable databases and a server; never touches the development database.
"""
from postgres_fixture import databases

import re
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
records = []
BASE = ''


def request(method, path, expected, body=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'})
    try:
        result = urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as error:
        result = error
    raw = result.read()
    data = json.loads(raw) if raw else None
    records.append({'method': method, 'path': path, 'input': body,
                    'expected': expected, 'obtained': result.status, 'response': data})
    assert result.status == expected, (method, path, expected, result.status, data)
    if expected >= 400:
        assert set(data) == {'error'} and set(data['error']) == {'code', 'message', 'details'}
        assert isinstance(data['error']['details'], list)
    return data


def run(report):
    global BASE
    with databases() as (database_url, rollback_url), tempfile.TemporaryDirectory(prefix='coworking-tests-') as tmp:
        env = dict(os.environ, DATABASE_URL=database_url)
        def command(*args):
            return subprocess.run([sys.executable, '-m', *args], cwd=ROOT,
                                  env=env, check=True, capture_output=True, text=True)
        command('alembic', 'upgrade', 'head')
        command('alembic', 'check')
        # Force a late seeding failure in a separate empty database and verify atomic rollback.
        rollback_env = dict(env, DATABASE_URL=rollback_url)
        subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'],
                       cwd=ROOT, env=rollback_env, check=True, capture_output=True)
        probe = """from app import main
from infrastructure.database import SessionLocal
from sqlalchemy import text
def fail(*args, **kwargs):
    raise RuntimeError('Injected seed failure')
main.seed_reservas = fail
try:
    main.cargar_datos_iniciales()
except RuntimeError:
    pass
else:
    raise AssertionError('Expected seed failure')
with SessionLocal() as session:
    for table in ['espacios', 'empresas', 'disponibilidades', 'reservas']:
        assert session.scalar(text('select count(*) from ' + table)) == 0
"""
        subprocess.run([sys.executable, '-c', probe], cwd=ROOT, env=rollback_env,
                       check=True, capture_output=True)
        command('infrastructure.seeders')
        command('infrastructure.seeders')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        BASE = f'http://127.0.0.1:{port}'
        log = open(Path(tmp)/'server.log', 'w+')
        process = None
        def start():
            proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app',
                '--host', '127.0.0.1', '--port', str(port)], cwd=ROOT, env=env,
                stdout=log, stderr=log)
            for _ in range(100):
                if proc.poll() is not None:
                    log.seek(0)
                    raise RuntimeError(log.read())
                try:
                    urllib.request.urlopen(BASE+'/espacios', timeout=.5).close()
                    return proc
                except (OSError, urllib.error.URLError):
                    time.sleep(.1)
            proc.terminate()
            proc.wait(timeout=10)
            raise RuntimeError('API did not become ready')
        try:
            process = start()
            schema = request('GET', '/openapi.json', 200)
            assert sum(len(v) for v in schema['paths'].values()) == 19
            for operations in schema['paths'].values():
                for operation in operations.values():
                    assert operation['summary'] and operation['description']
                    assert {'400','404','409','422'} <= operation['responses'].keys()
            for resource in ['espacios','empresas','disponibilidades','reservas']:
                page = request('GET', '/'+resource, 200)
                assert page['total'] >= 2 and len(page['items']) >= 2
            seed_counts = {r: request('GET', '/'+r, 200)['total'] for r in ['espacios','empresas','disponibilidades','reservas']}
            assert seed_counts['espacios'] == 5 and seed_counts['empresas'] == 3 and seed_counts['reservas'] == 2
            missing = str(uuid4())
            for resource in ['espacios','empresas','disponibilidades','reservas']:
                request('GET', '/'+resource+'/'+missing, 404)
            space_body = {'nombre': 'Prueba aislada', 'tipo':'oficina', 'capacidad':7, 'estado':'activo'}
            space = request('POST','/espacios',201,space_body)
            request('GET','/espacios/'+space['id'],200)
            space_body['capacidad'] = 9
            updated = request('PUT','/espacios/'+space['id'],200,space_body)
            assert updated['capacidad'] == 9
            for bad in [{'capacidad':0}, {'nombre':''}, {'estado':'desconocido'}, {'nombre':'x'*101}]:
                request('POST','/espacios',422,{**space_body, **bad})
            for query in ['limite=0','limite=101','pagina=0','direccion=otro','ordenar_por=sql']:
                request('GET','/espacios?'+query,422)
            page=request('GET','/espacios?tipo=oficina&ordenar_por=capacidad&direccion=desc&limite=1&pagina=1',200)
            page2=request('GET','/espacios?tipo=oficina&ordenar_por=capacidad&direccion=desc&limite=1&pagina=2',200)
            assert page['total'] == page['total_paginas'] and page['total'] >= 2
            assert page['items'][0]['tipo']=='oficina' and page['items'][0]['capacidad'] >= page2['items'][0]['capacidad']
            assert page['items'][0]['id'] != page2['items'][0]['id']
            empty=request('GET','/espacios?tipo=oficina&pagina=999&limite=1',200)
            assert empty['items']==[] and empty['total']==page['total']
            ascending=request('GET','/espacios?tipo=oficina&ordenar_por=capacidad&direccion=asc&limite=100',200)
            capacities=[item['capacidad'] for item in ascending['items']]
            assert capacities==sorted(capacities) and ascending['total']==len(capacities)
            company_body={'nombre' :'Prueba empresa','rut':'11111111-1','contacto':'test@example.test','activa':True}
            company=request('POST','/empresas',201,company_body)
            request('POST','/empresas',409,{**company_body,'rut':'11.111.111-1'})
            request('POST','/empresas',400,{**company_body,'rut':'11111111-2'})
            request('GET','/empresas/'+company['id'],200)
            company_body['nombre']='Empresa actualizada'
            assert request('PUT','/empresas/'+company['id'],200,company_body)['nombre']=='Empresa actualizada'
            date=(datetime.now(timezone.utc)+timedelta(days=7)).replace(hour=10,minute=0,second=0,microsecond=0)
            availability_body={'espacio_id':space['id'],'dia_semana':date.weekday(),'hora_apertura':'09:00:00','hora_cierre':'18:00:00','activa':True}
            request('POST','/disponibilidades',404,{**availability_body,'espacio_id':missing})
            request('POST','/disponibilidades',400,{**availability_body,'hora_cierre':'08:00:00'})
            availability=request('POST','/disponibilidades',201,availability_body)
            request('GET','/disponibilidades/'+availability['id'],200)
            request('PUT','/disponibilidades/'+availability['id'],200,availability_body)
            booking_body={'espacio_id':space['id'],'empresa_id':company['id'], 'fecha_inicio':date.isoformat(),'fecha_fin':(date+timedelta(hours=1)).isoformat()}
            request('POST','/reservas',400,{**booking_body,'fecha_fin':(date+timedelta(minutes=15)).isoformat()})
            request('POST','/reservas',422,{**booking_body,'fecha_inicio':date.replace(tzinfo=None).isoformat()})
            request('POST','/reservas',404,{**booking_body,'empresa_id':missing})
            inactive={**company_body,'activa':False}
            request('PUT','/empresas/'+company['id'],200,inactive)
            request('POST','/reservas',400,booking_body)
            request('PUT','/empresas/'+company['id'],200,company_body)
            request('POST','/reservas',400,{**booking_body,
                'fecha_inicio':date.replace(hour=7).isoformat(),
                'fecha_fin':date.replace(hour=8).isoformat()})
            request('PUT','/espacios/'+space['id'],200,{**space_body,'estado':'mantenimiento'})
            request('POST','/reservas',400,booking_body)
            request('PUT','/espacios/'+space['id'],200,space_body)
            booking=request('POST','/reservas',201,booking_body)
            assert booking['fecha_inicio'].endswith('Z')
            request('GET','/reservas/'+booking['id'],200)
            request('POST','/reservas',409,booking_body)
            date_from=date.isoformat().replace('+00:00','Z')
            date_to=(date+timedelta(hours=2)).isoformat().replace('+00:00','Z')
            filtered=request('GET',f'/reservas?empresa_id={company["id"]}&desde={date_from}&hasta={date_to}&limite=1',200)
            assert filtered['total']==1 and filtered['items'][0]['id']==booking['id']
            request('DELETE','/espacios/'+space['id'],409)
            request('DELETE','/empresas/'+company['id'],409)
            # A real process restart validates persistence and seed repeatability.
            process.terminate(); process.wait(timeout=10)
            process=start()
            persisted=request('GET','/espacios/'+space['id'],200)
            assert persisted['capacidad']==9
            assert request('GET','/reservas/'+booking['id'],200)['id']==booking['id']
            for resource in seed_counts:
                expected=seed_counts[resource]+1
                assert request('GET','/'+resource,200)['total']==expected
            cancelled=request('POST','/reservas/'+booking['id']+'/cancelar',200)
            assert cancelled['estado']=='cancelada'
            request('POST','/reservas/'+booking['id']+'/cancelar',409)
            request('POST','/reservas/'+missing+'/cancelar',404)
            request('DELETE','/disponibilidades/'+availability['id'],204)
            request('DELETE','/disponibilidades/'+availability['id'],404)
            # Clean test-only CRUD resources without references.
            disposable=request('POST','/espacios',201,space_body)
            request('DELETE','/espacios/'+disposable['id'],204)
            request('GET','/espacios/'+disposable['id'],404)
            disposable=request('POST','/empresas',201,{**company_body,'rut':'22222222-2'})
            request('DELETE','/empresas/'+disposable['id'],204)
            request('GET','/empresas/'+disposable['id'],404)
            # Verify successful execution of every documented method/path, not only count.
            covered=[]
            for path, operations in schema['paths'].items():
                pattern=re.sub(r'\{[^}]+\}', '[^/]+', path)
                for method in operations:
                    assert any(case['method'].lower()==method
                               and re.fullmatch(pattern,case['path'].split('?')[0])
                               and 200 <= case['obtained'] < 300 for case in records), (method,path)
                    covered.append(method.upper()+' '+path)
            command('alembic','check')
        finally:
            if process and process.poll() is None:
                process.terminate();process.wait(timeout=10)
            log.close()
    output={'executed_at_utc':datetime.now(timezone.utc).isoformat(), 'python':sys.version.split()[0], 'status':'passed','requests':len(records), 'successful_operations':covered,'migration':'passed','seeding_twice':'passed',
            'seed_failure_atomic_rollback':'passed', 'process_restart_persistence':'passed','database':'PostgreSQL; two uniquely named databases removed after checks', 'driver':'psycopg2','cases':records}
    Path(report).write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(f'PASS: {len(records)} HTTP checks; migrations, seed repeatability and process restart persistence. Evidence: {report}')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--report',default=str(ROOT/'tests_manual/results.json'))
    args=parser.parse_args()
    try:
        run(args.report)
    except Exception as error:
        Path(args.report).write_text(json.dumps({
            'status': 'failed', 'error': str(error), 'cases': records,
        }, ensure_ascii=False, indent=2) + '\n')
        raise
