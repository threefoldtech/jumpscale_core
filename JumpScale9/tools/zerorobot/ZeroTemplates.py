
from js9 import j
import sys
import inspect


TemplateCollectionClass= j.tools.zerorobot.models.TemplateCollection
TemplateModelClass= j.tools.zerorobot.models.TemplateModel

class ZeroTemplate(TemplateModelClass):

    def __init__(self, key="", new=False, collection=None):
        pass

class ZeroTemplates(TemplateCollectionClass):
    def _init(self):
        #is executed after the __init__ of the superclass
        self.__templateTmpDir=None

    @property
    def _templateTmpDir(self):
        if self.__templateTmpDir==None:
            self.__templateTmpDir=j.dirs.TMPDIR+"/actions"
            j.sal.fs.createDir(self.__templateTmpDir)
            if self.__templateTmpDir not in sys.path:
                sys.path.append(self.__templateTmpDir)
            j.sal.fs.touch(self.__templateTmpDir+"/__init__.py")
        return self.__templateTmpDir


    def load(self, path=None,repo=None):
        if path is None:
            repos = j.clients.git.getGitReposListLocal()
            for key, repo in repos.items():
                if key.startswith("zerorobot"):
                    self.load(repo=repo,path=repos[key])
        else:
            tpath = "%s/templates/" % path
            if j.sal.fs.exists(tpath):
                for tpath2 in j.sal.fs.listDirsInDir(tpath, recursive=True, dirNameOnly=False):
                    self._loadTemplate(repo=repo,path=tpath2)

    def _checkConfig(self,config):
        good=["recurring","log","job","timeout_policy"]
        for key,val in config.items():
            if key not in good:
                raise j.exceptions.Input("Cannot parse config, key '%s' in dict unknown, needs to be in %s"%(key,good))
        return config



    def _parse(self,code): #DO NOT TRY OTHER METHODS PLEASE, its easiest to do believe me (despiegk)
        state="start"
        out=""
        doc=""
        config=""
        for line in code.split("\n"):
            linestrip=line.strip()

            # print("state:%s '%s'"%(state,linestrip))

            if state=="start" and linestrip.startswith("def"):
                state="method"
                continue

            if state=="method":
                if linestrip.startswith("```") or linestrip.startswith("'''") or linestrip.startswith("\"\"\""):
                    state="doc"
                    continue

            if state=="doc" and (linestrip.startswith("config=") or linestrip.startswith("config =")):
                state="config"
                continue

            if state=="doc":
                if linestrip.startswith("```") or linestrip.startswith("'''") or linestrip.startswith("\"\"\""):
                    state="end"
                    continue
                else:
                    doc+=line+"\n"

            if state=="config":
                if line.strip().startswith("```") or line.strip().startswith("'''"):
                    state="doc"
                    continue
                else:
                    config+=line+"\n"

            if state in ["end","method"]:
                out+=line+"\n"

        out=j.data.text.strip(out)
        doc=j.data.text.strip(doc)
        config=j.data.text.strip(config)
        
        if config.strip()!="":
            try:
                config2= j.data.serializer.yaml.loads(config)
            except Exception as e:
                raise j.exceptions.Input("Cannot parse config out of method:%s\n%s"%(code,e))
            try:
                config2=self._checkConfig(config2)
            except Exception as e:
                raise j.exceptions.Input("Cannot parse config out of method:%s\n%s"%(code,e))
        else:
            config2={}
        return out,doc,config2
        


    def _loadTemplate(self, repo,path):
        if not [j.sal.fs.getBaseName(item) for item in j.sal.fs.listFilesInDir(path,False,filter="*.py")] == ["actions.py"]:
            raise j.exceptions.Input("Cannot find actions.py file, or too many python files")
        tpath=path+"/actions.py"
        name=j.sal.fs.getBaseName(path).replace(".","_")
        dpath=self._templateTmpDir+"/actions_%s.py"%name
        j.sal.fs.copyFile(tpath,dpath)
        Name=name[0].upper()+name[1:]
        exec("from actions_%s import Service as %s"%(name,Name))
        cl=eval("%s()"%(Name))

        for name,method in inspect.getmembers(cl, predicate=inspect.ismethod):
            code=inspect.getsource(method.__func__)
            try:
                code,doc,config=self._parse(code)
            except Exception as e:
                raise j.exceptions.Input("Cannot parse method:%s in path:%s\n%s"%(name,path,e))     

        from IPython import embed;embed(colors='Linux')       
            
        gitrepo=j.clients.git.get(repo)
        key="%s/%s"%(gitrepo.unc,name)
        from IPython import embed;embed(colors='Linux')
        templNew = ZeroTemplate(key,new=True,collection=self)
        templ._loadFromPath(path)
