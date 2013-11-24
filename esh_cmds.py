import sys
import imp
import time
import os
import traceback

esh_jsutil = imp.load_source('esh_jsutil', os.environ['ESH_DIR'] + '/esh_jsutil.py')
#from esh_jsutil import JSIOError

LOW_INIT_LEVEL    = 0		#initial state, no init
IMPORT_INIT_LEVEL = 1		#ccs java packages have been imported
SCRIPT_INIT_LEVEL = 2		#scripting environment has been created
CCS_INIT_LEVEL    = 3		#if wanted, ccs gui is started
DEBSVR_INIT_LEVEL = 4		#debug server has been created
DEBSES_INIT_LEVEL = 5		#debug sessions have been created
HIGH_INIT_LEVEL   = 6		#targets have been connected

def cmd_help(jsproc, options, args):
  selfmodule = sys.modules[__name__]
  CMDS = [cmd_name.split('cmd_')[1] for cmd_name in dir(selfmodule) if cmd_name.startswith('cmd_')]
  print 'Known commands:', CMDS

  return 0

def cmd_ping(jsproc, options, args):
  print 'ping request received'
  print 'returning 0'

  return 0

def cmd_bye(jsproc, options, args):
  pass

  return 0

def cmd_options(jsproc, options, args):
  print options

  return 0

def cmd_prog(jsproc, options, args):
  if len(args) > 0:
    prog = args[0]
    prog = ensure_quoted(prog)
    print 'Setting program to', prog
    options.prog = prog
  else:
    prog = options.prog

  print 'program image:', prog

  return 0

def cmd_tcf(jsproc, options, args):
  print options.tcf

  return 0

def cmd_lscpu(jsproc, options, args):
  for cpu in options.debugSessions:
    print cpu, options.debugSessions[cpu]

  return 0

def cmd_load(jsproc, options, args):
  if not assert_init_level(HIGH_INIT_LEVEL, options):
    return -1

  if len(args) > 0:
    session_id = args[0]
  else:
    print 'ERROR: need a session_id to identify load target'
    return 1

  prog = options.prog

  print 'loading program to', session_id
  print 'program image:', prog

  r = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_load_program(session_id, prog))
  return r

def ensure_quoted(s):
  if (not s.startswith('"')) and (not s.endswith('"')):
    return '"' + s + '"'
  else:
    return s
  
def cmd_loadall(jsproc, options, args):
  if not assert_init_level(HIGH_INIT_LEVEL, options):
    return -1

  rs = []
  for session_id in options.debugSessions:
    print 'loading on debug session', session_id
    r = cmd_load(jsproc, options, [session_id])
    print 'retval=%d' % r
    rs.append(r)
  r = sum([abs(x) for x in rs])
  return r

def cmd_run(jsproc, options, args):
  if not assert_init_level(HIGH_INIT_LEVEL, options):
    return -1

  if len(args) > 0:
    session_id = args[0]
  else:
    print 'ERROR: need a session_id to identify run target'
    return 1

  r = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_run_target(session_id))
  return r

def cmd_runall(jsproc, options, args):
  if not assert_init_level(HIGH_INIT_LEVEL, options):
    return -1

  rs = []
  for session_id in options.debugSessions:
    print 'running debug session', session_id
    r = cmd_run(jsproc, options, [session_id])
    print 'retval=%d' % r
    rs.append(r)
  r = sum([abs(x) for x in rs])
  return r

def cmd_halt(jsproc, options, args):
  if not assert_init_level(HIGH_INIT_LEVEL, options):
    return -1

  if len(args) > 0:
    session_id = args[0]
  else:
    print 'ERROR: need a session_id to identify halt target'
    return 1

  esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_halt_target(session_id))
  return 0

def cmd_haltall(jsproc, options, args):
  if not assert_init_level(HIGH_INIT_LEVEL, options):
    return -1

  rs = []
  for session_id in options.debugSessions:
    print 'halting debug session', session_id
    r = cmd_halt(jsproc, options, [session_id])
    print 'retval=%d' % r
    rs.append(r)
  r = sum([abs(x) for x in rs])
  return r

def cmd_restart(jsproc, options, args):
  if not assert_init_level(HIGH_INIT_LEVEL, options):
    return -1

  if len(args) > 0:
    session_id = args[0]
  else:
    print 'ERROR: need a session_id to identify restart target'
    return 1

  esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_restart_target(session_id))
  return 0

def cmd_restartall(jsproc, options, args):
  if not assert_init_level(HIGH_INIT_LEVEL, options):
    return -1

  rs = []
  for session_id in options.debugSessions:
    print 'restarting debug session', session_id
    r = cmd_restart(jsproc, options, [session_id])
    print 'retval=%d' % r
    rs.append(r)
  r = sum([abs(x) for x in rs])
  return r

def cmd_reset(jsproc, options, args):
  if not assert_init_level(DEBSES_INIT_LEVEL, options):
    return -1

  if len(args) > 0:
    session_id = args[0]
  else:
    print 'ERROR: need a session_id to identify reset target'
    return 1

  esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_reset_target(session_id))
  return 0

def cmd_startccs(jsproc, options, args):
  if not assert_init_level(SCRIPT_INIT_LEVEL, options):
    return -1

  print 'Starting CCS'
  r = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_start_ccs())
  print
  #wait = 20
  #print 'Waiting %d secs to let CCS start...' % wait
  #time.sleep(wait)

  return r

def cmd_stopccs(jsproc, options, args):
  print 'Stopping CCS'
  r = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_stop_ccs())
  time.sleep(10)

  return r


def cmd_evminitlevel(jsproc, options, args):
  print 'EVM initlevel = %d' % options.init

  return 0

def cmd_evminit(jsproc, options, args):
  print 'Initiating evm init'

  init = options.init
  selfmodule = sys.modules[__name__]


  if len(args) > 0:
    last_init_level = min(int(args[0]), HIGH_INIT_LEVEL)
  else:
    last_init_level = HIGH_INIT_LEVEL

  if init < LOW_INIT_LEVEL or init > HIGH_INIT_LEVEL:
    return -1

  while init < last_init_level:
    init_func_name = 'evminit%d' % (init + 1)
    init_func = getattr(selfmodule, init_func_name)
    r = init_func(jsproc, options, args)
    if r == 0:
      init += 1
      options.init = init
    else:
      print 'Encountered error in %s' % init_func_name
      return r

  print 'Finished evm init'

  return 0

#init1
def evminit1(jsproc, options, args):
  print 'evminit1: Importing packages'
  r0 = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_import_packages())
  return r0

#init2
def evminit2(jsproc, options, args):
  print 'evminit2: Creating scripting environment'
  r1 = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_create_scripting_env())

  return r1

def evminit3(jsproc, options, args):
  r = 0
  if ((not options.cleanup) and options.gui):
    print 'evminit3: Starting ccs'
    r = cmd_startccs(jsproc, options, args)

  return r

#init4
def evminit4(jsproc, options, args):
  print 'evminit4: Starting debug server'
  r2 = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_start_debugger(options.tcf))
  time.sleep(10)

  return r2

#init5
def evminit5(jsproc, options, args):
  print 'evminit5: Starting debug sessions'
  r3 = []
  for session_id in options.debugSessions:
    target_name = options.debugSessions[session_id]
    r = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_start_debug_session(session_id, target_name))
    r3.append(r)
    time.sleep(12)

  return sum([abs(r) for r in r3])
    
#init6
def evminit6(jsproc, options, args):
  print 'evminit6: Connecting debug sessions'
  r4 = []
  for session_id in options.debugSessions:
    r = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_connect_debug_session(session_id))
    r4.append(r)
    time.sleep(12)

  return sum([abs(r) for r in r4])

def cmd_evmreset(jsproc, options, args):
  print 'EVM reset'
  options.init = -1

  return 0

def cmd_evmshutdown(jsproc, options, args):
  print 'Initiating evm shutdown'

  init = options.init
  selfmodule = sys.modules[__name__]

  if len(args) > 0:
    last_init_level = max(int(args[0]), LOW_INIT_LEVEL)
  else:
    last_init_level = LOW_INIT_LEVEL

  force_shutdown = False
  if len(args) > 1:
    if args[1] == 'force':
      force_shutdown = True

  if init < LOW_INIT_LEVEL or init > HIGH_INIT_LEVEL:
    return -1

  while init > last_init_level:
    shut_func_name = 'evmshutdown%d' % (init)
    shut_func = getattr(selfmodule, shut_func_name)
    r = shut_func(jsproc, options, args)
    if r == 0:
      init -= 1
      options.init = init
    else:
      print 'Encountered error in %s' % shut_func_name
      if force_shutdown:
        print 'Forcing to lower init level and continuing shutdown...'
	init -= 1
	options.init = init
      else:
	return r

  print 'Finished evm shutdown'

  return 0

def evmshutdown6(jsproc, options, args):
  print 'NOP'
  
  return 0

def evmshutdown5(jsproc, options, args):
  print 'Stopping debug sessions'
  r3 = []
  for session_id in options.debugSessions:
    r = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_terminate_debug_session(session_id))
    r3.append(r)
    time.sleep(4)

  return sum([abs(r) for r in r3])


def evmshutdown4(jsproc, options, args):
  print 'Stopping debug server'
  r2 = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_stop_debug_server())
  time.sleep(5)

  return r2

def evmshutdown3(jsproc, options, args):
  r = 0
  if ((not options.cleanup) and options.gui):
    print 'Stopping ccs'
    r = cmd_stopccs(jsproc, options, args)

  return r

def evmshutdown2(jsproc, options, args):
  print 'Stopping scripting environment'
  r1 = esh_jsutil.exec_jscmd(jsproc, esh_jsutil.code_stop_scripting_env())
  time.sleep(5)

  return r1

def evmshutdown1(jsproc, options, args):
  print 'NOP'

  return 0

def cmd_cleanup(jsproc, options, args):
  print 'cleanup sequence...'

  print 'force shutdown...'
  cmd_evmshutdown(jsproc, options, [0,'force'])

  print 'evminit to init level 3...'
  cmd_evminit(jsproc, options, [3])

  print 'shutdown...'
  cmd_evmshutdown(jsproc, options, [])

  print 'end of cleanup sequence...'

  return 0

def assert_init_level(init_level, options):
  if (options.init < init_level):
    print 'Init level too low'
    return False

  return True

def main():
  cmd_help()

if __name__ == "__main__":
  main()
