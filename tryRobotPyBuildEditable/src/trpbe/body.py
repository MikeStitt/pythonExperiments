import os
import tomli
import click
import json
import subprocess
from trpbe.singleton import Singleton

from pathlib import Path
from typing import NamedTuple

os.environ["RPYBUILD_PARALLEL"] = "1"
os.environ["RPYBUILD_CC_LAUNCHER"] = "ccache"
os.environ["GCC_COLORS"] = "1"

class Repo(NamedTuple):
    name: str
    url: str
    branch: str


class ConfigEnv():

    def __init__(self, tomlDict):
        self.envList = []

        if 'env' in tomlDict \
                and 'add_to_env' in tomlDict['env'] \
                and tomlDict['env']['add_to_env'] \
                and isinstance(tomlDict['env']['add_to_env'], list):
            for e in tomlDict['env']['add_to_env']:
                for k, v in e.items():
                    self.envList.append({k:v})
                    os.environ[k] = v


class ConfigRepos():

    def __init__(self, tomlDict):
        self.mostRepo: Repo|None = None
        self.addReposRobotPy: list[Repo] = []
        self.addFullRobotRepos: list[Repo] = []

        if 'robotpyrepos' in tomlDict:
            if 'mostRobotPyRepo' in tomlDict['robotpyrepos'] \
                and isinstance(tomlDict['robotpyrepos']['mostRobotPyRepo'], dict):
                r = tomlDict['robotpyrepos']['mostRobotPyRepo']
                self.mostRepo = Repo(name=r['name'], url=r['url'], branch=r['branch'])

            if 'mostRobotPyAddRepos' in tomlDict['robotpyrepos'] \
                    and isinstance(tomlDict['robotpyrepos']['mostRobotPyAddRepos'], list):
                for r in tomlDict['robotpyrepos']['mostRobotPyAddRepos']:
                    self.addReposRobotPy.append(Repo(name=r['name'], url=r['url'], branch=r['branch']))

            if 'addFullRobotRepos' in tomlDict['robotpyrepos'] \
                    and isinstance(tomlDict['robotpyrepos']['addFullRobotRepos'], list):
                for r in tomlDict['robotpyrepos']['addFullRobotRepos']:
                    self.addFullRobotRepos.append(Repo(name=r['name'], url=r['url'], branch=r['branch']))




class Config(metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.ctx = None
        self.tomlFilename = None
        self.tomlDict = {}

    def initialize(self, ctx, tomlFilename:str, clone:bool, quiet:bool):
        self.ctx = ctx
        self.tomlFilename = tomlFilename
        self.clone = clone
        self.quiet = quiet
        if not self.quiet:
            print(f"self.tomlFilename={self.tomlFilename}")

        with open(tomlFilename, "rb") as f:
            self.tomlDict = tomli.load(f)

            if not self.quiet:
                print(json.dumps(self.tomlDict, indent=4))

        self.env = ConfigEnv(self.tomlDict)
        self.robotpyrepos = ConfigRepos(self.tomlDict)



@click.group()
@click.option('--toml', default='trpbeConfig.toml', help='Configuration file.')
@click.option('--clone/--no-clone', default=True, help='Clone/checkout the repos.')
@click.option('--quiet/--no-quiet', default=False, help='Do not print tool output.')
@click.pass_context
def cli(ctx, toml, clone, quiet):
    ctx.ensure_object(dict)

    Config().initialize(ctx, toml, clone, quiet)


def runCd(path:str):
    print(f'command=cd {path}')
    os.chdir(path)


def runCommand(args, cwd=None, shell=True)->subprocess.CompletedProcess:
    print(f"command={args}")
    result = subprocess.run(
        args=args,
        check=True,
        cwd=cwd,
        shell=True,
        input=None,
        text=True,
        encoding='utf-8',
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if not Config().quiet:
        print(f"result=>\n{result.stdout}<=result\n")
    return result

def runCommandNoWaitForOutput(args, cwd=None, shell=False):

    print(f"command={args}")
    with subprocess.Popen(
            args=args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=shell,
            encoding="utf-8",
            errors="replace",
            bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            if not Config().quiet:
                print(line, end='')  # process line here

    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)

def buildAddOnRobotPyPackageEditable(ctx, name:str):
    """Build add on robot py repos editable"""
    runCd(name)
    runCommandNoWaitForOutput('python setup.py develop -N', shell=True)
    runCd('..')

def syncAFullRobotRepo(ctx, name:str):
    """sync full robotpy repos"""
    runCd(name)
    runCommandNoWaitForOutput('python -m robotpy sync', shell=True)
    runCd('..')


@click.command()
@click.pass_context
def showenv(ctx):
    """Show environment variables"""
    runCommand('env')

cli.add_command(showenv)

def gitClone(repo: Repo):
    runCommand(f'git clone {repo.url} {repo.name}')
    runCommand(f"git -C {repo.name} checkout {repo.branch}")

@click.command()
@click.pass_context
def clone(ctx):
    """Clone the necessary repos"""
    if Config().clone:
        gitClone(Config().robotpyrepos.mostRepo)
        for r in Config().robotpyrepos.addReposRobotPy:
            gitClone(r)
        for r in Config().robotpyrepos.addFullRobotRepos:
            gitClone(r)
    else:
        print("Clone is disabled")

cli.add_command(clone)

@click.command()
@click.pass_context
def installformostrobotpy(ctx):
    """Install python modules that mostrobotpy needs to build"""
    runCommand('pip install robotpy')
    runCd(Config().robotpyrepos.mostRepo.name)
    runCommand('pip install -r rdev_requirements.txt')
    runCommand('pip install numpy')
    runCd('..')

cli.add_command(installformostrobotpy)


@click.command()
@click.pass_context
def installformostrobotpyeditable(ctx):
    """Install python modules that mostrobotpy needs to build editable"""
    runCommand('pip install robotpy-build')


cli.add_command(installformostrobotpyeditable)


@click.command()
@click.pass_context
def buildmostrobotpy(ctx):
    """Build mostrobotpy"""
    runCd(Config().robotpyrepos.mostRepo.name)
    runCommandNoWaitForOutput('python -m devtools ci run', shell=True )
    runCd('..')

cli.add_command(buildmostrobotpy)


@click.command()
@click.pass_context
def installeditablemostrobotpy(ctx):
    """Build editable mostrobotpy"""
    runCd(Config().robotpyrepos.mostRepo.name)
    runCommandNoWaitForOutput('python -m devtools develop', shell=True)
    runCd('..')


cli.add_command(installeditablemostrobotpy)

uninstallPackages = [
    "pyntcore",
    "robotpy-apriltag",
    "robotpy-cscore",
    "robotpy-hal",
    "robotpy-halsim-ds-socket",
    "robotpy-halsim-gui",
    "robotpy-halsim-ws",
    "robotpy-romi",
    "robotpy-wpimath",
    "robotpy-wpinet",
    "robotpy-wpiutil",
    "robotpy-xrp",
    "wpilib",
    "robotpy-rev",
]

uninstallPackagesSet = set(uninstallPackages)

def getListOfInstalledPackagesFromPip()->list[dict[str, str]]:
    result: subprocess.CompletedProcess = runCommand('pip list --format json')
    firstLine = result.stdout.splitlines()[0]
    listOfInstalledPackagesAsDicts = json.loads(firstLine)
    return listOfInstalledPackagesAsDicts

@click.command()
@click.pass_context
def uninstallpkgsformostrobotpyeditable(ctx):
    countOfPackages = None
    totalCountOfPackages = None
    oldTotalCountOfPackages = None

    uninstallPackagesSuperSet = uninstallPackagesSet.update([ r.name for r in Config().robotpyrepos.addReposRobotPy])

    while countOfPackages is None or oldTotalCountOfPackages is None or (countOfPackages > 1 and totalCountOfPackages < oldTotalCountOfPackages):
        listOfInstalledPackagesAsDicts = getListOfInstalledPackagesFromPip()
        listOfInstalledPackages = [s['name'] for s in listOfInstalledPackagesAsDicts]
        oldTotalCountOfPackages = totalCountOfPackages
        totalCountOfPackages = len(listOfInstalledPackages)
        listOfInstalledPackagesSet = set(listOfInstalledPackages)

        uninstallThesePackages = list(uninstallPackagesSuperSet.intersection(listOfInstalledPackagesSet))

        countOfPackages = len(uninstallThesePackages)

        for packageStr in uninstallThesePackages:
            runCommand(f'pip uninstall -y {packageStr}')


cli.add_command(uninstallpkgsformostrobotpyeditable)


@click.command()
@click.pass_context
def buildreveditable(ctx):
    """build robotpy-rev editable"""
    buildAddOnRobotPyPackageEditable(ctx, 'robotpy-rev')

cli.add_command(buildreveditable)

@click.command()
@click.pass_context
def buildnavxeditable(ctx):
    """build robotpy-navx editable"""
    buildAddOnRobotPyPackageEditable(ctx, 'robotpy-navx')

cli.add_command(buildreveditable)

@click.command()
@click.pass_context
def buildAddOnRobotPyEditablePackages(ctx):
    """build robotpy add on packages editable"""
    for r in Config().robotpyrepos.addReposRobotPy:
        buildAddOnRobotPyPackageEditable(ctx, r.name)

cli.add_command(buildAddOnRobotPyEditablePackages)


@click.command()
@click.pass_context
def syncFullRobotRepos(ctx):
    """build robotpy add on packages editable"""
    for r in Config().robotpyrepos.addFullRobotRepos:
        syncAFullRobotRepo(ctx, r.name)

cli.add_command(syncFullRobotRepos)


@click.command()
@click.pass_context
def exp(ctx):
    """try an experiment"""
    runCommandNoWaitForOutput("ls")
cli.add_command(exp)



@click.command()
@click.pass_context
def dobuildall(ctx):
    """run all steps"""
    ctx.invoke(clone)
    ctx.invoke(installformostrobotpy)
    ctx.invoke(buildmostrobotpy)

cli.add_command(dobuildall)

@click.command()
@click.pass_context
def doeditable(ctx):
    """run all steps"""
    ctx.invoke(clone)
    ctx.invoke(installformostrobotpy)
    ctx.invoke(installformostrobotpyeditable)
    ctx.invoke(syncFullRobotRepos)
    ctx.invoke(uninstallpkgsformostrobotpyeditable)
    ctx.invoke(installeditablemostrobotpy)
    ctx.invoke(buildAddOnRobotPyEditablePackages)

cli.add_command(doeditable)




def mainEntryPoint():
    cli()