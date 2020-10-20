#!/usr/bin/env python3
from crccheck.crc import CrcArc
from crccheck.checksum import Checksum16
import os, os.path
import sys, getopt
from itemlist import *
import argparse # native command line argument module superior to getopt

__doc__ = """
Xenoblade Chronicles (Wii) Colony 6 Save Editor

XC1SaveEdit.py -s <savefile> -c <command>
savefile: monado01 monado02 monado03
command:  MaxGold ListGems ListItems Housing1 Commerce2 Nature3 Special4 Replica5
ex: to add the items needed to rebuild commerce level 3 in Colony 6:
python3 XC1SaveEdit.py -s monado01 -c Commerce3
"""

# global variables
debug = False # Debug mode, deactivated by default

def readsave(savefile):
    with open(savefile, 'rb') as f:
        f.seek(0x22)
        r = f.read(8)
        a = int.from_bytes(r[2:4], "big")
        print('Save time: {}/{}/{} {}:{}:{}'.format(a, r[5], r[7], r[6], r[0], r[1]))
    
        f.seek(0xb264, 0)
        psn = f.read(4)
        psn = psn.hex()
        print('Location:', Maps.get(psn, "location unknown"))


def gold(savefile,gold_amount=None):
    """Sets Gold amount to maximum 99999997 by default or to a given value gold_amount"""
    gold_offset = 0x24048
    if gold_amount is None:
        gold_amount = 99999997 # 0x05f5e0fd
    with open(savefile, 'r+b') as g:
        g.seek(gold_offset)
        g.write(gold_amount.to_bytes(4, "big")) 
    if gold_amount == 99999997:
        print('Max gold added : 99 999 997')
    else:
        print('Gold amount is now : {}'.format(gold_amount))

def getGold(savefile):
    gold_offset = 0x24048
    gold_amount = None
    with open(savefile, 'rb') as g:
        g.seek(gold_offset)
        r = g.read(4)
        gold_amount = int.from_bytes(r[:4], "big")
    print('Current Gold amount : {}'.format(gold_amount))

def crc(savefile):
    offsets =  [0x20, 0xA030, 0xB260, 0x11EB0, 0x11EE0, 0x11F30, 0x11F60, 0x24090, 0x240C0, 0x240F0, 0x244A0, 0x248B0]
    sizes = [0x9C80, 0x1214, 0x6C28, 0xC, 0x34, 0x10, 0x12120, 0x10, 0x10, 0x384, 0x234, 0x40]
    section = ["THUM", "FLAG", "GAME", "TIME",  "PCPM",  "CAMD",  "ITEM",  "WTHR",  "SNDS",  "MINE",  "TBOX",  "OPTD"]
    for i in range(12):
        with open(savefile, 'rb') as f:
            f.seek(offsets[i]-4)
            r = f.read(sizes[i]+4) 
        crc_orig = int.from_bytes(r[:4], "big")
        data = r[4:]
        crc_calc = CrcArc.calc(data)
        if crc_calc != crc_orig:
            print(section[i], ': CRC FIXED') 
            with open(savefile, 'r+b') as g:
                g.seek(offsets[i]-4)
                g.write(crc_calc.to_bytes(4, "big")) 


def colony6(savefile, add):
    with open(savefile, 'rb') as f:  
        nb = 0
        myCollectable = {}
        f.seek(0x22118, 0)
        for i in range(300):
            r = f.read(8)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0': 
                Id = int(x[:3], 16)
                Qte = int(x[12:-2], 16)
                myCollectable.update( {Id : Qte} )
                print('{:3}  {}'.format(Qte, Collectable[Id]))
                nb += 1   
        print("Collectable:", nb)
    
        nb = 0
        myMaterial = {}
        f.seek(0x22a78, 0)
        for i in range(150):
            r = f.read(8)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0': 
                Id = int(x[:3], 16)
                Qte = int(x[12:-2], 16)
                myMaterial.update( {Id : Qte} )
                print('{:3}  {}'.format(Qte, Material[Id]))
                nb += 1
        print("Material:", nb)
     
        nb = 0
        f.seek(0x233d8, 0)
        for i in range(300):
            r = f.read(8)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0': 
                Id = int(x[:3], 16)
                Qte = int(x[12:-2], 16)
                print('{:3}  {}'.format(Qte, KeyItem[Id]))
                nb += 1
        print("KeyItem:", nb)
    
    addMaterial = Colony6[add][1]
    addCollectible = Colony6[add][2]
    for key, value in addMaterial.items():
        if key in myMaterial:
            if myMaterial[key] < value:
                myMaterial.update({key: value})
        else:
            myMaterial.update({key: value})
    
    for key, value in addCollectible.items():
        if key in myCollectable:
            if myCollectable[key] < value:
                myCollectable.update({key: value})
        else:
            myCollectable.update({key: value})
        
    if len(myMaterial.items()) > 150:
        print("# Too many materials in inventory, aborting")
        sys.exit()
    if len(myCollectable.items()) > 300:
        print("# Too many collectables in inventory, aborting")
        sys.exit()
    
    pick = 2
    even = 0
    newMaterial = ''
    i = 0
    for item, cnt in myMaterial.items():
        i += 1
        pick += 1
        even += 2   
        itm = str(hex(item)[-3:])
        newMaterial += itm + 'b' + '{:03x}'.format(even) + '00' + '{:03x}'.format(pick) + '{:02x}'.format(cnt) +'00'
    
    pick = 2
    even = 0
    newCollectable = ''
    i = 0
    for item, cnt in myCollectable.items():
        i += 1
        pick += 1
        even += 2   
        itm = str(hex(item)[-3:])
        newCollectable += itm + 'b' + '{:03x}'.format(even) + '00' + '{:03x}'.format(pick) + '{:02x}'.format(cnt) +'00'
    
    newCollectable += (4800-len(newCollectable)) * '0'
    newMaterial += (2400-len(newMaterial)) * '0'
    with open(savefile, 'r+b') as f:
        f.seek(0x22118, 0)
        f.write(bytearray.fromhex(newCollectable))
        f.seek(0x22a78, 0)
        f.write(bytearray.fromhex(newMaterial))
    print('Items added for', add)

def gems(savefile):
    with open(savefile, 'r+b') as f:
        myGems = []
        f.seek(0x206D8, 0)
        for i in range(300):
            r = f.read(16)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0': 
                Id = int(x[:3], 16)
                #Gems = Gem[Id]
                EffId = int(x[24:27], 16)
                Effects = Effect[EffId]
                Pct1 = int(int(x[19:22], 16)/4) 
                Pct2 = int(x[22:24], 16)
                GemsLvl = GemLvl.get(int(x[6:8], 16), "?")
                Elements = Element.get(int(x[5:6], 16), "?")
                if Pct2 > 0x8f: Pct2 -= 0x80
                if Pct2 == 0 or Pct2 == 128:        
                    myGems.append("{:19} LVL: {:3} Effect: {:6} Type: {}".format(Effects, GemsLvl, str(Pct1), Elements))
                elif Pct1 == 0:
                    myGems.append("{:19} LVL: {:3} Effect: {:6} Type: {}".format(Effects, GemsLvl, str(Pct2), Elements))
                else:
                    myGems.append("{:19} LVL: {:3} Effect: {:6} Type: {}".format(Effects, GemsLvl, str(Pct1) +'/'+ str(Pct2), Elements))
    
    myGems.sort()
    for g in myGems:
        print(g)
    print("Gems:",len(myGems))


def listItems(savefile, filter=None):
    """List of all items in the save file.
    If filter is a valid name, then print it only."""

    if filter is not None: # test if given filter is a valid name
        filterItem = checkItemName(filter)
        if filterItem is None:
            print('{} is not a valid item name. Aborting.'.format(filter))
            sys.exit()
    with open(savefile, 'rb') as f:
        nb = 0
        myCollectable = {}
        f.seek(0x22118, 0)
        for i in range(300):
            r = f.read(8)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0':
                Id = int(x[:3], 16)
                Qte = int(x[12:-2], 16)
                myCollectable.update({Id: Qte})
                if filter is None or filter == Collectable[Id]: # print only is no filter or valid name
                    print('{:3}  {}'.format(Qte, Collectable[Id]))
                nb += 1
        print("Collectable:", nb)

        nb = 0
        myMaterial = {}
        f.seek(0x22a78, 0)
        for i in range(150):
            r = f.read(8)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0':
                Id = int(x[:3], 16)
                Qte = int(x[12:-2], 16)
                myMaterial.update({Id: Qte})
                if filter is None or filter == Material[Id]: # print only is no filter or valid name
                    print('{:3}  {}'.format(Qte, Material[Id]))
                nb += 1
        print("Material:", nb)

        nb = 0
        f.seek(0x233d8, 0)
        for i in range(300):
            r = f.read(8)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0':
                Id = int(x[:3], 16)
                Qte = int(x[12:-2], 16)
                if filter is None or filter == KeyItem[Id]:  # print only is no filter or valid name
                    print('{:3}  {}'.format(Qte, KeyItem[Id]))
                nb += 1
        print("KeyItem:", nb)

def checkItemName(filter):
    """Checks if provided item name is valid and, if so, returns its category and index, or None is invalid"""
    validItem = None  # Provided item, by its name, is not valid at first glance
    for categoryName, items in AllItems.items():  # Loop on all categories
        if filter in items['list'].values():
            print("'{}' is a valid item name from '{}' category".format(filter, categoryName))
            for itemIndex, itemName in items['list'].items():  # Looking for the proper item
                if filter in itemName:
                    if debug: # show some details (item index)
                        print('{} item index: {}'.format(categoryName, itemIndex))
                    validItem = (categoryName, itemIndex)
    return validItem

def setItem(savefile, filter, nbItem):
    """Set the number of items with name to value if nbItem is superior to existing one"""
    filterItem = checkItemName(filter)
    if filterItem is None:
        print('{} is not a valid item name. Aborting.'.format(filter))
        sys.exit()
    myID = None # ID which corresponds to item name in Collectable, Materials or KeyItems dictionaries
    with open(savefile, 'rb') as f:
        nb = 0
        myCollectable = {}
        f.seek(0x22118, 0)
        for i in range(300):
            r = f.read(8)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0':
                Id = int(x[:3], 16)
                Qte = int(x[12:-2], 16)
                myCollectable.update({Id: Qte})
                if filter == Collectable[Id]: # print only is no filter or valid name
                    print('{:3}  {}'.format(Qte, Collectable[Id]))
                    myID = Id
                    myCollectable.update({myID: nbItem}) # set number of items
                nb += 1
        print("Collectable:", nb)

        nb = 0
        myMaterial = {}
        f.seek(0x22a78, 0)
        for i in range(150):
            r = f.read(8)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0':
                Id = int(x[:3], 16)
                Qte = int(x[12:-2], 16)
                myMaterial.update({Id: Qte})
                if filter == Material[Id]: # print only is no filter or valid name
                    print('{:3}  {}'.format(Qte, Material[Id]))
                    myID = Id
                    myMaterial.update({myID: nbItem}) # set number of items
                nb += 1
        print("Material:", nb)

        nb = 0
        f.seek(0x233d8, 0)
        for i in range(300):
            r = f.read(8)
            h = int.from_bytes(r, "big")
            x = hex(h)[2:]
            if x != '0':
                Id = int(x[:3], 16)
                Qte = int(x[12:-2], 16)
                if filter == KeyItem[Id]: # print only is no filter or valid name
                    print('{:3}  {}'.format(Qte, KeyItem[Id]))
                    myID = Id
                    print("Warning: this KeyItem will not be set to a different number. Not implemented yet.")
                nb += 1
        print("KeyItem:", nb)

    if len(myMaterial.items()) > 150:
        print("# Too many materials in inventory, aborting")
        sys.exit()
    if len(myCollectable.items()) > 300:
        print("# Too many collectables in inventory, aborting")
        sys.exit()

    pick = 2
    even = 0
    newMaterial = ''
    i = 0
    for item, cnt in myMaterial.items():
        i += 1
        pick += 1
        even += 2
        itm = str(hex(item)[-3:])
        newMaterial += itm + 'b' + '{:03x}'.format(even) + '00' + '{:03x}'.format(pick) + '{:02x}'.format(cnt) + '00'

    pick = 2
    even = 0
    newCollectable = ''
    i = 0
    for item, cnt in myCollectable.items():
        i += 1
        pick += 1
        even += 2
        itm = str(hex(item)[-3:])
        newCollectable += itm + 'b' + '{:03x}'.format(even) + '00' + '{:03x}'.format(pick) + '{:02x}'.format(cnt) + '00'

    newCollectable += (4800 - len(newCollectable)) * '0'
    newMaterial += (2400 - len(newMaterial)) * '0'
    with open(savefile, 'r+b') as f:
        f.seek(0x22118, 0)
        f.write(bytearray.fromhex(newCollectable))
        f.seek(0x22a78, 0)
        f.write(bytearray.fromhex(newMaterial))
    print('Item {} with ID {} is set to value {}'.format(filter,myID,nbItem) )


def main():
    """Main program which is executed when used as a program from a terminal"""
    assert (sys.version_info > (3, 0)) # python 3 only
    global debug # global variables defined at the beginning of the file
    # Reading command line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    available_commands = ('MaxGold','GetGold','SetGold',
                            'ListGems','ListItems','SetItem',
							'Housing1','Housing2','Housing3','Housing4','Housing5',
							'Commerce1','Commerce2','Commerce3','Commerce4','Commerce5',
							'Nature1','Nature2','Nature3','Nature4','Nature5',
							'Special1','Special2','Special3','Special4','Special5',
							'Replica1','Replica2','Replica3','Replica4','Replica5')
    parser.add_argument('-s', '--savefile',dest='savefile',default='monado01',choices=('monado01','monado02','monado03'),help='Save file to read data from or to write data to, e.g., monado01 which is the default choice.')
    parser.add_argument('-c', '--command',dest='command',default=None,choices=available_commands,help='Command, e.g., set maximum gold, list all gems and levels, list items, or add necessary collectables in order to be able to rebuild one part of Colony6 for a given level.')
    parser.add_argument('-f', '--filter',dest='filter',default=None,help='Filter list of items/collectables to the provided name.')
    parser.add_argument('-g', '--gold',dest='gold_amount',default=None,help='New gold amount value command is: SetGold (max=99999997).')
    parser.add_argument('-n', '--nb',dest='nb',default=None,help='Number of items to set with -c SetItem command and -f itemName filter.')
    parser.add_argument('-d', '--debug',dest='debug',action='store_true',help='Debug mode, which shows more information.')
    args = parser.parse_args()
    savefile = args.savefile
    command = args.command
    filter = args.filter
    gold_amount = args.gold_amount
    nb = args.nb
    if args.debug:
        debug = True
    else:
        debug = False
    if os.path.isfile(savefile): # Check savefile exists and is valid
        if os.stat(savefile).st_size != 163840:
            print("# Invalid savefile")
            sys.exit() 
    else:
        print("# Savefile not found")
        sys.exit()
    readsave(savefile)
    if command == 'MaxGold':
        gold(savefile)
    elif command == 'ListGems':
        gems(savefile)
    elif command in Colony6:
        colony6(savefile,command)
    elif command == 'GetGold':
        getGold(savefile)
    elif command == 'SetGold':
        if gold_amount is None:
            print("Gold amount is not provided. Please use -g argument")
            sys.exit() 
        elif int(gold_amount) > 99999997:
            print("Gold amount is more than maximum allowed : 99999997.")
            sys.exit()
        elif int(gold_amount) < 0:
            print("Gold amount has to be positive or null.")
            sys.exit()
        else:
            gold(savefile,int(gold_amount))
    elif command == 'ListItems':
        listItems(savefile, filter)
    elif command == 'SetItem':
        setItem(savefile,filter,int(nb))
    crc(savefile)
    print('Done')

if __name__ == '__main__':
    main()