# portia-miner
Datamining utility for My Time at Portia

## Disclaimer
This script is by no means perfect-- it was originally created to gather a small amount of data, but has since grown. As a result, the code is currently a mish mash of many different things (so please forgive its inefficiencies).
In the future, the script will be optimized to run more quickly, and more documentation will be added to the script itself to make it easier to understand.
Feel free to make suggestions or point out problems, and we'll do what we can to address them soon.

## What you'll need
* [Eclipse](https://www.eclipse.org/downloads/) or similar software: To run the script and pull game data from the database
* [Notepad++](https://notepad-plus-plus.org/download/v7.6.3.html) (Recommended): For viewing the results of the script
* [DB Browser for SQLite](https://sqlitebrowser.org/dl/) or similar software (Optional): To browse the game database
* **portia-miner**: The script, which you can download here on this page

### How to navigate the files used by the script
1. Download portia-miner files.
2. Locate the folder **portia-miner** in the files that you downloaded.
3. Inside that folder, you will find the following important files:
   * **main.py** - This is the most important part of the script. It interfaces with the game's database to pull out game data.
   * **all.txt** - After the script finishes running, this is where you will find all of the data pulled from the game's database.
   * **datasets** folder - This contains subfolders, which in turn contain bits of code that correspond to the different types of game data to be pulled from the database. There is a subfolder for each of the following topics: Animals, BTS (Behind the Scenes), Characters, Commerce Guild, Cooking, Crafting, Dates/Minigames, Dialogue, Dungeons, Factory, Farming, Festivals, Fish, Furniture, Gathering, Gifting, House, Items, Map, Missions, Museum, Recycling, Relationship Mechanic, Shops, Skills, Spar, Treasure Chests, Weather

### How to view the game's database
1. Launch DB Browser for SQLite.
2. Select Open Database and locate the database in the game's files. (You will have to find this on your own through your own copy of the game.) To find it, follow this path on PC:
```
Local Disk (C:) > Program Files (x86) > Steam > steamapps > common > My Time at Portia > Portia_Data > Streaming Assets > CccData > LocalDb.bytes
```
3. Once you've opened the database, you can start browsing the many tables located in the database.

## Running the script
### How to run the full script
1. Download **portia-miner**.
2. Launch Eclipse and add the portia-miner folder to the Eclipse Explorer.
3. Find **main.py** in the Explorer and open it.
4. Run main.py and wait for the full script to run. (This will take some time.)
5. To view all of the script's results in one file, go to Windows Explorer, find **all.txt** in the portia-miner folder, and open it in Notepad++. You can view the results of individual sections of the script (e.g. "FishList"), by locating the appropriate text file in Windows Explorer and opening it (e.g. portia-miner > datasets > Fish > FishList.txt).

### How to run only the parts of the script that you want
1. Repeat steps 1-3 above.
2. Locate the following lines of code in **main.py**, near the end of the script:
```
"if __name__ == '__main__':
folder = os.path.join('datasets')
files = []
```
* If you leave the code above unchanged, the script will run on every folder and every file contained within the datasets folder. To narrow the scope of the script, you can specify a subfolder within the datasets folder, which will run the script on that subfolder only, or you can specify a file within the datasets folder, which will run the script on that file only.
* To specify a certain subfolder within "datasets", you can change the code like so (in this example, the subfolder is "Fish"):
```
"if __name__ == '__main__':
folder = os.path.join('datasets', 'Fish')
files = []
```
- To specify a certain file within "datasets", you can change the code like so (in this example, the file is "Fishlist", which is located in the subfolder "Fish"):
```
"if __name__ == '__main__':
folder = os.path.join('datasets', 'Fish')
files = ['FishList']
```

## Things to note while viewing the results of the script
* This script is a work in progress.
* Every time there is an update to the game, things change in the database, which sometimes breaks parts of the script. Most things in the script will continue to function. Feel free to let the owner know if you encounter new errors. 
* The database tends to be vague and requires interpretation, and we are still trying to understand certain areas of the database.
* You may notice that certain data labels in the script are marked with asterisks (** Example **). The asterisks simply point out that the owner of the script isn't 100% sure yet what the data attached to the label refers to, but it seems important enough that it should be included in the script anyway.
* The very last subfolder located in "datasets" is called "ztesting". This folder contains parts of the script that are broken, that may not be relevant, or that still need work before they can be useful. When they are ready to go, they will be moved to a non-testing subfolder. It is recommended that you disregard them until they are moved out of the testing folder.
