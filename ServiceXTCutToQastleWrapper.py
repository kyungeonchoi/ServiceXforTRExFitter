import re
import logging
import func_adl_uproot,qastle,ast

def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 

def tcut_to_qastle( selection, variable ):
    # 1st step: recognize all variable names
    ignore_patterns = { # These are supported by Qastle
        "abs" : " ",
        "(" : " ",
        ")" : " ",
        "*" : " ",
        "/" : " ",
        "+" : " ",
        "-" : " "
    }
    temp = multiple_replace(ignore_patterns, selection)

    output1 = re.sub('[<&>!=|-]',' ',temp)
    variables = []
    for x in output1.split():
        try:
            float(x)
        except ValueError:
            variables.append(x)
    variables = list(dict.fromkeys(variables)) # Remove duplicates
    logging.info(f'Number of accessed branches for the selection: {len(variables)}')

    # 2nd step: replace variable names with event.
    for x in variables:
        selection = re.sub(r'\b(%s)\b'%x, r'event.%s'%x, selection)

    # 3rd step: replace operators 
    replace_patterns = {
        "&&" : " and ",
        "||" : " or ",
        "!=" : " != ",
        ">=" : " >= ",
        "<=" : " <= ",
        ">" : " > ",
        "<" : " < "    
    }
    output = multiple_replace(replace_patterns, selection)
    output = " ".join(output.split()) # Remove duplicate whitespace

    # 4th step: bool (!! Still missing many combinations!!)
    output = "and " + output + " and" # Prepare for search. Better idea?
    for x in variables:
        if re.search(r'and\s*event.%s\s*and'%x, output): # and variable and
            output = re.sub(r'and\s*event.%s\s*and'%x, r'and event.%s > 0 and'%x, output)
        if re.search(r'and\s*!event.%s\s*and'%x, output): # and !variable and
            output = re.sub(r'and\s*!event.%s\s*and'%x, r'and event.%s == 0 and'%x, output)
        if re.search(r'and\s*event.%s\s*\)'%x, output): # and variable )
            output = re.sub(r'and\s*event.%s\s*\)'%x, r'and event.%s > 0)'%x, output)
        if re.search(r'and\s*!event.%s\s*\)'%x, output): # and !variable )
            output = re.sub(r'and\s*!event.%s\s*\)'%x, r'and event.%s == 0)'%x, output)
        if re.search(r'\(\s*event.%s\s*and'%x, output): # ( variable and
            output = re.sub(r'\(\s*event.%s\s*and'%x, r'(event.%s > 0 and'%x, output)
        if re.search(r'\(\s*!event.%s\s*and'%x, output): # ( !variable and
            output = re.sub(r'\(\s*!event.%s\s*and'%x, r'(event.%s == 0 and'%x, output)
        if re.search(r'or\s*event.%s\s*or'%x, output): # or variable or
            output = re.sub(r'or\s*event.%s\s*or'%x, r'or event.%s > 0 or'%x, output)
        if re.search(r'or\s*!event.%s\s*or'%x, output): # or !variable or
            output = re.sub(r'or\s*!event.%s\s*or'%x, r'or event.%s == 0 or'%x, output)
        if re.search(r'and\s*event.%s\s*or'%x, output): # and variable or
            output = re.sub(r'and\s*event.%s\s*or'%x, r'and event.%s > 0 or'%x, output)
        if re.search(r'and\s*!event.%s\s*or'%x, output): # and !variable or
            output = re.sub(r'and\s*!event.%s\s*or'%x, r'and event.%s == 0 or'%x, output)   
        if re.search(r'or\s*event.%s\s*and'%x, output): # or variable and
            output = re.sub(r'or\s*event.%s\s*and'%x, r'or event.%s > 0 and'%x, output)
        if re.search(r'or\s*!event.%s\s*and'%x, output): # or !variable and
            output = re.sub(r'or\s*!event.%s\s*and'%x, r'or event.%s == 0 and'%x, output)
        if re.search(r'\(\s*event.%s\s*or'%x, output): # ( variable or
            output = re.sub(r'\(\s*event.%s\s*or'%x, r'(event.%s > 0 or'%x, output)
        if re.search(r'\(\s*!event.%s\s*or'%x, output): # ( !variable or
            output = re.sub(r'\(\s*!event.%s\s*or'%x, r'(event.%s == 0 or'%x, output)
        if re.search(r'or\s*event.%s\s*\)'%x, output): # or variable )
            output = re.sub(r'or\s*event.%s\s*\)'%x, r'or event.%s > 0)'%x, output)
        if re.search(r'or\s*!event.%s\s*\)'%x, output): # or !variable )
            output = re.sub(r'or\s*!event.%s\s*\)'%x, r'or event.%s == 0)'%x, output)
        if re.search(r'!\([^()]*\)', output): # Search for !(something)
            output = re.sub(r'!\([^()]*\)',re.search(r'!\([^()]*\)', output).group(0).lstrip('!') + "==0",output)
        
    output = output.rsplit(' ', 1)[0].split(' ', 1)[1] # Delete `and` at the beginning and the last

    # Add Func ADL wrapper
    query = "EventDataset().Where('lambda event: " + output + "').Select('lambda event: (event." + variable + ",)')"
    text_ast = qastle.python_ast_to_text_ast(qastle.insert_linq_nodes(ast.parse(query)))

    return text_ast