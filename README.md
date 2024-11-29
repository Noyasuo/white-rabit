# White Rabbit Player

## Create Installer

1. Go to the main folder and activate the virtual environment

```shell
source venv/bin/activate
```

2. Create the Installer/DMG file
```shell
pyinstaller --name 'WhiteRabbit' --icon 'rabbit.png' --windowed white_rabbit_player.py
mkdir -p dist/dmg
cp -r "dist/WhiteRabbit.app" dist/dmg
create-dmg --volname "WhiteRabbit" --volicon "rabbit.png" --window-pos 200 120 --window-size 600 300 --icon-size 100 --icon "WhiteRabbit.app" 175 120 --hide-extension "WhiteRabbit.app" --app-drop-link 425 120 "dist/WhiteRabbit.dmg" "dist/dmg/"
```

3. Run the app using command:
```shell
open -a /Applications/WhiteRabbit.app --args <Audio file name here>
```

