# Android crypto UI sample

This sample contains two static Android screens implemented using both XML
layouts and Jetpack Compose. The component-based screens are test material for
PixelFit. Images are PNGs on a 375 × 812 canvas at 160 dpi.

The design is based on the [Crypto Trading App UI Kit (Community) in Figma](https://www.figma.com/design/80dwfUq05FwD4FRCY5GLon/Crypto-Trading-App-UI-Kit--Community-).
The Rewards illustrations in `app/src/main/res/drawable-nodpi/` were exported
from that design. Review the source design's terms before reusing its assets.

## Compare the supplied images

Run from the repository root:

```sh
python -m pixelfit samples/android-crypto/images/rewards-figma.png samples/android-crypto/images/rewards-xml.png --out pixelfit-out/rewards-xml
python -m pixelfit samples/android-crypto/images/rewards-figma.png samples/android-crypto/images/rewards-compose.png --out pixelfit-out/rewards-compose
python -m pixelfit samples/android-crypto/images/home-figma.png samples/android-crypto/images/home-xml.png --out pixelfit-out/home-xml
python -m pixelfit samples/android-crypto/images/home-figma.png samples/android-crypto/images/home-compose.png --out pixelfit-out/home-compose
```

`images/*-diff.png` are saved PixelFit overlays at the default threshold.
The Home and Rewards references were exported after the Figma font changes.
The generated screens use Android's Roboto. See [TEST_RESULTS.md](TEST_RESULTS.md)
for measured scores, observations, and the tolerance experiment.

The sample reproduces visual layouts. Home coin logos are text placeholders.
Status bar and navigation icons are incomplete; these and other layout
differences are visible in the comparison. Figma and Android text rendering
can differ even when the font family matches.

## Build and render

Install Android SDK Platform 35, JDK 21, and an Android emulator or device.
From this directory, run `./gradlew assembleDebug` (on Windows use
`gradlew.bat assembleDebug`), then install the resulting
`app/build/outputs/apk/debug/app-debug.apk`. The default screen is Home Compose.
Select a screen using an activity extra:

```sh
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -S -n com.example.pixelfitfixtures/.MainActivity --es screen xml
adb shell am start -S -n com.example.pixelfitfixtures/.MainActivity --es screen compose
adb shell am start -S -n com.example.pixelfitfixtures/.MainActivity --es screen rewards_xml
adb shell am start -S -n com.example.pixelfitfixtures/.MainActivity --es screen rewards_compose
```

The supplied captures were taken on an emulator configured to 375 × 836
pixels at 160 dpi, with the bottom 24-pixel emulator navigation strip cropped
from the screenshot. Text scale, OS font rendering, system navigation and
emulator configuration can affect a new capture. Restore any device display
settings you change for a capture.
