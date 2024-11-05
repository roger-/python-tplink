import re
import json


REGEX_HTML_SCRIPT = re.compile(r'^\s*<script>([\s\S]*?)<\/script>', flags=re.MULTILINE)
REGEX_JS_VARS = re.compile(r'^[ \t]*var (\w+) *= *([\s\S]+?);', flags=re.MULTILINE)
REGEX_JS_DICT = re.compile(r'^\s*(\w+):(.*)$', flags=re.MULTILINE)

def parse_script_variables(html):
    # quick and dirty JavaScript variable parser

    dict_out = {}

    # find script tag contents
    match = REGEX_HTML_SCRIPT.search(html)

    if not match:
        return dict_out
    
    # hack to make sure all variable declarations end with semicolon
    js = fix_semicolons(match.group(0))

    # find all JS variable assignments
    js_vars = REGEX_JS_VARS.findall(js)
    
    # iterate over each variable
    for js_name, js_val in js_vars:       
        val = js_val.strip().replace("'", '"')

        # handle dictionaries as special case
        if val.startswith('{'):
            dict_out[js_name] = handle_dict(val)

        # handle "new Array" as list
        elif val.startswith('new Array'):
            dict_out[js_name] = handle_array(val)

        # handle multiple definitions per single var
        elif '=' in val:
            vars_all = handle_multiple_vars(js_name, val)
            dict_out.update(vars_all)

        # use json module to parse directly
        else:
            dict_out[js_name] = json.loads(js_val)

    return dict_out

def fix_semicolons(js):
    # hack to make sure all variable declarations end with semicolon
    lines = list(line.strip() for line in js.splitlines() if line.strip())

    if len(lines) > 1 and lines[0].startswith('var') and not lines[0].endswith(';'):
        lines[0] = lines[0] + ';'

    for i in range(1, len(lines)):
        if lines[i].startswith('var') and not lines[i - 1].endswith(';'):
            lines[i - 1] = lines[i - 1] + ';'

    js_out = '\n'.join(lines)

    return js_out

def handle_dict(val):
    # strip brackets
    val = val[1:-1] 

    # add quotes and remove trailing comma
    val_quoted = REGEX_JS_DICT.sub(r'"\1":\2', val)[:-1]

    # use json module to parse
    return json.loads('{' + val_quoted + '}')

def handle_array(val):
    val = val.replace('new Array(', '')
    val = val[:-1] # remove final bracket

    return json.loads('[' + val + ']')

def handle_multiple_vars(name, val):
    vars_all = name + '=' + val # re-join

    output = {}

    for var_def in vars_all.split(','):
        name, val = var_def.strip().split('=')

        output[name.strip()] = json.loads(val)

    return output

def main():
    html_string = '''
    <html>
    <head>
    <script>
        var info_ds = {
            descriStr: ["TL-SG108E"],
            macStr: ["AA:BB:CC:DD:EE:FF"],
            ipStr: ["192.168.1.1"],
            netmaskStr: ["255.255.255.0"],
            gatewayStr: ["192.168.1.1"],
            firmwareStr: ["1.0.0 Build 20230218 Rel.50633"],
            hardwareStr: ["TL-SG108E 6.0"]
        };
        var tip = "";

        var max_port_num = 8;
        var port_middle_num = 16;
        var all_info = {
            state: [1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            link_status: [6, 6, 6, 5, 6, 0, 0, 0, 0, 0],
            pkts: [10059843, 0, 16729111, 0, 1205953, 0, 51044, 0, 47756073, 0, 25673093, 0, 1919325, 0, 1224960, 0, 27658731, 0, 41220480, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        };
        var tip = "";
    var g_Lan = 1
      , g_level = 1
      , g_year = 2023
      , g_title = 'TL-SG108E';

    var selState = new Array(0,0,0,0,0,0,0,0);
    var trunk_info = new Array(""," (LAG1)"," (LAG2)");
    var pTrunk = new Array(0,0,0,0,0,0,0,0);
    var pPri = new Array(1,1,1,1,1,1,1,1);
    var pri_info = new Array("","1(Lowest)","2(Normal)","3(Medium)","4(Highest)","Unknown");
    var portNumber = 8;
    var qosMode = 2;
    var tip = "";

    var led = 1
    var tip = "";

    </script>
    </html>
    '''

    parsed_vars = parse_script_variables(html_string)
    print(json.dumps(parsed_vars, indent=2))

if __name__ == '__main__':
    main()