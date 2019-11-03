from .pathvar import replace_variables

import os
opt = os.path
from datetime import (datetime as dt, timedelta as td)
import functools
import zipfile
from shutil import copy2
import traceback


def _is_relative(path):
    return ':' not in path


def _resolve(pth, envdir):
    pth = opt.normpath(pth)
    
    if _is_relative(pth):
        pth = opt.join(envdir, pth)
        
    pth = opt.realpath(pth)
    
    return pth


def archive(project, package=None,
            destination='$PRJPATH\\..\\_backup',
            compression='ZIP_DEFLATED',
            include_pycache=False,
            exists='rename'):
    
    import prj.prj
    
    if isinstance(project, prj.prj.Project):
        p = project
    else:
        p = prj.prj.setup(project, ins_to=[], build=False)
    
    path = opt.join(p.path,package) if package else p.path

    pths_resolved = replace_variables(destination, aPrj=p)
    if not len(pths_resolved):
        raise ValueError('destination="{}" could not be resolved'.format(destination))
    
    real_dest = opt.normpath(pths_resolved[0])
    if not opt.isdir(real_dest):
        os.mkdir(real_dest)
    
    name = p.name if not package else opt.basename(path)
    is_version = lambda x: '=' in x and x.split('=')[0].strip() == '__version__'
    extract_version = lambda x: x.split('=')[1].strip(' "\'')
    
    if package:
        with open(opt.join(path,'__init__.py'), encoding='utf-8') as initfile:
            lines = initfile.read().split('\n')
        versions = map(get_version, filter(is_version, lines))
        version = next(versions,'?')
    elif p.version:
        version = p.version
    else:
        version = '?'
    
    zfName = '{}-{}{}.zip'.format(name, version, '') #'_'+dt.utcnow().strftime(datefmt))
    zfPath = opt.join(real_dest, zfName)
    #print(real_dest)
    #print(zfPath)
    
    zfPath = zip_contents(path, zfPath, compression, include_pycache)
    
    bkp_replaced = replace_variables('$BACKUP', aPrj=p)
    bkpPaths = list(map(opt.realpath, filter(opt.isdir, bkp_replaced)))
    if not len(bkpPaths):
        print('Backup path(s) could not be resolved.')
    
    for bkpPath in bkpPaths:
        try: copy2(zfPath, bkpPath)
        except Exception:
            traceback.print_exc()

    return zfPath



def zip_contents(path, destination=None,
                 compression='ZIP_DEFLATED',
                 include_pycache=False,
                 exists='error'):
    
    """
    :param path: path or list of paths.
                 If a path is directory, all its contents will be zipped under
                 the name of the directory. Relative paths are assumed to be relative
                 to the parent directory of the first path in the list, and the first path
                 to the current working directory.
                 In case an outermost directory/file already exists in the in-the-making
                 zip file, the directory/file is renamed to "{original_base}({n}){original_suffix}"
                 (the suffix is for files only).
    
    :param exists: "error" or "rename"
                The action applies to `destination`.
    """
    
    if isinstance(compression,str):
        compression = getattr(zipfile, compression)
        
    if exists not in (None,'error','rename'):
        raise ValueError("`exists` must be either 'error' or 'rename'; got: {}".format(exists))
    
    paths = [path] if isinstance(path, str) else path
    paths[0] = main_path = opt.realpath(paths[0])
    main_envdir = opt.dirname(main_path)
    
    paths = [paths[0]] + [_resolve(pth, main_envdir) for pth in paths[1:]]
    
    if destination is None:
        destination = opt.join(main_envdir, opt.basename(main_path)+'.zip')
    
    destination = _resolve(destination, main_envdir)

    if exists in (None,'error') and opt.exists(exists):
        raise OSError('Destination {} already exists'.format(destination))    

    i = 0
    has_zipend = destination.endswith('.zip')
    body = destination[:-4] if has_zipend else destination
    
    while opt.exists(destination):
        destination = '{}({}){}'.format(body, i+2, '.zip' if has_zipend else '')
        i+=1
        
    cache = ('__pycache__', '.cache', '.pytest_cache')
    _contains_cache_dir = lambda tail: any(c in tail for c in cache)
    
    ignore = 'geckodriver.log'
    _filter = lambda files: [f for f in files if f not in ignore]
    
    zf = zipfile.ZipFile(destination, 'w', compression)
    
    
    def _rename(pth, is_file=False, zf_outermost_dirs=set(), zf_outermost_files=set()):
        name = opt.basename(pth)
        
        if is_file and '.' in name:
            dot_loc = name.rfind('.')
            body, suffix = name[:dot_loc], name[dot_loc:]
        else:
            body, suffix = name, ''
        
        reg = zf_outermost_dirs if not is_file else zf_outermost_files  
        i = 0
        
        while name in reg:
            name = '{}({}){}'.format(body, i+2, suffix)
            i +=1
            
        reg.add(name)
        
        return opt.join(opt.dirname(pth), name)
    
    
    def _zip_directory(pth):
        len_pth = len(pth)
        len_split = len(pth.split('\\'))
                
        pth2 = _rename(pth)
        basedir = opt.basename(pth2)
        
        for root, dirs, files in os.walk(pth):
            tail = root.split('\\')[len_split:]
            if include_pycache: pass
            elif _contains_cache_dir(tail): continue
            else: files = _filter(files)
            
            rel_path = opt.join(basedir, root[len_pth+1:])
                
            for f in files:
                zf.write(opt.join(root,f), opt.join(rel_path, f))
    
    
    for pth in paths:
        if opt.isdir(pth):
            _zip_directory(pth)
        else:
            pth2 = _rename(pth, is_file=True)
            zf.write(pth, opt.basename(pth2))
 
    zf.close()


    return destination
