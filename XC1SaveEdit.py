#!/usr/bin/env python3
from crccheck.crc import CrcArc
from crccheck.checksum import Checksum16
import os, os.path
import sys, getopt
from itemlist import *

def readsave():
    with open(file, 'rb') as f:
        f.seek(0x22)
        r = f.read(8)
        a = int.from_bytes(r[2:4], "big")
        print('Save time: {}/{}/{} {}:{}:{}'.format(a, r[5], r[7], r[6], r[0], r[1]))
    
        f.seek(0xb264, 0)
        psn = f.read(4)
        psn = psn.hex()
        print('Location:', Maps.get(psn, "location unknown"))


def gold():
    gold_offset = 0x24048
    gold_amount = 0x05f5e0fd
    with open(file, 'r+b') as g:
        g.seek(gold_offset)
        g.write(gold_amount.to_bytes(4, "big")) 
    print('Max gold added')

def crc():
    offsets =  [0x20, 0xA030, 0xB260, 0x11EB0, 0x11EE0, 0x11F30, 0x11F60, 0x24090, 0x240C0, 0x240F0, 0x244A0, 0x248B0]
    sizes = [0x9C80, 0x1214, 0x6C28, 0xC, 0x34, 0x10, 0x12120, 0x10, 0x10, 0x384, 0x234, 0x40]
    section = ["THUM", "FLAG", "GAME", "TIME",  "PCPM",  "CAMD",  "ITEM",  "WTHR",  "SNDS",  "MINE",  "TBOX",  "OPTD"]
    for i in range(12):
        with open(file, 'rb') as f:
            f.seek(offsets[i]-4)
            r = f.read(sizes[i]+4) 
        crc_orig = int.from_bytes(r[:4], "big")
        data = r[4:]
        crc_calc = CrcArc.calc(data)
        if crc_calc != crc_orig:
            print(section[i], ': CRC FIXED') 
            with open(file, 'r+b') as g:
                g.seek(offsets[i]-4)
                g.write(crc_calc.to_bytes(4, "big")) 


def colony6(add):
    with open(file, 'rb') as f:  
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
    with open(file, 'r+b') as f:
        f.seek(0x22118, 0)
        f.write(bytearray.fromhex(newCollectable))
        f.seek(0x22a78, 0)
        f.write(bytearray.fromhex(newMaterial))
    print('Items added for', add)

def gems():
    with open(file, 'r+b') as f:
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

def start(argv):
    savefile = ''
    command = ''
    try:
        opts, args = getopt.getopt(argv,"hs:c:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('test.py -s <savefile> -c <command> [-h]')
        sys.exit()
    for opt, arg in opts:
        if opt == '-h' or len(sys.argv[1:]) != 4:
            print('Xenoblade Chronicles (Wii) Colony 6 Save Editor\n')
            print('XC1SaveEdit.py -s <savefile> -c <command>')
            print('  savefile: monado01 monado02 monado03')
            print('  command:  MaxGold ListGems Housing1 Commerce2 Nature3 Special4 Replica5\n')
            print('ex: to add the items needed to rebuild commerce level 3 in Colony 6: ')
            print('python3 XC1SaveEdit.py -s monado01 -c Commerce3')
            sys.exit()
        elif opt in ("-s", "--savefile"):
            savefile = arg
        elif opt in ("-c", "--command"):
            command = arg
    if os.path.isfile(savefile):
        if os.stat(savefile).st_size != 163840:
            print("# Invalid savefile")
            sys.exit() 
    else:
        print("# Savefile not found")
        print('test.py -s <savefile> -c <command> [-h]')
        sys.exit()
    return(savefile, command)  


if __name__ == '__main__':
    assert (sys.version_info > (3, 0)) # python 3 only
    file, command = start(sys.argv[1:])
    readsave()
    if command == 'MaxGold': gold()
    elif command == 'ListGems': gems()
    elif command in Colony6: colony6(command)
    else: print('# Command unknown')        
    crc()
    print('Done')

