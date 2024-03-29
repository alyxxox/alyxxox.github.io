#!/usr/bin/env python3
import os
import subprocess
import argparse
import threading
parser = argparse.ArgumentParser(
    description='Pyrex2 system manager. Built with the intention of simplifying package distribution via declarative initialisation of nix, pacman, flatpak, and npm in one function.', 
    epilog='Use nix.[unit], aur.[unit], flatpak.[unit], or npm.[unit] to specify source.\nexample: pyrex --station aur.firefox')
parser.add_argument('-s', '--station', dest='install', action='store_true', help='Install units')
parser.add_argument('-t', '--trash', dest='remove', action='store_true', help='Remove units')
parser.add_argument('-o', '--overhaul', dest='update', action='store_true', help='Update system')
parser.add_argument('-f', '--find', dest='find', action='store_true', help='find units')
parser.add_argument('-rr', '--rebase', dest='source', action='store_true', help='Build and install unit from source (Nix only for now)')
parser.add_argument('-gc', '--garbage-collector', dest='collectGarbage', action='store_true', help='Collect unused units/paths (nix only for now)')
parser.add_argument('-c', '--compactor', dest='compactor', action='store_true', help='Consolidate shared dependencies to save storage and optimize file paths at the expense of less reproducibility. (Set to true per install by default)')
parser.add_argument('--shell', dest='shell', action='store_true', help='Install unit in non-persistent shell environment. (nix only for now)')
parser.add_argument('-v', '--version', dest='version', action='store_true', help='Show version number')
parser.add_argument(dest='stdinn', action='append', nargs='?')

# user configs 
class configs():
    autoCompactor = True
    autoCollectGarbage = True
    autoRebase = False

args = parser.parse_args()
class cliParser():
    initarg = '%s' % (args.stdinn)
    noLbracket = initarg.replace('[', '')
    noRbracket = noLbracket.replace(']', '')
    noQuotes = noRbracket.replace("'", "")
    specin = noQuotes
# add custom maintained installed units list >>
def compactor():
    subprocess.Popen(['nix-store', '--optimise', '--log-format', 'bar-with-logs'])
if args.install == True:
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
            if configs.autoRebase == True:
                os.system('nix-build "<nixpkgs>" -A %s --check' % (unit))
            if configs.autoCompactor == True:
                compactor()
            exit()
        elif 'aur.' in cliParser.specin:
            unit = cliParser.specin.replace('aur.', '')
            os.system('yay -S %s' % (unit))
            exit()
        elif 'nur.' in cliParser.specin:
            #getting issue with string formatting when using subprocess over os.system
            os.system("nix-env -f '<nixpkgs>' -iA --log-format bar-with-logs %s" % (cliParser.specin))
            subprocess.Popen(['nix-store', '--optimize', '--log-format', 'bar-with-logs'])
            exit()
        elif 'flatpak.' in cliParser.specin:
            unit = cliParser.specin.replace('flatpak.', '')
            subprocess.Popen(['flatpak install', '%s' % (unit)])
            exit()
        elif 'npm.' in cliParser.specin:
            unit = cliParser.specin.replace('npm.', '')
            subprocess.Popen(['npm install', '%s' % (unit)])
            exit()
if args.compactor == True:
    compactor()
    exit()
def collectGarbage():
    print('Cleaning up workspace/')
    subprocess.Popen(['nix-collect-garbage', '-d', '--log-format', 'bar-with-logs'])
    #os.system('nix-collect-garbage')
if args.source == True:
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
if args.remove == True:
    if 'nix.' in cliParser.specin:
        unit = cliParser.specin.replace('nix.', '')
        subprocess.Popen(['nix-env', '-e', '--log-format', 'bar-with-logs', '%s' % (unit)])
        if configs.autoCollectGarbage == True:
            collectGarbage()
        exit()
    elif 'aur.' in cliParser.specin:
        unit = cliParser.specin.replace('aur.', '')
        subprocess.Popen(['yay', '-R', '%s' % (unit)])
        exit()
    elif 'flatpak.' in cliParser.specin:
        unit = cliParser.specin.replace('flatpak.', '')
        subprocess.Popen(['flatpak', 'remove', '%s' % (unit)])
        exit()
    elif 'npm.' in cliParser.specin:
        unit = cliParser.specin.replace('npm.', '')
        os.system('npm remove %s' % (unit))
        exit()
class update():
    def nix():
        if args.source == True:
            subprocess.Popen(['nix-channel', '--update', '--log-format', 'bar-with-logs'])
            subprocess.Popen(['nix-env', '--upgrade', '--option', 'substitute', 'false', '--log-format', 'bar-with-logs'])
        else:
            subprocess.Popen(['nix-channel', '--update', '--log-format', 'bar-with-logs'])
            subprocess.Popen(['nix-env', '--upgrade', '--log-format', 'bar-with-logs'])
    def aur():
        aurUpdate = subprocess.Popen(['yay', '-y'])
        output = aurUpdate.communicate()[0]
    def flatpak():
        subprocess.Popen(['flatpak', 'update', '-y'])
    def npm():
        subprocess.Popen(['npm', 'update'])
nixUpdate = threading.Thread(target=update.nix)
aurUpdate = threading.Thread(target=update.aur)
flatpakUpdate = threading.Thread(target=update.flatpak)
npmUpdate = threading.Thread(target=update.npm)
if args.update == True:
    if cliParser.specin == 'None':
        aurUpdate.start()
        nixUpdate.start()
        flatpakUpdate.start()
        npmUpdate.start()
        exit()
    elif cliParser.specin == 'nix':
        update.nix()
        exit()
    elif cliParser.specin == 'aur':
        update.aur()
        exit()
    elif cliParser.specin == 'flatpak':
        update.flatpak()
        exit()
    elif cliParser.specin == 'npm':
        update.npm()
        exit()
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
if args.find == True:
    if 'nix.' in cliParser.specin:
        nixFind()
    elif 'aur.' in cliParser.specin:
        aurFind()
    elif 'flatpak.' in cliParser.specin:
        flatpakFind()
    elif 'npm.' in cliParser.specin:
        npmFind()
    elif cliParser.specin == 'installed':
        def listunits():
            print('To avoid flooding terminal with text, pacman units are retained to their own command. Use "pyrex -q aur.installed" to see those units.\n')
            os.system('echo "Nix units:" >> ~/.pkgs-installed.txt')
            os.system('nix-env -q --installed >> ~/.pkgs-installed.txt')
            #os.system('echo "\nFlatpaks:" >> ~/.pkgs-installed.txt')
            os.system('echo "\node.js units:" >> ~/.pkgs-installed.txt')
            os.system('npm list >> ~/.pkgs-installed.txt')
            os.system('cat ~/.pkgs-installed.txt')
            print('Flatpaks:')
            os.system('flatpak list') #>> ~/.pkgs-installed.txt')
            os.system('rm ~/.pkgs-installed.txt') 
        listunits()
        exit()
    else:
        nixFind()
        #aurSearch.start()
        flatpakFind()
        npmFind()

if args.collectGarbage == True:
    collectGarbage()
    exit()
if args.version == True:
    print('Pyrex2 Version 3.2')
    exit()
elif cliParser.specin == 'None':
    subprocess.Popen(['pyrex', '-h'])