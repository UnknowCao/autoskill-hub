"""Diagnostic: check DOORS COM connectivity."""
import sys, struct

print(f"Python {sys.version}")
print(f"Python bitness: {struct.calcsize('P')*8}-bit")
print(f"Python executable: {sys.executable}")
print()

try:
    import win32com.client, pythoncom
except ImportError:
    print("ERROR: pywin32 not installed")
    sys.exit(1)

# 1. Try GetActiveObject with known ProgIDs
progids = ['DOORS.Application', 'DOORS.application', 'Telelogic.DOORS']
for pid in progids:
    try:
        obj = win32com.client.GetActiveObject(pid)
        print(f"GetActiveObject('{pid}'): SUCCESS -> {obj}")
    except Exception as e:
        print(f"GetActiveObject('{pid}'): FAIL -> {type(e).__name__}: {e}")

print()

# 2. Try Dispatch (creates or connects)
for pid in ['DOORS.Application']:
    try:
        obj = win32com.client.Dispatch(pid)
        print(f"Dispatch('{pid}'): SUCCESS -> {obj}")
        # Try a simple call
        try:
            r = obj.runStr('print "DOORS COM OK"')
            print(f"  runStr test: '{r}'")
        except Exception as e2:
            print(f"  runStr test FAIL: {e2}")
    except Exception as e:
        print(f"Dispatch('{pid}'): FAIL -> {type(e).__name__}: {e}")

print()

# 3. Scan Running Object Table
print("--- Running Object Table (ROT) ---")
try:
    ctx = pythoncom.CreateBindCtx(0)
    rot = pythoncom.GetRunningObjectTable()
    count = 0
    for mk in rot.EnumRunning():
        try:
            name = mk.GetDisplayName(ctx, None)
            if 'door' in name.lower() or 'ibm' in name.lower() or 'rational' in name.lower():
                print(f"  [MATCH] {name}")
            count += 1
        except:
            count += 1
    print(f"  Total ROT entries scanned: {count}")
except Exception as e:
    print(f"  ROT scan error: {e}")

print()

# 4. Check DOORS process
import subprocess
result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq doors.exe', '/FO', 'CSV', '/NH'],
                       capture_output=True, text=True)
if 'doors.exe' in result.stdout.lower():
    for line in result.stdout.strip().split('\n'):
        print(f"  Process: {line}")
else:
    print("  No doors.exe process found!")
