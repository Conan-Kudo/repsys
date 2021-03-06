from RepSys import Error, config
from RepSys.rpmutil import get_pkg_tag, clone
from RepSys.util import execcmd
from RepSys.git import GIT
from os.path import join
import re

class GitFedora(object):
    binrepo = "https://src.fedoraproject.org/repo/pkgs/"
    def __init__(self, package):
        self._package = package
        self._login = config.get("fedora", "login")
        if self._login:
            self._repourl = "ssh://"+self._login+"@pkgs.fedoraproject.org/rpms/"+self._package
        else:
            self._repourl = "https://src.fedoraproject.org/git/rpms/"+self._package+GIT.vcs_dirname
        self._git = GIT(url=self._repourl)

    def clone_repository(self):
        self._git.clone()
        self.download_sources()

        return True

    def download_sources(self):
        f = open(join(self._git.path, "sources"))
        downloader = config.get("global", "download-command",
                "wget -c -O '$dest' $url").strip("'$dest' $url").split()
        for line in f.readlines():
            fields = line.split()
            binurl = self.binrepo+"/"+self._package+"/"
            if len(fields) == 2:
                checksum, source = fields
                binurl += source+"/"
            else:
                pattern = re.compile(r'^(.*) \((.*)\) = (.*)')
                match = pattern.match(line)
                hashtype = match.group(1)
                source = match.group(2)
                checksum = match.group(3)
                binurl += source+"/"+hashtype.lower()+"/"

            binurl += checksum+"/"+source
            cmd = downloader + [join(self._git.path,source), binurl]
        f.close()

        status, output = execcmd(cmd, show=True)
        if status == 0:
            return True
        else:
            raise Error("Failed downloading %s, retcode: %d err: %s\n", status, output)
