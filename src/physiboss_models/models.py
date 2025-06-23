import platform
import urllib.request
import os
import sys
import tarfile
import stat
import shutil
from github import Github
import yaml

class Database(object):

    def __init__(self):
        self._github = Github()
        self._organisation = self._github.get_organization("PhysiBoSS-Models")
        self.models = self._list_models()
        self.current_model_yaml = None
        self.current_model_info = None
        
    def keys(self):
        return self.models.keys()

    def values(self):
        return self.models.values()

    def items(self):
        return self.models.items()

    def __getitem__(self, name):
        return self.models[name]
    
    def _list_models(self):
        repos = self._organisation.get_repos()
        i=0
        page = repos.get_page(i)
        r = []
        while len(page) > 0:
            r += page
            i += 1
            page = repos.get_page(i)
        
        return {repo.name:repo for repo in r if repo.name[0].isupper()}        

    # def get_default_config(self):
    #     if self.current_model_yaml is not None and os.path.exists(self.current_model_yaml):
    #         self.model_info = yaml.load(self.current_model_yaml)

    def load_current_model_info(self):
        if self.current_model_yaml is not None and os.path.exists(self.current_model_yaml):
            with open(self.current_model_yaml) as yaml_file: 
                self.current_model_info = yaml.load(yaml_file, Loader=yaml.Loader)
            
    
    def download_model(self, model, path, backup=False):
        self.current_model_yaml = None
        self.current_model_info = None
        
        url = self._get_model_url(model)
        filename = url.split("/")[-1]
        my_file = os.path.join(path, filename)

        urllib.request.urlretrieve(url, my_file, download_cb)
        
        if backup:
            # print('> Creating backup of XML settings, Makefile, main.cpp')
            if os.path.exists("Makefile"):
                shutil.copyfile("Makefile", "Makefile-backup")
            if os.path.exists("main.cpp"):
                shutil.copyfile("main.cpp", "main-backup.cpp")
            if os.path.exists(os.path.join("config", "PhysiCell_settings.xml")):
                shutil.copyfile(os.path.join("config", "PhysiCell_settings.xml"), os.path.join("PhysiCell_settings-backup.xml"))
        old_path = os.getcwd()       
        os.chdir(path)
        # print('> Uncompressing the model')
        
        try:
            tar = tarfile.open(filename)
            tar.extractall()
            binary_name = [names for names in tar.getnames() if not names.endswith(".dll")][0]
            tar.close()
            os.remove(filename)
        
        except:
            print('! Error untarring the file')
            exit(1)
        
        st = os.stat(binary_name)
        os.chmod(binary_name, st.st_mode | stat.S_IEXEC)
        os.chdir(old_path)
        
        self.current_model_yaml = os.path.join(path, "model.yml")
        self.load_current_model_info()
        
    def _get_model_url(self, model):
        repo = self.models[model]
        latest_release = repo.get_releases().get_page(0)[0]
        assets = [asset.browser_download_url for asset in latest_release.assets]
    
        os_type = platform.system()
        suffix = None
        if os_type.lower() == 'darwin':
            suffix = "-macos.tar.gz"
        elif os_type.lower().startswith("win") or os_type.lower().startswith("msys_nt") or os_type.lower().startswith("mingw64_nt"):
            suffix = "-win.tar.gz"
        elif os_type.lower().startswith("linux"):
            suffix = "-linux.tar.gz"
        else:
            raise Exception("Your operating system seems to be unsupported. Please create an new issue at https://github.com/PhysiBoSS/PhysiBoSS/issues/ ")
    
        assets_os = [asset for asset in assets if asset.endswith(suffix)]
        if len(assets_os) == 0:
            raise Exception("Your operating system is not handled by this model.")
        elif len(assets_os) > 1:
            raise Exception("There are multiple versions of this model ??")

        return assets_os[0]    
    

def download_cb(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (percent, len(str(totalsize)), readsofar, totalsize)
        # sys.stderr.write(s)
        # if readsofar >= totalsize: # near the end
        #     sys.stderr.write("\n")
        # else: # total size is unknown
        #     sys.stderr.write("read %d\n" % (readsofar,))

# def download(model):
    
#     url = list_models[model] + mb_file
#     print('> Downloading from: ', url)
    
#     dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     print('> Loading into directory: ', dir_name)
    
#     my_file = os.path.join(dir_name, mb_file)
#     print('> File: ',my_file)
