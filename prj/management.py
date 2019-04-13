from .pathvar import replace_variables

import os
opt = os.path
from datetime import (datetime as dt, timedelta as td)
import zipfile
from shutil import copy2
import traceback


def archive(project, package=None,
            destination='$PRJPATH\\..\\_backup',
            compression='ZIP_DEFLATED',
            include_pycache=False,
            exists='rename'):
    
    #datefmt = '%Y-%m-%d'):
    import prj.prj
    
    if isinstance(project,prj.prj.Project): p = project
    else: p = prj.prj.setup(project,ins_to=[],build=False)
    
    if package: path = opt.join(p.path,package)
    else: path = p.path
    
    pths_resolved = replace_variables(destination,aPrj=p)
    if not len(pths_resolved):
        raise ValueError('destination="{}" could not be resolved'.format(destination))
    
    real_dest = opt.normpath(pths_resolved[0])
    if not opt.isdir(real_dest): os.mkdir(real_dest)
    
    name = p.name if not package else opt.basename(path)
    
    if package:
        with open(opt.join(path,'__init__.py')) as initf:
            lines = initf.read().split('\n')
            linesfilter = filter(lambda x: '=' in x and x.split('=')[0].strip() == '__version__', lines)
            versionmap = map(lambda x: x.split('=')[1].strip(" \"'"), linesfilter)
            version = next(versionmap,'?')
    elif p.version: version = p.version
    else: version = '?'
    
    zfName = '{}-{}{}.zip'.format(name,version,'') #'_'+dt.utcnow().strftime(datefmt))
    zfPath = opt.join(real_dest,zfName)
    #print(real_dest)
    #print(zfPath)
    
    zfPath = zip_contents(path,zfPath,compression,include_pycache)
    
    bkp_replaced = replace_variables('$BACKUP', aPrj=p)
    bkpPaths = list(map(opt.realpath,filter(opt.isdir,bkp_replaced)))
    if not len(bkpPaths):
        print('Backup path(s) could not be resolved.')
    
    for bkpPath in bkpPaths:
        try: copy2(zfPath,bkpPath)
        except Exception: traceback.print_exc()

    return zfPath



def zip_contents(path,destination=None,
                 compression='ZIP_DEFLATED',
                 include_pycache=False,
                 exists='error'):
    
    if isinstance(compression,str):
        compression = getattr(zipfile,compression)
    if exists not in (None,'error','rename'):
        raise ValueError('`exists` must be either \'error\' or \'rename\'; got: {}'.format(exists))
        
    path = opt.realpath(path)
    p_len = len(path.split('\\'))
    
    envdir = opt.dirname(path)
    len_env = len(envdir)
    if destination is None:
        destination = opt.join(envdir,opt.basename(path)+'.zip')
    destination = opt.normpath(destination)

    is_relative = ':' not in destination
    if is_relative:
        destination = opt.join(envdir,destination)
    
    destination = opt.realpath(destination)
    if exists in (None,'error') and opt.exists(exists):
        raise OSError('Destination {} already exists'.format(destination))    
    """if opt.isdir(destination): #and not is_relative:
        destination = opt.join(destination,opt.basename(path)+'.zip')"""

    i = 0
    zipend = destination.endswith('.zip')
    while opt.exists(destination):
        j = 0 if not i else (len(str(j+1))+2)
        if zipend: j+=4
        body = destination if not j else destination[:-j]
        destination = '{}({}){}'.format(body,i+2,'.zip' if zipend else '')
        i+=1
        
    zf = zipfile.ZipFile(destination, 'w', compression)
    pc = ('__pycache__', '.cache', '.pytest_cache')
    
    if opt.isdir(path):
        for root, dirs, files in os.walk(path):
            interest = root.split('\\')[p_len:]
            if include_pycache: pass
            elif any(x in interest for x in pc): continue
            else: files = (x for x in files if not x=='geckodriver.log')
            
            rel_path = root[len_env+1:]
                
            for f in files:
                """date = mt.decode_ctime(opt.getctime(opt.join(root,f)))
                if date < SINCE: continue"""
        
                zf.write(opt.join(root,f), opt.join(rel_path, f))

    else:
        zf.write(path,opt.basename(path))
 
    zf.close()

    return destination
