# Xenoblade Chronicles (Wii) Colony 6 Save Editor
Add items needed to rebuild the colony 6 or change gold amount to max or desired value
  

XC1SaveEdit.py -s \<savefile\> -c \<command\>  
  *savefile*: monado01 monado02 monado03  
  *command*:  MaxGold ListGems Housing1 Commerce2 Nature3 Special4 Replica5  

ex: to add the items needed to rebuild commerce level 3 in Colony 6:  
```python3 XC1SaveEdit.py -s monado01 -c Commerce3```

```
usage: XC1SaveEdit.py [-h] [-s {monado01,monado02,monado03}]
                      [-c {MaxGold,GetGold,SetGold,ListGems,ListItems,Housing1,Housing2,Housing3,Housing4,Housing5,Commerce1,Commerce2,Commerce3,Commerce4,Commerce5,Nature1,Nature2,Nature3,Nature4,Nature5,Special1,Special2,Special3,Special4,Special5,Replica1,Replica2,Replica3,Replica4,Replica5}]
                      [-f FILTER] [-g GOLD_AMOUNT]

optional arguments:
  -h, --help            show this help message and exit
  -s {monado01,monado02,monado03}, --savefile {monado01,monado02,monado03}
                        Save file to read data from or to write data to, e.g.,
                        monado01 which is the default choice.
  -c {MaxGold,GetGold,SetGold,ListGems,ListItems,Housing1,Housing2,Housing3,Housing4,Housing5,Commerce1,Commerce2,Commerce3,Commerce4,Commerce5,Nature1,Nature2,Nature3,Nature4,Nature5,Special1,Special2,Special3,Special4,Special5,Replica1,Replica2,Replica3,Replica4,Replica5}, --command {MaxGold,GetGold,SetGold,ListGems,ListItems,Housing1,Housing2,Housing3,Housing4,Housing5,Commerce1,Commerce2,Commerce3,Commerce4,Commerce5,Nature1,Nature2,Nature3,Nature4,Nature5,Special1,Special2,Special3,Special4,Special5,Replica1,Replica2,Replica3,Replica4,Replica5}
                        Command, e.g., set maximum gold, list all gems and
                        levels, list items, or add necessary collectables in
                        order to be able to rebuild one part of Colony6 for a
                        given level.
  -f FILTER, --filter FILTER
                        Filter list of items/collectables to the provided
                        name.
  -g GOLD_AMOUNT, --gold GOLD_AMOUNT
                        New gold amount value command is: SetGold
                        (max=99999997).
```
