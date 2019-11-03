from prj.management import zip_contents
import os
import zipfile


def _cleanup():
    contents = set(os.listdir('test'))
        
    for x in contents:
        if x.endswith('.zip') and x != 'test_mgmt_folder.zip':
            try:
                os.remove(os.path.join('test',x))
            except OSError:
                pass


def assert_test_zip_contents_structure(zf_pth):
    data = [
        'test_mgmt_folder/subf/subf1.txt',
        'test_mgmt_folder/file1.txt',
        'test_mgmt_folder/file2.log',
        'test_mgmt_folder/file3',
        'test_mgmt_folder(2)/file1.txt',
        'test_mgmt_folder(3)/file1.txt',
        'test_mgmt_file.txt',
        'test_mgmt_file(2).txt',
        'test_mgmt_file(3).txt',
    ]

    with zipfile.ZipFile(zf_pth) as zf:
        namelist = zf.namelist()

    for f in data:
        assert f in namelist

    assert len(namelist) == len(data)


def test_zip_contents():
    zf_pth = None
    try:
        zf_pth = zip_contents(
                     ['test/test_mgmt_folder',
                      'test_mgmt_folder2/test_mgmt_folder',
                      'test_mgmt_folder3/test_mgmt_folder',
                      'test_mgmt_file.txt',
                      'test_mgmt_folder2/test_mgmt_file.txt',
                      'test_mgmt_folder3/test_mgmt_file.txt'],
                     exists='rename')
        assert os.path.basename(zf_pth) == 'test_mgmt_folder(2).zip'
        assert_test_zip_contents_structure(zf_pth)
    finally:
        _cleanup()
