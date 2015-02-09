import os, sys
from warnings import warn

class Empty_Thing(object): pass

def mock_input(filename):
  for segment in get_lines(filename):
    yield segment

def get_io_filename_tuples(p):

  def full_path(filename):
    return os.path.join(p, filename)

  old_path = os.getcwd()
  os.chdir(io_path)

  files = [f for f in os.listdir(os.curdir) if os.path.isfile(f)]
  triples = []
  for f in files:
    if f.startswith("input") and f.endswith(".txt"):
      suffix           = f[5:]
      exp_path, a_path = [text.format(suffix) for text in ("output{0}", "actual{0}")]
      if exp_path in files:
        triples.append((f, exp_path, a_path))
      else:
        warn("Output file {0} not found.".format(exp_path))

  os.chdir(old_path)
  return [(full_path(i), full_path(e), full_path(a)) for i, e, a in triples]

def get_lines(filename):
  lines = [line if not line.endswith("\n") else line[:-1] \
           for line in open(filename, 'r').readlines()]
  return lines

def match_lines(expected, actual):
  if len(expected) != len(actual):
    return False
  for exp_line, act_line in zip(expected, actual):
    if exp_line != act_line:
      return False
  return True

def print_io(data, test_index, total_tests):
  print "Test {0} of {1}.\n".format(test_index + 1, total_tests)
  for desc, lines in data:
    print "{0}:\n{1}\n".format(desc, str.join("\n", lines))

def run_one_test(script_path, input_path, output_path):
  os.environ["OUTPUT_PATH"] = output_path

  try:
    execfile(script_path, { "raw_input": mock_input(input_path).next })
  except Exception as e: 
    print "Error: {0}\n".format(e.message)

  del os.environ["OUTPUT_PATH"]

def run_tests(script_path, io_path, filenames=None):
  """Runs Python script at script_path once for each pair of files 
     'input###.txt' and 'output###.txt' in director io_path, and compares
     'output###.txt' to the contents of a temporary file created by the 
     script at path os.environ[OUTPUT_PATH]. A function that takes a directory
     path as its argument and returns a list of tuples (input_file_path,
      expected_output_file_path, available_temporary_file_path_for_script_output)
     can be supplied as a third argument to replace the default, which outputs
     tuples of the form ('test_dir/input002.txt', 'test_dir/output002.txt',
      'test_dir/actual002.txt')"""

  if filenames is None:
    filenames = get_io_filename_tuples

  filename_tuples = filenames(io_path)
  total           = len(filename_tuples)
  passed          = 0

  for index, (i, e, a) in enumerate(filename_tuples):
    run_one_test(script_path, i, a)
    in_lines, exp_lines, a_lines = (get_lines(f) for f in (i, e, a))
    try:
      os.remove(a)
    except:
      pass
    print_io([("Input", in_lines), 
              ("Expected output", exp_lines), 
              ("Actual output", a_lines)],
             index, total)
    if match_lines(exp_lines, a_lines):
      print "PASS\n"
      passed += 1
    else:
      print "FAIL\n"

  print "Passed {0} of {1} tests.".format(passed, total)


if __name__ == "__main__":

  if len(sys.argv) != 3:
    this_file = sys.argv[0]
    raise Exception("Usage: python {0} script_path test_dir").format(this_file)

  script_path = sys.argv[1]
  io_path     = sys.argv[2]

  run_tests(script_path, io_path)

