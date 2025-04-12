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
        self.addRepos: list[Repo] = []

        if 'robotpyrepos' in tomlDict:
            if 'mostRobotPyRepo' in tomlDict['robotpyrepos'] \
                and isinstance(tomlDict['robotpyrepos']['mostRobotPyRepo'], dict):
                r = tomlDict['robotpyrepos']['mostRobotPyRepo']
                self.mostRepo = Repo(name=r['name'], url=r['url'], branch=r['branch'])

            if 'mostRobotPyAddRepos' in tomlDict['robotpyrepos'] \
                    and isinstance(tomlDict['robotpyrepos']['mostRobotPyAddRepos'], list):
                for r in tomlDict['robotpyrepos']['mostRobotPyAddRepos']:
                    self.addRepos.append(Repo(name=r['name'], url=r['url'], branch=r['branch']))





class Config(metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.ctx = None
        self.tomlFilename = None
        self.tomlDict = {}

    def initialize(self, ctx, tomlFilename:str):
        self.ctx = ctx
        self.tomlFilename = tomlFilename
        print(f"self.tomlFilename={self.tomlFilename}")

        with open(tomlFilename, "rb") as f:
            self.tomlDict = tomli.load(f)

            print(json.dumps(self.tomlDict, indent=4))

        self.env = ConfigEnv(self.tomlDict)
        self.robotpyrepos = ConfigRepos(self.tomlDict)



@click.group()
@click.option('--toml', default='trpbeConfig.toml', help='Configuration file.')
@click.pass_context
def cli(ctx, toml):
    ctx.ensure_object(dict)

    Config().initialize(ctx, toml)


def runCd(path:str):
    print(f'command=cd {path}')
    os.chdir(path)


def runCommand(args, cwd=None)->subprocess.CompletedProcess:
    print(f"command={' '.join(args)}")
    result = subprocess.run(
        args=args,
        check=True,
        cwd=cwd,
        input=None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(f"result=>\n{result.stdout}<=result\n")
    return result

def runCommandNoWaitForOutput(args, cwd=None):

    with subprocess.Popen(
            args=args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')  # process line here

    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)

def buildAddOnRobotPyPackageEditable(ctx, name:str):
    """Build mostrobotpy"""
    runCd(name)
    runCommandNoWaitForOutput(['python', 'setup.py', 'develop'])
    runCd('..')


@click.command()
@click.pass_context
def showenv(ctx):
    """Show environment variables"""
    runCommand(['env'])

cli.add_command(showenv)

def gitClone(repo: Repo):
    runCommand(['git', 'clone', repo.url])
    runCommand(["git", "-C", repo.name, "checkout", repo.branch])

@click.command()
@click.pass_context
def clone(ctx):
    """Clone the necessary repos"""
    gitClone(Config().robotpyrepos.mostRepo)
    for r in Config().robotpyrepos.addRepos:
        gitClone(r)

cli.add_command(clone)

@click.command()
@click.pass_context
def installformostrobotpy(ctx):
    """Install python modules that mostrobotpy needs to build"""
    runCommand(['pip', 'install', 'robotpy'])
    runCd(Config().robotpyrepos.mostRepo.name)
    runCommand(['pip', 'install', '-r', 'rdev_requirements.txt'])
    runCommand(['pip', 'install', 'numpy'])
    runCd('..')

cli.add_command(installformostrobotpy)


@click.command()
@click.pass_context
def installformostrobotpyeditable(ctx):
    """Install python modules that mostrobotpy needs to build editable"""
    runCommand(['pip', 'install', 'robotpy-build'])


cli.add_command(installformostrobotpyeditable)


@click.command()
@click.pass_context
def buildmostrobotpy(ctx):
    """Build mostrobotpy"""
    runCd(Config().robotpyrepos.mostRepo.name)
    if os.name == 'nt':
        runCommandNoWaitForOutput(['python', '-m', 'devtools', 'ci', 'run' ])
    else:
        runCommandNoWaitForOutput(['./rdev.sh', 'ci', 'run'])
    runCd('..')

cli.add_command(buildmostrobotpy)


@click.command()
@click.pass_context
def installeditablemostrobotpy(ctx):
    """Build mostrobotpy"""
    runCd(Config().robotpyrepos.mostRepo.name)
    if os.name == 'nt':
        # todo why doesn't this work?
        runCommandNoWaitForOutput(['python', '-m', 'devtools', 'develop' ])
    else:
        runCommandNoWaitForOutput(['./rdev.sh', 'develop'])
    runCd('..')


cli.add_command(buildmostrobotpy)

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
]

uninstallPackagesSet = set(uninstallPackages)

def getListOfInstalledPackagesFromPip()->list[dict[str, str]]:
    result: subprocess.CompletedProcess = runCommand(['pip', 'list', '--format', 'json'])
    firstLine = result.stdout.splitlines()[0]
    listOfInstalledPackagesAsDicts = json.loads(firstLine)
    return listOfInstalledPackagesAsDicts

@click.command()
@click.pass_context
def uninstallpkgsformostrobotpyeditable(ctx):
    countOfPackages = None
    totalCountOfPackages = None
    oldTotalCountOfPackages = None

    while countOfPackages is None or oldTotalCountOfPackages is None or (countOfPackages > 1 and totalCountOfPackages < oldTotalCountOfPackages):
        listOfInstalledPackagesAsDicts = getListOfInstalledPackagesFromPip()
        listOfInstalledPackages = [s['name'] for s in listOfInstalledPackagesAsDicts]
        oldTotalCountOfPackages = totalCountOfPackages
        totalCountOfPackages = len(listOfInstalledPackages)
        listOfInstalledPackagesSet = set(listOfInstalledPackages)

        uninstallThesePackages = list(uninstallPackagesSet.intersection(listOfInstalledPackagesSet))

        countOfPackages = len(uninstallThesePackages)

        for packageStr in uninstallThesePackages:
            runCommand(['pip', 'uninstall', '-y', packageStr])


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
    for r in Config().robotpyrepos.addRepos:
        buildAddOnRobotPyPackageEditable(ctx, r.name)

cli.add_command(buildAddOnRobotPyEditablePackages)



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
    ctx.invoke(uninstallpkgsformostrobotpyeditable)
    ctx.invoke(installeditablemostrobotpy)
    ctx.invoke(buildAddOnRobotPyEditablePackages)

cli.add_command(doeditable)




def mainEntryPoint():
    cli()