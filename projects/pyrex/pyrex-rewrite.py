#!/usr/bin/env python3
import os
import subprocess
import argparse
import threading
parser = argparse.ArgumentParser(
    description='Pyrex4 system manager. Built with the intention of simplifying package distribution via declarative initialisation of nix, pacman, flatpak, and npm in one function.', 
    epilog='Use nix.[unit], aur.[unit], flatpak.[unit], or npm.[unit] to specify source.\nexample: pyrex --station aur.firefox')
parser.add_argument('-p', '--prep', dest='install', action='store_true', help='Install units')
parser.add_argument('-t', '--trash', dest='remove', action='store_true', help='Remove units')
parser.add_argument('-o', '--overhaul', dest='update', action='store_true', help='Update system')
parser.add_argument('-f', '--find', dest='find', action='store_true', help='find units')
parser.add_argument('-fs', '--from-scratch', dest='source', action='store_true', help='Build and install unit from source (Nix only for now)')
parser.add_argument('-cc', '--contain', dest='shell', action='store_true', help='Install unit in non-persistent shell environment. (nix only for now)')
parser.add_argument('--garbage-disposal', dest='collectGarbage', action='store_true', help='Collect unused units/paths (nix only for now)')
parser.add_argument('--compact', dest='compactor', action='store_true', help='Consolidate shared dependencies to save storage and optimize file paths at the expense of less reproducibility. (Set to true per install by default)')
parser.add_argument('-v', '--version', dest='version', action='store_true', help='Show version number')
parser.add_argument(dest='stdinn', action='append', nargs='?')

# user configs 
class env_vars():
    autoCompactor = True
    autoCollectGarbage = True
    autoRebase = False
    launcherDir = '$HOME/.local/share/applications/'

args = parser.parse_args()
class cliParser():
    initarg = '%s' % (args.stdinn)
    noLbracket = initarg.replace('[', '')
    noRbracket = noLbracket.replace(']', '')
    noQuotes = noRbracket.replace("'", "")
    specin = noQuotes

def compactor():
    subprocess.Popen(['nix-store', '--optimise', '--log-format', 'bar-with-logs'])

def collectGarbage():
    print('Cleaning up workspace/')
    subprocess.Popen(['nix-collect-garbage', '-d', '--log-format', 'bar-with-logs'])
    #os.system('nix-collect-garbage')

def nixFind():
    unit = cliParser.specin.replace('nix.', '')
    if '.installed' in cliParser.specin:
        if unit == 'installed':
            print('Installed nixpkgs:')
            os.system('nix-env -q --installed >> ~/.nix-installed.txt')
        else:
            noInstall = unit.replace('.installed', '')
            os.system('nix-env -q %s --installed >> ~/.nix-installed.txt' % (noInstall))
        os.system('cat ~/.nix-installed.txt')
        os.system('rm ~/.nix-installed.txt')
        exit()
    else:
        os.system('nix-env -q %s --available' % (unit)) #>> ~/.nix-search.txt' % (unit))
        # print('Available nixpkgs:')
        # os.system('cat ~/.nix-search.txt')
        # os.system('rm ~/.nix-search.txt')
        exit()

def aurFind():
    unit = cliParser.specin.replace('aur.', '')
    if '.installed' in cliParser.specin:
        subprocess.Popen(['yay', '-Ss'])
        exit()
    else:
        #print('Available AUR units:')
        aurfind = subprocess.Popen(['yay', '-Ss', '%s' % (unit)])
        output = aurfind.communicate()[0]
        exit()

def flatpakFind():
    unit = cliParser.specin.replace('flatpak.', '')
    if '.installed' in cliParser.specin:
        subprocess.Popen(['flatpak', 'list'])
        exit()
    else:
        print('Available Flatpak units:')
        os.system('flatpak search %s' % (unit))
        exit()

def npmFind():
    unit = cliParser.specin.replace('npm.', '')
    if '.installed' in cliParser.specin:
        subprocess.Popen(['npm', 'list'])
        exit()
    else:
        print('Available node.js units:')
        os.system('npm search %s' % (unit))
        exit()

def nixBuild():
    if args.shell == True:
        if 'nix.' in cliParser.specin:
            unit = cliParser.specin.replace('nix.', '')
            subprocess.Popen(['nix-shell', '-p' '--option substitute', 'false', '--log-format', 'bar-with-logs', '%s' % (unit)])
            exit()
        elif 'nur.' in cliParser.specin:
            subprocess.Popen(['nix-shell', '-p', '--option', 'substitute', 'false', '--log-format', 'bar-with-logs', '%s' % (cliParser.specin)])
            #os.system('nix-shell -p --option substitute false --log-format bar-with-logs %s' % (cliParser.specin))
            exit()
    else:
        if 'nix.' in cliParser.specin:
            unit = cliParser.specin.replace('nix.', '')
            subprocess.Popen(['nix-env', '-iA', '--option', 'substitute', 'false', '--log-format', 'bar-with-logs', 'nixpkgs.%s' % (unit)])
            #os.system('nix-env -iA --option substitute false --log-format bar-with-logs nixpkgs.%s' % (unit))
            exit()
        elif 'nur.' in cliParser.specin:
            subprocess.Popen(["nix-env", "-f", "'<nixpkgs>'", "-iA", "--option", "substitute", "false", "--log-format", "bar-with-logs", "%s" % (cliParser.specin)])
            #os.system("nix-env -f '<nixpkgs>' -iA --option substitute false --log-format bar-with-logs %s" % (cliParser.specin))
            exit()

def nixInstall():
    if args.shell == True:
        if 'nix.' in cliParser.specin:
            unit = cliParser.specin.replace('nix.', '')
            os.system('nix-shell -p --log-format bar-with-logs %s' % (unit))
            exit()
        elif 'nur.' in cliParser.specin:
            os.system('nix-shell -p --log-format bar-with-logs %s' % (cliParser.specin))
            exit()
    else:
        if 'nix.' in cliParser.specin:
            unit = cliParser.specin.replace('nix.', '')
            subprocess.Popen(['nix-env', '-iA', '--log-format', 'bar-with-logs', 'nixpkgs.%s' % (unit)])
            if env_vars.autoRebase == True:
                os.system('nix-build "<nixpkgs>" -A %s --check' % (unit))
            if env_vars.autoCompactor == True:
                compactor()
            exit()
        else:
            print('Unknown repo in %s' % (cliParser.specin))

def aurInstall():
    if 'aur.' in cliParser.specin:
        unit = cliParser.specin.replace('aur.', '')
        os.system('yay -S %s' % (unit))
        exit()
    else:
        print('Unknown repo in %s' % (cliParser.specin))

def flatpakInstall():
    if 'flatpak.' in cliParser.specin:
        unit = cliParser.specin.replace('flatpak.', '')
        subprocess.Popen(['flatpak install', '%s' % (unit)])
        exit()
    else:
        print('Unknown repo in %s' % (cliParser.specin))

def nixRemove():
    if 'nix.' in cliParser.specin:
        unit = cliParser.specin.replace('nix.', '')
        subprocess.Popen(['nix-env', '-e', '--log-format', 'bar-with-logs', '%s' % (unit)])
        if env_vars.autoCollectGarbage == True:
            collectGarbage()
        exit()
    else:
        print('Unknown repo in %s' % (cliParser.specin))

def aurRemove():
    if 'aur.' in cliParser.specin:
        unit = cliParser.specin.replace('aur.', '')
        subprocess.Popen(['yay', '-R', '%s' % (unit)])
        exit()
    else:
        print('Unknown repo in %s' % (cliParser.specin))

def flatpakRemove():
    if 'flatpak.' in cliParser.specin:
        unit = cliParser.specin.replace('flatpak.', '')
        subprocess.Popen(['flatpak', 'remove', '%s' % (unit)])
        exit()
    else:
        print('Unknown repo in %s' % (cliParser.specin))

def nixUpdate():
    if args.source == True:
        subprocess.Popen(['nix-channel', '--update', '--log-format', 'bar-with-logs'])
        subprocess.Popen(['nix-env', '--upgrade', '--option', 'substitute', 'false', '--log-format', 'bar-with-logs'])
    else:
        subprocess.Popen(['nix-channel', '--update', '--log-format', 'bar-with-logs'])
        subprocess.Popen(['nix-env', '--upgrade', '--log-format', 'bar-with-logs'])

def aurUpdate():
    aurUpdate = subprocess.Popen(['yay', '-y'])
    output = aurUpdate.communicate()[0]

def flatpakUpdate():
    subprocess.Popen(['flatpak', 'update', '-y'])

if args.install == True:
    if 'nix.' in cliParser.specin:
        nixInstall()
        exit
    if 'aur.' in cliParser.specin:
        aurInstall()
        exit
    if 'flatpak.' in cliParser.specin:
        flatpakInstall()
        exit
if args.remove == True:
    if 'nix.' in cliParser.specin:
        nixRemove()
        exit()
    if 'aur.' in cliParser.specin:
        aurRemove()
        exit()
    if 'flatpak.' in cliParser.specin:
        flatpakRemove()
        exit()
if args.update == True:
    if 'nix' in cliParser.specin:
        nixUpdate()
        exit()
    if 'aur' in cliParser.specin:
        aurUpdate()
        exit()
    if 'flatpak' in cliParser.specin:
        flatpakUpdate()
        exit()
    else:
        nixUpdateThread = threading.Thread(target=nixUpdate)
        aurUpdateThread = threading.Thread(target=aurUpdate)
        flatpakUpdateThread = threading.Thread(target=flatpakUpdate)
        
        nixUpdateThread.start()
        aurUpdateThread.start()
        flatpakUpdateThread.start()
        exit()
if args.find == True:
    if 'nix.' in cliParser.specin:
        nixFind()
        exit()
    if 'aur.' in cliParser.specin:
        aurFind()
        exit()
    if 'flatpak.' in cliParser.specin:
        flatpakFind()
        exit()

if args.collectGarbage == True:
    collectGarbage()
if args.version == True:
    print('Pyrex System Manager v4.8.23')