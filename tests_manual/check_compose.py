"""Check PostgreSQL persistence across API recreation, using one owned test record."""
import argparse
import os
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]


def run(project, report):
    if not os.getenv('CHECK_ACCESS_TOKEN'):
        raise RuntimeError('Define CHECK_ACCESS_TOKEN con un access JWT de administrador vigente.')
    compose = ['docker', 'compose', '-p', project]
    def invoke(*args):
        return subprocess.run(compose + (['exec', '-e', 'CHECK_ACCESS_TOKEN'] + list(args[1:]) if args[0] == 'exec' else list(args)), cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout

    record_id = None
    result = {'executed_at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'failed', 'database': 'PostgreSQL', 'driver': 'psycopg2'}
    try:
        record = json.loads(invoke('exec', '-T', 'api', 'python', '-c', """
import json, urllib.request, os
from infrastructure.database import engine
assert engine.dialect.name == 'postgresql' and engine.dialect.driver == 'psycopg2'
body={'nombre':'Persistencia Docker','tipo':'oficina','capacidad':13,'estado':'activo'}
request=urllib.request.Request('http://127.0.0.1:8000/espacios',
    data=json.dumps(body).encode(),headers={'Content-Type':'application/json', 'Authorization':'Bearer ' + os.environ['CHECK_ACCESS_TOKEN']})
with urllib.request.urlopen(request, timeout=10) as response:
    assert response.status == 201
    print(response.read().decode())
"""))
        record_id = str(UUID(record['id']))
        invoke('up', '--force-recreate', '--no-build', '--no-deps', '-d', '--wait', 'api')
        obtained = json.loads(invoke('exec', '-T', 'api', 'python', '-c', f"""
import json, urllib.request, os
request = urllib.request.Request('http://127.0.0.1:8000/espacios/{record_id}', headers={{'Authorization': 'Bearer ' + os.environ['CHECK_ACCESS_TOKEN']}})
with urllib.request.urlopen(request,timeout=10) as response:
    assert response.status == 200
    print(response.read().decode())
"""))
        assert obtained['id'] == record_id and obtained['capacidad'] == 13
        result.update(status='passed', compose_healthcheck='healthy',
                      volume_persistence_after_container_recreation='passed',
                      created_space_id=record_id, expected_capacity=13,
                      obtained_capacity=obtained['capacidad'])
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        try:
            if record_id:
                invoke('exec', '-T', 'api', 'python', '-c', f"""
import urllib.request, os
request=urllib.request.Request('http://127.0.0.1:8000/espacios/{record_id}',method='DELETE', headers={{'Authorization': 'Bearer ' + os.environ['CHECK_ACCESS_TOKEN']}})
with urllib.request.urlopen(request,timeout=10) as response:
    assert response.status == 204
""")
                result['cleanup_of_test_record'] = '204'
        except Exception:
            result['status'] = 'failed'
            result['cleanup_of_test_record'] = 'failed; remove only created_space_id after restoring API'
            raise
        finally:
            Path(report).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('PASS: PostgreSQL conserva el registro tras recrear la API; registro de prueba eliminado.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', default='sql')
    parser.add_argument('--report', default=str(ROOT/'tests_manual/compose_results.json'))
    args = parser.parse_args()
    run(args.project, args.report)
