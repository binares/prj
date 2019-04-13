import os, sys
opt = os.path


def fix_drive_letter(x):
    x = opt.normpath(x)
    
    if x.endswith(':'):
        x += '\\'
    elif not x.endswith('\\'):
        x += ':\\'
        
    return x
    
    
def drive_exists(letter):
    return fix_drive_letter(letter) in get_drives()


def get_drives():
    from win32 import win32api
    return win32api.GetLogicalDriveStrings().split("\x00")[:-1]


#path given is meant to start with one of the variables: $DRIVE: $2DRIVE: $3DRIVE: $CURDRIVE: 
# otherwise matched directly and only against the (literal) path given
def search_path_in_drives(path,start='$CURDRIVE:',op='exists',select='all'):
    from .pathvar import _replace_drive_variable
    #select - first/all
    return_first = (select == 'first')
    
    if op not in ('exists','isdir','isfile'):
        raise ValueError(op)
    realop = getattr(os.path, op)
    
    paths = _replace_drive_variable(path,start=start)
    paths = [opt.realpath(x) for x in paths]
    
    
    realfilter = filter(realop,paths)
    real_paths = []
    
    if return_first:
        try: real_paths = [next(realfilter)]
        except StopIteration: pass
    else: real_paths = list(realfilter)
    
        
    return real_paths



def insert_paths(paths, ins_to='sys.path', order='override'):
    #ins_these are dir_names with their (determined) path
    # later inserted to ins_to (e.g. sys.path, if given)
    if paths is None: paths = []
    elif isinstance(paths,str): paths = [paths]
    if ins_to == 'sys.path': ins_to = sys.path

    i = 0
    keep = (order == 'keep')
    
    for pth in paths:
        prev_index = -1
        
        while True:
            try: prev_index = ins_to.index(pth)
            except ValueError: break
            
            if keep: break
            elif prev_index < i: i-=1  
              
            del ins_to[prev_index]
        
        if not keep or prev_index == -1:
            ins_to.insert(i, pth)
            i+=1
