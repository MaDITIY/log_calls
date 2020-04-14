import json
import pickle
import os
import yaml
import uuid

from datetime import datetime
from functools import wraps


def log_calls(format='JSON'):
  if format in ('JSON', 'YAML'):
    file_ext = format.lower()
  else:
    raise ValueError
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      log = {
        'timestamp': datetime.utcnow().isoformat(),
        'callable': getattr(func, '__name__', 'Unknown'),
        'args': [],
        'kwargs': {},
        'result': None,
      }
      result = func(*args, **kwargs)
      pkl_path = get_path_pkl()
      log_args(args, log, pkl_path)
      log_kwargs(kwargs, log, pkl_path)
      log_result(result, log, pkl_path)
      log_func_call(log, file_ext)
      return result
    return wrapper
  return decorator


def get_path_pkl():
  dir_path = os.path.abspath(os.path.join(os.getcwd(), 'pkl_files'))
  if not os.path.exists(dir_path):
    os.mkdir(dir_path)
  return dir_path


def log_args(args, log, path):
  for arg in args:
    pkl_file_name = str(uuid.uuid4())+'.pkl'
    with open(os.path.join(path, pkl_file_name), 'wb') as f:
      pickle.dump(arg, f)
    log['args'].append(pkl_file_name)


def log_kwargs(kwargs, log, path):
  for key, value in kwargs.items():
    pkl_file_name = str(uuid.uuid4())+'.pkl'
    with open(os.path.join(path, pkl_file_name), 'wb') as f:
      pickle.dump(value, f)
    log['kwargs'][key] = pkl_file_name


def log_result(result, log, path):
  pkl_file_name = str(uuid.uuid4())+'.pkl'
  with open(os.path.join(path, pkl_file_name), 'wb') as f:
    pickle.dump(result, f)
  log['result'] = pkl_file_name


def log_func_call(log, extension):
  file_path = os.path.abspath(os.path.join(os.getcwd(), 'app.log.'+extension))
  if extension == 'yaml':
    with open(file_path, 'a+') as f:
      text = yaml.dump(log)
      f.write(text)
  else:
    data = None
    if os.path.exists(file_path):
      with open(file_path, 'r') as f:
        data = json.load(f)
    if not data is None:
      data.append(log)
      text = json.dumps(data)
    else:
      text = json.dumps([log])
    with open(file_path, 'w') as f:
      f.write(text)


@log_calls(format='JSON')
def sum(a, b, d):
  return a + b + d


print(sum(1, 4, d=6))