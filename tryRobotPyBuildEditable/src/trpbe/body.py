import json

import subprocess
from pathlib import Path
from typing import NamedTuple
import os

import tomli
import click

os.environ["RPYBUILD_PARALLEL"] = "1"
os.environ["RPYBUILD_CC_LAUNCHER"] = "ccache"
os.environ["GCC_COLORS"] = "1"

class Repo(NamedTuple):
    name: str
    url: str
    branch: str

mostRepo = Repo(name='mostrobotpy', url='https://github.com/robotpy/mostrobotpy', branch='main')
repos = [
    Repo(name='robotpy-rev', url='https://github.com/robotpy/robotpy-rev', branch='main'),
    Repo(name='robotpy-navx', url='https://github.com/robotpy/robotpy-navx', branch='main'),
]

def processConfigEnv(tomlDict):
    if 'env' in tomlDict \
            and 'add_to_env' in tomlDict['env'] \
            and tomlDict['env']['add_to_env'] \
            and isinstance(tomlDict['env']['add_to_env'], list):
        for e in tomlDict['env']['add_to_env']:
            for k, v in e.items():
                os.environ[k] = v


def processConfig(ctx):
    tomlDict = ctx.obj['tomldict']




@click.group()
@click.option('--toml', default='trpbeConfig.toml', help='Configuration file.')
@click.pass_context
def cli(ctx, toml):
    ctx.ensure_object(dict)
    ctx.obj['toml'] = toml
    print(f"ctx.obj['toml']={ctx.obj['toml']}")

    with open(toml, "rb") as f:
        toml_dict = tomli.load(f)

        print(json.dumps(toml_dict))
        ctx.obj['tomldict'] = toml_dict

    processConfig(ctx)



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
    gitClone(mostRepo)
    for r in repos:
        gitClone(r)

cli.add_command(clone)

@click.command()
@click.pass_context
def installformostrobotpy(ctx):
    """Install python modules that mostrobotpy needs to build"""
    runCommand(['pip', 'install', 'robotpy'])
    runCommand(['pwd'], cwd=str(Path.cwd() / mostRepo.name))
    runCd(mostRepo.name)
    runCommand(['pip', 'install', '-r', 'rdev_requirements.txt'])
    runCommand(['pip', 'install', 'numpy'])
    runCd('..')

cli.add_command(installformostrobotpy)

@click.command()
@click.pass_context
def buildmostrobotpy(ctx):
    """Build mostrobotpy"""
    runCd(mostRepo.name)
    runCommandNoWaitForOutput(['./rdev.sh', 'ci', 'run'])
    runCd('..')

cli.add_command(buildmostrobotpy)


@click.command()
@click.pass_context
def installeditablemostrobotpy(ctx):
    """Build mostrobotpy"""
    runCd(mostRepo.name)
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
def doall(ctx):
    """run all steps"""
    ctx.invoke(clone)
    ctx.invoke(installformostrobotpy)
    ctx.invoke(buildmostrobotpy)
    ctx.invoke(uninstallpkgsformostrobotpyeditable)
    ctx.invoke(installeditablemostrobotpy)

cli.add_command(doall)

@click.command()
@click.pass_context
def trytoml(ctx):
    """try a toml file"""

    ctx.ensure_object(dict)
    toml = ctx.obj['toml']
    print(f"toml={toml}")
    print(f"tomldict={json.dumps(ctx.obj['tomldict'], indent=2)}")

cli.add_command(trytoml)

@click.command()
@click.pass_context
def dummy(ctx):
    print("Here in dummy...")

cli.add_command(dummy)


@click.command()
@click.pass_context
def two(ctx):
    ctx.invoke(dummy)
    ctx.invoke(trytoml)

cli.add_command(two)


def mainEntryPoint():
    cli()