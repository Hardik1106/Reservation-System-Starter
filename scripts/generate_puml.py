import os
import re

def parse_java_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Simple cleanups
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    package = ""
    pkg_match = re.search(r'package\s+([\w\.]+);', content)
    if pkg_match:
        package = pkg_match.group(1)

    # Find class/interface/enum
    # Support public abstract class etc.
    class_pattern = re.compile(r'(public|protected|private)?\s*(abstract)?\s*(class|interface|enum)\s+(\w+)\s*(extends\s+\w+)?\s*(implements\s+[\w\s,]+)?\s*\{', re.MULTILINE)
    
    classes = []
    for match in class_pattern.finditer(content):
        type_ = match.group(3)
        name = match.group(4)
        extends_raw = match.group(5)
        implements_raw = match.group(6)
        
        extends = extends_raw.replace('extends', '').strip() if extends_raw else ""
        implements = [i.strip() for i in implements_raw.replace('implements', '').split(',')] if implements_raw else []
        
        # very basic body extraction
        body_start = match.end()
        brace_count = 1
        body_end = body_start
        for i in range(body_start, len(content)):
            if content[i] == '{': brace_count += 1
            elif content[i] == '}': brace_count -= 1
            if brace_count == 0:
                body_end = i
                break
                
        body = content[body_start:body_end]
        
        fields = []
        methods = []
        
        if type_ != 'enum':
            # extract fields: something like "private String name;"
            # extremely simplified 
            lines = body.split(';')
            for line in lines:
                line = line.strip()
                if not line or '{' in line or '}' in line:
                    continue
                # strip off any initialization to avoid capturing values as names
                line = re.sub(r'=.*', '', line)
                if '(' in line: 
                    continue  # probably a method declaration

                parts = line.split()
                # only consider lines that start with a Java modifier (public/private/protected/static/final...)
                modifiers_set = {'public', 'private', 'protected', 'static', 'final', 'transient', 'volatile'}
                if len(parts) >= 2 and parts[0] in modifiers_set:
                    # heuristic for fields: remove leading modifiers so the remaining tokens start with the type
                    modifiers = parts[0] if parts[0] in ['public', 'private', 'protected'] else ''
                    tokens = parts[:]  # copy
                    while tokens and tokens[0] in modifiers_set:
                        tokens.pop(0)
                    if len(tokens) >= 2:
                        # type may span multiple tokens (e.g. Map<String, String>) so take all except last as type
                        name_ = tokens[-1]
                        typ = ' '.join(tokens[:-1])
                        fields.append((modifiers, typ, name_))
            # extract methods: capture both declared methods with modifiers (classes)
            # and methods without modifiers (interfaces). Capture parameters as string.
            method_pattern_class = re.compile(r'(public|private|protected)\s+([\w<>, <>\[\]]+)\s+(\w+)\s*\(([^)]*)\)')
            for m in method_pattern_class.finditer(body):
                params = m.group(4).strip()
                methods.append((m.group(1), m.group(2).strip(), m.group(3), params))

            # for interfaces, methods often omit visibility/modifier; capture those too
            if type_ == 'interface':
                method_pattern_interface = re.compile(r'(?:(public|private|protected)\s+)?([\w<>, <>\[\]]+)\s+(\w+)\s*\(([^)]*)\)\s*(?:;|\{)')
                for m in method_pattern_interface.finditer(body):
                    modifier = m.group(1) if m.group(1) else 'public'
                    params = m.group(4).strip()
                    methods.append((modifier, m.group(2).strip(), m.group(3), params))
                
        classes.append({
            'package': package,
            'type': type_,
            'name': name,
            'extends': extends,
            'implements': implements,
            'fields': fields,
            'methods': methods,
            'enum_body': body if type_ == 'enum' else ""
        })
        
    return classes

def write_puml(classes_data, out_file):
    with open(out_file, 'w') as f:
        f.write("@startuml\n")
        f.write("skinparam classAttributeIconSize 0\n")
        f.write("left to right direction\n\n")
        
        # declare classes
        for cls in classes_data:
            if cls['type'] == 'enum':
                f.write(f"enum {cls['name']} {{\n")
                enum_items = [x.strip() for x in cls['enum_body'].split(',') if x.strip()]
                for item in enum_items:
                    clean_item = item.split(';')[0].split('{')[0].strip()
                    if clean_item and not " " in clean_item:
                        f.write(f"  {clean_item}\n")
                f.write("}\n")
            else:
                f.write(f"{cls['type']} {cls['name']} {{\n")
                for mod, typ, name in cls['fields']:
                    symbol = "+" if mod == "public" else "-" if mod == "private" else "#"
                    f.write(f"  {symbol}{name} : {typ}\n")
                for method in cls['methods']:
                    # methods now may include params
                    if len(method) == 4:
                        mod, typ, name, params = method
                    else:
                        mod, typ, name = method
                        params = ""
                    symbol = "+" if mod == "public" else "-" if mod == "private" else "#"
                    if params:
                        # shorten parameter list to types only
                        # keep full string for now
                        f.write(f"  {symbol}{name}({params}) : {typ}\n")
                    else:
                        f.write(f"  {symbol}{name}() : {typ}\n")
                f.write("}\n")
                
        f.write("\n")
                
        # declare relationships
        seen = set()  # to avoid duplicate associations
        for cls in classes_data:
            if cls['extends']:
                f.write(f"{cls['extends']} <|-- {cls['name']}\n")
            
            for impl in cls['implements']:
                f.write(f"{impl} <|.. {cls['name']}\n")
            
            # associations from fields
            for mod, typ, name in cls['fields']:
                clean_typ = typ.replace('List<', '').replace('>', '').replace('[]', '').strip()
                if any(clean_typ == c['name'] for c in classes_data if c['name'] != cls['name']):
                    pair = (cls['name'], clean_typ)
                    if pair not in seen:
                        f.write(f"{cls['name']} --> {clean_typ}\n")
                        seen.add(pair)
        f.write("@enduml\n")

def main():
    import glob
    src_dir = '../src/main/java'
    java_files = glob.glob(src_dir + '/**/*.java', recursive=True)
    
    all_classes = []
    for f in java_files:
        all_classes.extend(parse_java_file(f))
        
    write_puml(all_classes, 'class_diagram.puml')
    print("Generated class_diagram.puml")

if __name__ == "__main__":
    main()
