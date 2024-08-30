import sys

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


from waivek.color import Code
# from .ic import ic, ib
from waivek.timer import Timer
from waivek.ic import ic

from contextlib import contextmanager

def get_args(frame, summary):
    import inspect # builtin
    if summary.name in [ "<module>", "<listcomp>" ]:
        # Line is not inside a function
        return []
    if summary.name in frame.f_globals.keys():
        # Line is inside a GLOBAL function
        return inspect.getfullargspec(frame.f_globals[summary.name]).args
    # Line is inside a LOCAL function of a class
    import gc # builtin
    # https://stackoverflow.com/a/52762678
    function_object = [obj for obj in gc.get_referrers(frame.f_code) if hasattr(obj, '__code__') and obj.__code__ is frame.f_code][0]

    return inspect.getfullargspec(function_object).args

class Frame:
    def __init__(self, frame, summary):
        from os.path import basename
        keys = get_args(frame, summary)
        self.signature = "(" + ", ".join(keys) + ")"
        self.method = summary.name
        self.locals = frame.f_locals 
        self.line_number = str(summary.lineno)
        self.path = basename(summary.filename)

    def pretty(self):
        from waivek.ic import Table
        header = "\n".join([ self.path+":"+self.line_number, self.method + self.signature ])

        rows = [ (k, v) for k, v in self.locals.items() ]
        table = Table()
        for row in rows:
            table.row(row)

        import textwrap # built-in
        if table.table:
            table_string = "\n".join(str(table).split("\n")[1:])
        else:
            table_string = "    (empty table)"
        table_string = textwrap.dedent(table_string)
        table_string = textwrap.indent(table_string, "    ")
        # print(header + "\n" + table_string)
        print(header)
        print_variables(self.locals)

    def __repr__(self):
        repr_string = f"Frame(method={self.method}, locals={self.locals})"
        return repr_string

    def __getitem__(self, key):
        return self.locals[key]
    def __str__(self):
        return repr(self)


class Frames:
    def __init__(self, error):
        import traceback
        tb = error.__traceback__
        frames = [ frame for frame, _ in traceback.walk_tb(tb) ]
        summaries = traceback.extract_tb(tb)
        pairs = list(reversed(list(zip(frames, summaries))))
        self.frames = []
        for frame, summary in pairs:

            frm = Frame(frame, summary)
            self.frames.append(frm)
        # self.frames = [ Frame(frame, summary) for frame, summary in pairs ]

    def __getitem__(self, index):
        return self.frames[index]

    def __str__(self):
        return str(self.frames)

    def __repr__(self):
        return str(self.frames)

    def pretty(self):
        from waivek.ic import Table
        from waivek.common import truncate
        dictionaries = [ ( "i", "method", "local_count", "locals" ) ]
        dictionaries = dictionaries + [ ( i, D.method, D.local_count, truncate(str(D.locals), 120) ) for i, D in enumerate(self.frames) ]
        table = Table()
        for row in dictionaries:
            table.row(row)

    def print_stack(self):
        print()
        for frame in self.frames:
            frame.pretty()

def color_D_if_big(D):
    if len(str(D)) < 120:
        return str(D)
    else:
        colored_items = []
        for i, (k, v) in enumerate(D.items()):
            code = Code.CYAN if i % 2 == 0 else Code.LIGHTCYAN_EX
            # code = "[cyan]" if i % 2 == 0 else "[blue]"
            colored_items.append(code + f"{repr(k)}: {repr(v)}")
        return "{" + ", ".join(colored_items) + "}"

def print_variables_by_frame(error):
    import traceback
    from os.path import basename
    import os
    import textwrap
    import types
    from waivek.ic import Table

    tb = error.__traceback__
    frames = [ frame for frame, _ in traceback.walk_tb(tb) ]
    summaries = traceback.extract_tb(tb)
    pairs = list(reversed(list(zip(frames, summaries))))
    exclude_types = [types.FunctionType, types.ModuleType, types.BuiltinFunctionType, type]
    tuples = []
    table = Table()

    method_lines = []
    for frame, summary in pairs:
        keys = get_args(frame, summary)
        signature = "(" + ", ".join(keys) + ")"
        method = summary.name
        method_line = method + signature if summary.name != "<module>" else "<module>"
        method_lines.append(method_line)
    METHOD_LINE_LENGTH_LIMIT = 60
    variable_line_width = os.get_terminal_size()[0] - 2*len(table.gutter) - len(table.separator) - min(max(len(method_line) for method_line in method_lines), METHOD_LINE_LENGTH_LIMIT)
    for frame, summary in pairs:
        keys = get_args(frame, summary)
        signature = "(" + ", ".join(keys) + ")"
        method = summary.name
        local_D = frame.f_locals 
        method_line = method + signature if summary.name != "<module>" else "<module>"
        path_line = basename(summary.filename) + ":" + str(summary.lineno)
        variable_D = { k:v for k, v in local_D.items() 
                if type(v) not in exclude_types and k[0:2] != "__" and str(v)[0] != "<"  and not isinstance(v, Exception) }
        variable_lines = textwrap.wrap(color_D_if_big(variable_D), variable_line_width)
        variable_line = "\n".join(variable_lines)
        # print(method_line)
        # print(path_line)
        method_line_wrapped = "\n".join(textwrap.wrap(method_line, METHOD_LINE_LENGTH_LIMIT))
        table.row([method_line_wrapped, variable_line])
    table_string = textwrap.indent(textwrap.dedent("\n".join(str(table).split("\n")[1:])), '    ')
    print(Code.LIGHTCYAN_EX + 'Variables by frame')
    print(table_string)

def color_error_repr_old(error):
    string = repr(error)
    lhs, rhs = string.split("'", 1)
    rhs = "'" + rhs[:-1]
    lhs = Code.LIGHTRED_EX + lhs 
    rhs = (Code.YELLOW + rhs) + (Code.LIGHTRED_EX + ')')
    colored_string = lhs + rhs
    return colored_string

def color_error_regex(error):
    string = repr(error)
    import re
    m = re.match(r"""(\w+\(["'])(.*)(["']\))""", string)
    if m is None:
        return string
    
    lhs = Code.LIGHTRED_EX + m.group(1) 
    middle =  Code.YELLOW + m.group(2) 
    # middle = re.sub(r"('\w+')", Code.LIGHTCYAN_EX + r'\1', middle)
    rhs = Code.LIGHTRED_EX + m.group(3)
    colored_string = lhs + middle + rhs
    return colored_string

def color_arg(arg):
    BLACK           = '\x1b[30m'
    RED             = '\x1b[31m'
    GREEN           = '\x1b[32m'
    YELLOW          = '\x1b[33m'
    BLUE            = '\x1b[34m'
    MAGENTA         = '\x1b[35m'
    CYAN            = '\x1b[36m'
    WHITE           = '\x1b[37m'
    LIGHTBLACK_EX   = '\x1b[90m'
    LIGHTRED_EX     = '\x1b[91m'
    LIGHTGREEN_EX   = '\x1b[92m'
    LIGHTYELLOW_EX  = '\x1b[93m'
    LIGHTBLUE_EX    = '\x1b[94m'
    LIGHTMAGENTA_EX = '\x1b[95m'
    LIGHTCYAN_EX    = '\x1b[96m'
    LIGHTWHITE_EX   = '\x1b[97m'
    RESET = '\x1b[39m'

    if type(arg) == str:
        arg = YELLOW + repr(arg)
    else:
        arg = CYAN + repr(arg)
    return arg


def color_error_repr(error):
    BLACK           = '\x1b[30m'
    RED             = '\x1b[31m'
    GREEN           = '\x1b[32m'
    YELLOW          = '\x1b[33m'
    BLUE            = '\x1b[34m'
    MAGENTA         = '\x1b[35m'
    CYAN            = '\x1b[36m'
    WHITE           = '\x1b[37m'
    LIGHTBLACK_EX   = '\x1b[90m'
    LIGHTRED_EX     = '\x1b[91m'
    LIGHTGREEN_EX   = '\x1b[92m'
    LIGHTYELLOW_EX  = '\x1b[93m'
    LIGHTBLUE_EX    = '\x1b[94m'
    LIGHTMAGENTA_EX = '\x1b[95m'
    LIGHTCYAN_EX    = '\x1b[96m'
    LIGHTWHITE_EX   = '\x1b[97m'
    RESET = '\x1b[39m'

    string = repr(error)
    args = ', '.join(color_arg(arg) for arg in error.args)
    colored_string = f"{LIGHTRED_EX}{error.__class__.__name__}({YELLOW}{args}{LIGHTRED_EX}){RESET}"
    return colored_string
    # lhs = Code.LIGHTRED_EX + m.group(1) 
    # middle =  Code.YELLOW + m.group(2) 
    # # middle = re.sub(r"('\w+')", Code.LIGHTCYAN_EX + r'\1', middle)
    # rhs = Code.LIGHTRED_EX + m.group(3)
    # colored_string = lhs + middle + rhs
    return colored_string


def print_error_information(error):
    # C:\Users\vivek\Documents\Python                               -> ~/Documents/Python
    # C:\Users\vivek\AppData\Roaming\Python\Python310\site-packages -> $APPDATA/Python/site-packages
    # C:\Program Files\Python310\Lib\site-packages                  -> 
    import traceback
    import os
    from pathlib import Path

    tb = error.__traceback__

    print()
    print(color_error_repr(error))
    # print(Code.LIGHTRED_EX + repr(error))

    from waivek.frame import frame_gen
    call_frames = list(frame_gen())
    call_file = call_frames[3].f_code.co_filename

    frames = [ frame for frame, _ in traceback.walk_tb(tb) ]

    summaries = traceback.extract_tb(tb)
    pairs = reversed(list(zip(frames, summaries)))
    
    from waivek.ic import Table
    table = Table()
    table.gutter = '    '
    table.separator = ' ... '

    green_done = False
    for i, (frame, summary) in enumerate(pairs):
        filepath = summary.filename
        filepath = str(Path(filepath).resolve()) # C:\users -> C:\Users
        if os.getcwd() in filepath:
            filepath = os.path.relpath(os.path.abspath(filepath))
        else:
            homedir = os.path.expanduser("~")
            filepath = filepath.replace(homedir, "~")

        line_number = summary.lineno
        line = summary.line
        # line = Code.LIGHTGREEN_EX + line if i == 0 else line
        if green_done is False and frame.f_code.co_filename == call_file:
            line = Code.LIGHTGREEN_EX + line
            green_done = True
        lhs_string = f"{filepath}:{line_number}"
        table.row([lhs_string, line])
    table_string = str(table)
    table_lines = table_string.split("\n")
    table_lines = table_lines[1:]
    table_string = "\n".join(table_lines)
    print(table_string)
    # print()

def print_variables(D):
    import types
    from waivek.common import truncate
    exclude_types = [types.FunctionType, types.ModuleType, types.BuiltinFunctionType, type]
    table = [ {"name":k,"type":type(v), "value": truncate(str(v), 160)} for k,v in D.items() 
              if type(v) not in exclude_types and k[0:2] != "__" and str(v)[0] != "<"  and not isinstance(v, Exception) ]
    if table:
        ic(table)
    else:
        print("    (empty table)")

def get_error_filepath():
    import platform
    import os.path
    if platform.system() == 'Linux':
        vimpath = "~/.vim"
    else:
        vimpath = "~/.vimfiles"
    folder = os.path.join(os.path.expanduser(vimpath), "tmp")
    os.makedirs(folder, exist_ok=True)
    filename = 'handler_error.txt'
    filepath = os.path.join(folder, filename)
    filepath = os.path.abspath(filepath)
    return filepath



def write_vim_error_file(error: Exception):
    # test.py:34:5:    import sys
    import linecache
    import traceback
    import re
    from waivek.ic import ic
    import os

    from waivek.frame import frame_gen
    call_frames = list(frame_gen())
    call_file = call_frames[3].f_code.co_filename

    filepath = get_error_filepath()
    frames = [ frame for frame, _ in reversed(list(traceback.walk_tb(error.__traceback__))) ]
    error_lines = []
    cc_nr = -1
    for index, frame in enumerate(frames):
        path = frame.f_code.co_filename
        lineno = frame.f_lineno
        line = linecache.getline(path, lineno)
        if cc_nr == -1 and path == call_file:
            cc_nr = index + 1
        m = re.search(r"\S", line)
        if not m:
            raise ValueError(f"Error: {line}")
        column = m.start() + 1
        error_line = f"{path}:{lineno}:{column}:{line}".rstrip()
        error_lines.append(error_line)
    with open(filepath, "w") as f:
        f.write("\n".join(error_lines))
    # we use threading to make os\.system call not take up 0.08 seconds
    if sys.platform == 'win32':
        gvim_command = lambda : os.system(f'''start gvim --servername GVIM --remote-send ":call RHEF('{filepath}', {cc_nr})<CR>" ''')
        import threading
        threading.Thread(target=gvim_command).start()
    elif sys.platform == 'linux':
        command = f'''
        vim --servername FOO --remote-send "<C-w><C-w>:call RHEF('{filepath}', {cc_nr})<CR>"
        '''.strip()
        # os.system(command)
        import threading
        threading.Thread(target=lambda : os.system(command)).start()

@contextmanager
def handler():
    try:
        yield
    except Exception as e:
        error = e
        # append_traceback_to_file(error)
        # return
        if type(e).__name__ == 'bdb.BdbQuit':
            # Exit Via CTRL-D
            pass
        else:
            if False:
                write_vim_error_file(e)
            print_error_information(e)
            # print_variables_by_frame(e)
            import sys
            # frames = Frames(error)

            # for frame in frames:
            #
            #     print(frame.method)

            print(Code.LIGHTCYAN_EX + "alias ic, ib | import sys, ic, ib")
            print()
            # try __builtins__.__dict__
            # if "ipython" in sys.argv[0] or __builtins__.get("get_ipython", False):
            if "ipython" in sys.argv[0]:
                import importlib
                # import ipdb
                ipdb = importlib.import_module("ipdb")
                ipdb.post_mortem(e.__traceback__)
            else:
                import pdb
                pdb.post_mortem(e.__traceback__)

def divide_by_zero():

    # Error 1:
    # ========
    # upper = 5
    # lower = 0
    # result = upper / lower

    # Error 2:
    # ========
    # item = bytes()
    # bytes.encode()


    # Error 3:
    # ========
    from waivek.reltools import here
    path = here() / "f1/f2/f3/item.txt" # type: ignore[reportOperatorIssue]
    path.mkdir(exist_ok=True)

    result = 1
    return result

def append_traceback_to_file(error: Exception):
    import os.path
    import traceback
    path = os.path.expanduser("~/.cache/python_common_cache/error-traceback.txt")
    folder = os.path.dirname(path)
    # ansi constant codes {{{
    ANSI_RED_BG_BLACK_FG = "\x1b[41;30m"
    ANSI_GRAY_FG = "\x1b[90m"
    ANSI_MAGENTA_FG = "\x1b[35m"
    ANSI_BLUE_FG = "\x1b[34m"
    ANSI_RESET = "\x1b[0m"
    # }}}
    dt = datetime.now(ZoneInfo("Asia/Kolkata")).replace(microsecond=0)
    if not os.path.exists(folder):
        
        error_tag = ANSI_RED_BG_BLACK_FG + " OSError " + ANSI_RESET
        file_tag = ANSI_MAGENTA_FG + "{}".format(os.path.join(os.path.basename(os.path.dirname(__file__)), os.path.basename(__file__))) + ANSI_RESET
        datetime_tag = ANSI_GRAY_FG + dt.isoformat() + ANSI_RESET
        folder_tag = ANSI_BLUE_FG + folder + ANSI_RESET
        error_string = f"{datetime_tag} {file_tag} {error_tag} Directory does not exist: {folder_tag}"
        print(error_string)
        sys.exit(1)

    traceback_string = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    print(traceback_string)
    

def table_wide():
    pass
    # from .ic import Table
    # import textwrap
    # import json
    # # L = [['_make_api_call(self, operation_name, api_params)', '{\'operation_name\': \'PutIntegration\',\'api_params\': {\'restApiId\': \'p343uq88aa\', \'resourceId\':\'tbfu9qe6w7\', \'type\': \'HTTP_PROXY\', \'httpMethod\': \'ANY\',\'integrationHttpMethod\': \'ANY\', \'uri\': \'gql.twitch.tv\',\'connectionType\': \'INTERNET\', \'requestParameters\':{\'integration.request.path.proxy\':\'method.request.path.proxy\',\'integration.request.header.X-Forwarded-For\':\'method.request.header.X-My-X-Forwarded-For\'}},\'operation_model\':OperationModel(name=PutIntegration),\'service_name\': \'apigateway\',\'request_context\': {\'client_region\': \'us-east-2\',\'client_config\': <botocore.config.Config object at0x00000241D3DE7730>, \'has_streaming_input\': False,\'auth_type\': None, \'timestamp\': \'20220209T204914Z\'},\'request_dict\': {\'url_path\': \'/restapis/p343uq88aa/resources/tbfu9qe6w7/methods/ANY/integration\', \'query_string\':{}, \'method\': \'PUT\', \'headers\': {\'Content-Type\':\'application/json\', \'User-Agent\': \'Boto3/1.20.37Python/3.10.1 Windows/10 Botocore/1.23.37\', \'Accept\':\'application/json\'}, \'body\': b\'{"type": "HTTP_PROXY","httpMethod": "ANY", "uri": "gql.twitch.tv","connectionType": "INTERNET", "requestParameters":{"integration.request.path.proxy":"method.request.path.proxy","integration.request.header.X-Forwarded-For":"method.request.header.X-My-X-Forwarded-For"}}\', \'url\':\'https://apigateway.us-east-2.amazonaws.com/restapis/p343uq88aa/resources/tbfu9qe6w7/methods/ANY/integration\', \'context\': {\'client_region\': \'us-east-2\', \'client_config\': <botocore.config.Config object at0x00000241D3DE7730>, \'has_streaming_input\': False,\'auth_type\': None, \'timestamp\': \'20220209T204914Z\'}},\'service_id\': \'api-gateway\',\'event_response\': None, \'parsed_response\':{\'Error\': {\'Message\': \'Invalid HTTP endpoint specified forURI\', \'Code\': \'BadRequestException\'}, \'ResponseMetadata\':{\'RequestId\': \'31570f5f-1014-4d12-a555-9ba1b845a0d9\',\'HTTPStatusCode\': 400, \'HTTPHeaders\': {\'date\': \'Wed, 09 Feb2022 20:49:14 GMT\', \'content-type\': \'application/json\',\'content-length\': \'54\', \'connection\': \'keep-alive\', \'x-amzn-requestid\': \'31570f5f-1014-4d12-a555-9ba1b845a0d9\', \'x-amzn-errortype\': \'BadRequestException\', \'x-amz-apigw-id\':\'NStPrLmBCYcEdtQ=\'}, \'RetryAttempts\': 0}, \'message\':\'Invalid HTTP endpoint specified for URI\'},\'error_code\': \'BadRequestException\'}'], ['_api_call(self)', "{'args': (), 'kwargs': {'restApiId':'p343uq88aa', 'resourceId': 'tbfu9qe6w7', 'type':'HTTP_PROXY', 'httpMethod': 'ANY', 'integrationHttpMethod':'ANY', 'uri': 'gql.twitch.tv', 'connectionType': 'INTERNET','requestParameters': {'integration.request.path.proxy':'method.request.path.proxy','integration.request.header.X-Forwarded-For':'method.request.header.X-My-X-Forwarded-For'}},'operation_name': 'PutIntegration','py_operation_name': 'put_integration'}"], ['init_gateway(self, region, force)', "{'region': 'us-east-2', 'force': False,'session': Session(region_name='us-west-2'),'current_apis': [{'id': 'dtob7epyn2', 'name':'https://api.ipify.org/ - IP Rotate API', 'createdDate':datetime.datetime(2022, 2, 10, 1, 5, 41, tzinfo=tzlocal()),'apiKeySource': 'HEADER', 'endpointConfiguration': {'types':['REGIONAL']}, 'disableExecuteApiEndpoint': False}, {'id':'hfzgbt7mo0', 'name': 'https://gql.twitch.tv/ - IP RotateAPI', 'createdDate': datetime.datetime(2022, 1, 15, 18, 31,15, tzinfo=tzlocal()), 'apiKeySource': 'HEADER','endpointConfiguration': {'types': ['REGIONAL']},'disableExecuteApiEndpoint': False}], 'api':{'id': 'hfzgbt7mo0', 'name': 'https://gql.twitch.tv/ - IPRotate API', 'createdDate': datetime.datetime(2022, 1, 15,18, 31, 15, tzinfo=tzlocal()), 'apiKeySource': 'HEADER','endpointConfiguration': {'types': ['REGIONAL']},'disableExecuteApiEndpoint': False},'create_api_response': {'ResponseMetadata':{'RequestId': 'b46c081f-8baa-4ee4-99a8-5c76ef0a419b','HTTPStatusCode': 201, 'HTTPHeaders': {'date': 'Wed, 09 Feb2022 20:49:13 GMT', 'content-type': 'application/json','content-length': '202', 'connection': 'keep-alive','x-amzn-requestid': 'b46c081f-8baa-4ee4-99a8-5c76ef0a419b','x-amz-apigw-id': 'NStPcLEoiYcEb-Q='}, 'RetryAttempts': 0},'id': 'p343uq88aa', 'name': 'gql.twitch.tv - IP Rotate API','createdDate': datetime.datetime(2022, 2, 10, 2, 19, 13,tzinfo=tzlocal()), 'apiKeySource': 'HEADER','endpointConfiguration': {'types': ['REGIONAL']},'disableExecuteApiEndpoint': False},'get_resource_response': {'ResponseMetadata':{'RequestId': 'd7a96d82-3eca-4b6c-b602-e9944b56e009','HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Wed, 09 Feb2022 20:49:13 GMT', 'content-type': 'application/json','content-length': '42', 'connection': 'keep-alive', 'x-amzn-requestid': 'd7a96d82-3eca-4b6c-b602-e9944b56e009', 'x-amz-apigw-id': 'NStPiKaLCYcEbpA='}, 'RetryAttempts': 0},'items': [{'id': 'tbfu9qe6w7', 'path': '/'}]},'rest_api_id': 'p343uq88aa','create_resource_response': {'ResponseMetadata':{'RequestId': '61d46688-1caf-4e87-8e11-d564d4a6904d','HTTPStatusCode': 201, 'HTTPHeaders': {'date': 'Wed, 09 Feb2022 20:49:13 GMT', 'content-type': 'application/json','content-length': '81', 'connection': 'keep-alive', 'x-amzn-requestid': '61d46688-1caf-4e87-8e11-d564d4a6904d', 'x-amz-apigw-id': 'NStPlLrMiYcEd1w='}, 'RetryAttempts': 0}, 'id':'830kkp', 'parentId': 'tbfu9qe6w7', 'pathPart': '{proxy+}','path': '/{proxy+}'}}"], ['run(self)', "{'self': None}"], ['__get_result(self)', "{'self': None}"], ['result(self, timeout)', "{'self': None, 'timeout': None}"], ['start(self, force, endpoints)', "{'force': False, 'endpoints': [],'new_endpoints': 0, 'futures': [<Future at0x241d10a49d0 state=finished returned dict>, <Future at0x241d10dc970 state=finished raised BadRequestException>,<Future at 0x241d10f8af0 state=finished returned dict>,<Future at 0x241d1128c10 state=finished returned dict>,<Future at 0x241d1128f40 state=finished returned dict>,<Future at 0x241d116cd00 state=finished returned dict>,<Future at 0x241d118cd30 state=finished returned dict>,<Future at 0x241d11b8d60 state=finished returned dict>,<Future at 0x241d11d8d90 state=finished returned dict>,<Future at 0x241d12228c0 state=finished returneddict>], 'region': 'ca-central-1','result': {'success': True, 'endpoint':'mpwkk460o2.execute-api.us-west-2.amazonaws.com', 'new':False}}"], ['post_anonymous(url, data, json, params, headers, cookies, files, auth, timeout, allow_redirects, proxies, hooks, stream, verify, cert)', '{\'url\': \'https://gql.twitch.tv/gql\', \'data\':None, \'json\': {\'query\': \' query {c0:clip(slug:"AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC"){slug, videoOffsetSeconds}c1:clip(slug:"HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V"){slug, videoOffsetSeconds}c2:clip(slug:"SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5"){slug, videoOffsetSeconds}c3:clip(slug:"PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9"){slug, videoOffsetSeconds}c4:clip(slug:"CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u"){slug, videoOffsetSeconds} }\'},\'params\': None, \'headers\': {\'Client-Id\':\'kimne78kx3ncx6brgo4mv6wki5h1ko\'}, \'cookies\':None, \'files\': None, \'auth\': None,\'timeout\': None, \'allow_redirects\':None, \'proxies\': None, \'hooks\':None, \'stream\': None, \'verify\':None, \'cert\': None, \'fu\':furl(\'https://gql.twitch.tv/gql\'), \'domain\':\'gql.twitch.tv\', \'endpoints\': {\'api.ipify.org\':[\'f2zfzh3tq3.execute-api.eu-west-1.amazonaws.com\',\'jt27jndj26.execute-api.eu-west-2.amazonaws.com\',\'iwi6olde13.execute-api.eu-central-1.amazonaws.com\',\'5aan9q8hkb.execute-api.eu-north-1.amazonaws.com\',\'2lv7s6djz2.execute-api.eu-west-3.amazonaws.com\',\'hwxvmq4d0k.execute-api.ca-central-1.amazonaws.com\',\'dtob7epyn2.execute-api.us-east-2.amazonaws.com\',\'7ogy03096l.execute-api.us-east-1.amazonaws.com\',\'bw4siipcr8.execute-api.us-west-1.amazonaws.com\',\'0f3l66pta8.execute-api.us-west-2.amazonaws.com\']}}'], ['gql(query)', '{\'query\': \' query {c0:clip(slug:"AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC"){slug, videoOffsetSeconds}c1:clip(slug:"HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V"){slug, videoOffsetSeconds}c2:clip(slug:"SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5"){slug, videoOffsetSeconds}c3:clip(slug:"PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9"){slug, videoOffsetSeconds}c4:clip(slug:"CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u"){slug, videoOffsetSeconds} }\'}'], ['get_clip_offsets(clip_ids)', '{\'clip_ids\': [\'AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC\', \'HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V\', \'SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5\', \'PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9\', \'CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u\'], \'slugs\':[\'AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC\',\'HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V\',\'SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5\',\'PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9\',\'CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u\'],\'aliases\': [\'c0\', \'c1\', \'c2\', \'c3\', \'c4\'],\'url\': \'https://gql.twitch.tv/gql\',\'query_slugs\': [\'AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC\', \'HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V\', \'SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5\', \'PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9\', \'CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u\'], \'query_aliases\': [\'c0\', \'c1\',\'c2\', \'c3\', \'c4\'], \'query_strings\':[\'c0:clip(slug:"AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC"){slug, videoOffsetSeconds}\',\'c1:clip(slug:"HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V"){slug, videoOffsetSeconds}\',\'c2:clip(slug:"SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5"){slug, videoOffsetSeconds}\',\'c3:clip(slug:"PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9"){slug, videoOffsetSeconds}\',\'c4:clip(slug:"CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u"){slug, videoOffsetSeconds}\'],\'query\': \' query {c0:clip(slug:"AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC"){slug, videoOffsetSeconds}c1:clip(slug:"HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V"){slug, videoOffsetSeconds}c2:clip(slug:"SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5"){slug, videoOffsetSeconds}c3:clip(slug:"PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9"){slug, videoOffsetSeconds}c4:clip(slug:"CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u"){slug, videoOffsetSeconds} }\',\'i\': 0, \'alias_to_slug\': {\'c0\':\'AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC\', \'c1\':\'HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V\', \'c2\':\'SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5\', \'c3\':\'PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9\', \'c4\':\'CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u\'},\'slug_to_offset\': {\'AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC\': None, \'HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V\': None, \'SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5\': None, \'PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9\': None, \'CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u\': None}}'], ['duration_runner()', "{'CLIP_COUNT': 5, 'slugs':['AbrasiveGeniusClintTheRinger-eEswgwJ6b0pSfSEC','HappyArborealClipsmomBlargNaut-Qd9yKSJdoj6ghj1V','SpineyMuddyPuddingYouDontSay-qYSaw1qvv4bbn_D5','PuzzledColdbloodedGarbage4Head-XClB8beXWPeSXFf9','CarelessObliqueApeSquadGoals-KR8NUysH7GJ0nV-u']}"], ['<module>', "{'get_dictionaries': []}"], ['handler()', '{}']]
    # table = Table()
    # for name, value in L:
    #     w_name = "\n".join(textwrap.wrap(name, 60))
    #     row = (w_name, color_D_if_big(D))
    #     table.row(row)
    # print(table)
    #

def library_error():
    import json
    json.loads("{'a': 1}")

def main():
    library_error()

if __name__ == "__main__":
    timer = Timer()
    with handler():
        main()
